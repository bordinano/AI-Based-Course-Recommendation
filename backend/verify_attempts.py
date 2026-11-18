from sqlalchemy import inspect

from app.database import engine

inspector = inspect(engine)

print("ASSESSMENT ATTEMPT COLUMNS:")
for column in inspector.get_columns("assessment_attempts"):
    print(
        f"- {column['name']}: "
        f"{column['type']}, "
        f"nullable={column['nullable']}"
    )

print("\nFOREIGN KEYS:")
for fk in inspector.get_foreign_keys("assessment_attempts"):
    print(
        f"- {fk['constrained_columns']} -> "
        f"{fk['referred_table']}.{fk['referred_columns']}"
    )

print("\nCHECK CONSTRAINTS:")
for constraint in inspector.get_check_constraints("assessment_attempts"):
    print(f"- {constraint['name']}: {constraint['sqltext']}")

engine.dispose()