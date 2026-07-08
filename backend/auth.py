import os
import uuid
from jose import jwt, JWTError
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import get_db
from models import User, UserStatus,LoginSession,SessionStatus

# ---------------- CONFIG ----------------

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ---------------- PASSWORD HASHING ----------------


pwd_context = CryptContext(schemes=["argon2", "bcrypt"], default="argon2", deprecated="auto")

def hash_password(password: str) -> str:
    # passlib accepts str; it will encode internally
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# ---------------- TOKEN CREATION ----------------

def create_token(
    user_id: int,
    email: str,
    role: str,
    company_id: int,
    status: str,
    session_identifier: str | None = None
):
    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "id": user_id,
        "sub": email,
        "role": role,
        "company_id": company_id,
        "status": status,
        "session_identifier": (
        session_identifier or str(uuid.uuid4())
        ),
        "exp": expire
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

# ---------------- GET CURRENT USER ----------------

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Missing token"
        )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Token expired or invalid"
        )    

    email = payload.get("sub")
    session_identifier = payload.get("session_identifier")
        
    session = (db.query(LoginSession).filter(
        LoginSession.session_identifier == session_identifier
    ).first()
               )

    if not session:
        raise HTTPException(
            status_code=401,
            detail="Session not found"
            )

    if session.status != SessionStatus.active:
        raise HTTPException(
            status_code=401,
            detail="Session has expired or has been revoked. Please login again."
            )

    if not email:
        raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

    user = db.query(User).filter(
        User.email == email
        ).first()
    
    session.last_activity = datetime.utcnow()
    
    db.commit()

    if not user:
        raise HTTPException(
                status_code=401,
                detail="User not found"
            )

    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "company_id": user.company_id,
        "status": user.status.value,
        "session_identifier": session_identifier, 
        
        "user": user
        }
#------------Get Current Admin--------------------    

def get_current_admin(
    current_user=Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required."
        )

    return current_user
    
# ---------------- ACTIVE USER CHECK ----------------

def require_active_user(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.id == current_user["id"],
        User.company_id == current_user["company_id"]
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Suspended
    if user.status == UserStatus.suspended:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "ACCOUNT_SUSPENDED",
                "status": user.status.value,
                "suspended_reason": user.suspended_reason,
                "suspended_by": user.suspended_by,
                "suspended_at": (
                    user.suspended_at.isoformat()
                    if user.suspended_at
                    else None
                )
            }
        )

    # Deactivated
    if user.status == UserStatus.deactivated:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "ACCOUNT_DEACTIVATED",
                "status": user.status.value,
                "deactivated_by": user.deactivated_by,
                "deactivation_reason": user.deactivated_reason
            }
        )

    return current_user

#------------Suspended User------------

def require_suspended_user(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.id == current_user["id"],
        User.company_id == current_user["company_id"]
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.status not in [
        UserStatus.suspended,
        UserStatus.deactivated
    ]:
        raise HTTPException(
            status_code=403,
            detail="Only suspended/deactivated users can perform this action."
        )

    return current_user

#--------------User Status Details--------------

def get_user_status_details(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.id == current_user["id"],
        User.company_id == current_user["company_id"]
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "status": user.status.value,
        "suspended_at": user.suspended_at,
        "suspended_by": user.suspended_by,
        "suspended_reason": user.suspended_reason,
        "deactivated_by": user.deactivated_by,
        "deactivated_reason": user.deactivated_reason
    }

# ---------------- ADMIN CHECK ----------------

def require_admin(
    current_user=Depends(require_active_user)
):
    if current_user["role"].lower() != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return current_user

# ---------------- USER VALIDATION ----------------

def verify_user_identity(
    db: Session,
    email: str,
    password: str
) -> User:

    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    if not verify_password(
        password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Wrong password"
        )

    return user

# ---------------- CLIENT INFO ----------------

def get_client_info(request: Request):

    forwarded = request.headers.get(
        "X-Forwarded-For"
    )

    if forwarded:
        ip_address = forwarded.split(",")[0].strip()
    else:
        ip_address = request.client.host

    browser = request.headers.get(
        "User-Agent",
        "Unknown Browser"
    )

    return ip_address, browser