from unittest.mock import patch

from src.orchestration.workflow import run_accessibility_audit
from src.services.audit_service.schemas.audit_result import (
    AuditResult,
    AuditSummary,
    AccessibilityViolation,
    AuditNode,
)

from src.llm.schemas import ViolationClassification

def test_run_accessibility_audit():
    mock_webpage = {
        "url": "https://example.com",
        "title": "Example",
        "html": "<html><body><h1>Hello</h1></body></html>",
    }

    mock_result = AuditResult(
        page_url="https://example.com",
        summary=AuditSummary(
            violation_count=1,
            passes=5,
            incomplete=0,
            inapplicable=2,
        ),
        violations=[
            AccessibilityViolation(
                id="image-alt",
                impact="critical",
                description="Images must have alternative text",
                help="Add alternative text to images",
                help_url="https://example.com/help",
                nodes=[
                    AuditNode(
                        html='<img src="product.jpg">',
                        failure_summary=(
                            "Element does not have an alt attribute"
                        ),
                    )
                ],
            )
        ],
    )

    mock_classification = ViolationClassification(
        problem="Image is missing alternative text.",
        affected_users="Screen-reader users.",
        why_it_matters="Users cannot understand the image.",
        recommended_fix="Add a descriptive alt attribute.",
    )

    with patch(
        "src.orchestration.workflow.inspect_webpage",
        return_value=mock_webpage,
    ) as mock_browser:

        with patch(
            "src.orchestration.workflow.audit_accessibility",
            return_value=mock_result,
        ) as mock_audit:

            with patch(
                "src.orchestration.workflow.classify_audit_violation",
                return_value=[mock_classification],
            ) as mock_classifier:

                result = run_accessibility_audit(
                    "https://example.com"
                )

    mock_browser.assert_called_once_with("https://example.com")
    mock_audit.assert_called_once()

    audit_request = mock_audit.call_args.args[0]

    assert audit_request.html == mock_webpage["html"]
    assert audit_request.page_url == mock_webpage["url"]

    mock_classifier.assert_called_once_with(
        mock_result.violations[0]
    )

    assert result["audit_result"] == mock_result

    assert result["classifications"] == [
        mock_classification
    ]
