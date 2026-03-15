import json
from llm.ollama_client import OllamaClient
from schemas.exam_schema import Question


class QuestionGeneratorAgent:

    def __init__(self):
        self.llm = OllamaClient()

    def run(self, topic, exam_type, level, num_questions):

        prompt = f"""
Generate exactly {num_questions} multiple choice questions.

Training Topic: {topic}
Exam Type: {exam_type}
Certification Level: {level}

Difficulty Guidelines:
- Beginner: basic concepts and definitions
- Intermediate: conceptual understanding and practical application
- Advanced: complex scenarios, deeper understanding, or problem-solving questions

Return ONLY valid JSON in the following format:

[
  {{
    "question": "question text",
    "options": ["option1", "option2", "option3", "option4"],
    "answer": "correct option text"
  }}
]

Rules:
- Exactly {num_questions} questions
- Each question must have exactly 4 options
- The answer must match one of the options
- The questions MUST match the certification level: {level}
- Do not include explanations
- Do not include text outside the JSON
"""

        response = self.llm.generate(prompt)

        print("\nOLLAMA RAW OUTPUT:\n", response)

        # Try direct JSON parsing
        try:
            data = json.loads(response)

        except json.JSONDecodeError:

            print("JSON parsing failed. Attempting to extract JSON block...")

            # Extract JSON array if model included extra text
            start = response.find("[")
            end = response.rfind("]") + 1

            if start == -1 or end == -1:
                raise Exception("LLM did not return valid JSON")

            json_block = response[start:end]

            try:
                data = json.loads(json_block)
            except json.JSONDecodeError:
                print("Invalid JSON returned by LLM. Regenerating...")
                return self.run(topic)

        questions = []

        for item in data:

            if (
                isinstance(item, dict)
                and "question" in item
                and "options" in item
                and "answer" in item
            ):

                options = item["options"]

                if isinstance(options, list) and len(options) == 4:

                    questions.append(
                        Question(
                            question=item["question"],
                            options=options,
                            answer=item["answer"]
                        )
                    )

        print("Parsed questions:", len(questions))

        # Retry generation if LLM failed
        if len(questions) < 5:

            print("Retrying question generation due to insufficient questions...")

            return self.run(topic, exam_type, level, num_questions)

        return questions