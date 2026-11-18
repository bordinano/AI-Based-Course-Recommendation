from sqlalchemy import inspect
from app.database import engine

inspector = inspect(engine)

print("DATABASE TABLES:")
for table in inspector.get_table_names():
    print("-", table)

print("\nASSESSMENT QUESTION COLUMNS:")
for column in inspector.get_columns("assessment_questions"):
    print(f"- {column['name']}: {column['type']}, nullable={column['nullable']}")

print("\nFOREIGN KEYS:")
for fk in inspector.get_foreign_keys("assessment_questions"):
    print(
        f"- {fk['constrained_columns']} -> "
        f"{fk['referred_table']}.{fk['referred_columns']}"
    )

engine.dispose()
