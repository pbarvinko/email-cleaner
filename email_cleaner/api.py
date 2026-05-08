from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request
from pydantic import ValidationError

from .models import ScanRequest
from .service import ClassifierNotConfiguredError

api = Blueprint("api", __name__, url_prefix="/api")


def _serialize_validation_errors(exc: ValidationError) -> list[dict]:
    details: list[dict] = []
    for item in exc.errors():
        serialized = dict(item)
        if "ctx" in serialized:
            serialized["ctx"] = {key: str(value) for key, value in serialized["ctx"].items()}
        details.append(serialized)
    return details


@api.get("/health")
def health():
    return jsonify({"status": "ok"})


@api.post("/scan")
def scan():
    payload = request.get_json(silent=True) or {}
    try:
        scan_request = ScanRequest.model_validate(payload)
    except ValidationError as exc:
        return (
            jsonify(
                {
                    "error": {
                        "code": "validation_error",
                        "message": "Invalid scan request",
                        "details": _serialize_validation_errors(exc),
                    }
                }
            ),
            400,
        )

    try:
        response = current_app.extensions["scan_service"].scan(scan_request)
    except ClassifierNotConfiguredError as exc:
        return (
            jsonify(
                {
                    "error": {
                        "code": "classifier_not_configured",
                        "message": "Classifier is not configured",
                        "details": [{"msg": str(exc)}],
                    }
                }
            ),
            503,
        )
    except Exception as exc:
        return (
            jsonify(
                {
                    "error": {
                        "code": "scan_failed",
                        "message": "Scan failed",
                        "details": [{"msg": str(exc)}],
                    }
                }
            ),
            502,
        )

    return jsonify(response.model_dump())
