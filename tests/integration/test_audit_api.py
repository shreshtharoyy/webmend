from fastapi.testclient import TestClient
from unittest.mock import patch
from src.services.audit_service.api import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "audit-service",
    }


def test_audit_endpoint_with_valid_html():
    html = """
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <title>WebMend Test</title>
        </head>
        <body>
            <img src="example.jpg">
            <h1>Accessibility Test</h1>
        </body>
    </html>
    """

    response = client.post(
        "/audit",
        json={"html": html},
    )

    assert response.status_code == 200

    result = response.json()

    assert "summary" in result
    assert "violations" in result
    assert result["summary"]["violation_count"] >= 1

    violation_ids = [
        violation["id"]
        for violation in result["violations"]
    ]

    assert "image-alt" in violation_ids


def test_audit_endpoint_rejects_empty_html():
    response = client.post(
        "/audit",
        json={"html": ""},
    )

    assert response.status_code == 422


def test_audit_endpoint_rejects_unknown_fields():
    response = client.post(
        "/audit",
        json={
            "html": "<html><body>Hello</body></html>",
            "unexpected_field": "not allowed",
        },
    )

    assert response.status_code == 422

def test_audit_endpoint_handles_internal_failure():
    with patch(
        "src.services.audit_service.api.audit_accessibility",
        side_effect=RuntimeError("Internal test failure"),
    ):
        response = client.post(
            "/audit",
            json={"html": "<html><body>Hello</body></html>"},
        )

    assert response.status_code == 500
    assert response.json() == {
        "detail": "The accessibility audit could not be completed."
    }

def test_audit_endpoint_rejects_oversized_html():
    oversized_html = "a" * 2_000_001

    response = client.post(
        "/audit",
        json={"html": oversized_html},
    )

    assert response.status_code == 422

def test_audit_endpoint_rejects_oversized_request_body():
    oversized_html = "a" * (4 * 1024 * 1024 + 1)

    response = client.post(
        "/audit",
        json={"html": oversized_html},
    )

    assert response.status_code == 413
    assert response.json() == {
        "detail": "Request body too large."
    }