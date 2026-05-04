def test_root_serves_static_ui(client):
    response = client.get('/')

    assert response.status_code == 200
    assert b'<script src="/app.js"></script>' in response.data
    assert b'name="from_query"' in response.data
    assert b'name="from_email"' not in response.data
    assert b'name="from_name_contains"' not in response.data
    assert b'{{' not in response.data


def test_static_app_asset_uses_api_routes_only(client):
    response = client.get('/app.js')

    assert response.status_code == 200
    assert b"fetch('/api/scan'" in response.data
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


def test_scan_rejects_blank_since_date_without_other_search_criteria(client):
    response = client.post('/api/scan', json={'since_date': '', 'limit': 5})
    body = response.get_json()

    assert response.status_code == 400
    assert body['error']['code'] == 'validation_error'
    assert 'At least one search criterion is required' in str(body['error']['details'])


def test_scan_returns_structured_results(client):
    response = client.post('/api/scan', json={'from_query': 'store@example.com'})
    body = response.get_json()

    assert response.status_code == 200
    assert body['count'] == 1
    assert body['results'][0]['label'] == 'move'
    assert body['results'][0]['reason'] == 'Promotional sale content'


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
