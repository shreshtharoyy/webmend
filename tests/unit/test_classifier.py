from unittest.mock import patch
from src.llm.classifier import classify_violation, classify_audit_violation
from src.llm.schemas import ViolationClassification
from src.services.audit_service.schemas.audit_result import (
    AccessibilityViolation,
    AuditNode,
)

def test_classify_violation():
    violation = {
        "id": "image-alt",
        "impact": "critical",
        "description": "Images must have alternative text",
        "html": '<img src="product.jpg">',
        "failure_summary": "Element does not have an alt attribute",
    }

    with patch(
        "src.llm.classifier.get_classification_chain"
    ) as mock_chain_factory:

        mock_chain = mock_chain_factory.return_value
        mock_chain.invoke.return_value = ViolationClassification(
        problem="Image is missing alternative text.",
        affected_users="Screen-reader users.",
        why_it_matters="Users cannot understand the image's content.",
        recommended_fix='Add a descriptive alt attribute to the image.',
    )

        result = classify_violation(violation)

    assert isinstance(result, ViolationClassification)

    assert result.problem == "Image is missing alternative text."
    assert result.affected_users == "Screen-reader users."
    assert result.why_it_matters == (
        "Users cannot understand the image's content."
    )
    assert result.recommended_fix == (
        "Add a descriptive alt attribute to the image."
    )

    mock_chain.invoke.assert_called_once()


def test_classify_audit_violation():
    violation = AccessibilityViolation(
        id="image-alt",
        impact="critical",
        description="Images must have alternative text",
        help="Add alternative text to images",
        help_url="https://example.com",
        nodes=[
            AuditNode(
                html='<img src="product.jpg">',
                failure_summary="Element does not have an alt attribute",
            ),
            AuditNode(
                html='<img src="logo.png">',
                failure_summary="Element does not have an alt attribute",
            ),
        ],
    )

    with patch(
        "src.llm.classifier.classify_violation"
    ) as mock_classifier:
        mock_classifier.side_effect = [
            "Product image is missing alt text.",
            "Logo image is missing alt text.",
        ]

        result = classify_audit_violation(violation)

    assert len(result) == 2
    assert mock_classifier.call_count == 2