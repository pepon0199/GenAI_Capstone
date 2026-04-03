import pytest

import agents.question_generator_agent as question_generator_module


class FakeLLM:
    def __init__(self, responses):
        self.responses = list(responses)

    def generate_json(self, prompt, system_prompt=None):
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def test_question_generator_retries_then_succeeds(monkeypatch):
    monkeypatch.setattr(
        question_generator_module,
        "create_llm_client",
        lambda provider=None: FakeLLM([]),
    )
    agent = question_generator_module.QuestionGeneratorAgent(max_retries=2)
    agent.llm = FakeLLM(
        [
            {"questions": [{"question": "Bad", "options": ["A"], "answer": "A"}]},
            {
                "questions": [
                    {
                        "question": "What is Python?",
                        "options": ["A language", "A snake", "A browser", "A database"],
                        "answer": "A language",
                        "difficulty": "Easy",
                        "explanation": "Python is a programming language.",
                    }
                ]
            },
        ]
    )

    questions = agent.run("Python", "Practice Exam", "Beginner", 1)

    assert len(questions) == 1
    assert questions[0].question == "What is Python?"
    assert questions[0].answer == "A language"


def test_question_generator_raises_after_retry_limit(monkeypatch):
    monkeypatch.setattr(
        question_generator_module,
        "create_llm_client",
        lambda provider=None: FakeLLM([]),
    )
    agent = question_generator_module.QuestionGeneratorAgent(max_retries=2)
    agent.llm = FakeLLM([ValueError("bad payload"), ValueError("still bad")])

    with pytest.raises(ValueError, match="Question generation failed after 2 attempts"):
        agent.run("Python", "Practice Exam", "Beginner", 1)
