import pytest

import llm.factory as factory


class DummyGroqClient:
    pass


class DummyOllamaClient:
    pass


def test_factory_returns_groq_client(monkeypatch):
    monkeypatch.setattr(factory, "GroqClient", DummyGroqClient)
    monkeypatch.setattr(factory, "OllamaClient", DummyOllamaClient)

    client = factory.create_llm_client(provider="groq")

    assert isinstance(client, DummyGroqClient)


def test_factory_returns_ollama_client(monkeypatch):
    monkeypatch.setattr(factory, "GroqClient", DummyGroqClient)
    monkeypatch.setattr(factory, "OllamaClient", DummyOllamaClient)

    client = factory.create_llm_client(provider="ollama")

    assert isinstance(client, DummyOllamaClient)


def test_factory_rejects_unknown_provider():
    with pytest.raises(ValueError, match="Unsupported LLM_PROVIDER"):
        factory.create_llm_client(provider="unknown")
