from sqlalchemy import CheckConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AnswerOption(Base):
    __tablename__ = "answer_options"

    __table_args__ = (
        CheckConstraint(
            "score BETWEEN 1 AND 5",
            name="ck_answer_option_score_range",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    label: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    score: Mapped[int] = mapped_column(
        Integer,
        unique=True,
        nullable=False,
    )