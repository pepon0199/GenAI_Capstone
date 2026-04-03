class LLMProviderError(RuntimeError):
    """Raised when an upstream LLM provider cannot complete a request."""


def to_user_message(exc: Exception) -> str:
    if isinstance(exc, LLMProviderError):
        return (
            "The selected AI provider is unavailable or returned an invalid response. "
            "Please try again in a moment or switch providers."
        )

    message = str(exc)

    if "validated questions" in message or "Question generation failed" in message:
        return (
            "The exam could not be generated with enough valid questions. "
            "Please try again or adjust the topic and level."
        )

    return "Something went wrong while processing the exam. Please try again."
