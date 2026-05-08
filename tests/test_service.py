from __future__ import annotations

from contextlib import contextmanager

import pytest

from email_cleaner.models import ClassificationResult, NormalizedEmail, ScanRequest
from email_cleaner.service import ClassifierNotConfiguredError, ScanService


class FakeScanSession:
    def __init__(self, messages):
        self._messages = messages
        self.moves = []

    def __iter__(self):
        return iter(self._messages)

    def move_message(self, message_id, destination_folder):
        self.moves.append((message_id, destination_folder))


class FakeImapClient:
    def __init__(self, messages):
        self.messages = messages
        self.closed = False
        self.entered = False
        self.exited = False
        self.readonly_arguments = []
        self.session = FakeScanSession(messages)

    @contextmanager
    def scan_messages(self, request, limit, *, readonly):
        self.entered = True
        self.readonly_arguments.append(readonly)
        try:
            yield self.session
        finally:
            self.closed = True
            self.exited = True


class FakeClassifier:
    def __init__(self, classifications=None, error=None):
        self.classifications = iter(classifications or [])
        self.error = error
        self.calls = []

    def classify(self, email):
        self.calls.append(email.message_id)
        if self.error is not None:
            raise self.error
        return next(self.classifications)


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

    monkeypatch.setattr("email_cleaner.service.normalize_email", fake_normalize_email)
    classifier = FakeClassifier([ClassificationResult(label="keep", reason="Looks important")] * 2)
    monkeypatch.setattr(
        "email_cleaner.service.safe_classify",
        lambda classifier_instance, email: observed_session_state.append((email.message_id, "classified", imap_client.closed))
        or classifier_instance.classify(email),
    )

    service._classifier = classifier

    response = service.scan(ScanRequest(from_query="store@example.com", mode="classify"))

    assert imap_client.entered is True
    assert imap_client.exited is True
    assert imap_client.readonly_arguments == [True]
    assert observed_session_state == [
        (b"raw-1", "1", 120, False),
        ("1", "classified", False),
        (b"raw-2", "2", 120, False),
        ("2", "classified", False),
    ]
    assert response.count == 2
    assert response.mode == "classify"
    assert response.applied_count == 0
    assert response.stages.model_dump() == {"searched": True, "classified": True, "applied": False}
    assert [item.message_id for item in response.results] == ["1", "2"]


def test_resolve_destination_folder_maps_labels():
    service = ScanService(
        imap_client=FakeImapClient([]),
        classifier=FakeClassifier(),
        snippet_length=120,
        default_limit=10,
        max_limit=25,
    )

    assert service._resolve_destination_folder("move") == "promo"
    assert service._resolve_destination_folder("uncertain") == "promo-check"
    assert service._resolve_destination_folder("keep") is None


def test_search_mode_skips_classifier_entirely(monkeypatch):
    imap_client = FakeImapClient([(b"1", b"raw-1"), (b"2", b"raw-2")])
    classifier = FakeClassifier(error=AssertionError("classifier should not be used"))
    service = ScanService(
        imap_client=imap_client,
        classifier=classifier,
        snippet_length=120,
        default_limit=10,
        max_limit=25,
    )

    monkeypatch.setattr(
        "email_cleaner.service.normalize_email",
        lambda raw_message, message_id, snippet_length: NormalizedEmail(
            message_id=message_id,
            subject=f"Subject {message_id}",
            snippet=f"Snippet {message_id}",
            classifier_input=f"Classifier input {message_id}",
        ),
    )

    response = service.scan(ScanRequest(from_query="store@example.com", mode="search"))

    assert imap_client.readonly_arguments == [True]
    assert imap_client.session.moves == []
    assert response.applied_count == 0
    assert response.stages.model_dump() == {"searched": True, "classified": False, "applied": False}
    assert classifier.calls == []
    assert [item.classification_status for item in response.results] == ["not_classified", "not_classified"]
    assert [item.action_reason for item in response.results] == ["search only", "search only"]


def test_classify_mode_uses_read_only_imap_and_suggests_moves(monkeypatch):
    imap_client = FakeImapClient([(b"1", b"raw-1"), (b"2", b"raw-2"), (b"3", b"raw-3")])
    classifier = FakeClassifier(
        [
            ClassificationResult(label="move", reason="Promo"),
            ClassificationResult(label="uncertain", reason="Needs review"),
            ClassificationResult(label="keep", reason="Important"),
        ]
    )
    service = ScanService(
        imap_client=imap_client,
        classifier=classifier,
        snippet_length=120,
        default_limit=10,
        max_limit=25,
    )

    monkeypatch.setattr(
        "email_cleaner.service.normalize_email",
        lambda raw_message, message_id, snippet_length: NormalizedEmail(
            message_id=message_id,
            subject=f"Subject {message_id}",
            snippet=f"Snippet {message_id}",
            classifier_input=f"Classifier input {message_id}",
        ),
    )

    response = service.scan(ScanRequest(from_query="store@example.com", mode="classify"))

    assert imap_client.readonly_arguments == [True]
    assert imap_client.session.moves == []
    assert response.mode == "classify"
    assert response.applied_count == 0
    assert response.stages.model_dump() == {"searched": True, "classified": True, "applied": False}
    assert [item.action for item in response.results] == ["suggested_move", "suggested_move", "none"]
    assert [item.action_reason for item in response.results] == [
        "analysis only",
        "analysis only",
        "label keep",
    ]


def test_clean_mode_moves_only_moveable_labels(monkeypatch):
    imap_client = FakeImapClient([(b"1", b"raw-1"), (b"2", b"raw-2"), (b"3", b"raw-3")])
    classifier = FakeClassifier(
        [
            ClassificationResult(label="move", reason="Promo"),
            ClassificationResult(label="uncertain", reason="Needs review"),
            ClassificationResult(label="keep", reason="Important"),
        ]
    )
    service = ScanService(
        imap_client=imap_client,
        classifier=classifier,
        snippet_length=120,
        default_limit=10,
        max_limit=25,
    )

    monkeypatch.setattr(
        "email_cleaner.service.normalize_email",
        lambda raw_message, message_id, snippet_length: NormalizedEmail(
            message_id=message_id,
            subject=f"Subject {message_id}",
            snippet=f"Snippet {message_id}",
            classifier_input=f"Classifier input {message_id}",
        ),
    )

    response = service.scan(ScanRequest(from_query="store@example.com", mode="clean"))

    assert imap_client.readonly_arguments == [False]
    assert imap_client.session.moves == [(b"1", "promo"), (b"2", "promo-check")]
    assert response.mode == "clean"
    assert response.applied_count == 2
    assert response.stages.model_dump() == {"searched": True, "classified": True, "applied": True}
    assert [item.action for item in response.results] == ["moved", "moved", "none"]
    assert [item.action_reason for item in response.results] == [
        "moved to promo",
        "moved to promo-check",
        "label keep",
    ]


def test_classifier_availability_is_checked_before_scan_starts():
    imap_client = FakeImapClient([])
    service = ScanService(
        imap_client=imap_client,
        classifier=None,
        snippet_length=120,
        default_limit=10,
        max_limit=25,
    )

    with pytest.raises(ClassifierNotConfiguredError, match="Classifier is not configured"):
        service.scan(ScanRequest(from_query="store@example.com", mode="clean"))

    assert imap_client.entered is False


def test_infrastructure_classification_failure_aborts_clean_before_moves(monkeypatch):
    imap_client = FakeImapClient([(b"1", b"raw-1")])
    service = ScanService(
        imap_client=imap_client,
        classifier=FakeClassifier(error=RuntimeError("anthropic unavailable")),
        snippet_length=120,
        default_limit=10,
        max_limit=25,
    )

    monkeypatch.setattr(
        "email_cleaner.service.normalize_email",
        lambda raw_message, message_id, snippet_length: NormalizedEmail(
            message_id=message_id,
            subject=f"Subject {message_id}",
            snippet=f"Snippet {message_id}",
            classifier_input=f"Classifier input {message_id}",
        ),
    )

    with pytest.raises(RuntimeError, match="anthropic unavailable"):
        service.scan(ScanRequest(from_query="store@example.com", mode="clean"))

    assert imap_client.session.moves == []
