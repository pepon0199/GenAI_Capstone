from typing import List, Optional

from pydantic import BaseModel, Field


class Question(BaseModel):
    question: str
    options: List[str]
    answer: str
    difficulty: Optional[str] = None
    explanation: Optional[str] = None


class Exam(BaseModel):
    topic: str
    questions: List[Question]
    review_notes: List[str] = Field(default_factory=list)
