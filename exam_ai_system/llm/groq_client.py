import json
import os

from llm.errors import LLMProviderError


class GroqClient:
    def __init__(self, model=None):
        self.model = model or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

        try:
            from groq import Groq
        except ImportError as exc:
            raise ImportError(
                "Groq support requires the 'groq' package. Install it with 'pip install groq'."
            ) from exc

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY is not set.")

        self.client = Groq(api_key=api_key)

    def generate(self, prompt, system_prompt=None, json_mode=False):
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
        }

        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        try:
            response = self.client.chat.completions.create(**payload)
            return response.choices[0].message.content
        except Exception as exc:
            raise LLMProviderError(
                f"Groq request failed or returned an unexpected response for model "
                f"'{self.model}': {exc}"
            ) from exc

    def generate_json(self, prompt, system_prompt=None):
        content = self.generate(
            prompt,
            system_prompt=system_prompt,
            json_mode=True,
        )

        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise LLMProviderError("Groq did not return valid JSON.") from exc
