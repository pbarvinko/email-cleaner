from datetime import date

import pytest

from email_cleaner.imap_client import ImapClient, MailboxFetchFailed, MailboxMoveFailed
from email_cleaner.models import ScanRequest


class FakeConnection:
    def __init__(
        self,
        search_response=("OK", [b"1 2 3"]),
        fetch_responses=None,
        copy_response=("OK", [b""]),
        store_response=("OK", [b""]),
        expunge_response=("OK", [b""]),
    ):
        self.search_response = search_response
        self.fetch_responses = fetch_responses or {}
        self.copy_response = copy_response
        self.store_response = store_response
        self.expunge_response = expunge_response
        self.login_calls = []
        self.select_calls = []
        self.search_calls = []
        self.fetch_calls = []
        self.copy_calls = []
        self.store_calls = []
        self.expunge_calls = 0
        self.close_calls = 0
        self.logout_calls = 0

    def login(self, username, password):
        self.login_calls.append((username, password))
        return "OK", [b""]

    def select(self, mailbox, readonly=True):
        self.select_calls.append((mailbox, readonly))
        return "OK", [b""]

    def search(self, charset, *criteria):
        self.search_calls.append((charset, criteria))
        return self.search_response

    def fetch(self, message_id, query):
        self.fetch_calls.append((message_id, query))
        return self.fetch_responses.get(message_id, ("OK", []))

    def copy(self, message_id, destination_folder):
        self.copy_calls.append((message_id, destination_folder))
        return self.copy_response

    def store(self, message_id, command, flags):
        self.store_calls.append((message_id, command, flags))
        return self.store_response

    def expunge(self):
        self.expunge_calls += 1
        return self.expunge_response

    def close(self):
        self.close_calls += 1
        return "OK", [b""]

    def logout(self):
        self.logout_calls += 1
        return "BYE", [b""]


def test_search_maps_from_query_directly_to_imap_from(monkeypatch):
    fake_connection = FakeConnection()
    monkeypatch.setattr("email_cleaner.imap_client.imaplib.IMAP4_SSL", lambda host, port: fake_connection)
    client = ImapClient("imap.example.com", 993, "user@example.com", "secret")

    result = client.search(
        ScanRequest(
            from_query="Acme",
            subject_contains="sale",
            since_date=date(2026, 5, 3),
            before_date=date(2026, 5, 5),
        ),
        limit=2,
    )

    assert fake_connection.search_calls == [
        (
            None,
            ("FROM", '"Acme"', "SUBJECT", '"sale"', "SINCE", "03-May-2026", "BEFORE", "05-May-2026"),
        )
    ]
    assert result == [b"3", b"2"]


def test_search_does_not_fetch_headers_for_local_sender_name_filtering(monkeypatch):
    fake_connection = FakeConnection()
    monkeypatch.setattr("email_cleaner.imap_client.imaplib.IMAP4_SSL", lambda host, port: fake_connection)
    client = ImapClient("imap.example.com", 993, "user@example.com", "secret")

    client.search(ScanRequest(from_query="store@example.com"), limit=3)

    assert fake_connection.fetch_calls == []


def test_scan_messages_reuses_single_read_only_connection_for_search_and_fetches(monkeypatch):
    fake_connection = FakeConnection(
        fetch_responses={
            b"3": ("OK", [(b"3", b"message-3")]),
            b"2": ("OK", [(b"2", b"message-2")]),
        }
    )
    connection_creations = []

    def make_connection(host, port):
        connection_creations.append((host, port))
        return fake_connection

    monkeypatch.setattr("email_cleaner.imap_client.imaplib.IMAP4_SSL", make_connection)
    client = ImapClient("imap.example.com", 993, "user@example.com", "secret")

    with client.scan_messages(ScanRequest(from_query="store@example.com"), limit=2, readonly=True) as messages:
        assert fake_connection.close_calls == 0
        assert fake_connection.logout_calls == 0
        result = list(messages)

    assert connection_creations == [("imap.example.com", 993)]
    assert fake_connection.login_calls == [("user@example.com", "secret")]
    assert fake_connection.select_calls == [("INBOX", True)]
    assert fake_connection.search_calls == [(None, ("FROM", '"store@example.com"'))]
    assert fake_connection.fetch_calls == [(b"3", "(RFC822)"), (b"2", "(RFC822)")]
    assert result == [(b"3", b"message-3"), (b"2", b"message-2")]
    assert fake_connection.close_calls == 1
    assert fake_connection.logout_calls == 1


def test_scan_messages_opens_read_write_connection_in_clean_mode(monkeypatch):
    fake_connection = FakeConnection(fetch_responses={b"3": ("OK", [(b"3", b"message-3")])})
    monkeypatch.setattr("email_cleaner.imap_client.imaplib.IMAP4_SSL", lambda host, port: fake_connection)
    client = ImapClient("imap.example.com", 993, "user@example.com", "secret")

    with client.scan_messages(ScanRequest(from_query="store@example.com", mode="clean"), limit=1, readonly=False) as messages:
        assert list(messages) == [(b"3", b"message-3")]

    assert fake_connection.select_calls == [("INBOX", False)]


def test_scan_messages_cleans_up_connection_when_fetch_fails(monkeypatch):
    fake_connection = FakeConnection(
        search_response=("OK", [b"7"]),
        fetch_responses={b"7": ("NO", [b"fetch failed"])}
    )
    monkeypatch.setattr("email_cleaner.imap_client.imaplib.IMAP4_SSL", lambda host, port: fake_connection)
    client = ImapClient("imap.example.com", 993, "user@example.com", "secret")

    with pytest.raises(MailboxFetchFailed, match="IMAP fetch failed"):
        with client.scan_messages(ScanRequest(from_query="store@example.com"), limit=1, readonly=True) as messages:
            list(messages)

    assert fake_connection.select_calls == [("INBOX", True)]
    assert fake_connection.close_calls == 1
    assert fake_connection.logout_calls == 1


def test_scan_session_move_message_performs_imap_move_mechanics(monkeypatch):
    fake_connection = FakeConnection(fetch_responses={b"3": ("OK", [(b"3", b"message-3")])})
    monkeypatch.setattr("email_cleaner.imap_client.imaplib.IMAP4_SSL", lambda host, port: fake_connection)
    client = ImapClient("imap.example.com", 993, "user@example.com", "secret")

    with client.scan_messages(ScanRequest(from_query="store@example.com", mode="clean"), limit=1, readonly=False) as session:
        session.move_message(b"3", "promo")

    assert fake_connection.copy_calls == [(b"3", "promo")]
    assert fake_connection.store_calls == [(b"3", "+FLAGS", "(\\Deleted)")]
    assert fake_connection.expunge_calls == 1


def test_scan_session_move_message_raises_when_copy_fails(monkeypatch):
    fake_connection = FakeConnection(copy_response=("NO", [b"copy failed"]))
    monkeypatch.setattr("email_cleaner.imap_client.imaplib.IMAP4_SSL", lambda host, port: fake_connection)
    client = ImapClient("imap.example.com", 993, "user@example.com", "secret")

    with pytest.raises(MailboxMoveFailed, match="IMAP move failed"):
        with client.scan_messages(ScanRequest(from_query="store@example.com", mode="clean"), limit=1, readonly=False) as session:
            session.move_message(b"3", "promo")
