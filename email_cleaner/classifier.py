from __future__ import annotations

import json
from typing import Protocol

from anthropic import Anthropic

from .models import ClassificationResult, NormalizedEmail


class EmailClassifier(Protocol):
    def classify(self, email: NormalizedEmail) -> ClassificationResult:
        ...


class AnthropicEmailClassifier:
    def __init__(self, api_key: str, model: str):
        self._client = Anthropic(api_key=api_key)
        self._model = model

    def classify(self, email: NormalizedEmail) -> ClassificationResult:
        prompt = {
            "task": "Classify this email for inbox cleanup.",
            "labels": ["keep", "move", "uncertain"],
            "rules": [
                "keep = important transactional or personal email the user likely wants in inbox",
                "move = likely promotional, marketing, newsletter, discount, or bulk update",
                "uncertain = mixed or insufficient evidence",
                "Return concise JSON only with keys label and reason",
            ],
            "email": email.model_dump(),
        }
        response = self._client.messages.create(
            model=self._model,
            max_tokens=120,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": json.dumps(prompt),
                }
            ],
        )
        text = "".join(
            block.text for block in response.content if getattr(block, "type", None) == "text"
        ).strip()
        payload = json.loads(text)
        return ClassificationResult.model_validate(payload)


def safe_classify(classifier: EmailClassifier, email: NormalizedEmail) -> ClassificationResult:
    try:
        result = classifier.classify(email)
    except Exception as exc:  # pragma: no cover - exercised via response shaping behavior
        return ClassificationResult(label="uncertain", reason=f"Classification unavailable: {exc}")

    if result.label not in {"keep", "move", "uncertain"}:
        return ClassificationResult(label="uncertain", reason="Classifier returned an unsupported label")

    return result
