import os
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from models import User

# ---------------- CONFIG ----------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

#  Load secret key from environment variable (fallback for dev)
SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ---------------- PASSWORD HASHING ----------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# ---------------- TOKEN CREATION ----------------
def create_token(email: str, role: str, company_id: int, status: str):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": email,              #  use email consistently
        "role": role,
        "company_id": company_id,
        "status": status,
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# ---------------- GET CURRENT USER ----------------
def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        role = payload.get("role")
        company_id = payload.get("company_id")
        status = payload.get("status")

        if not email or not role or company_id is None or status is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        return {
            "email": email,         
            "role": role,
            "company_id": company_id,
            "status": status
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Token expired or invalid")

# ---------------- USER VALIDATION ----------------

def verify_user_identity(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Wrong password")
    return user
