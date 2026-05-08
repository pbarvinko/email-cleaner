from __future__ import annotations

from .classifier import EmailClassifier, safe_classify
from .imap_client import ImapClient
from .models import (
    ClassificationResult,
    NormalizedEmail,
    ScanRequest,
    ScanResponse,
    ScanResultItem,
    ScanStages,
)
from .normalize import normalize_email


class ClassifierNotConfiguredError(RuntimeError):
    pass


class ScanService:
    def __init__(
        self,
        imap_client: ImapClient,
        classifier: EmailClassifier | None,
        snippet_length: int,
        default_limit: int,
        max_limit: int,
    ):
        self._imap_client = imap_client
        self._classifier = classifier
        self._snippet_length = snippet_length
        self._default_limit = default_limit
        self._max_limit = max_limit

    def scan(self, request: ScanRequest) -> ScanResponse:
        self._ensure_classification_available(request.mode)
        effective_limit = min(request.limit or self._default_limit, self._max_limit)
        results: list[ScanResultItem] = []
        applied_count = 0
        readonly = request.mode != "clean"

        with self._imap_client.scan_messages(request, effective_limit, readonly=readonly) as messages:
            for message_id, raw_message in messages:
                normalized = normalize_email(
                    raw_message,
                    message_id.decode("utf-8", errors="ignore"),
                    self._snippet_length,
                )
                if request.mode == "search":
                    results.append(self._build_search_result_item(normalized))
                    continue

                classification = safe_classify(self._classifier, normalized)
                result = self._build_classified_result_item(normalized, classification, request.mode)

                if request.mode == "clean" and result.target_folder:
                    messages.move_message(message_id, result.target_folder)
                    result.action = "moved"
                    result.action_reason = f"moved to {result.target_folder}"
                    applied_count += 1

                results.append(result)

        return ScanResponse(
            count=len(results),
            mode=request.mode,
            applied_count=applied_count,
            stages=ScanStages(
                searched=True,
                classified=request.mode != "search",
                applied=request.mode == "clean",
            ),
            results=results,
        )

    def _ensure_classification_available(self, mode: str) -> None:
        if mode in {"classify", "clean"} and self._classifier is None:
            raise ClassifierNotConfiguredError("Classifier is not configured")

    def _build_search_result_item(self, normalized: NormalizedEmail) -> ScanResultItem:
        return ScanResultItem(
            **normalized.model_dump(),
            classification_status="not_classified",
            action="none",
            action_reason="search only",
        )

    def _build_classified_result_item(
        self,
        normalized: NormalizedEmail,
        classification: ClassificationResult,
        mode: str,
    ) -> ScanResultItem:
        target_folder = self._resolve_destination_folder(classification.label)
        action = "none"
        action_reason = "label keep"

        if target_folder and mode == "classify":
            action = "suggested_move"
            action_reason = "analysis only"

        return ScanResultItem(
            **normalized.model_dump(),
            classification_status="classified",
            label=classification.label,
            reason=classification.reason,
            target_folder=target_folder,
            action=action,
            action_reason=action_reason,
        )

    def _resolve_destination_folder(self, label: str) -> str | None:
        if label == "move":
            return "promo"
        if label == "uncertain":
            return "promo-check"
        return None
