from database import SessionLocal
from models import Company

db = SessionLocal()

companies = db.query(Company).all()

print("Companies:")
for c in companies:
    print(c.id, c.name)

db.close()