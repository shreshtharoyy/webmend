import pytest

from src.services.audit_service.engine.axe_runner import (
    run_axe_audit,
    AXE_SCRIPT_PATH,
)


def test_run_axe_audit_returns_expected_structure():
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>WebMend Audit Test</title>
    </head>
    <body>
        <h1>Accessibility Test</h1>
        <img src="profile.png">
        <button></button>
    </body>
    </html>
    """

    results = run_axe_audit(html)

    assert "violations" in results
    assert "passes" in results
    assert "incomplete" in results
    assert "inapplicable" in results


def test_run_axe_audit_detects_missing_image_alt():
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Image Test</title>
    </head>
    <body>
        <img src="profile.png">
    </body>
    </html>
    """

    results = run_axe_audit(html)

    violation_ids = [
        violation["id"]
        for violation in results["violations"]
    ]

    assert "image-alt" in violation_ids


def test_run_axe_audit_detects_empty_button():
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Button Test</title>
    </head>
    <body>
        <button></button>
    </body>
    </html>
    """

    results = run_axe_audit(html)

    violation_ids = [
        violation["id"]
        for violation in results["violations"]
    ]

    assert "button-name" in violation_ids


def test_run_axe_audit_rejects_empty_html():
    with pytest.raises(ValueError):
        run_axe_audit("")


def test_run_axe_audit_rejects_whitespace_html():
    with pytest.raises(ValueError):
        run_axe_audit("   ")


def test_run_axe_audit_rejects_missing_axe_asset(monkeypatch):
    monkeypatch.setattr(
        "src.services.audit_service.engine.axe_runner.AXE_SCRIPT_PATH",
        AXE_SCRIPT_PATH.parent / "missing-axe.min.js",
    )

    with pytest.raises(FileNotFoundError):
        run_axe_audit("<html></html>")