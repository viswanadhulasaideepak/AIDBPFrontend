from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///./employees.db")

with engine.connect() as conn:
    result = conn.execute(text("PRAGMA table_info(employees)"))

    for row in result:
        print(row)