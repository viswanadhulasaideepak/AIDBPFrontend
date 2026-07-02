from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///./employees.db")

queries = [
    "ALTER TABLE employees ADD COLUMN employee_code TEXT;",
    "ALTER TABLE employees ADD COLUMN profile_completion INTEGER DEFAULT 0;",
    "ALTER TABLE employees ADD COLUMN last_profile_update DATETIME;"
]

with engine.begin() as conn:
    for query in queries:
        try:
            conn.execute(text(query))
            print("SUCCESS:", query)
        except Exception as e:
            print("SKIPPED:", e)

print("Migration completed.")