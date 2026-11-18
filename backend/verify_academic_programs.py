from sqlalchemy import inspect
from app.database import engine

inspector = inspect(engine)

print("ACADEMIC PROGRAMS TABLE EXISTS:")
print("academic_programs" in inspector.get_table_names())

print("\nCOLUMNS:")
for column in inspector.get_columns("academic_programs"):
    print(f"- {column['name']}: {column['type']}, nullable={column['nullable']}")

print("\nCHECK CONSTRAINTS:")
for constraint in inspector.get_check_constraints("academic_programs"):
    print(f"- {constraint['name']}: {constraint['sqltext']}")

print("\nUNIQUE CONSTRAINTS:")
for constraint in inspector.get_unique_constraints("academic_programs"):
    print(f"- {constraint['name']}: {constraint['column_names']}")

engine.dispose()