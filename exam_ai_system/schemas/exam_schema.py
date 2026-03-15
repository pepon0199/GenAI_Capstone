from pydantic import BaseModel
from typing import List

class Question(BaseModel):

    question: str
    options: List[str]
    answer: str
    difficulty: str | None = None


class Exam(BaseModel):

    topic: str
    questions: List[Question]