import json
import os

import ollama

from llm.errors import LLMProviderError


class OllamaClient:
    def __init__(self, model=None):
        self.model = model or os.getenv("OLLAMA_MODEL", "mistral")

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
            payload["format"] = "json"

        try:
            response = ollama.chat(**payload)
        except Exception as exc:
            raise LLMProviderError(
                f"Ollama request failed for model '{self.model}': {exc}"
            ) from exc

        return response["message"]["content"]

    def generate_json(self, prompt, system_prompt=None):
        content = self.generate(
            prompt,
            system_prompt=system_prompt,
            json_mode=True,
        )

        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise LLMProviderError("Ollama did not return valid JSON.") from exc
