import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT/".env"

load_dotenv(dotenv_path=ENV_FILE)
APP_ENV = os.getenv("APP_ENV", "development")
DEBUG = os.getenv("DEBUG", "false").strip().lower() in {
    "true",
    "1",
    "yes",
    "on",
}

def get_groq_api_key():
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in the environment variables.")
    return api_key
