from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.assessment_attempt import AssessmentAttempt
    from app.models.academic_program import AcademicProgram
    from app.models.school import School
    from app.models.school_program import SchoolProgram
    from app.models.scoring_matrix import ScoringMatrixVersion


class AssessmentResult(Base):
    __tablename__ = "assessment_results"

    __table_args__ = (
        UniqueConstraint(
            "attempt_id",
            name="uq_assessment_result_attempt",
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

    matrix_version_id: Mapped[int] = mapped_column(
        ForeignKey("scoring_matrix_versions.id", ondelete="RESTRICT"),
        nullable=False,
    )

    aptitude_scores: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    interest_scores: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    career_scores: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    final_scores: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    attempt: Mapped["AssessmentAttempt"] = relationship(
        "AssessmentAttempt",
        back_populates="result",
    )

    matrix_version: Mapped["ScoringMatrixVersion"] = relationship(
        "ScoringMatrixVersion",
        back_populates="assessment_results",
    )

    recommended_programs: Mapped[list["RecommendedProgram"]] = relationship(
        "RecommendedProgram",
        back_populates="result",
        cascade="all, delete-orphan",
    )

    recommended_schools: Mapped[list["RecommendedSchool"]] = relationship(
        "RecommendedSchool",
        back_populates="result",
        cascade="all, delete-orphan",
    )


class RecommendedProgram(Base):
    __tablename__ = "recommended_programs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    result_id: Mapped[int] = mapped_column(
        ForeignKey("assessment_results.id", ondelete="CASCADE"),
        nullable=False,
    )

    academic_program_id: Mapped[int] = mapped_column(
        ForeignKey("academic_programs.id", ondelete="RESTRICT"),
        nullable=False,
    )

    compatibility_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    rank: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    aptitude_component: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    interest_component: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    career_component: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    explanation: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    result: Mapped["AssessmentResult"] = relationship(
        "AssessmentResult",
        back_populates="recommended_programs",
    )

    academic_program: Mapped["AcademicProgram"] = relationship("AcademicProgram")


class RecommendedSchool(Base):
    __tablename__ = "recommended_schools"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    result_id: Mapped[int] = mapped_column(
        ForeignKey("assessment_results.id", ondelete="CASCADE"),
        nullable=False,
    )

    school_id: Mapped[int] = mapped_column(
        ForeignKey("schools.id", ondelete="RESTRICT"),
        nullable=False,
    )

    program_id: Mapped[int] = mapped_column(
        ForeignKey("academic_programs.id", ondelete="RESTRICT"),
        nullable=False,
    )

    is_public: Mapped[bool] = mapped_column(
        nullable=False,
    )

    result: Mapped["AssessmentResult"] = relationship(
        "AssessmentResult",
        back_populates="recommended_schools",
    )

    school: Mapped["School"] = relationship("School")

    program: Mapped["AcademicProgram"] = relationship("AcademicProgram")