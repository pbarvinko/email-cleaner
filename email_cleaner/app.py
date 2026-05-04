from __future__ import annotations

from flask import Flask

from .api import api
from .classifier import AnthropicEmailClassifier
from .config import Settings, load_settings
from .imap_client import ImapClient
from .service import ScanService


def create_app(
    settings: Settings | None = None,
    *,
    scan_service: ScanService | None = None,
) -> Flask:
    resolved_settings = settings or load_settings()

    app = Flask(__name__, static_folder="web", static_url_path="")
    app.config["SETTINGS"] = resolved_settings

    if scan_service is None:
        classifier = AnthropicEmailClassifier(
            api_key=resolved_settings.anthropic_api_key,
            model=resolved_settings.anthropic_model,
        )
        imap_client = ImapClient(
            host=resolved_settings.imap_host,
            port=resolved_settings.imap_port,
            username=resolved_settings.imap_username,
            password=resolved_settings.imap_password,
        )
        scan_service = ScanService(
            imap_client=imap_client,
            classifier=classifier,
            snippet_length=resolved_settings.classifier_snippet_length,
            default_limit=resolved_settings.scan_default_limit,
            max_limit=resolved_settings.scan_max_limit,
        )

    app.extensions["scan_service"] = scan_service

    @app.get("/")
    def index():
        return app.send_static_file("index.html")

    app.register_blueprint(api)
    return app


def run_app() -> None:
    app = create_app()
    settings = app.config["SETTINGS"]
    app.run(host="0.0.0.0", port=settings.server_port)
