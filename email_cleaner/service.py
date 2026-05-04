from __future__ import annotations

from .classifier import EmailClassifier, safe_classify
from .imap_client import ImapClient
from .models import ScanRequest, ScanResponse, ScanResultItem
from .normalize import normalize_email


class ScanService:
    def __init__(self, imap_client: ImapClient, classifier: EmailClassifier, snippet_length: int, default_limit: int, max_limit: int):
        self._imap_client = imap_client
        self._classifier = classifier
        self._snippet_length = snippet_length
        self._default_limit = default_limit
        self._max_limit = max_limit

    def scan(self, request: ScanRequest) -> ScanResponse:
        effective_limit = min(request.limit or self._default_limit, self._max_limit)
        message_ids = self._imap_client.search(request, effective_limit)
        results: list[ScanResultItem] = []

        for message_id in message_ids:
            raw_message = self._imap_client.fetch_message(message_id)
            normalized = normalize_email(raw_message, message_id.decode("utf-8", errors="ignore"), self._snippet_length)
            classification = safe_classify(self._classifier, normalized)
            results.append(
                ScanResultItem(
                    **normalized.model_dump(),
                    label=classification.label,
                    reason=classification.reason,
                )
            )

        return ScanResponse(count=len(results), results=results)
