class ExamCheckerAgent:
    def validate_questions(self, questions, level):
        validated = []
        seen = set()
        allowed_difficulties = self._allowed_difficulties(level)

        for question in questions:
            normalized_question = " ".join(question.question.lower().split())
            normalized_options = tuple(" ".join(option.lower().split()) for option in question.options)
            question_key = (normalized_question, normalized_options)

            if question_key in seen:
                continue

            if len(question.options) != 4:
                continue

            if len(set(normalized_options)) != 4:
                continue

            if question.answer not in question.options:
                continue

            if question.difficulty and question.difficulty not in allowed_difficulties:
                continue

            seen.add(question_key)
            validated.append(question)

        return validated

    def run(self, exam, expected_count):
        if len(exam.questions) != expected_count:
            raise ValueError(
                f"Expected {expected_count} validated questions, got {len(exam.questions)}."
            )

        return exam

    def _allowed_difficulties(self, level):
        mapping = {
            "Beginner": {"Easy", "Medium"},
            "Intermediate": {"Medium"},
            "Advanced": {"Medium", "Hard"},
        }
        return mapping.get(level, {"Medium"})
