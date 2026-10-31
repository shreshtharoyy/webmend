import pytest
from src.config import get_groq_api_key

def test_get_groq_api_key_returns_value(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test_api_key")

    api_key = get_groq_api_key()
    assert api_key == "test_api_key"

def test_get_groq_api_key_missing(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    with pytest.raises(ValueError, match="GROQ_API_KEY is not set"):
        get_groq_api_key()

def test_get_groq_api_key_strips_whitespace(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "  test_api_key  ")

    assert get_groq_api_key() == "test_api_key"


def test_get_groq_api_key_rejects_whitespace(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "   ")

    with pytest.raises(ValueError):
        get_groq_api_key()