from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.skill_category import SkillCategory
    from app.models.interest import Interest
    from app.models.academic_program import AcademicProgram


class ScoringMatrixVersion(Base):
    __tablename__ = "scoring_matrix_versions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    version: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    aptitude_weights: Mapped[list["AptitudeWeight"]] = relationship(
        "AptitudeWeight",
        back_populates="matrix_version",
        cascade="all, delete-orphan",
    )

    interest_weights: Mapped[list["InterestWeight"]] = relationship(
        "InterestWeight",
        back_populates="matrix_version",
        cascade="all, delete-orphan",
    )

    career_weights: Mapped[list["CareerWeight"]] = relationship(
        "CareerWeight",
        back_populates="matrix_version",
        cascade="all, delete-orphan",
    )

    assessment_results: Mapped[list["AssessmentResult"]] = relationship(
        "AssessmentResult",
        back_populates="matrix_version",
    )


class AptitudeWeight(Base):
    __tablename__ = "aptitude_weights"

    __table_args__ = (
        UniqueConstraint(
            "matrix_version_id",
            "skill_category_id",
            name="uq_aptitude_weight_matrix_category",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    matrix_version_id: Mapped[int] = mapped_column(
        ForeignKey("scoring_matrix_versions.id", ondelete="CASCADE"),
        nullable=False,
    )

    skill_category_id: Mapped[int] = mapped_column(
        ForeignKey("skill_categories.id", ondelete="RESTRICT"),
        nullable=False,
    )

    weight: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    matrix_version: Mapped["ScoringMatrixVersion"] = relationship(
        "ScoringMatrixVersion",
        back_populates="aptitude_weights",
    )

    skill_category: Mapped["SkillCategory"] = relationship(
        "SkillCategory",
    )


class InterestWeight(Base):
    __tablename__ = "interest_weights"

    __table_args__ = (
        UniqueConstraint(
            "matrix_version_id",
            "interest_id",
            "academic_program_id",
            name="uq_interest_weight_matrix_interest_program",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    matrix_version_id: Mapped[int] = mapped_column(
        ForeignKey("scoring_matrix_versions.id", ondelete="CASCADE"),
        nullable=False,
    )

    interest_id: Mapped[int] = mapped_column(
        ForeignKey("interests.id", ondelete="RESTRICT"),
        nullable=False,
    )

    academic_program_id: Mapped[int] = mapped_column(
        ForeignKey("academic_programs.id", ondelete="RESTRICT"),
        nullable=False,
    )

    weight: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    matrix_version: Mapped["ScoringMatrixVersion"] = relationship(
        "ScoringMatrixVersion",
        back_populates="interest_weights",
    )

    interest: Mapped["Interest"] = relationship("Interest")

    academic_program: Mapped["AcademicProgram"] = relationship("AcademicProgram")


class CareerWeight(Base):
    __tablename__ = "career_weights"

    __table_args__ = (
        UniqueConstraint(
            "matrix_version_id",
            "career_name",
            "academic_program_id",
            name="uq_career_weight_matrix_career_program",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    matrix_version_id: Mapped[int] = mapped_column(
        ForeignKey("scoring_matrix_versions.id", ondelete="CASCADE"),
        nullable=False,
    )

    career_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    academic_program_id: Mapped[int] = mapped_column(
        ForeignKey("academic_programs.id", ondelete="RESTRICT"),
        nullable=False,
    )

    weight: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    matrix_version: Mapped["ScoringMatrixVersion"] = relationship(
        "ScoringMatrixVersion",
        back_populates="career_weights",
    )

    academic_program: Mapped["AcademicProgram"] = relationship("AcademicProgram")