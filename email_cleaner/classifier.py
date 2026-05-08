from __future__ import annotations

import json
from json import JSONDecodeError
from typing import Protocol

from anthropic import Anthropic
from pydantic import ValidationError

from .models import ClassificationResult, NormalizedEmail

_MAX_REASON_LENGTH = 280
SYSTEM_PROMPT = " ".join(
    [
        "Classify this email for inbox cleanup.",
        "keep = important transactional (orders, support communication, delivery) or personal email the user likely wants in inbox.",
        "move = likely promotional, marketing, newsletter, discount, or bulk update.",
        "uncertain = mixed or insufficient evidence.",
    ]
)

_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "label": {"type": "string", "enum": ["keep", "move", "uncertain"]},
        "reason": {"type": "string"},
    },
    "required": ["label", "reason"],
    "additionalProperties": False,
}


class EmailClassifier(Protocol):
    def classify(self, email: NormalizedEmail) -> ClassificationResult:
        ...


class AnthropicEmailClassifier:
    def __init__(self, api_key: str, model: str):
        self._client = Anthropic(api_key=api_key)
        self._model = model

    def classify(self, email: NormalizedEmail) -> ClassificationResult:
        email_payload = email.model_dump()
        email_payload["snippet"] = email.classifier_input
        response = self._client.messages.create(
            model=self._model,
            max_tokens=512,
            temperature=0,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": json.dumps({"email": email_payload}),
                }
            ],
            output_config={"format": {"type": "json_schema", "schema": _OUTPUT_SCHEMA}},
        )
        text = "".join(
            block.text for block in response.content if getattr(block, "type", None) == "text"
        ).strip()
        result = json.loads(text)
        if isinstance(result, dict) and isinstance(result.get("reason"), str):
            result["reason"] = _truncate_reason(result["reason"])
        return ClassificationResult.model_validate(result)


def _truncate_reason(reason: str) -> str:
    if len(reason) <= _MAX_REASON_LENGTH:
        return reason

    return f"{reason[: _MAX_REASON_LENGTH - 1]}…"


def _is_unsupported_label_error(exc: ValidationError) -> bool:
    return any(error.get("loc") == ("label",) and error.get("type") == "literal_error" for error in exc.errors())


def safe_classify(classifier: EmailClassifier, email: NormalizedEmail) -> ClassificationResult:
    try:
        return classifier.classify(email)
    except ValidationError as exc:
        if _is_unsupported_label_error(exc):
            return ClassificationResult(
                label="uncertain",
                reason="Classifier returned an unsupported label",
            )
        return ClassificationResult(
            label="uncertain",
            reason=_truncate_reason(f"Classification unavailable: {exc}"),
        )
    except (JSONDecodeError, TypeError) as exc:
        return ClassificationResult(
            label="uncertain",
            reason=_truncate_reason(f"Classification unavailable: {exc}"),
        )
