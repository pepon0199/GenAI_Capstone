class ExamCheckerAgent:

    def run(self, exam):

        if len(exam.questions) == 0:

            raise Exception("Not enough valid questions generated")

        return exam