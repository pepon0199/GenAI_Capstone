from agents.question_generator_agent import QuestionGeneratorAgent
from agents.fact_checker_agent import FactCheckerAgent
from agents.exam_builder_agent import ExamBuilderAgent
from agents.exam_checker_agent import ExamCheckerAgent


class ExamOrchestratorAgent:

    def __init__(self, provider=None):

        self.q_agent = QuestionGeneratorAgent(provider=provider)
        self.f_agent = FactCheckerAgent(provider=provider)
        self.b_agent = ExamBuilderAgent()
        self.c_agent = ExamCheckerAgent()

    def generate_exam(self, topic, exam_type, level, num_questions):

        approved_questions = []
        review_notes = []
        max_attempts = 3

        # map certification level → expected difficulty
        for _ in range(max_attempts):

            remaining = num_questions - len(approved_questions)

            if remaining <= 0:
                break

            needed = max(remaining + 3, remaining * 2)

            generated_questions = self.q_agent.run(
                topic,
                exam_type,
                level,
                needed
            )

            valid_questions = self.c_agent.validate_questions(generated_questions, level)
            reviewed_questions, notes = self.f_agent.run(valid_questions, topic, level)
            review_notes.extend(notes)

            merged_questions = approved_questions + reviewed_questions
            approved_questions = self.c_agent.validate_questions(merged_questions, level)

        questions = approved_questions[:num_questions]

        exam = self.b_agent.run(topic, questions)

        exam.review_notes = review_notes

        return self.c_agent.run(exam, expected_count=num_questions)
