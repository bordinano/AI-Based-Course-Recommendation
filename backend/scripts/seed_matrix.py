#!/usr/bin/env python
"""Seed script for scoring matrix v1 with placeholder weights."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import (
    ScoringMatrixVersion,
    AptitudeWeight,
    InterestWeight,
    CareerWeight,
    SkillCategory,
    Interest,
    AcademicProgram,
)


def seed_matrix(db: Session) -> None:
    """Insert scoring matrix v1 with placeholder weights."""
    # Check if v1 already exists
    existing = db.query(ScoringMatrixVersion).filter_by(version="v1").first()
    if existing:
        print("Scoring matrix v1 already exists")
        return

    # Create matrix version
    matrix = ScoringMatrixVersion(
        version="v1",
        description="Initial placeholder weights - to be validated by guidance counselor",
        is_active=True,
    )
    db.add(matrix)
    db.flush()

    # Get all skill categories
    categories = db.query(SkillCategory).order_by(SkillCategory.id).all()
    # Equal weights for aptitude (sum = 1.0)
    aptitude_weight_per_category = 1.0 / len(categories)
    for cat in categories:
        db.add(AptitudeWeight(
            matrix_version_id=matrix.id,
            skill_category_id=cat.id,
            weight=aptitude_weight_per_category,
        ))

    # Get all interests and academic programs for interest weights
    interests = db.query(Interest).all()
    programs = db.query(AcademicProgram).filter(AcademicProgram.is_active == True).all()

    # Placeholder: equal weights for all interest-program combinations
    # In reality, these should be set by counselor based on program-interest alignment
    interest_weight_value = 1.0 / (len(interests) * len(programs)) if interests and programs else 0
    for interest in interests:
        for program in programs:
            db.add(InterestWeight(
                matrix_version_id=matrix.id,
                interest_id=interest.id,
                academic_program_id=program.id,
                weight=interest_weight_value,
            ))

    # Career weights - placeholder equal weights
    careers = [
        "Technology", "Business", "Healthcare", "Education", "Arts", "None"
    ]
    career_weight_value = 1.0 / (len(careers) * len(programs)) if programs else 0
    for career in careers:
        for program in programs:
            db.add(CareerWeight(
                matrix_version_id=matrix.id,
                career_name=career,
                academic_program_id=program.id,
                weight=career_weight_value,
            ))

    db.commit()
    print("Seeded scoring matrix v1 with placeholder weights")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_matrix(db)
    finally:
        db.close()