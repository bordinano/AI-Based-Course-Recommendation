from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class StudentInterest(Base):
    __tablename__ = "student_interests"

    __table_args__ = (
        CheckConstraint(
            """
            (interest_id IS NOT NULL AND other_interest IS NULL)
            OR
            (interest_id IS NULL AND other_interest IS NOT NULL
             AND length(trim(other_interest)) > 0)
            """,
            name="ck_student_interest_valid_selection",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
    )

    interest_id: Mapped[int | None] = mapped_column(
        ForeignKey("interests.id", ondelete="CASCADE"),
        nullable=True,
    )

    other_interest: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )