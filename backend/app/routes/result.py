from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.database import get_db
from app.schemas.result import AssessmentResultResponse
from app.services.recommendation import get_recommendation_results
from app.services.email import send_results_email as send_email_service
from app.models.assessment_attempt import AssessmentAttempt
from app.models.student import Student


router = APIRouter(
    prefix="/assessment",
    tags=["Assessment Results"],
)


class SendResultsRequest(BaseModel):
    email: EmailStr


@router.get(
    "/attempts/{attempt_id}/results",
    response_model=AssessmentResultResponse,
)
def get_assessment_results(
    attempt_id: int,
    school_type: str | None = Query(None, pattern="^(Public|Private)$"),
    db: Session = Depends(get_db),
):
    """
    Get recommendation results for a completed assessment attempt.

    Optional query parameter:
    - school_type: Filter schools by "Public" or "Private"
    """
    results = get_recommendation_results(db, attempt_id, school_type)
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Results not found for this attempt"
        )
    return results


@router.post(
    "/attempts/{attempt_id}/send-results",
    status_code=status.HTTP_200_OK,
)
def send_results_email(
    attempt_id: int,
    request: SendResultsRequest,
    db: Session = Depends(get_db),
):
    """
    Send assessment results to the provided email address.
    """
    # Verify the attempt exists and has results
    results = get_recommendation_results(db, attempt_id)
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Results not found for this attempt"
        )

    # Get student name for personalized email
    attempt = db.query(AssessmentAttempt).filter(AssessmentAttempt.id == attempt_id).first()
    student_name = "Student"
    if attempt:
        student = db.query(Student).filter(Student.id == attempt.student_id).first()
        if student:
            student_name = student.full_name

    # Send email
    success = send_email_service(request.email, student_name, results)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email. Please check email configuration."
        )

    return {"message": "Results sent successfully", "email": request.email}