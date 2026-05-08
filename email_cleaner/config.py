from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")

    imap_host: str = Field(min_length=1)
    imap_port: int = Field(default=993, ge=1, le=65535)
    imap_username: str = Field(min_length=1)
    imap_password: str = Field(min_length=1)

    anthropic_api_key: str | None = Field(default=None, min_length=1)
    anthropic_model: str = Field(default="claude-haiku-4-5-20251001", min_length=1)

    server_port: int = Field(default=38452, ge=1, le=65535)

    scan_default_limit: int = Field(default=20, ge=1, le=100)
    scan_max_limit: int = Field(default=100, ge=1, le=500)
    classifier_snippet_length: int = Field(default=1200, ge=200, le=5000)


def load_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as exc:
        raise RuntimeError(f"Invalid application configuration: {exc}") from exc
