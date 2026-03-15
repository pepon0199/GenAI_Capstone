from llm.ollama_client import OllamaClient

class DifficultyEvaluatorAgent:

    def __init__(self):

        self.llm = OllamaClient()

    def run(self, questions):

        for q in questions:

            prompt = f"""
Classify the difficulty of this question.

Question: {q.question}

Answer only: easy, medium, or hard.
"""

            response = self.llm.generate(prompt)

            print("OLLAMA OUTPUT:", response)

            text = response.lower()

            if "easy" in text:
                difficulty = "Easy"

            elif "medium" in text:
                difficulty = "Medium"

            elif "hard" in text or "difficult" in text:
                difficulty = "Hard"

            else:
                difficulty = "Medium"

            q.difficulty = difficulty.strip()

        return questions