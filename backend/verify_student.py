from sqlalchemy import select
from app.database import SessionLocal
from app.models.student import Student

with SessionLocal() as db:
    student = db.scalar(
        select(Student).where(Student.id == 1)
    )

    if student:
        print("STUDENT FOUND IN DATABASE")
        print(f"ID: {student.id}")
        print(f"Name: {student.full_name}")
        print(f"Email: {student.email}")
        print(f"Created: {student.created_at}")
    else:
        print("STUDENT NOT FOUND")