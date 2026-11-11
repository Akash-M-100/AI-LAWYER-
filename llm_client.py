"""Small LLM wrapper for the coffee-machine agent practice project using LangChain.

Set GROQ_API_KEY in your environment or .env before running the agent.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

# Load environment variables from .env
ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

DEFAULT_MODELS = "openai/gpt-oss-120b,openai/gpt-oss-20b"
MODELS = [
    model.strip()
    for model in os.getenv("GROQ_MODELS", os.getenv("GROQ_MODEL", DEFAULT_MODELS)).split(",")
    if model.strip()
]


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """Send system/user prompts to the model and return its text response."""
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in environment or .env")

    errors = []
    for model in MODELS:
        try:
            llm = ChatGroq(
                model=model,
                temperature=0,
                api_key=api_key,
            )
            response = llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ])
            return str(response.content)
        except Exception as exc:
            errors.append(f"{model}: {exc}")

    raise RuntimeError("All configured Groq models failed. " + " | ".join(errors))
