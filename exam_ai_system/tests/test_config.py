from config import get_default_provider, validate_provider


def test_get_default_provider_falls_back_for_invalid_value(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "invalid-provider")
    assert get_default_provider() == "groq"


def test_validate_provider_requires_groq_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    status = validate_provider("groq")

    assert status.provider == "groq"
    assert status.model == "llama-3.3-70b-versatile"
    assert not status.is_ready
    assert "`GROQ_API_KEY` is missing." in status.errors


def test_validate_provider_marks_ollama_as_ready(monkeypatch):
    monkeypatch.setenv("OLLAMA_MODEL", "mistral")

    status = validate_provider("ollama")

    assert status.provider == "ollama"
    assert status.model == "mistral"
    assert status.is_ready
    assert status.errors == []
