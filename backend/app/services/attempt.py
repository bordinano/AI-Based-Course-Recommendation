from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.assessment_attempt import AssessmentAttempt
from app.models.student_response import StudentResponse
from app.models.assessment_question import AssessmentQuestion
from app.models.answer_option import AnswerOption
from app.services.recommendation import generate_recommendations


def create_attempt(db: Session, student_id: int) -> AssessmentAttempt:
    """Create a new assessment attempt for a student."""
    attempt = AssessmentAttempt(
        student_id=student_id,
        status="in_progress",
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


def get_attempt(db: Session, attempt_id: int) -> AssessmentAttempt | None:
    """Retrieve an attempt by ID."""
    return db.query(AssessmentAttempt).filter(AssessmentAttempt.id == attempt_id).first()


def submit_responses(
    db: Session,
    attempt_id: int,
    responses: list[dict],
) -> int:
    """
    Bulk upsert student responses for an attempt.
    Uses ON CONFLICT to prevent duplicate responses for same question.
    Returns count of responses saved.
    """
    attempt = get_attempt(db, attempt_id)
    if not attempt:
        raise ValueError("Attempt not found")
    if attempt.status != "in_progress":
        raise ValueError("Attempt is not in progress")

    # Validate all questions exist and are active
    question_ids = [r["question_id"] for r in responses]
    questions = db.query(AssessmentQuestion).filter(
        AssessmentQuestion.id.in_(question_ids),
        AssessmentQuestion.is_active == True,
    ).all()
    valid_question_ids = {q.id for q in questions}
    invalid_ids = set(question_ids) - valid_question_ids
    if invalid_ids:
        raise ValueError(f"Invalid or inactive question IDs: {invalid_ids}")

    # Validate all answer options exist
    answer_option_ids = [r["answer_option_id"] for r in responses]
    answer_options = db.query(AnswerOption).filter(
        AnswerOption.id.in_(answer_option_ids),
    ).all()
    valid_answer_ids = {a.id for a in answer_options}
    invalid_answer_ids = set(answer_option_ids) - valid_answer_ids
    if invalid_answer_ids:
        raise ValueError(f"Invalid answer option IDs: {invalid_answer_ids}")

    # Bulk upsert using PostgreSQL ON CONFLICT
    stmt = pg_insert(StudentResponse).values([
        {
            "attempt_id": attempt_id,
            "question_id": r["question_id"],
            "answer_option_id": r["answer_option_id"],
        }
        for r in responses
    ])
    stmt = stmt.on_conflict_do_update(
        index_elements=["attempt_id", "question_id"],
        set_={"answer_option_id": stmt.excluded.answer_option_id},
    )
    result = db.execute(stmt)
    db.commit()

    return result.rowcount


def complete_attempt(db: Session, attempt_id: int) -> AssessmentAttempt:
    """Mark an attempt as completed and generate recommendations."""
    attempt = get_attempt(db, attempt_id)
    if not attempt:
        raise ValueError("Attempt not found")
    if attempt.status != "in_progress":
        raise ValueError("Attempt is not in progress")

    attempt.status = "completed"
    attempt.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(attempt)

    # Generate recommendations
    try:
        generate_recommendations(db, attempt_id)
    except Exception as e:
        # Log error but don't fail the completion
        print(f"Warning: Failed to generate recommendations for attempt {attempt_id}: {e}")

    return attempt


def get_attempt_responses(db: Session, attempt_id: int) -> list[StudentResponse]:
    """Get all responses for an attempt with related data."""
    return (
        db.query(StudentResponse)
        .filter(StudentResponse.attempt_id == attempt_id)
        .order_by(StudentResponse.question_id)
        .all()
    )