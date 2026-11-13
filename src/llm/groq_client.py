import os
from langchain_groq import ChatGroq
from pydantic import SecretStr
from src.config import get_groq_api_key

def get_groq_chat_model() -> ChatGroq:
    model_name = os.getenv("GROQ_MODEL", "").strip()

    if not model_name:
        raise ValueError("GROQ_MODEL is not configured.")

    api_key = SecretStr(get_groq_api_key())

    return ChatGroq(
        model=model_name,
        api_key=api_key,
        temperature=0,
    )