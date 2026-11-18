from sqlalchemy.orm import Session, joinedload

from app.models.skill_category import SkillCategory
from app.models.assessment_question import AssessmentQuestion
from app.models.answer_option import AnswerOption


def get_assessment_questions(db: Session) -> list[SkillCategory]:
    """
    Retrieve all active skill categories with their active questions.
    Answer options are fetched separately (global 5-point Likert scale).
    """
    # Get all active answer options (global Likert scale)
    answer_options = (
        db.query(AnswerOption)
        .order_by(AnswerOption.score)
        .all()
    )

    # Get skill categories with active questions
    categories = (
        db.query(SkillCategory)
        .options(
            joinedload(SkillCategory.questions)
        )
        .filter(SkillCategory.id.in_(
            db.query(AssessmentQuestion.category_id)
            .filter(AssessmentQuestion.is_active == True)
            .distinct()
        ))
        .order_by(SkillCategory.id)
        .all()
    )

    # Attach answer options to each question for serialization
    for category in categories:
        for question in category.questions:
            question.answer_options = answer_options

    return categories