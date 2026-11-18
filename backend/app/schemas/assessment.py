from pydantic import BaseModel, ConfigDict
from typing import Optional


class AnswerOptionSchema(BaseModel):
    id: int
    label: str
    score: int

    model_config = ConfigDict(from_attributes=True)


class AssessmentQuestionSchema(BaseModel):
    id: int
    question_text: str
    answer_options: list[AnswerOptionSchema]

    model_config = ConfigDict(from_attributes=True)


class SkillCategoryWithQuestions(BaseModel):
    id: int
    name: str
    description: str | None = None
    questions: list[AssessmentQuestionSchema]

    model_config = ConfigDict(from_attributes=True)


class AssessmentQuestionsResponse(BaseModel):
    categories: list[SkillCategoryWithQuestions]