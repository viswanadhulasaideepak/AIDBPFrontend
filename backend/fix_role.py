from database import SessionLocal
import models

db = SessionLocal()
user = db.query(models.User).filter(models.User.email == "test123@gmail.com").first()
if user:
    user.role = "user"
    db.commit()
    print("Updated role successfully")
else:
    print("User not found")
db.close()
