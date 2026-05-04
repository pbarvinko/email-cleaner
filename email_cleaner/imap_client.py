from __future__ import annotations

import imaplib
from contextlib import contextmanager

from .models import ScanRequest


class ImapClient:
    def __init__(self, host: str, port: int, username: str, password: str):
        self._host = host
        self._port = port
        self._username = username
        self._password = password

    @contextmanager
    def _connection(self):
        connection = imaplib.IMAP4_SSL(self._host, self._port)
        try:
            connection.login(self._username, self._password)
            connection.select("INBOX", readonly=True)
            yield connection
        finally:
            try:
                connection.close()
            except Exception:
                pass
            connection.logout()

    def search(self, request: ScanRequest, limit: int) -> list[bytes]:
        criteria = []
        if request.from_query:
            criteria.extend(["FROM", f'"{request.from_query}"'])
        if request.subject_contains:
            criteria.extend(["SUBJECT", f'"{request.subject_contains}"'])
        if request.since_date:
            criteria.extend(["SINCE", request.since_date.strftime("%d-%b-%Y")])

        with self._connection() as connection:
            status, data = connection.search(None, *criteria)
            if status != "OK":
                raise RuntimeError("IMAP search failed")

            ids = data[0].split()
            return list(reversed(ids[-limit:]))

    def fetch_message(self, message_id: bytes) -> bytes:
        with self._connection() as connection:
            status, data = connection.fetch(message_id, "(RFC822)")
            if status != "OK" or not data or not isinstance(data[0], tuple):
                raise RuntimeError("IMAP fetch failed")
            return data[0][1]
