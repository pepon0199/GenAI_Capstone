from llm.factory import create_llm_client
from schemas.exam_schema import Question


class QuestionGeneratorAgent:
    def __init__(self, max_retries=3, provider=None):
        self.llm = create_llm_client(provider=provider)
        self.max_retries = max_retries

    def run(self, topic, exam_type, level, num_questions):
        system_prompt = """
You generate high-quality certification-style multiple choice exam questions.
Return valid JSON only.
""".strip()

        prompt = f"""
Create exactly {num_questions} multiple choice questions for the topic "{topic}".

Exam type: {exam_type}
Certification level: {level}

Difficulty guidelines:
- Beginner: basic concepts, terminology, and straightforward recall
- Intermediate: conceptual understanding and practical application
- Advanced: scenario-based reasoning, tradeoffs, and deeper problem solving

Return a JSON object with this shape:
{{
  "questions": [
    {{
      "question": "question text",
      "options": ["option1", "option2", "option3", "option4"],
      "answer": "one option copied exactly",
      "difficulty": "Easy | Medium | Hard",
      "explanation": "one short explanation of why the answer is correct"
    }}
  ]
}}

Rules:
- Return exactly {num_questions} questions.
- Each question must have exactly 4 distinct options.
- The answer must exactly match one option.
- Keep questions aligned with the requested certification level.
- Avoid duplicate or near-duplicate questions.
- Do not include markdown or any text outside the JSON object.
""".strip()

        last_error = None

        for _ in range(self.max_retries):
            try:
                data = self.llm.generate_json(prompt, system_prompt=system_prompt)
                questions = self._parse_questions(data)

                if len(questions) >= num_questions:
                    return questions[:num_questions]

                last_error = ValueError(
                    f"Expected {num_questions} valid questions, got {len(questions)}."
                )
            except (ValueError, TypeError, KeyError) as exc:
                last_error = exc

        raise ValueError(
            f"Question generation failed after {self.max_retries} attempts: {last_error}"
        )

    def _parse_questions(self, data):
        items = data.get("questions", [])

        if not isinstance(items, list):
            raise ValueError("JSON payload is missing a 'questions' list.")

        questions = []

        for item in items:
            if not isinstance(item, dict):
                continue

            question_text = str(item.get("question", "")).strip()
            answer = str(item.get("answer", "")).strip()
            difficulty = str(item.get("difficulty", "")).strip().title() or None
            explanation = str(item.get("explanation", "")).strip() or None
            raw_options = item.get("options", [])

            if not isinstance(raw_options, list):
                continue

            options = [str(option).strip() for option in raw_options if str(option).strip()]

            if not question_text or len(options) != 4 or answer not in options:
                continue

            questions.append(
                Question(
                    question=question_text,
                    options=options,
                    answer=answer,
                    difficulty=difficulty,
                    explanation=explanation,
                )
            )

        return questions
