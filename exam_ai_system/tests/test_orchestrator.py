import orchestrator.exam_orchestrator as orchestrator_module
from schemas.exam_schema import Exam, Question


class FakeQuestionAgent:
    def run(self, topic, exam_type, level, needed):
        return [
            Question(
                question=f"Question {i}",
                options=[f"Correct {i}", f"Wrong {i}A", f"Wrong {i}B", f"Wrong {i}C"],
                answer=f"Correct {i}",
                difficulty="Easy" if i % 2 else "Medium",
            )
            for i in range(1, needed + 1)
        ]


class FakeFactCheckerAgent:
    def run(self, questions, topic, level):
        return questions[:5], ["Reviewed batch"]


class FakeCheckerAgent:
    def validate_questions(self, questions, level):
        deduped = []
        seen = set()
        for question in questions:
            if question.question not in seen:
                deduped.append(question)
                seen.add(question.question)
        return deduped

    def run(self, exam, expected_count):
        if len(exam.questions) != expected_count:
            raise ValueError("Wrong count")
        return exam


class FakeBuilderAgent:
    def run(self, topic, questions):
        return Exam(topic=topic, questions=questions)


def test_orchestrator_builds_exam_with_notes(monkeypatch):
    monkeypatch.setattr(orchestrator_module, "QuestionGeneratorAgent", lambda provider=None: FakeQuestionAgent())
    monkeypatch.setattr(orchestrator_module, "FactCheckerAgent", lambda provider=None: FakeFactCheckerAgent())
    monkeypatch.setattr(orchestrator_module, "ExamCheckerAgent", lambda: FakeCheckerAgent())
    monkeypatch.setattr(orchestrator_module, "ExamBuilderAgent", lambda: FakeBuilderAgent())

    orchestrator = orchestrator_module.ExamOrchestratorAgent(provider="groq")

    exam = orchestrator.generate_exam(
        topic="AI Fundamentals",
        exam_type="Practice Exam",
        level="Beginner",
        num_questions=5,
    )

    assert len(exam.questions) == 5
    assert exam.topic == "AI Fundamentals"
    assert exam.review_notes == ["Reviewed batch"]
