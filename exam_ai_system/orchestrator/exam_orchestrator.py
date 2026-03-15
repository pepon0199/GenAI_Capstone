from agents.question_generator_agent import QuestionGeneratorAgent
from agents.fact_checker_agent import FactCheckerAgent
from agents.difficulty_evaluator_agent import DifficultyEvaluatorAgent
from agents.exam_builder_agent import ExamBuilderAgent
from agents.exam_checker_agent import ExamCheckerAgent


class ExamOrchestratorAgent:

    def __init__(self):

        self.q_agent = QuestionGeneratorAgent()
        self.f_agent = FactCheckerAgent()
        self.d_agent = DifficultyEvaluatorAgent()
        self.b_agent = ExamBuilderAgent()
        self.c_agent = ExamCheckerAgent()

    def generate_exam(self, topic, exam_type, level, num_questions):

        valid_questions = []
        attempts = 0
        max_attempts = 3

        # map certification level → expected difficulty
        expected = {
            "Beginner": "Easy",
            "Intermediate": "Medium",
            "Advanced": "Hard"
        }

        target_difficulty = expected.get(level, "Medium")

        while len(valid_questions) < num_questions and attempts < max_attempts:

            needed = max(10, num_questions * 2)

            new_questions = self.q_agent.run(
                topic,
                exam_type,
                level,
                needed
            )

            # Fact check
            checked_questions = self.f_agent.run(new_questions)

            # Evaluate difficulty
            checked_questions = self.d_agent.run(checked_questions)

            # Keep only questions matching certification level
            for q in checked_questions:
                if q.difficulty == target_difficulty:
                    valid_questions.append(q)

                # fallback acceptance if still lacking questions
                elif level == "Advanced" and q.difficulty == "Medium":
                    valid_questions.append(q)

            attempts += 1

        questions = valid_questions[:num_questions]

        exam = self.b_agent.run(topic, questions)

        exam = self.c_agent.run(exam)

        return exam