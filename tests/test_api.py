def test_root_serves_static_ui(client):
    response = client.get('/')

    assert response.status_code == 200
    assert b'<script src="/app.js"></script>' in response.data
    assert b'name="from_query"' in response.data
    assert b'name="before_date"' in response.data
    assert b'name="mode"' in response.data
    assert b'Search only' in response.data
    assert b'Classify' in response.data
    assert b'Clean' in response.data
    assert b'On or after the date' in response.data
    assert b'Before the date' in response.data
    assert b'label-select' not in response.data
    assert b'name="from_email"' not in response.data
    assert b'name="from_name_contains"' not in response.data
    assert b'{{' not in response.data


def test_static_app_asset_uses_api_routes_only(client):
    response = client.get('/app.js')

    assert response.status_code == 200
    assert b"fetch('/api/scan'" in response.data
    assert b'label-select' not in response.data
    assert b'render_template' not in response.data


def test_health_endpoint(client):
    response = client.get('/api/health')

    assert response.status_code == 200
    assert response.get_json() == {'status': 'ok'}


def test_scan_requires_search_criteria(client):
    response = client.post('/api/scan', json={'limit': 5})
    body = response.get_json()

    assert response.status_code == 400
    assert body['error']['code'] == 'validation_error'
    assert 'At least one search criterion is required' in str(body['error']['details'])


def test_scan_accepts_blank_since_date_with_other_search_criterion(client):
    response = client.post(
        '/api/scan',
        json={'from_query': 'store@example.com', 'since_date': ''},
    )
    body = response.get_json()

    assert response.status_code == 200
    assert body['count'] == 1
    assert body['mode'] == 'classify'
    assert body['applied_count'] == 0


def test_scan_rejects_blank_since_date_without_other_search_criteria(client):
    response = client.post('/api/scan', json={'since_date': '', 'limit': 5})
    body = response.get_json()

    assert response.status_code == 400
    assert body['error']['code'] == 'validation_error'
    assert 'At least one search criterion is required' in str(body['error']['details'])


def test_scan_accepts_before_date(client):
    response = client.post('/api/scan', json={'before_date': '2026-05-05'})
    body = response.get_json()

    assert response.status_code == 200
    assert body['count'] == 1


def test_scan_rejects_blank_date_fields_without_other_search_criteria(client):
    response = client.post('/api/scan', json={'since_date': '', 'before_date': ''})
    body = response.get_json()

    assert response.status_code == 400
    assert body['error']['code'] == 'validation_error'
    assert 'At least one search criterion is required' in str(body['error']['details'])


def test_scan_rejects_invalid_date_window(client):
    response = client.post(
        '/api/scan',
        json={'since_date': '2026-05-05', 'before_date': '2026-05-05'},
    )
    body = response.get_json()

    assert response.status_code == 400
    assert body['error']['code'] == 'validation_error'
    assert 'before_date must be later than since_date' in str(body['error']['details'])


def test_scan_returns_structured_results(client):
    response = client.post('/api/scan', json={'from_query': 'store@example.com'})
    body = response.get_json()

    assert response.status_code == 200
    assert body['count'] == 1
    assert body['mode'] == 'classify'
    assert body['applied_count'] == 0
    assert body['stages'] == {'searched': True, 'classified': True, 'applied': False}
    assert body['results'][0]['classification_status'] == 'classified'
    assert body['results'][0]['label'] == 'move'
    assert body['results'][0]['reason'] == 'Promotional sale content'
    assert body['results'][0]['target_folder'] == 'promo'
    assert body['results'][0]['action'] == 'suggested_move'
    assert body['results'][0]['action_reason'] == 'analysis only'


def test_scan_defaults_mode_to_classify(client):
    response = client.post('/api/scan', json={'from_query': 'store@example.com'})
    body = response.get_json()

    assert response.status_code == 200
    assert body['mode'] == 'classify'


def test_scan_accepts_search_mode(client, app):
    from email_cleaner.models import ScanResponse, ScanResultItem, ScanStages

    class SearchScanService:
        def scan(self, request):
            assert request.mode == 'search'
            return ScanResponse(
                count=1,
                mode='search',
                applied_count=0,
                stages=ScanStages(searched=True, classified=False, applied=False),
                results=[
                    ScanResultItem(
                        message_id='abc',
                        snippet='Buy now',
                        headers={},
                        classification_status='not_classified',
                        action='none',
                        action_reason='search only',
                    )
                ],
            )

    app.extensions['scan_service'] = SearchScanService()

    response = client.post('/api/scan', json={'from_query': 'store@example.com', 'mode': 'search'})
    body = response.get_json()

    assert response.status_code == 200
    assert body['results'][0]['classification_status'] == 'not_classified'
    assert body['results'][0]['label'] is None
    assert body['results'][0]['action_reason'] == 'search only'


def test_scan_rejects_unknown_mode(client):
    response = client.post('/api/scan', json={'from_query': 'store@example.com', 'mode': 'archive'})
    body = response.get_json()

    assert response.status_code == 400
    assert body['error']['code'] == 'validation_error'


def test_scan_returns_classifier_not_configured_error(app):
    from email_cleaner.service import ClassifierNotConfiguredError

    class MissingClassifierScanService:
        def scan(self, request):
            raise ClassifierNotConfiguredError('Classifier is not configured')

    app.extensions['scan_service'] = MissingClassifierScanService()
    client = app.test_client()

    response = client.post('/api/scan', json={'from_query': 'store@example.com', 'mode': 'clean'})
    body = response.get_json()

    assert response.status_code == 503
    assert body['error']['code'] == 'classifier_not_configured'
    assert body['error']['details'][0]['msg'] == 'Classifier is not configured'


def test_scan_returns_json_when_service_fails(app):
    class FailingScanService:
        def scan(self, request):
            raise RuntimeError('imap unavailable')

    app.extensions['scan_service'] = FailingScanService()
    client = app.test_client()

    response = client.post('/api/scan', json={'from_query': 'store@example.com'})
    body = response.get_json()

    assert response.status_code == 502
    assert body['error']['code'] == 'scan_failed'
    assert body['error']['details'][0]['msg'] == 'imap unavailable'


def test_scan_rejects_obsolete_sender_fields(client):
    response = client.post('/api/scan', json={'from_email': 'store@example.com'})
    body = response.get_json()

    assert response.status_code == 400
    assert body['error']['code'] == 'validation_error'
    assert 'Extra inputs are not permitted' in str(body['error']['details'])
