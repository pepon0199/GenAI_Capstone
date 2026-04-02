import os

from llm.groq_client import GroqClient
from llm.ollama_client import OllamaClient


def create_llm_client(provider=None):
    provider = (provider or os.getenv("LLM_PROVIDER", "ollama")).strip().lower()

    if provider == "groq":
        return GroqClient()

    if provider == "ollama":
        return OllamaClient()

    raise ValueError(
        f"Unsupported LLM_PROVIDER '{provider}'. Use 'ollama' or 'groq'."
    )
