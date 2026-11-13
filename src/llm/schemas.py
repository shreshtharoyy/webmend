from pydantic import BaseModel, Field


class ViolationClassification(BaseModel):
    problem: str = Field(
        description="Explain the accessibility problem."
    )

    affected_users: str = Field(
        description="Explain who is affected by this problem."
    )

    why_it_matters: str = Field(
        description="Explain why this accessibility issue matters."
    )

    recommended_fix: str = Field(
        description="Recommend a practical correction for the issue."
    )