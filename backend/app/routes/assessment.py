from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.assessment import AssessmentQuestionsResponse
from app.services.assessment import get_assessment_questions


router = APIRouter(
    prefix="/assessment",
    tags=["Assessment"],
)


@router.get(
    "/questions",
    response_model=AssessmentQuestionsResponse,
)
def get_questions(
    db: Session = Depends(get_db),
):
    """
    Get all assessment questions grouped by skill category.
    Each question includes the standard 5-point Likert scale answer options.
    """
    categories = get_assessment_questions(db)
    return {"categories": categories}