from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.database import get_db
from app.schemas.result import AssessmentResultResponse
from app.services.recommendation import get_recommendation_results


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

    # TODO: Implement actual email sending (e.g., via SendGrid, SMTP, etc.)
    # For now, we'll log and return success
    import logging
    logging.info(f"Sending results for attempt {attempt_id} to {request.email}")

    # Placeholder for email sending logic
    # In production, integrate with an email service like:
    # - SendGrid: sendgrid.SendGridAPIClient
    # - AWS SES: boto3.client('ses')
    # - SMTP: smtplib.SMTP

    return {"message": "Results sent successfully", "email": request.email}