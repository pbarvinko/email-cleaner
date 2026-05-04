import pytest

from email_cleaner.config import load_settings


def test_load_settings_requires_required_environment(monkeypatch):
    for key in ["IMAP_HOST", "IMAP_USERNAME", "IMAP_PASSWORD", "ANTHROPIC_API_KEY"]:
        monkeypatch.delenv(key, raising=False)

    with pytest.raises(RuntimeError) as exc:
        load_settings()

    assert "Invalid application configuration" in str(exc.value)


def test_load_settings_reads_environment(monkeypatch):
    monkeypatch.setenv("IMAP_HOST", "imap.example.com")
    monkeypatch.setenv("IMAP_USERNAME", "user@example.com")
    monkeypatch.setenv("IMAP_PASSWORD", "secret")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "key")

    settings = load_settings()

    assert settings.imap_host == "imap.example.com"
    assert settings.scan_default_limit == 20
    assert settings.server_port == 38452
    assert not hasattr(settings, "server_host")
