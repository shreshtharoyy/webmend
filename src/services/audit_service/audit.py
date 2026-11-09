from src.services.audit_service.engine.axe_runner import run_axe_audit
from src.services.audit_service.schemas.audit_request import AuditRequest
from src.services.audit_service.schemas.audit_result import (
    AuditNode,
    AccessibilityViolation,
    AuditSummary,
    AuditResult,
)


def audit_accessibility(request: AuditRequest) -> AuditResult:
    raw_results = run_axe_audit(request.html)

    violations = []

    for violation in raw_results.get("violations", []):
        nodes = []

        for node in violation.get("nodes", []):
            audit_node = AuditNode(
                target=node.get("target", []),
                html=node.get("html", ""),
                failure_summary=node.get("failureSummary"),
            )

            nodes.append(audit_node)

        accessibility_violation = AccessibilityViolation(
            id=violation["id"],
            impact=violation.get("impact"),
            description=violation["description"],
            help=violation["help"],
            help_url=violation["helpUrl"],
            tags=violation.get("tags", []),
            nodes=nodes,
        )

        violations.append(accessibility_violation)

    summary = AuditSummary(
        violation_count=len(raw_results.get("violations", [])),
        passes=len(raw_results.get("passes", [])),
        incomplete=len(raw_results.get("incomplete", [])),
        inapplicable=len(raw_results.get("inapplicable", [])),
    )

    return AuditResult(
        page_url=request.page_url,
        summary=summary,
        violations=violations,
    )