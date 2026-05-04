from datetime import date

from email_cleaner.imap_client import ImapClient
from email_cleaner.models import ScanRequest


class FakeConnection:
    def __init__(self, search_response=("OK", [b"1 2 3"])):
        self.search_response = search_response
        self.search_calls = []
        self.fetch_calls = []

    def login(self, username, password):
        return "OK", [b""]

    def select(self, mailbox, readonly=True):
        return "OK", [b""]

    def search(self, charset, *criteria):
        self.search_calls.append((charset, criteria))
        return self.search_response

    def fetch(self, message_id, query):
        self.fetch_calls.append((message_id, query))
        return "OK", []

    def close(self):
        return "OK", [b""]

    def logout(self):
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
        ),
        limit=2,
    )

    assert fake_connection.search_calls == [
        (
            None,
            ("FROM", '"Acme"', "SUBJECT", '"sale"', "SINCE", "03-May-2026"),
        )
    ]
    assert result == [b"3", b"2"]


def test_search_does_not_fetch_headers_for_local_sender_name_filtering(monkeypatch):
    fake_connection = FakeConnection()
    monkeypatch.setattr("email_cleaner.imap_client.imaplib.IMAP4_SSL", lambda host, port: fake_connection)
    client = ImapClient("imap.example.com", 993, "user@example.com", "secret")

    client.search(ScanRequest(from_query="store@example.com"), limit=3)

    assert fake_connection.fetch_calls == []
