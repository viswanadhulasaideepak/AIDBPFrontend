from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///./employees.db")

with engine.begin() as conn:
    employees = conn.execute(
        text("SELECT id FROM employees")
    ).fetchall()

    for emp in employees:
        conn.execute(
            text("""
                UPDATE employees
                SET employee_code = :code
                WHERE id = :id
            """),
            {
                "code": f"EMP{emp.id:03d}",
                "id": emp.id
            }
        )

print("Employee codes updated successfully.")