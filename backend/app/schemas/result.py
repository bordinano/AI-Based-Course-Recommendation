from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ComponentScores(BaseModel):
    aptitude: float
    interest: float
    career: float


class RecommendedProgramResponse(BaseModel):
    academic_program_id: int
    program_name: str
    degree_level: str
    description: Optional[str] = None
    compatibility_score: float
    rank: int
    components: ComponentScores
    explanation: Optional[str] = None


class RecommendedSchoolResponse(BaseModel):
    school_id: int
    school_name: str
    institution_type: str
    address: str
    website_url: Optional[str] = None
    program_offered: str
    program_id: int


class AssessmentResultResponse(BaseModel):
    attempt_id: int
    matrix_version: str
    recommended_programs: list[RecommendedProgramResponse]
    recommended_schools: list[RecommendedSchoolResponse]

    model_config = ConfigDict(from_attributes=True)