import ollama

class OllamaClient:

    def generate(self, prompt):

        response = ollama.chat(
            model="mistral",
            messages=[{"role": "user", "content": prompt}]
        )

        content = response["message"]["content"]

        print("OLLAMA OUTPUT:", content)

        return content