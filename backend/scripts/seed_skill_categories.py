from sqlalchemy import select

from app.database import SessionLocal
from app.models import SkillCategory


SKILL_CATEGORIES = [
    {
        "name": "Analytical and Logical Skills",
        "description": "Analyzing information, identifying patterns, and solving problems logically.",
    },
    {
        "name": "Verbal and Linguistic Skills",
        "description": "Understanding language and communicating ideas through speaking and writing.",
    },
    {
        "name": "Quantitative and Numerical Skills",
        "description": "Working with numbers, mathematical concepts, and quantitative information.",
    },
    {
        "name": "Spatial and Mechanical Skills",
        "description": "Understanding visual relationships, spatial arrangements, and mechanical concepts.",
    },
    {
        "name": "Interpersonal and Emotional Skills",
        "description": "Understanding others, managing emotions, and working effectively with people.",
    },
    {
        "name": "Organizational and Detail-Oriented Skills",
        "description": "Planning tasks, managing information, and paying attention to details.",
    },
]


def seed_skill_categories():
    with SessionLocal.begin() as db:
        existing_names = set(
            db.scalars(select(SkillCategory.name)).all()
        )

        new_categories = [
            SkillCategory(**category)
            for category in SKILL_CATEGORIES
            if category["name"] not in existing_names
        ]

        db.add_all(new_categories)

        print(f"Inserted: {len(new_categories)}")
        print(f"Already existing: {len(existing_names)}")


if __name__ == "__main__":
    seed_skill_categories()
