from database import SessionLocal
import models

db = SessionLocal()

rows = db.query(models.Attendance).all()

for r in rows:
    print("ID:", r.id)
    print("EMP:", r.employee_id)
    print("STATUS:", r.status)
    print("COMPANY:", r.company_id)
    print("------")

db.close()