from unittest.mock import patch

from src.orchestration.workflow import run_accessibility_audit
from src.services.audit_service.schemas.audit_result import (
    AuditResult,
    AuditSummary,
)


def test_run_accessibility_audit():
    mock_webpage = {
        "url": "https://example.com",
        "title": "Example",
        "html": "<html><body><h1>Hello</h1></body></html>",
    }

    mock_result = AuditResult(
        page_url="https://example.com",
        summary=AuditSummary(
            violation_count=0,
            passes=5,
            incomplete=0,
            inapplicable=2,
        ),
        violations=[],
    )

    with patch(
        "src.orchestration.workflow.inspect_webpage",
        return_value=mock_webpage,
    ) as mock_browser:

        with patch(
            "src.orchestration.workflow.audit_accessibility",
            return_value=mock_result,
        ) as mock_audit:

            result = run_accessibility_audit("https://example.com")

    mock_browser.assert_called_once_with("https://example.com")
    mock_audit.assert_called_once()

    audit_request = mock_audit.call_args.args[0]

    assert audit_request.html == mock_webpage["html"]
    assert audit_request.page_url == mock_webpage["url"]

    assert result == mock_result