from src.services.browser_service.browser import inspect_webpage

from src.services.audit_service.audit import audit_accessibility
from src.services.audit_service.schemas.audit_request import AuditRequest
from src.services.audit_service.schemas.audit_result import AuditResult


def run_accessibility_audit(url: str) -> AuditResult:
    webpage = inspect_webpage(url)

    audit_request = AuditRequest(
        html=webpage["html"],
        page_url=webpage["url"],
    )

    audit_result = audit_accessibility(audit_request)

    return audit_result