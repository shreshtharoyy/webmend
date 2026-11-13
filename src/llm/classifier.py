from langchain_core.prompts import ChatPromptTemplate
from src.llm.groq_client import get_groq_chat_model
from src.services.audit_service.schemas.audit_result import AccessibilityViolation
from src.llm.schemas import ViolationClassification

classification_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", """
        You are an expert web accessibility analyst.

        Analyze the supplied axe-core violation.

        Return concise, technically accurate information:
        1. Problem: Explain the issue in one sentence.
        2. Affected users: Identify who is affected.
        3. Why it matters: Explain the main consequence in one sentence.
        4. Recommended fix: Give a practical correction.

        Rules:
        - Keep each field to 1-2 short sentences.
        - Base your answer only on supplied information.
        - Do not invent webpage details.
        - Avoid legal claims and unrelated SEO advice.
        - Do not repeat the violation description unnecessarily.
        """),
        ("human",  """
        Violation ID: {violation_id}

        Impact: {impact}

        Description: {description}

        Affected HTML:
        {html}

        Axe-core failure summary:
        {failure_summary}
        """)
    ])

def get_classification_chain():
    llm = get_groq_chat_model()
    structured_llm = llm.with_structured_output(
        ViolationClassification
    )
    return classification_prompt | structured_llm

def classify_violation(violation: dict):
    chain = get_classification_chain()

    response = chain.invoke({
        "violation_id": violation["id"],
        "impact": violation.get("impact", "unknown"),
        "description": violation["description"],
        "html": violation.get("html", ""),
        "failure_summary": violation.get("failure_summary", ""),
    })

    return response

def classify_audit_violation(
    violation: AccessibilityViolation,
) -> list[ViolationClassification]:

    classifications = []

    for node in violation.nodes:
        violation_data = {
            "id": violation.id,
            "impact": violation.impact or "unknown",
            "description": violation.description,
            "html": node.html,
            "failure_summary": node.failure_summary or "",
        }

        result = classify_violation(violation_data)
        classifications.append(result)

    return classifications

