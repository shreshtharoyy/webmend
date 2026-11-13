from src.services.browser_service.browser import inspect_webpage

from src.services.audit_service.audit import audit_accessibility
from src.services.audit_service.schemas.audit_request import AuditRequest
from src.services.audit_service.schemas.audit_result import AuditResult

from src.llm.classifier import classify_audit_violation
from src.llm.schemas import ViolationClassification


def run_accessibility_audit(url: str) -> dict:
    webpage = inspect_webpage(url)

    audit_request = AuditRequest(
        html=webpage["html"],
        page_url=webpage["url"],
    )

    audit_result = audit_accessibility(audit_request)

    classifications = []

    for violation in audit_result.violations:
        results = classify_audit_violation(violation)

        classifications.extend(results)

    return {
        "audit_result": audit_result,
        "classifications": classifications,
    }