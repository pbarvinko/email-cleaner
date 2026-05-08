from __future__ import annotations

import pytest

from email_cleaner.app import create_app
from email_cleaner.config import Settings
from email_cleaner.models import ScanResponse, ScanResultItem, ScanStages


class FakeScanService:
    def __init__(self, response: ScanResponse):
        self.response = response

    def scan(self, request):
        return self.response


@pytest.fixture
def settings():
    return Settings(
        imap_host="imap.example.com",
        imap_username="user@example.com",
        imap_password="secret",
        anthropic_api_key="test-key",
    )


@pytest.fixture
def app(settings):
    response = ScanResponse(
        count=1,
        mode="classify",
        applied_count=0,
        stages=ScanStages(searched=True, classified=True, applied=False),
        results=[
            ScanResultItem(
                message_id="abc",
                from_name="Store",
                from_email="store@example.com",
                subject="Spring sale",
                date="2026-05-03T10:00:00+00:00",
                snippet="Buy now",
                headers={"List-Unsubscribe": "mailto:unsubscribe@example.com"},
                classification_status="classified",
                label="move",
                reason="Promotional sale content",
                target_folder="promo",
                action="suggested_move",
                action_reason="analysis only",
            )
        ],
    )
    application = create_app(settings=settings, scan_service=FakeScanService(response))
    application.config.update(TESTING=True)
    return application


@pytest.fixture
def client(app):
    return app.test_client()
