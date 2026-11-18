from sqlalchemy import inspect

from app.database import engine

inspector = inspect(engine)

print("STUDENT RESPONSE COLUMNS:")
for column in inspector.get_columns("student_responses"):
    print(
        f"- {column['name']}: "
        f"{column['type']}, nullable={column['nullable']}"
    )

print("\nFOREIGN KEYS:")
for fk in inspector.get_foreign_keys("student_responses"):
    print(
        f"- {fk['constrained_columns']} -> "
        f"{fk['referred_table']}.{fk['referred_columns']}, "
        f"ondelete={fk['options'].get('ondelete')}"
    )

print("\nUNIQUE CONSTRAINTS:")
for constraint in inspector.get_unique_constraints("student_responses"):
    print(f"- {constraint['name']}: {constraint['column_names']}")

engine.dispose()