#!/usr/bin/env python
"""Seed script for academic programs (CHED-recognized in Muntinlupa)."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import AcademicProgram


# Sample CHED-recognized programs commonly offered in Muntinlupa colleges
PROGRAMS = [
    # Bachelor's degrees
    {"name": "Bachelor of Science in Information Technology", "degree_level": "Bachelor's", "description": "Focus on software development, systems analysis, and IT infrastructure"},
    {"name": "Bachelor of Science in Computer Science", "degree_level": "Bachelor's", "description": "Focus on algorithms, programming languages, and computational theory"},
    {"name": "Bachelor of Science in Information Systems", "degree_level": "Bachelor's", "description": "Focus on business information systems and technology management"},
    {"name": "Bachelor of Science in Computer Engineering", "degree_level": "Bachelor's", "description": "Focus on hardware-software integration and embedded systems"},
    {"name": "Bachelor of Science in Nursing", "degree_level": "Bachelor's", "description": "Professional nursing education and clinical practice"},
    {"name": "Bachelor of Science in Pharmacy", "degree_level": "Bachelor's", "description": "Pharmaceutical science and pharmacy practice"},
    {"name": "Bachelor of Science in Medical Technology", "degree_level": "Bachelor's", "description": "Clinical laboratory science and diagnostics"},
    {"name": "Bachelor of Science in Psychology", "degree_level": "Bachelor's", "description": "Human behavior, mental processes, and psychological assessment"},
    {"name": "Bachelor of Science in Business Administration", "degree_level": "Bachelor's", "description": "General business management with major options"},
    {"name": "Bachelor of Science in Accountancy", "degree_level": "Bachelor's", "description": "Financial accounting, auditing, and taxation"},
    {"name": "Bachelor of Science in Entrepreneurship", "degree_level": "Bachelor's", "description": "Business creation, innovation, and venture management"},
    {"name": "Bachelor of Science in Hospitality Management", "degree_level": "Bachelor's", "description": "Hotel, restaurant, and tourism operations"},
    {"name": "Bachelor of Science in Tourism Management", "degree_level": "Bachelor's", "description": "Travel industry, tour operations, and destination management"},
    {"name": "Bachelor of Science in Education", "degree_level": "Bachelor's", "description": "Teacher education with specialization options"},
    {"name": "Bachelor of Science in Civil Engineering", "degree_level": "Bachelor's", "description": "Infrastructure design, construction, and project management"},
    {"name": "Bachelor of Science in Electrical Engineering", "degree_level": "Bachelor's", "description": "Power systems, electronics, and electrical design"},
    {"name": "Bachelor of Science in Mechanical Engineering", "degree_level": "Bachelor's", "description": "Mechanical systems, thermodynamics, and manufacturing"},
    {"name": "Bachelor of Science in Architecture", "degree_level": "Bachelor's", "description": "Building design, urban planning, and architectural theory"},
    {"name": "Bachelor of Arts in Communication", "degree_level": "Bachelor's", "description": "Media, journalism, and strategic communication"},
    {"name": "Bachelor of Arts in Political Science", "degree_level": "Bachelor's", "description": "Government, public policy, and political theory"},
    {"name": "Bachelor of Arts in Psychology", "degree_level": "Bachelor's", "description": "Liberal arts approach to psychological science"},
    {"name": "Bachelor of Arts in English Language Studies", "degree_level": "Bachelor's", "description": "English language, linguistics, and literature"},
    {"name": "Bachelor of Science in Criminology", "degree_level": "Bachelor's", "description": "Criminal justice, law enforcement, and corrections"},
    {"name": "Bachelor of Science in Radiologic Technology", "degree_level": "Bachelor's", "description": "Medical imaging and radiation therapy"},
    {"name": "Bachelor of Science in Physical Therapy", "degree_level": "Bachelor's", "description": "Rehabilitation, movement science, and therapeutic exercise"},
    # Associate degrees
    {"name": "Associate in Computer Technology", "degree_level": "Associate", "description": "Two-year program in computer hardware and software fundamentals"},
    {"name": "Associate in Information Technology", "degree_level": "Associate", "description": "Two-year program in IT support and basic programming"},
    {"name": "Associate in Business Administration", "degree_level": "Associate", "description": "Two-year program in business fundamentals"},
    {"name": "Associate in Hospitality Management", "degree_level": "Associate", "description": "Two-year program in hotel and restaurant operations"},
    {"name": "Associate in Health Science", "degree_level": "Associate", "description": "Two-year program in health services fundamentals"},
]


def seed_programs(db: Session) -> None:
    """Insert academic programs if not already present."""
    existing_names = {p.name for p in db.query(AcademicProgram.name).all()}
    new_count = 0

    for data in PROGRAMS:
        if data["name"] not in existing_names:
            program = AcademicProgram(**data, is_active=True)
            db.add(program)
            new_count += 1

    if new_count:
        db.commit()
        print(f"Seeded {new_count} new academic programs")
    else:
        print("All academic programs already exist")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_programs(db)
    finally:
        db.close()