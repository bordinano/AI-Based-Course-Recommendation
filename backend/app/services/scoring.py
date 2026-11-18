from sqlalchemy.orm import Session
from collections import defaultdict

from app.models.assessment_attempt import AssessmentAttempt
from app.models.student_response import StudentResponse
from app.models.assessment_question import AssessmentQuestion
from app.models.answer_option import AnswerOption
from app.models.skill_category import SkillCategory


def calculate_aptitude_scores(db: Session, attempt_id: int) -> dict[int, float]:
    """
    Calculate normalized aptitude scores (0-100) for each skill category.

    Scoring: Likert 1-5 per question, 10 questions per category
    Raw score range: 10-50 per category
    Normalized: ((raw - 10) / 40) * 100 = 0-100
    """
    # Get all responses for this attempt with answer option scores
    responses = (
        db.query(StudentResponse, AnswerOption.score, AssessmentQuestion.category_id)
        .join(AnswerOption, StudentResponse.answer_option_id == AnswerOption.id)
        .join(AssessmentQuestion, StudentResponse.question_id == AssessmentQuestion.id)
        .filter(StudentResponse.attempt_id == attempt_id)
        .all()
    )

    # Sum scores by category
    category_scores: dict[int, int] = defaultdict(int)
    category_question_counts: dict[int, int] = defaultdict(int)

    for response, score, category_id in responses:
        category_scores[category_id] += score
        category_question_counts[category_id] += 1

    # Normalize to 0-100
    normalized_scores = {}
    for category_id, raw_score in category_scores.items():
        num_questions = category_question_counts[category_id]
        if num_questions > 0:
            # Raw range: num_questions * 1 to num_questions * 5
            min_raw = num_questions * 1
            max_raw = num_questions * 5
            if max_raw > min_raw:
                normalized = ((raw_score - min_raw) / (max_raw - min_raw)) * 100
            else:
                normalized = 50.0  # Default if only 1 question
            normalized_scores[category_id] = round(normalized, 2)
        else:
            normalized_scores[category_id] = 0.0

    # Ensure all categories have a score (0 if no responses)
    all_categories = db.query(SkillCategory.id).all()
    for (cat_id,) in all_categories:
        if cat_id not in normalized_scores:
            normalized_scores[cat_id] = 0.0

    return normalized_scores


def get_active_matrix_version(db: Session):
    """Get the currently active scoring matrix version."""
    from app.models.scoring_matrix import ScoringMatrixVersion
    return db.query(ScoringMatrixVersion).filter(ScoringMatrixVersion.is_active == True).first()


def calculate_interest_scores(
    db: Session,
    student_id: int,
    matrix_version_id: int,
) -> dict[int, float]:
    """
    Calculate interest compatibility scores for each academic program.
    Returns dict of program_id -> normalized score (0-100).
    """
    from app.models.student_interest import StudentInterest
    from app.models.scoring_matrix import InterestWeight
    from app.models.academic_program import AcademicProgram

    # Get student's interests
    student_interests = db.query(StudentInterest).filter(
        StudentInterest.student_id == student_id
    ).all()

    interest_ids = [si.interest_id for si in student_interests if si.interest_id is not None]
    other_interests = [si.other_interest for si in student_interests if si.other_interest]

    # Get interest weights for this matrix version
    weights = db.query(InterestWeight).filter(
        InterestWeight.matrix_version_id == matrix_version_id
    ).all()

    # Calculate raw scores per program
    program_scores: dict[int, float] = defaultdict(float)
    for weight in weights:
        if weight.interest_id in interest_ids:
            program_scores[weight.academic_program_id] += weight.weight

    # Custom "Other" interests: distribute equally or use keyword matching
    # For now, give a small bonus to all programs for each custom interest
    if other_interests:
        for program_id in program_scores:
            program_scores[program_id] += len(other_interests) * 0.01

    # Normalize to 0-100 (min-max across programs)
    if program_scores:
        min_score = min(program_scores.values())
        max_score = max(program_scores.values())
        if max_score > min_score:
            for pid in program_scores:
                program_scores[pid] = round(
                    ((program_scores[pid] - min_score) / (max_score - min_score)) * 100, 2
                )
        else:
            for pid in program_scores:
                program_scores[pid] = 50.0

    # Ensure all active programs have a score
    all_programs = db.query(AcademicProgram.id).filter(AcademicProgram.is_active == True).all()
    for (pid,) in all_programs:
        if pid not in program_scores:
            program_scores[pid] = 0.0

    return program_scores


def calculate_career_scores(
    db: Session,
    student_id: int,
    matrix_version_id: int,
) -> dict[int, float]:
    """
    Calculate career compatibility scores for each academic program.
    Returns dict of program_id -> normalized score (0-100).
    """
    from app.models.student import Student
    from app.models.scoring_matrix import CareerWeight
    from app.models.academic_program import AcademicProgram

    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return {}

    preferred_career = student.preferred_career

    # Get career weights for this matrix version
    weights = db.query(CareerWeight).filter(
        CareerWeight.matrix_version_id == matrix_version_id
    ).all()

    program_scores: dict[int, float] = defaultdict(float)

    if preferred_career:
        # Match exact career name
        for weight in weights:
            if weight.career_name.lower() == preferred_career.lower():
                program_scores[weight.academic_program_id] += weight.weight
    else:
        # "None/Not sure" - neutral weight for all
        # Use "None" career weights if available, otherwise equal distribution
        none_weights = [w for w in weights if w.career_name.lower() == "none"]
        if none_weights:
            for weight in none_weights:
                program_scores[weight.academic_program_id] += weight.weight
        else:
            # Equal distribution
            programs = db.query(AcademicProgram.id).filter(AcademicProgram.is_active == True).all()
            equal_weight = 1.0 / len(programs) if programs else 0
            for (pid,) in programs:
                program_scores[pid] = equal_weight

    # Normalize to 0-100
    if program_scores:
        min_score = min(program_scores.values())
        max_score = max(program_scores.values())
        if max_score > min_score:
            for pid in program_scores:
                program_scores[pid] = round(
                    ((program_scores[pid] - min_score) / (max_score - min_score)) * 100, 2
                )
        else:
            for pid in program_scores:
                program_scores[pid] = 50.0

    # Ensure all active programs have a score
    all_programs = db.query(AcademicProgram.id).filter(AcademicProgram.is_active == True).all()
    for (pid,) in all_programs:
        if pid not in program_scores:
            program_scores[pid] = 0.0

    return program_scores