from src.services.audit_service.audit import audit_accessibility
from src.services.audit_service.schemas.audit_request import AuditRequest


def test_audit_accessibility_returns_structured_result(monkeypatch):
    raw_results = {
        "violations": [
            {
                "id": "image-alt",
                "impact": "critical",
                "description": "Images must have alternative text.",
                "help": "Add alternative text to images.",
                "helpUrl": "https://example.com/image-alt",
                "tags": ["wcag2a", "wcag111"],
                "nodes": [
                    {
                        "target": ["img"],
                        "html": '<img src="profile.png">',
                        "failureSummary": "No alt attribute found.",
                    }
                ],
            }
        ],
        "passes": [{"id": "document-title"}],
        "incomplete": [],
        "inapplicable": [{"id": "video-caption"}],
    }

    monkeypatch.setattr(
        "src.services.audit_service.audit.run_axe_audit",
        lambda html: raw_results,
    )

    request = AuditRequest(
        html="<html><body><img src='profile.png'></body></html>",
        page_url="https://example.com",
    )

    result = audit_accessibility(request)

    assert result.page_url == "https://example.com"
    assert result.summary.violation_count == 1
    assert result.summary.passes == 1
    assert result.summary.incomplete == 0
    assert result.summary.inapplicable == 1

    assert result.violations[0].id == "image-alt"
    assert result.violations[0].impact == "critical"
    assert len(result.violations[0].nodes) == 1
    assert result.violations[0].nodes[0].target == ["img"]


def test_audit_accessibility_handles_zero_violations(monkeypatch):
    raw_results = {
        "violations": [],
        "passes": [{"id": "document-title"}],
        "incomplete": [],
        "inapplicable": [],
    }

    monkeypatch.setattr(
        "src.services.audit_service.audit.run_axe_audit",
        lambda html: raw_results,
    )

    request = AuditRequest(html="<html></html>")

    result = audit_accessibility(request)

    assert result.summary.violation_count == 0
    assert result.violations == []
    assert result.summary.passes == 1