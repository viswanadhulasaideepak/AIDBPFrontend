from database import SessionLocal
from models import User

db = SessionLocal()

user = db.query(User).filter(
    User.email == "admin456@gmail.com"
).first()

if user:
    user.company_id = 3
    db.commit()
    print("Updated successfully")
else:
    print("User not found")

db.close()