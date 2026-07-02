from database import SessionLocal
import models

db = SessionLocal()

print("EMPLOYEES")
for e in db.query(models.Employee).filter(models.Employee.company_id == 1).all():
    print(e.id, e.email)

print("\nUSERS")
for u in db.query(models.User).filter(models.User.company_id == 1).all():
    print(u.id, u.email, u.role)