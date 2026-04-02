import pytest

from agents.exam_checker_agent import ExamCheckerAgent
from schemas.exam_schema import Exam, Question


def make_question(question, options, answer, difficulty="Medium"):
    return Question(
        question=question,
        options=options,
        answer=answer,
        difficulty=difficulty,
    )


def test_validate_questions_filters_duplicates_and_invalid_questions():
    checker = ExamCheckerAgent()
    questions = [
        make_question(
            "What is Python?",
            ["A language", "A snake", "A database", "A browser"],
            "A language",
            "Easy",
        ),
        make_question(
            "What is Python?",
            ["A language", "A snake", "A database", "A browser"],
            "A language",
            "Easy",
        ),
        make_question(
            "Pick the valid option count",
            ["One", "Two", "Three"],
            "One",
            "Easy",
        ),
        make_question(
            "Which answer is valid?",
            ["One", "One", "Three", "Four"],
            "One",
            "Easy",
        ),
    ]

    validated = checker.validate_questions(questions, "Beginner")

    assert len(validated) == 1
    assert validated[0].question == "What is Python?"


def test_validate_questions_filters_difficulty_mismatch():
    checker = ExamCheckerAgent()
    questions = [
        make_question(
            "Advanced only question",
            ["A", "B", "C", "D"],
            "A",
            "Hard",
        )
    ]

    validated = checker.validate_questions(questions, "Intermediate")

    assert validated == []


def test_run_raises_when_expected_count_is_not_met():
    checker = ExamCheckerAgent()
    exam = Exam(topic="Topic", questions=[])

    with pytest.raises(ValueError, match="Expected 2 validated questions, got 0"):
        checker.run(exam, expected_count=2)
