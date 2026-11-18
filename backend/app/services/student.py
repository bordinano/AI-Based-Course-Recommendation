from sqlalchemy.orm import Session

from app.models.student import Student
from app.models.student_interest import StudentInterest
from app.schemas.student import StudentCreate


def create_student(db: Session, student_data: StudentCreate) -> Student:
    # Validate interests
    student_data.validate_interests()

    new_student = Student(
        full_name=student_data.full_name.strip(),
        email=student_data.email,
        preferred_career=student_data.preferred_career,
    )

    db.add(new_student)
    db.flush()  # Get student ID without committing

    # Create StudentInterest records
    for interest_input in student_data.interests:
        student_interest = StudentInterest(
            student_id=new_student.id,
            interest_id=interest_input.interest_id,
            other_interest=interest_input.other_interest.strip() if interest_input.other_interest else None,
        )
        db.add(student_interest)

    db.commit()
    db.refresh(new_student)

    return new_student