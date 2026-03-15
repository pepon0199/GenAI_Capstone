from llm.ollama_client import OllamaClient

class FactCheckerAgent:

    def __init__(self):

        self.llm = OllamaClient()

    def run(self, questions):

        verified = []

        for q in questions:

            prompt = f"""
Check if this question is factually correct.

Question: {q.question}

Answer yes or no only.
"""

            response = self.llm.generate(prompt)

            if "yes" in response.lower():
                verified.append(q)

        return verified