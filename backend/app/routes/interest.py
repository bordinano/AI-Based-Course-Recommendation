from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.interest import InterestResponse
from app.services.interest import get_all_interests


router = APIRouter(
    prefix="/interests",
    tags=["Interests"],
)


@router.get(
    "/",
    response_model=list[InterestResponse],
)
def list_interests(
    db: Session = Depends(get_db),
):
    """Get all available interests for student selection."""
    return get_all_interests(db)