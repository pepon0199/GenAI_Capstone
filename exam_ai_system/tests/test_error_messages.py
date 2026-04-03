from llm.errors import LLMProviderError, to_user_message


def test_provider_error_maps_to_friendly_message():
    message = to_user_message(LLMProviderError("provider failed"))
    assert "selected AI provider" in message


def test_generation_error_maps_to_friendly_message():
    message = to_user_message(ValueError("Question generation failed after 3 attempts"))
    assert "could not be generated" in message
