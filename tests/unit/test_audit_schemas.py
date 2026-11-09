import pytest
from pydantic import ValidationError

from src.services.audit_service.schemas.audit_request import AuditRequest
from src.services.audit_service.schemas.audit_result import (
    AuditNode,
    AccessibilityViolation,
    AuditSummary,
    AuditResult,
)


# AuditRequest tests

def test_audit_request_accepts_valid_html():
    request = AuditRequest(html="<html><body>Hello</body></html>")

    assert request.html == "<html><body>Hello</body></html>"
    assert request.page_url is None


def test_audit_request_accepts_page_url():
    request = AuditRequest(
        html="<html></html>",
        page_url="https://example.com",
    )

    assert request.page_url == "https://example.com"


def test_audit_request_rejects_empty_html():
    with pytest.raises(ValidationError):
        AuditRequest(html="")


def test_audit_request_rejects_html_exceeding_limit():
    with pytest.raises(ValidationError):
        AuditRequest(html="a" * 2_000_001)


def test_audit_request_rejects_unexpected_fields():
    with pytest.raises(ValidationError):
        AuditRequest(
            html="<html></html>",
            unexpected_field="value",
        )


# AuditNode tests

def test_audit_node_accepts_valid_data():
    node = AuditNode(
        target=["img"],
        html='<img src="profile.png">',
        failure_summary="Image is missing alternative text.",
    )

    assert node.target == ["img"]
    assert node.html == '<img src="profile.png">'


# AccessibilityViolation tests

def test_accessibility_violation_accepts_valid_data():
    violation = AccessibilityViolation(
        id="image-alt",
        impact="critical",
        description="Images must have alternative text.",
        help="Add alternative text to images.",
        help_url="https://example.com/rule",
        tags=["wcag2a", "wcag111"],
        nodes=[
            AuditNode(
                target=["img"],
                html='<img src="profile.png">',
                failure_summary="No alt attribute found.",
            )
        ],
    )

    assert violation.id == "image-alt"
    assert len(violation.nodes) == 1


def test_accessibility_violation_rejects_missing_required_fields():
    with pytest.raises(ValidationError):
        AccessibilityViolation(
            id="image-alt",
            description="Images must have alternative text.",
        )


# AuditResult tests

def test_audit_result_accepts_valid_data():
    result = AuditResult(
        page_url="https://example.com",
        summary=AuditSummary(
            violation_count=1,
            passes=10,
            incomplete=2,
            inapplicable=3,
        ),
        violations=[],
    )

    assert result.summary.violation_count == 1
    assert result.summary.passes == 10


def test_audit_result_serializes_to_json():
    result = AuditResult(
        summary=AuditSummary(),
        violations=[],
    )

    serialized_result = result.model_dump()

    assert serialized_result["summary"]["violation_count"] == 0
    assert serialized_result["violations"] == []