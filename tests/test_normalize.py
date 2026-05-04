from email_cleaner.classifier import safe_classify
from email_cleaner.models import NormalizedEmail
from email_cleaner.normalize import normalize_email

RAW_HTML_EMAIL = b"""From: Example Store <store@example.com>\nSubject: =?utf-8?q?Big_Sale?=\nDate: Sun, 03 May 2026 10:00:00 +0000\nMessage-ID: <msg-1@example.com>\nContent-Type: text/html; charset=utf-8\nList-Unsubscribe: <mailto:unsubscribe@example.com>\n\n<html><body><h1>Big Sale</h1><p>Save 20% today only.</p></body></html>"""


def test_normalize_email_extracts_readable_html_snippet():
    normalized = normalize_email(RAW_HTML_EMAIL, 'fallback-id', 120)

    assert normalized.message_id == '<msg-1@example.com>'
    assert normalized.from_name == 'Example Store'
    assert normalized.from_email == 'store@example.com'
    assert normalized.subject == 'Big Sale'
    assert 'Big Sale Save 20% today only.' == normalized.snippet
    assert normalized.headers['List-Unsubscribe'] == '<mailto:unsubscribe@example.com>'


class BrokenClassifier:
    def classify(self, email):
        raise RuntimeError('provider unavailable')


def test_safe_classify_shapes_failures_as_uncertain():
    result = safe_classify(
        BrokenClassifier(),
        NormalizedEmail(message_id='1', snippet='snippet'),
    )

    assert result.label == 'uncertain'
    assert 'Classification unavailable' in result.reason
