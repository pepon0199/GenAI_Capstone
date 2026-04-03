from types import SimpleNamespace

import pytest

import llm.ollama_client as ollama_module
from llm.errors import LLMProviderError
from llm.groq_client import GroqClient
from llm.ollama_client import OllamaClient


def test_groq_client_wraps_provider_exception():
    client = GroqClient.__new__(GroqClient)
    client.model = "test-model"
    client.client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda **kwargs: (_ for _ in ()).throw(RuntimeError("provider down"))
            )
        )
    )

    with pytest.raises(LLMProviderError, match="Groq request failed"):
        client.generate("hello")


def test_ollama_client_wraps_provider_exception(monkeypatch):
    client = OllamaClient(model="test-model")

    def fail_chat(**kwargs):
        raise RuntimeError("service unavailable")

    monkeypatch.setattr(ollama_module.ollama, "chat", fail_chat)

    with pytest.raises(LLMProviderError, match="Ollama request failed"):
        client.generate("hello")
