from sqlalchemy import inspect
from app.database import engine

inspector = inspect(engine)

print("DATABASE TABLES:")
for table in inspector.get_table_names():
    print(f"- {table}")

print("\nSTUDENT_INTERESTS FOREIGN KEYS:")
for fk in inspector.get_foreign_keys("student_interests"):
    print(f"- {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")

print("\nSTUDENT_INTERESTS CHECK CONSTRAINTS:")
for constraint in inspector.get_check_constraints("student_interests"):
    print(f"- {constraint['name']}: {constraint['sqltext']}")

engine.dispose()
