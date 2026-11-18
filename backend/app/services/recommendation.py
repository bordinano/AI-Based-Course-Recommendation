from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from app.models.assessment_attempt import AssessmentAttempt
from app.models.student import Student
from app.models.academic_program import AcademicProgram
from app.models.school import School
from app.models.school_program import SchoolProgram
from app.models.scoring_matrix import ScoringMatrixVersion, AptitudeWeight
from app.models.assessment_result import (
    AssessmentResult,
    RecommendedProgram,
    RecommendedSchool,
)
from app.services.scoring import (
    calculate_aptitude_scores,
    calculate_interest_scores,
    calculate_career_scores,
    get_active_matrix_version,
)


# Default component weights (to be validated by counselor)
DEFAULT_APTITUDE_WEIGHT = 0.50
DEFAULT_INTEREST_WEIGHT = 0.30
DEFAULT_CAREER_WEIGHT = 0.20


def get_aptitude_category_weights(db: Session, matrix_version_id: int) -> dict[int, float]:
    """Get aptitude weights per skill category for a matrix version."""
    weights = db.query(AptitudeWeight).filter(
        AptitudeWeight.matrix_version_id == matrix_version_id
    ).all()
    return {w.skill_category_id: w.weight for w in weights}


def calculate_weighted_aptitude_score(
    aptitude_scores: dict[int, float],
    category_weights: dict[int, float],
) -> float:
    """Calculate single weighted aptitude score from per-category scores."""
    total = 0.0
    total_weight = 0.0
    for cat_id, score in aptitude_scores.items():
        weight = category_weights.get(cat_id, 0.0)
        total += score * weight
        total_weight += weight
    return round(total / total_weight, 2) if total_weight > 0 else 0.0


def generate_recommendations(
    db: Session,
    attempt_id: int,
    school_type_filter: Optional[str] = None,  # "Public", "Private", or None
    top_n: int = 5,
) -> AssessmentResult:
    """
    Generate full recommendations for a completed assessment attempt.
    """
    attempt = db.query(AssessmentAttempt).filter(AssessmentAttempt.id == attempt_id).first()
    if not attempt:
        raise ValueError("Attempt not found")
    if attempt.status != "completed":
        raise ValueError("Attempt not completed")

    student = db.query(Student).filter(Student.id == attempt.student_id).first()
    if not student:
        raise ValueError("Student not found")

    # Get active matrix version
    matrix_version = get_active_matrix_version(db)
    if not matrix_version:
        raise ValueError("No active scoring matrix version")

    # Calculate three component scores
    aptitude_scores = calculate_aptitude_scores(db, attempt_id)
    interest_scores = calculate_interest_scores(db, student.id, matrix_version.id)
    career_scores = calculate_career_scores(db, student.id, matrix_version.id)

    # Get aptitude category weights
    aptitude_category_weights = get_aptitude_category_weights(db, matrix_version.id)
    weighted_aptitude = calculate_weighted_aptitude_score(
        aptitude_scores, aptitude_category_weights
    )

    # Calculate final scores for each program
    program_final_scores: dict[int, dict] = {}
    active_programs = db.query(AcademicProgram).filter(
        AcademicProgram.is_active == True
    ).all()

    for program in active_programs:
        pid = program.id
        apt = aptitude_scores.get(pid, 0.0)  # This is per-category, need to map
        # Actually, aptitude_scores is per skill_category, not per program
        # We use the weighted aptitude score (same for all programs)
        # The per-program aptitude would require a mapping from skill_category to program
        # For now, use the same weighted aptitude for all programs

        interest = interest_scores.get(pid, 0.0)
        career = career_scores.get(pid, 0.0)

        final = round(
            (weighted_aptitude * DEFAULT_APTITUDE_WEIGHT) +
            (interest * DEFAULT_INTEREST_WEIGHT) +
            (career * DEFAULT_CAREER_WEIGHT),
            2
        )

        program_final_scores[pid] = {
            "aptitude": weighted_aptitude,
            "interest": interest,
            "career": career,
            "final": final,
        }

    # Sort programs by final score descending
    sorted_programs = sorted(
        program_final_scores.items(),
        key=lambda x: x[1]["final"],
        reverse=True,
    )

    # Take top N
    top_programs = sorted_programs[:top_n]

    # Create AssessmentResult record
    result = AssessmentResult(
        attempt_id=attempt.id,
        matrix_version_id=matrix_version.id,
        aptitude_scores=aptitude_scores,
        interest_scores=interest_scores,
        career_scores=career_scores,
        final_scores={str(k): v["final"] for k, v in program_final_scores.items()},
    )
    db.add(result)
    db.flush()

    # Create RecommendedProgram records
    for rank, (pid, scores) in enumerate(top_programs, 1):
        program = db.query(AcademicProgram).filter(AcademicProgram.id == pid).first()
        if not program:
            continue

        # Generate explanation
        explanation = generate_explanation(
            program.name,
            scores["aptitude"],
            scores["interest"],
            scores["career"],
        )

        rec_program = RecommendedProgram(
            result_id=result.id,
            academic_program_id=pid,
            compatibility_score=scores["final"],
            rank=rank,
            aptitude_component=scores["aptitude"],
            interest_component=scores["interest"],
            career_component=scores["career"],
            explanation=explanation,
        )
        db.add(rec_program)

    # Create RecommendedSchool records
    # Get schools offering these programs
    top_program_ids = [pid for pid, _ in top_programs]
    school_programs = db.query(SchoolProgram).filter(
        SchoolProgram.program_id.in_(top_program_ids)
    ).all()

    # Filter by school type if requested
    school_ids = [sp.school_id for sp in school_programs]
    schools_query = db.query(School).filter(School.id.in_(school_ids), School.is_active == True)
    if school_type_filter:
        schools_query = schools_query.filter(School.institution_type == school_type_filter)
    schools = schools_query.all()
    school_map = {s.id: s for s in schools}

    for sp in school_programs:
        if sp.school_id not in school_map:
            continue
        school = school_map[sp.school_id]
        rec_school = RecommendedSchool(
            result_id=result.id,
            school_id=school.id,
            program_id=sp.program_id,
            is_public=(school.institution_type == "Public"),
        )
        db.add(rec_school)

    db.commit()
    db.refresh(result)
    return result


def generate_explanation(
    program_name: str,
    aptitude: float,
    interest: float,
    career: float,
) -> str:
    """Generate human-readable explanation for recommendation."""
    parts = []

    if aptitude >= 70:
        parts.append("strong aptitude alignment")
    elif aptitude >= 40:
        parts.append("moderate aptitude alignment")
    else:
        parts.append("developing aptitude alignment")

    if interest >= 70:
        parts.append("high interest match")
    elif interest >= 40:
        parts.append("moderate interest match")
    else:
        parts.append("low interest match")

    if career >= 70:
        parts.append("excellent career alignment")
    elif career >= 40:
        parts.append("good career alignment")
    else:
        parts.append("limited career alignment")

    return f"{program_name} recommended based on {', '.join(parts)}."


def get_recommendation_results(
    db: Session,
    attempt_id: int,
    school_type_filter: Optional[str] = None,
) -> dict:
    """
    Retrieve formatted recommendation results for API response.
    """
    result = db.query(AssessmentResult).filter(
        AssessmentResult.attempt_id == attempt_id
    ).first()

    if not result:
        return None

    # Get recommended programs with details
    rec_programs = db.query(RecommendedProgram).filter(
        RecommendedProgram.result_id == result.id
    ).order_by(RecommendedProgram.rank).all()

    programs_data = []
    for rp in rec_programs:
        program = db.query(AcademicProgram).filter(
            AcademicProgram.id == rp.academic_program_id
        ).first()
        if not program:
            continue

        programs_data.append({
            "academic_program_id": program.id,
            "program_name": program.name,
            "degree_level": program.degree_level,
            "description": program.description,
            "compatibility_score": rp.compatibility_score,
            "rank": rp.rank,
            "components": {
                "aptitude": rp.aptitude_component,
                "interest": rp.interest_component,
                "career": rp.career_component,
            },
            "explanation": rp.explanation,
        })

    # Get recommended schools
    rec_schools = db.query(RecommendedSchool).filter(
        RecommendedSchool.result_id == result.id
    ).all()

    schools_data = []
    for rs in rec_schools:
        school = db.query(School).filter(School.id == rs.school_id).first()
        program = db.query(AcademicProgram).filter(
            AcademicProgram.id == rs.program_id
        ).first()
        if not school or not program:
            continue

        # Apply school type filter
        if school_type_filter and school.institution_type != school_type_filter:
            continue

        schools_data.append({
            "school_id": school.id,
            "school_name": school.name,
            "institution_type": school.institution_type,
            "address": school.address,
            "website_url": school.website_url,
            "program_offered": program.name,
            "program_id": program.id,
        })

    return {
        "attempt_id": result.attempt_id,
        "matrix_version": result.matrix_version.version if result.matrix_version else "unknown",
        "recommended_programs": programs_data,
        "recommended_schools": schools_data,
    }