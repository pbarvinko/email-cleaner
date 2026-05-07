from __future__ import annotations

from contextlib import contextmanager

from email_cleaner.models import ClassificationResult, NormalizedEmail, ScanRequest
from email_cleaner.service import ScanService


class FakeImapClient:
    def __init__(self, messages):
        self.messages = messages
        self.closed = False
        self.entered = False
        self.exited = False

    @contextmanager
    def scan_messages(self, request, limit):
        self.entered = True
        try:
            yield iter(self.messages)
        finally:
            self.closed = True
            self.exited = True


class FakeClassifier:
    pass


def test_scan_processes_messages_before_shared_imap_session_closes(monkeypatch):
    imap_client = FakeImapClient([(b"1", b"raw-1"), (b"2", b"raw-2")])
    service = ScanService(
        imap_client=imap_client,
        classifier=FakeClassifier(),
        snippet_length=120,
        default_limit=10,
        max_limit=25,
    )
    observed_session_state = []

    def fake_normalize_email(raw_message, message_id, snippet_length):
        observed_session_state.append((raw_message, message_id, snippet_length, imap_client.closed))
        return NormalizedEmail(
            message_id=message_id,
            subject=f"Subject {message_id}",
            snippet=f"Snippet {message_id}",
            classifier_input=f"Classifier input {message_id}",
        )

    def fake_safe_classify(classifier, email):
        observed_session_state.append((email.message_id, "classified", imap_client.closed))
        return ClassificationResult(label="keep", reason="Looks important")

    monkeypatch.setattr("email_cleaner.service.normalize_email", fake_normalize_email)
    monkeypatch.setattr("email_cleaner.service.safe_classify", fake_safe_classify)

    response = service.scan(ScanRequest(from_query="store@example.com"))

    assert imap_client.entered is True
    assert imap_client.exited is True
    assert observed_session_state == [
        (b"raw-1", "1", 120, False),
        ("1", "classified", False),
        (b"raw-2", "2", 120, False),
        ("2", "classified", False),
    ]
    assert response.count == 2
    assert [item.message_id for item in response.results] == ["1", "2"]
