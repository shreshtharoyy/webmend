from fastapi import FastAPI, HTTPException
import logging
from src.services.audit_service.audit import audit_accessibility
from src.services.audit_service.schemas.audit_request import AuditRequest
from src.services.audit_service.schemas.audit_result import AuditResult
from src.services.audit_service.middleware import (
    RequestBodySizeLimitMiddleware,
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="WebMend Audit Service",
    description="API for automated web accessibility auditing.",
    version="0.1.0",
)
app.add_middleware(RequestBodySizeLimitMiddleware)

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "service": "audit-service",
    }


@app.post(
    "/audit",
    response_model=AuditResult,
    tags=["Accessibility Audit"],
)
def create_audit(request: AuditRequest) -> AuditResult:
    try:
        return audit_accessibility(request)
    except Exception:
        logger.exception("Accessibility audit failed.")

        raise HTTPException(
            status_code=500,
            detail="The accessibility audit could not be completed.",
        )