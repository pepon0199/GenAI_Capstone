import os
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class ProviderStatus:
    provider: str
    model: str
    errors: List[str]

    @property
    def is_ready(self) -> bool:
        return not self.errors


def get_default_provider() -> str:
    provider = os.getenv("LLM_PROVIDER", "groq").strip().lower()
    return provider if provider in {"groq", "ollama"} else "groq"


def get_active_model(provider: str) -> str:
    if provider == "groq":
        return os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    return os.getenv("OLLAMA_MODEL", "mistral")


def validate_provider(provider: str) -> ProviderStatus:
    provider = provider.strip().lower()
    errors: List[str] = []
    model = get_active_model(provider)

    if provider == "groq":
        if not os.getenv("GROQ_API_KEY"):
            errors.append("`GROQ_API_KEY` is missing.")
    elif provider == "ollama":
        if not model:
            errors.append("`OLLAMA_MODEL` is missing.")
    else:
        errors.append("Unsupported provider selected.")

    return ProviderStatus(provider=provider, model=model, errors=errors)
