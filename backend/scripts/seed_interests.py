#!/usr/bin/env python
"""Seed script for interest categories."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app.models import Interest


def seed_interests(db: Session) -> None:
    """Insert default interest categories if not already present."""
    interests_data = [
        {"name": "Science & Technology", "description": "Interest in scientific discovery, research, and technological innovation"},
        {"name": "Engineering & Mathematics", "description": "Interest in problem-solving, design, and mathematical reasoning"},
        {"name": "Healthcare & Medicine", "description": "Interest in patient care, medical science, and health services"},
        {"name": "Business & Entrepreneurship", "description": "Interest in management, finance, marketing, and starting ventures"},
        {"name": "Education & Teaching", "description": "Interest in instruction, mentoring, and educational development"},
        {"name": "Arts & Design", "description": "Interest in creative expression, visual arts, and design thinking"},
        {"name": "Social Sciences & Humanities", "description": "Interest in human behavior, society, culture, and history"},
        {"name": "Communication & Media", "description": "Interest in journalism, public relations, and digital media"},
        {"name": "Information Technology", "description": "Interest in software development, cybersecurity, and data systems"},
        {"name": "Environmental & Sustainability", "description": "Interest in conservation, climate action, and sustainable practices"},
        {"name": "Law & Public Service", "description": "Interest in legal systems, governance, and community advocacy"},
        {"name": "Hospitality & Tourism", "description": "Interest in service industry, travel, and event management"},
        {"name": "Sports & Fitness", "description": "Interest in athletics, physical training, and sports science"},
        {"name": "Agriculture & Food Science", "description": "Interest in farming, food technology, and agribusiness"},
        {"name": "Architecture & Construction", "description": "Interest in building design, urban planning, and construction management"},
    ]

    existing_names = {i.name for i in db.query(Interest.name).all()}
    new_count = 0

    for data in interests_data:
        if data["name"] not in existing_names:
            interest = Interest(**data)
            db.add(interest)
            new_count += 1

    if new_count:
        db.commit()
        print(f"Seeded {new_count} new interests")
    else:
        print("All interests already exist")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_interests(db)
    finally:
        db.close()