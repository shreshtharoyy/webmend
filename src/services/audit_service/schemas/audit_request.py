from pydantic import BaseModel, Field, ConfigDict

class AuditRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    html: str = Field(
        ...,
        min_length=1,
        max_length=2_000_000,
        description="HTML content to audit.",
    )

    page_url: str | None = Field(
        default=None,
        description="Optional source webpage URL.",
    )