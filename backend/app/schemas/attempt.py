from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class AttemptCreate(BaseModel):
    student_id: int = Field(gt=0)


class AttemptResponse(BaseModel):
    id: int
    student_id: int
    status: str
    started_at: datetime
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ResponseInput(BaseModel):
    question_id: int = Field(gt=0)
    answer_option_id: int = Field(ge=1, le=5)


class ResponsesSubmit(BaseModel):
    responses: list[ResponseInput]


class ResponseRecord(BaseModel):
    question_id: int
    answer_option_id: int

    model_config = ConfigDict(from_attributes=True)


class AttemptCompleteResponse(BaseModel):
    id: int
    student_id: int
    status: str
    started_at: datetime
    completed_at: datetime
    responses: list[ResponseRecord]

    model_config = ConfigDict(from_attributes=True)