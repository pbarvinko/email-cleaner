from email.message import EmailMessage

from email_cleaner.classifier import safe_classify
from email_cleaner.models import NormalizedEmail
from email_cleaner.normalize import normalize_email

RAW_HTML_EMAIL = b"""From: Example Store <store@example.com>\nSubject: =?utf-8?q?Big_Sale?=\nDate: Sun, 03 May 2026 10:00:00 +0000\nMessage-ID: <msg-1@example.com>\nContent-Type: text/html; charset=utf-8\nList-Unsubscribe: <mailto:unsubscribe@example.com>\n\n<html><body><h1>Big Sale</h1><p>Save 20% today only.</p></body></html>"""


def _message_bytes(*, plain_parts: list[str] | None = None, html_parts: list[str] | None = None) -> bytes:
    message = EmailMessage()
    message["From"] = "Example Store <store@example.com>"
    message["Subject"] = "Big Sale"
    message["Date"] = "Sun, 03 May 2026 10:00:00 +0000"
    message["Message-ID"] = "<msg-1@example.com>"

    plain_parts = plain_parts or []
    html_parts = html_parts or []

    if html_parts:
        message.set_content(plain_parts[0] if plain_parts else "")
        message.add_alternative(html_parts[0], subtype="html")
        for plain_part in plain_parts[1:]:
            message.attach(EmailMessage())
            message.get_payload()[-1].set_content(plain_part)
        for html_part in html_parts[1:]:
            message.attach(EmailMessage())
            message.get_payload()[-1].set_content(html_part, subtype="html")
    elif plain_parts:
        if len(plain_parts) == 1:
            message.set_content(plain_parts[0])
        else:
            message.make_mixed()
            for plain_part in plain_parts:
                part = EmailMessage()
                part.set_content(plain_part)
                message.attach(part)
    else:
        message.set_content("")

    return message.as_bytes()


def test_normalize_email_prefers_clean_plain_text_snippet():
    normalized = normalize_email(
        _message_bytes(plain_parts=["Readable order update", "Second readable paragraph"]),
        "fallback-id",
        120,
    )

    assert normalized.snippet == "Readable order update Second readable paragraph"
    assert normalized.classifier_input == "Readable order update Second readable paragraph"


def test_normalize_email_excludes_noisy_plain_text_parts_when_clean_text_exists():
    normalized = normalize_email(
        _message_bytes(
            plain_parts=[
                "Readable order update",
                "FONT-FAMILY: Arial; color: #333; line-height: 18px;",
            ],
            html_parts=["<p>HTML fallback</p>"],
        ),
        "fallback-id",
        120,
    )

    assert normalized.snippet == "Readable order update"


def test_normalize_email_falls_back_to_readable_html_text_when_plain_text_is_noisy():
    normalized = normalize_email(
        _message_bytes(
            plain_parts=["font-family: Arial; color: #333;"],
            html_parts=["<h1>Big Sale</h1><p>Save 20% today only.</p>"],
        ),
        "fallback-id",
        120,
    )

    assert normalized.snippet == "Big Sale Save 20% today only."
    assert normalized.classifier_input == "# Big Sale\n\nSave 20% today only."


def test_normalize_email_falls_back_to_html_when_plain_text_is_whitespace_only():
    normalized = normalize_email(
        _message_bytes(
            plain_parts=["   \n\t  "],
            html_parts=["<h1>Big Sale</h1><p>Save 20% today only.</p>"],
        ),
        "fallback-id",
        120,
    )

    assert normalized.snippet == "Big Sale Save 20% today only."


def test_normalize_email_matches_noisy_markers_case_insensitively():
    normalized = normalize_email(
        _message_bytes(
            plain_parts=["MSO-LINE-HEIGHT-RULE: exactly;"],
            html_parts=["<p>Readable fallback</p>"],
        ),
        "fallback-id",
        120,
    )

    assert normalized.snippet == "Readable fallback"


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
        NormalizedEmail(message_id='1', snippet='snippet', classifier_input='snippet'),
    )

    assert result.label == 'uncertain'
    assert 'Classification unavailable' in result.reason
