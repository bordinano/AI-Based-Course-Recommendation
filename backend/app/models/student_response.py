
from sqlalchemy import (
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class StudentResponse(Base):
    __tablename__ = "student_responses"

    __table_args__ = (
        UniqueConstraint(
            "attempt_id",
            "question_id",
            name="uq_student_response_attempt_question",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    attempt_id: Mapped[int] = mapped_column(
        ForeignKey("assessment_attempts.id", ondelete="CASCADE"),
        nullable=False,
    )

    question_id: Mapped[int] = mapped_column(
        ForeignKey("assessment_questions.id", ondelete="RESTRICT"),
        nullable=False,
    )

    answer_option_id: Mapped[int] = mapped_column(
        ForeignKey("answer_options.id", ondelete="RESTRICT"),
        nullable=False,
    )
