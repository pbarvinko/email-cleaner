from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

AllowedLabel = Literal["keep", "move", "uncertain"]
ScanAction = Literal["none", "suggested_move", "moved"]
ClassificationStatus = Literal["not_classified", "classified"]
ScanMode = Literal["search", "classify", "clean"]


class ScanRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    from_query: str | None = None
    subject_contains: str | None = None
    since_date: date | None = None
    before_date: date | None = None
    limit: int | None = Field(default=None, ge=1)
    mode: ScanMode = "classify"

    @field_validator(
        "from_query",
        "subject_contains",
        "since_date",
        "before_date",
        mode="before",
    )
    @classmethod
    def empty_to_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @model_validator(mode="after")
    def ensure_search_criteria(self) -> ScanRequest:
        if not any(
            [
                self.from_query,
                self.subject_contains,
                self.since_date,
                self.before_date,
            ]
        ):
            raise ValueError("At least one search criterion is required")
        return self

    @model_validator(mode="after")
    def ensure_valid_date_window(self) -> ScanRequest:
        if self.since_date and self.before_date and self.before_date <= self.since_date:
            raise ValueError("before_date must be later than since_date")
        return self


class NormalizedEmail(BaseModel):
    message_id: str
    from_name: str | None = None
    from_email: str | None = None
    subject: str | None = None
    date: str | None = None
    snippet: str
    classifier_input: str = Field(exclude=True)
    headers: dict[str, str] = Field(default_factory=dict)


class ClassificationResult(BaseModel):
    label: AllowedLabel
    reason: str = Field(min_length=1, max_length=280)


class ScanResultItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    message_id: str
    from_name: str | None = None
    from_email: str | None = None
    subject: str | None = None
    date: str | None = None
    snippet: str
    headers: dict[str, str] = Field(default_factory=dict)
    classification_status: ClassificationStatus
    label: AllowedLabel | None = None
    reason: str | None = None
    target_folder: str | None = None
    action: ScanAction
    action_reason: str


class ScanStages(BaseModel):
    searched: bool
    classified: bool
    applied: bool


class ScanResponse(BaseModel):
    count: int
    mode: ScanMode
    applied_count: int
    stages: ScanStages
    results: list[ScanResultItem]
