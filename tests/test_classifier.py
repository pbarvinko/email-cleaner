from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from email_cleaner.classifier import (
    SYSTEM_PROMPT,
    AnthropicEmailClassifier,
    safe_classify,
)
from email_cleaner.models import NormalizedEmail


class FakeAnthropicClient:
    def __init__(self, response_text: str = '{"label": "keep", "reason": "Looks important"}'):
        self.messages = self
        self.last_payload = None
        self.response_text = response_text

    def create(self, **kwargs):
        self.last_payload = kwargs
        return SimpleNamespace(content=[SimpleNamespace(type="text", text=self.response_text)])


class ExplodingClassifier:
    def __init__(self, message: str):
        self.message = message

    def classify(self, email: NormalizedEmail):
        raise RuntimeError(self.message)


def _classify(classifier_input: str, response_text: str = '{"label": "keep", "reason": "Looks important"}'):
    classifier = AnthropicEmailClassifier(api_key="test-key", model="test-model")
    classifier._client = FakeAnthropicClient(response_text=response_text)

    result = classifier.classify(
        NormalizedEmail(
            message_id="1",
            snippet="Readable order update",
            classifier_input=classifier_input,
        )
    )

    return result, classifier._client.last_payload


def _classify_and_get_prompt(classifier_input: str):
    _, request_payload = _classify(classifier_input)
    return request_payload, json.loads(request_payload["messages"][0]["content"])


def test_classifier_uses_plain_text_snippet_unchanged_when_available():
    _, payload = _classify_and_get_prompt("Readable order update")
    assert payload["email"]["snippet"] == "Readable order update"


def test_classifier_uses_markdown_when_html_fallback_was_selected():
    _, payload = _classify_and_get_prompt("# Big Sale\n\nSave 20% today only.")
    assert payload["email"]["snippet"] == "# Big Sale\n\nSave 20% today only."


def test_classifier_uses_structured_output_schema():
    request_payload, _ = _classify_and_get_prompt("Readable order update")

    assert request_payload["system"] == SYSTEM_PROMPT
    schema = request_payload["output_config"]["format"]["schema"]
    assert schema["properties"]["label"]["enum"] == ["keep", "move", "uncertain"]
    assert "reason" in schema["properties"]
    assert schema.get("additionalProperties") is False


def test_classifier_accepts_raw_json_response():
    result, _ = _classify("Readable order update", '{"label": "keep", "reason": "Looks important"}')

    assert result.label == "keep"
    assert result.reason == "Looks important"


def test_classifier_truncates_overlong_model_reason_and_preserves_label():
    long_reason = "a" * 300

    result, _ = _classify(
        "Readable order update",
        json.dumps({"label": "move", "reason": long_reason}),
    )

    assert result.label == "move"
    assert len(result.reason) == 280
    assert result.reason == f"{'a' * 279}…"


def test_safe_classify_returns_established_result_for_unsupported_label():
    classifier = AnthropicEmailClassifier(api_key="test-key", model="test-model")
    classifier._client = FakeAnthropicClient(
        response_text=json.dumps({"label": "archive", "reason": "Looks important"})
    )

    result = safe_classify(
        classifier,
        NormalizedEmail(
            message_id="1",
            snippet="Readable order update",
            classifier_input="Readable order update",
        ),
    )

    assert result.label == "uncertain"
    assert result.reason == "Classifier returned an unsupported label"


def test_safe_classify_returns_uncertain_on_unparseable_response():
    classifier = AnthropicEmailClassifier(api_key="test-key", model="test-model")
    classifier._client = FakeAnthropicClient(response_text="not json")

    result = safe_classify(
        classifier,
        NormalizedEmail(
            message_id="1",
            snippet="Readable order update",
            classifier_input="Readable order update",
        ),
    )

    assert result.label == "uncertain"
    assert "Classification unavailable" in result.reason


def test_safe_classify_truncates_overlong_fallback_reason():
    classifier = ExplodingClassifier("b" * 400)

    with pytest.raises(RuntimeError, match="b+"):
        safe_classify(
            classifier,
            NormalizedEmail(
                message_id="1",
                snippet="Readable order update",
                classifier_input="Readable order update",
            ),
        )
