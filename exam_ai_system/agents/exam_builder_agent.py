from schemas.exam_schema import Exam

class ExamBuilderAgent:

    def run(self, topic, questions):

        return Exam(
            topic=topic,
            questions=questions
        )