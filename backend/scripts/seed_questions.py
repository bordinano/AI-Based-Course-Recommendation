#!/usr/bin/env python
"""Seed script for assessment questions (10 per skill category = 60 total)."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import SkillCategory, AssessmentQuestion


# 60 questions: 10 per category
# Based on standard aptitude assessment domains
QUESTIONS_BY_CATEGORY = {
    "Analytical and Logical Skills": [
        "I enjoy solving complex problems that require careful analysis.",
        "I can easily identify patterns and relationships in data.",
        "I prefer tasks that require logical reasoning over routine work.",
        "I am good at breaking down difficult problems into manageable steps.",
        "I enjoy puzzles, brain teasers, and strategy games.",
        "I can evaluate arguments critically and spot logical fallacies.",
        "I like to understand the underlying principles behind how things work.",
        "I am comfortable making decisions based on data and evidence.",
        "I can think systematically and methodically when faced with challenges.",
        "I enjoy analyzing cause-and-effect relationships.",
    ],
    "Verbal and Linguistic Skills": [
        "I express my ideas clearly and effectively in writing.",
        "I enjoy reading and can comprehend complex texts easily.",
        "I have a rich vocabulary and use words precisely.",
        "I am good at explaining concepts to others in simple terms.",
        "I enjoy learning new languages or studying linguistics.",
        "I can write persuasively and structure arguments well.",
        "I pay attention to grammar, syntax, and word choice.",
        "I enjoy debates, discussions, and verbal exchanges.",
        "I can summarize lengthy information concisely.",
        "I am comfortable speaking in front of groups.",
    ],
    "Quantitative and Numerical Skills": [
        "I am comfortable working with numbers and mathematical concepts.",
        "I can interpret statistics, graphs, and numerical data accurately.",
        "I enjoy solving mathematical problems and equations.",
        "I have a good intuition for probabilities and risk assessment.",
        "I can perform mental calculations quickly and accurately.",
        "I understand mathematical formulas and can apply them to real situations.",
        "I enjoy working with spreadsheets, budgets, and financial data.",
        "I can identify trends and patterns in numerical data.",
        "I am comfortable with algebra, geometry, or calculus concepts.",
        "I like tasks that involve measurement, estimation, and quantification.",
    ],
    "Spatial and Mechanical Skills": [
        "I can visualize objects in three dimensions easily.",
        "I understand how mechanical systems and mechanisms work.",
        "I am good at reading maps, blueprints, and technical diagrams.",
        "I enjoy building, assembling, or fixing physical objects.",
        "I have a good sense of direction and spatial orientation.",
        "I can mentally rotate and manipulate objects in space.",
        "I understand basic principles of physics and mechanics.",
        "I enjoy hands-on work with tools, equipment, or materials.",
        "I am good at estimating distances, sizes, and proportions.",
        "I like designing or creating visual layouts and structures.",
    ],
    "Interpersonal and Emotional Skills": [
        "I can easily understand and empathize with others' feelings.",
        "I work well in teams and collaborate effectively.",
        "I am good at resolving conflicts and mediating disagreements.",
        "I can adapt my communication style to different people.",
        "I enjoy helping others and providing emotional support.",
        "I am aware of social cues and nonverbal communication.",
        "I can build and maintain positive relationships easily.",
        "I handle criticism and feedback constructively.",
        "I am comfortable leading or facilitating group discussions.",
        "I value diversity and can work well with people from different backgrounds.",
    ],
    "Organizational and Detail-Oriented Skills": [
        "I naturally create systems to organize information and tasks.",
        "I pay close attention to details and rarely make careless errors.",
        "I am good at planning projects and managing timelines.",
        "I can prioritize tasks effectively when faced with multiple deadlines.",
        "I maintain accurate records and documentation.",
        "I follow procedures and protocols carefully.",
        "I am good at spotting inconsistencies and errors in data.",
        "I enjoy creating schedules, checklists, and workflows.",
        "I can manage complex information without becoming overwhelmed.",
        "I take pride in producing thorough, high-quality work.",
    ],
}


def seed_questions(db: Session) -> None:
    """Insert assessment questions for each skill category."""
    categories = db.query(SkillCategory).order_by(SkillCategory.id).all()
    category_map = {c.name: c for c in categories}

    total_added = 0

    for category_name, questions in QUESTIONS_BY_CATEGORY.items():
        category = category_map.get(category_name)
        if not category:
            print(f"Warning: Category '{category_name}' not found in database")
            continue

        # Check existing questions for this category
        existing_texts = {
            q.question_text
            for q in db.query(AssessmentQuestion.question_text)
            .filter(AssessmentQuestion.category_id == category.id)
            .all()
        }

        for i, question_text in enumerate(questions, 1):
            if question_text not in existing_texts:
                question = AssessmentQuestion(
                    category_id=category.id,
                    question_text=question_text,
                    is_active=True,
                )
                db.add(question)
                total_added += 1
            else:
                print(f"  Skipping existing: {question_text[:50]}...")

    if total_added:
        db.commit()
        print(f"Seeded {total_added} new assessment questions")
    else:
        print("All assessment questions already exist")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_questions(db)
    finally:
        db.close()