from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.attempt import (
    AttemptCreate,
    AttemptResponse,
    ResponsesSubmit,
    AttemptCompleteResponse,
)
from app.services.attempt import (
    create_attempt,
    get_attempt,
    submit_responses,
    complete_attempt,
    get_attempt_responses,
)


router = APIRouter(
    prefix="/assessment/attempts",
    tags=["Assessment Attempts"],
)


@router.post(
    "/",
    response_model=AttemptResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_attempt(
    attempt_data: AttemptCreate,
    db: Session = Depends(get_db),
):
    """Create a new assessment attempt for a student."""
    return create_attempt(db, attempt_data.student_id)


@router.post(
    "/{attempt_id}/responses",
    status_code=status.HTTP_200_OK,
)
def save_responses(
    attempt_id: int,
    responses_data: ResponsesSubmit,
    db: Session = Depends(get_db),
):
    """Save or update student responses for an attempt."""
    try:
        count = submit_responses(
            db,
            attempt_id,
            [r.model_dump() for r in responses_data.responses],
        )
        return {"saved": count}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/{attempt_id}/complete",
    response_model=AttemptCompleteResponse,
)
def finish_attempt(
    attempt_id: int,
    db: Session = Depends(get_db),
):
    """Complete an assessment attempt and trigger scoring."""
    try:
        attempt = complete_attempt(db, attempt_id)
        responses = get_attempt_responses(db, attempt_id)
        return {
            "id": attempt.id,
            "student_id": attempt.student_id,
            "status": attempt.status,
            "started_at": attempt.started_at,
            "completed_at": attempt.completed_at,
            "responses": [
                {"question_id": r.question_id, "answer_option_id": r.answer_option_id}
                for r in responses
            ],
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))