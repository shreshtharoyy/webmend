from pydantic import BaseModel, Field


class AuditNode(BaseModel):
    target: list[str] = Field(default_factory=list)
    html: str
    failure_summary: str | None = None


class AccessibilityViolation(BaseModel):
    id: str
    impact: str | None = None
    description: str
    help: str
    help_url: str
    tags: list[str] = Field(default_factory=list)
    nodes: list[AuditNode] = Field(default_factory=list)


class AuditSummary(BaseModel):
    violation_count: int = 0
    passes: int = 0
    incomplete: int = 0
    inapplicable: int = 0


class AuditResult(BaseModel):
    page_url: str | None = None
    summary: AuditSummary
    violations: list[AccessibilityViolation] = Field(
        default_factory=list
    )