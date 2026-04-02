from llm.factory import create_llm_client


class FactCheckerAgent:
    def __init__(self, provider=None):
        self.llm = create_llm_client(provider=provider)

    def run(self, questions, topic, level):
        if not questions:
            return [], ["No questions were available for review."]

        system_prompt = """
You are reviewing exam questions for quality issues.
Return valid JSON only.
""".strip()

        serialized_questions = []

        for index, question in enumerate(questions):
            serialized_questions.append(
                {
                    "index": index,
                    "question": question.question,
                    "options": question.options,
                    "answer": question.answer,
                    "difficulty": question.difficulty,
                    "explanation": question.explanation,
                }
            )

        prompt = f"""
Review these exam questions for the topic "{topic}" at "{level}" certification level.

Flag only material issues such as:
- incorrect answer key
- ambiguous wording
- duplicate options
- more than one plausible correct answer
- weak distractors
- level mismatch

Return a JSON object with this shape:
{{
  "results": [
    {{
      "index": 0,
      "approved": true,
      "issues": []
    }}
  ]
}}

Questions to review:
{serialized_questions}
""".strip()

        data = self.llm.generate_json(prompt, system_prompt=system_prompt)
        results = data.get("results", [])
        approved_questions = []
        notes = []

        for item in results:
            if not isinstance(item, dict):
                continue

            index = item.get("index")
            approved = bool(item.get("approved"))
            issues = item.get("issues", [])

            if not isinstance(index, int) or not (0 <= index < len(questions)):
                continue

            if approved:
                approved_questions.append(questions[index])
            else:
                issue_text = ", ".join(str(issue).strip() for issue in issues if str(issue).strip())
                if issue_text:
                    notes.append(f"Question {index + 1}: {issue_text}")

        if not approved_questions:
            notes.append("Reviewer rejected all generated questions.")

        return approved_questions, notes
