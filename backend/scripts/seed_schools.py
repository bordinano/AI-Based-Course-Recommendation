#!/usr/bin/env python
"""Seed script for Muntinlupa City schools and their programs."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import School, AcademicProgram, SchoolProgram


# Verified Muntinlupa City schools with their known programs
# Sources: CHED, school websites, official publications
SCHOOLS_DATA = [
    {
        "name": "Pamantasan ng Lungsod ng Muntinlupa (PLMun)",
        "institution_type": "Public",
        "address": "Brgy. Poblacion, Muntinlupa City",
        "website_url": "https://plmun.edu.ph",
        "programs": [
            "Bachelor of Science in Information Technology",
            "Bachelor of Science in Computer Science",
            "Bachelor of Science in Information Systems",
            "Bachelor of Science in Nursing",
            "Bachelor of Science in Psychology",
            "Bachelor of Science in Business Administration",
            "Bachelor of Science in Accountancy",
            "Bachelor of Science in Entrepreneurship",
            "Bachelor of Science in Hospitality Management",
            "Bachelor of Science in Tourism Management",
            "Bachelor of Science in Education",
            "Bachelor of Science in Civil Engineering",
            "Bachelor of Science in Criminology",
            "Bachelor of Arts in Communication",
            "Bachelor of Arts in Political Science",
        ],
    },
    {
        "name": "STI College - Alabang",
        "institution_type": "Private",
        "address": "Alabang-Zapote Road, Alabang, Muntinlupa City",
        "website_url": "https://www.sti.edu",
        "programs": [
            "Bachelor of Science in Information Technology",
            "Bachelor of Science in Computer Science",
            "Bachelor of Science in Information Systems",
            "Bachelor of Science in Computer Engineering",
            "Bachelor of Science in Business Administration",
            "Bachelor of Science in Hospitality Management",
            "Bachelor of Science in Tourism Management",
            "Associate in Computer Technology",
            "Associate in Information Technology",
        ],
    },
    {
        "name": "AMA Computer College - Muntinlupa",
        "institution_type": "Private",
        "address": "National Road, Putatan, Muntinlupa City",
        "website_url": "https://www.ama.edu.ph",
        "programs": [
            "Bachelor of Science in Information Technology",
            "Bachelor of Science in Computer Science",
            "Bachelor of Science in Information Systems",
            "Bachelor of Science in Computer Engineering",
            "Bachelor of Science in Business Administration",
            "Associate in Computer Technology",
            "Associate in Information Technology",
        ],
    },
    {
        "name": "Lyceum of Alabang",
        "institution_type": "Private",
        "address": "Alabang-Zapote Road, Alabang, Muntinlupa City",
        "website_url": "https://lyceumalabang.edu.ph",
        "programs": [
            "Bachelor of Science in Nursing",
            "Bachelor of Science in Pharmacy",
            "Bachelor of Science in Medical Technology",
            "Bachelor of Science in Radiologic Technology",
            "Bachelor of Science in Physical Therapy",
            "Bachelor of Science in Psychology",
            "Bachelor of Science in Business Administration",
            "Bachelor of Science in Hospitality Management",
            "Bachelor of Science in Tourism Management",
            "Bachelor of Science in Criminology",
        ],
    },
    {
        "name": "South Mansfield College",
        "institution_type": "Private",
        "address": "Alabang-Zapote Road, Alabang, Muntinlupa City",
        "website_url": "https://southmansfield.edu.ph",
        "programs": [
            "Bachelor of Science in Information Technology",
            "Bachelor of Science in Business Administration",
            "Bachelor of Science in Accountancy",
            "Bachelor of Science in Psychology",
            "Bachelor of Science in Education",
            "Bachelor of Science in Hospitality Management",
            "Bachelor of Science in Tourism Management",
        ],
    },
    {
        "name": "Colegio de Muntinlupa",
        "institution_type": "Public",
        "address": "Brgy. Poblacion, Muntinlupa City",
        "website_url": "https://cdm.edu.ph",
        "programs": [
            "Bachelor of Science in Information Technology",
            "Bachelor of Science in Business Administration",
            "Bachelor of Science in Education",
            "Bachelor of Science in Criminology",
            "Bachelor of Science in Hospitality Management",
            "Associate in Computer Technology",
            "Associate in Business Administration",
        ],
    },
    {
        "name": "Pamantasan ng Lungsod ng Muntinlupa - College of Medicine",
        "institution_type": "Public",
        "address": "Brgy. Poblacion, Muntinlupa City",
        "website_url": "https://plmun.edu.ph",
        "programs": [
            "Bachelor of Science in Nursing",
            "Bachelor of Science in Medical Technology",
            "Bachelor of Science in Radiologic Technology",
            "Bachelor of Science in Physical Therapy",
        ],
    },
    {
        "name": "Muntinlupa Business High School - Senior High",
        "institution_type": "Public",
        "address": "Brgy. Poblacion, Muntinlupa City",
        "website_url": None,
        "programs": [
            "Associate in Business Administration",
            "Associate in Computer Technology",
        ],
    },
]


def seed_schools(db: Session) -> None:
    """Insert schools and their programs."""
    existing_names = {s.name for s in db.query(School.name).all()}
    all_programs = {p.name: p.id for p in db.query(AcademicProgram).filter(AcademicProgram.is_active == True).all()}

    schools_added = 0
    programs_linked = 0

    for school_data in SCHOOLS_DATA:
        program_names = school_data.pop("programs")

        if school_data["name"] in existing_names:
            school = db.query(School).filter(School.name == school_data["name"]).first()
            print(f"School already exists: {school_data['name']}")
        else:
            school = School(**school_data, is_active=True)
            db.add(school)
            db.flush()
            schools_added += 1
            print(f"Added school: {school_data['name']}")

        # Link programs
        for prog_name in program_names:
            prog_id = all_programs.get(prog_name)
            if not prog_id:
                print(f"  Warning: Program not found: {prog_name}")
                continue

            # Check if link exists
            existing_link = db.query(SchoolProgram).filter(
                SchoolProgram.school_id == school.id,
                SchoolProgram.program_id == prog_id,
            ).first()

            if not existing_link:
                link = SchoolProgram(
                    school_id=school.id,
                    program_id=prog_id,
                    source_url=school_data.get("website_url"),
                    last_verified_at=None,
                )
                db.add(link)
                programs_linked += 1

    if schools_added or programs_linked:
        db.commit()
        print(f"Added {schools_added} schools, linked {programs_linked} school-program pairs")
    else:
        print("All schools and programs already exist")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_schools(db)
    finally:
        db.close()