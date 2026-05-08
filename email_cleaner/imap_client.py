from __future__ import annotations

import imaplib
from collections.abc import Iterator
from contextlib import contextmanager

from .models import ScanRequest


class MailboxSearchFailed(RuntimeError):
    pass


class MailboxFetchFailed(RuntimeError):
    pass


class MailboxMoveFailed(RuntimeError):
    pass


class ImapScanSession:
    def __init__(self, connection, message_ids: list[bytes]):
        self._connection = connection
        self._message_ids = message_ids

    def __iter__(self) -> Iterator[tuple[bytes, bytes]]:
        for message_id in self._message_ids:
            yield message_id, self._fetch_message(message_id)

    def _fetch_message(self, message_id: bytes) -> bytes:
        status, data = self._connection.fetch(message_id, "(RFC822)")
        if status != "OK" or not data or not isinstance(data[0], tuple):
            raise MailboxFetchFailed("IMAP fetch failed")
        return data[0][1]

    def move_message(self, message_id: bytes, destination_folder: str) -> None:
        copy_status, _ = self._connection.copy(message_id, destination_folder)
        if copy_status != "OK":
            raise MailboxMoveFailed("IMAP move failed")

        store_status, _ = self._connection.store(message_id, "+FLAGS", "(\\Deleted)")
        if store_status != "OK":
            raise MailboxMoveFailed("IMAP move failed")

        expunge_status, _ = self._connection.expunge()
        if expunge_status != "OK":
            raise MailboxMoveFailed("IMAP move failed")


class ImapClient:
    def __init__(self, host: str, port: int, username: str, password: str):
        self._host = host
        self._port = port
        self._username = username
        self._password = password

    @contextmanager
    def _connection(self, *, readonly: bool):
        connection = imaplib.IMAP4_SSL(self._host, self._port)
        try:
            connection.login(self._username, self._password)
            connection.select("INBOX", readonly=readonly)
            yield connection
        finally:
            try:
                connection.close()
            except Exception:
                pass
            try:
                connection.logout()
            except Exception:
                pass

    def _build_search_criteria(self, request: ScanRequest) -> list[str]:
        criteria = []
        if request.from_query:
            criteria.extend(["FROM", f'"{request.from_query}"'])
        if request.subject_contains:
            criteria.extend(["SUBJECT", f'"{request.subject_contains}"'])
        if request.since_date:
            criteria.extend(["SINCE", request.since_date.strftime("%d-%b-%Y")])
        if request.before_date:
            criteria.extend(["BEFORE", request.before_date.strftime("%d-%b-%Y")])
        return criteria

    def _search(self, connection, request: ScanRequest, limit: int) -> list[bytes]:
        criteria = self._build_search_criteria(request)
        status, data = connection.search(None, *criteria)
        if status != "OK":
            raise MailboxSearchFailed("IMAP search failed")

        ids = data[0].split()
        return list(reversed(ids[-limit:]))

    def _fetch_message(self, connection, message_id: bytes) -> bytes:
        status, data = connection.fetch(message_id, "(RFC822)")
        if status != "OK" or not data or not isinstance(data[0], tuple):
            raise MailboxFetchFailed("IMAP fetch failed")
        return data[0][1]

    def search(self, request: ScanRequest, limit: int) -> list[bytes]:
        with self._connection(readonly=True) as connection:
            return self._search(connection, request, limit)

    def fetch_message(self, message_id: bytes) -> bytes:
        with self._connection(readonly=True) as connection:
            return self._fetch_message(connection, message_id)

    @contextmanager
    def scan_messages(self, request: ScanRequest, limit: int, *, readonly: bool) -> Iterator[ImapScanSession]:
        with self._connection(readonly=readonly) as connection:
            message_ids = self._search(connection, request, limit)
            yield ImapScanSession(connection, message_ids)
