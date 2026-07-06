import requests
import uuid
from fastapi import FastAPI, HTTPException, Depends, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime
from database import get_db
import schema, models, crud, database,auth
from models import Invitation, InvitationStatus
from auth import (
    verify_password,
    create_token,
    hash_password,
    get_client_info,
    get_current_user,
    require_active_user
)
from routers.analytics_routes import router as analytics_router
from routers.role_requests_routes import router as role_requests_router
from routers.suspension_routes import router as suspension_router
from routers import (
    employees_routes, departments_routes, attendance_routes, dashboard_routes,
    notifications_routes, auditlogs_routes, invitations_routes,  members_routes, 
    reactivation_routes, leave_routes, activity_routes, export_routes,holiday_routes,
    login_devices_routes)

app = FastAPI()
# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000",
                    "http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# ---------------- ROUTERS ----------------
app.include_router(employees_routes.router)
app.include_router(departments_routes.router)
app.include_router(attendance_routes.router)
app.include_router(dashboard_routes.router)
app.include_router(notifications_routes.router)
app.include_router(role_requests_router)
app.include_router(auditlogs_routes.router)
app.include_router(analytics_router)
app.include_router(invitations_routes.router)
app.include_router(members_routes.router)
app.include_router(reactivation_routes.router)
app.include_router(leave_routes.router)
app.include_router(activity_routes.router)
app.include_router(export_routes.router)
app.include_router(suspension_router)
app.include_router(holiday_routes.router)
app.include_router(login_devices_routes.router)
app.include_router(login_devices_routes.admin_router)

for route in app.routes:
    print(route.path)


# ---------------- FAKE API ----------------
FAKE_API_URL = "https://jsonplaceholder.typicode.com/users"

@app.get("/employees/fake")
def read_fake_employees():
    try:
        response = requests.get(FAKE_API_URL)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------- DB SETUP ----------------
models.Base.metadata.create_all(bind=database.engine)

'''def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()'''

# ---------------- SEED FUNCTION ----------------
from auth import hash_password
import random

def seed_data():
    db = database.SessionLocal()

    # Create companies if missing
    company_a = db.query(models.Company).filter_by(name="Company A").first()
    if not company_a:
        company_a = models.Company(name="Company A", domain="companya.com")
        db.add(company_a)
        db.commit()
        db.refresh(company_a)

    company_b = db.query(models.Company).filter_by(name="Company B").first()
    if not company_b:
        company_b = models.Company(name="Company B", domain="companyb.com")
        db.add(company_b)
        db.commit()
        db.refresh(company_b)

    companies = [company_a, company_b]

    if db.query(models.Employee).count() > 0:
        print("⚠️ Already seeded, skipping fake data.")
        db.close()
        return

    # Fetch fake users
    response = requests.get(FAKE_API_URL)
    users = response.json()

    # Insert employees + users
    for i, u in enumerate(users):
        company = companies[i % 2]  # alternate A/B

        dept_name = u["company"]["name"]
        dept = db.query(models.Department).filter_by(
            name=dept_name, company_id=company.id
        ).first()
        if not dept:
            dept = models.Department(name=dept_name, company_id=company.id)
            db.add(dept)
            db.commit()
            db.refresh(dept)

        emp = models.Employee(
            name=u["name"],
            email=u["email"],
            department_id=dept.id,
            role="Employee",
            status=random.choice([models.UserStatus.active, models.UserStatus.suspended, models.UserStatus.deactivated]),
            company_id=company.id
        )
        db.add(emp)
        db.flush()

        # Create matching User with default password "deepak"
        new_user = models.User(
            username=u["username"] if "username" in u else u["name"].replace(" ", "").lower(),
            email=u["email"],
            hashed_password=hash_password("deepak"),
            role="user",
            company_id=company.id,
            status=models.UserStatus.active
        )
        db.add(new_user)

        att = models.Attendance(
            employee_id=emp.id,
            date=datetime.utcnow(),
            status="Present",
            company_id=company.id
        )
        db.add(att)

        log = models.AuditLog(
            user_name="system",
            action="Seeded Fake Data",
            related_user=u["email"],
            company_id=company.id
        )
        db.add(log)

    db.commit()
    db.close()
    print(" Seed completed successfully!")


# ---------------- STARTUP ----------------
@app.on_event("startup")
def startup_event():
    seed_data()
    
#-------debugUsers------------
@app.get("/debug-users")
def debug_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()

    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": u.role,
            "status": str(u.status),
            "company_id": u.company_id
        }
        for u in users
    ]

# ---------------- COMPANIES ----------------
@app.get("/companies")
def get_companies(db: Session = Depends(get_db)):
    return db.query(models.Company).all()

# ---------------- LOGIN ----------------

class TokenResponse(BaseModel):
    token: str
    id: int
    email: str
    role: str
    company_id: int
    status: str

@app.post("/login", response_model=TokenResponse)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        or_(
        models.User.email == form_data.username,
        models.User.username == form_data.username
    )
        ).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Get client details
    ip_address, browser = get_client_info(request)

    # Generate unique session id
    session_identifier = str(uuid.uuid4())

    # Record normal login activity (existing functionality)
    crud.record_user_login(
        db=db,
        user=user,
        ip_address=ip_address,
        browser=browser
        )

    # Create login session (new functionality)
    crud.create_login_session(
        db=db,
        user=user,
        session_identifier=session_identifier,
        device_name=browser,     
        browser=browser,
        ip_address=ip_address
        )

# Create JWT containing session id
    token = create_token(
        user.id,
        user.email,
        user.role,
        user.company_id,
        user.status.value,
        session_identifier=session_identifier
        )

    return {
    "token": token,
    "id": user.id,
    "email": user.email,
    "role": user.role,
    "company_id": user.company_id,
    "status": user.status.value,

    "suspended_at": getattr(user, "suspended_at", None),
    "suspended_by": getattr(user, "suspended_by", None),
    "suspended_reason": getattr(user, "suspended_reason", None)
    }
    
 #----------------Logout--------------------
 
@app.post("/logout")
def logout(
    request: Request,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    user = db.query(models.User).filter(
        models.User.id == current_user["id"]
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    ip_address, browser = get_client_info(request)

    crud.record_user_logout(
    db=db,
    user=user,
    ip_address=ip_address,
    browser=browser,
    session_identifier=current_user["session_identifier"]
    )

    crud.logout_session(
    db=db,
    session_identifier=current_user["session_identifier"],
    user_id=current_user["id"]
    )

    return {
        "message": "Logged out successfully."
    }    
    
class InvitationSignupRequest(BaseModel):
    token: str
    username: str
    password: str
    
# ---------------- SIGNUP ----------------
@app.post("/signup")
def signup(user: schema.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(
    or_(
        models.User.email == user.email,
        models.User.username == user.username
        )
    ).first()
    if existing:
        raise HTTPException(
        status_code=400,
        detail="Email or Username already registered"
        )

    company = db.query(models.Company).filter_by(name=user.company_name).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    print("Signup Password:", user.password)
    print("Length:", len(user.password))
    
    print("Signup Password:", user.password)
    print("Length:", len(user.password))
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
        role=user.role,
        company_id=company.id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    db.add(models.AuditLog(
        user_name=new_user.email,
        action="User Signup",
        related_user=new_user.email,
        company_id=company.id
    ))
    db.commit()

    crud.create_notification(
        db=db,
        message=f"New user signed up: {new_user.email}",
        recipient_email=new_user.email,
        company_id=company.id
    )

    return {"message": "User created successfully"}

@app.post("/signup/invitation")
def signup_with_invitation(
    request: InvitationSignupRequest,
    db: Session = Depends(get_db)
):
    invitation = db.query(models.Invitation).filter(
        models.Invitation.token == request.token,
        models.Invitation.status == models.InvitationStatus.pending
    ).first()

    if not invitation:
        raise HTTPException(
            status_code=404,
            detail="Invalid or expired invitation."
        )

    existing_user = db.query(models.User).filter(
        models.User.email == invitation.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User already exists."
        )

    new_user = models.User(
        username=request.username,
        email=invitation.email,
        hashed_password=hash_password(request.password),
        role="user",
        company_id=invitation.company_id,
        status=models.UserStatus.active
    )

    db.add(new_user)

    invitation.status = models.InvitationStatus.accepted

    db.commit()
    db.refresh(new_user)

    crud.create_audit_log(
        db=db,
        user_name=new_user.email,
        action="Accepted Invitation",
        related_user=new_user.email,
        company_id=new_user.company_id
    )

    crud.create_notification(
        db=db,
        message="Invitation accepted successfully.",
        recipient_email=new_user.email,
        company_id=new_user.company_id
    )

    return {
        "message": "Account created successfully. Please login."
    }

@app.get("/invitation/{token}")
def validate_invitation(
    token: str,
    db: Session = Depends(get_db)
):
    invitation = db.query(models.Invitation).filter(
        models.Invitation.token == token,
        models.Invitation.status == models.InvitationStatus.pending
    ).first()

    if not invitation:
        raise HTTPException(
            status_code=404,
            detail="Invitation is invalid or expired."
        )

    return {
        "email": invitation.email,
        "company_id": invitation.company_id,
        "company_name": invitation.company.name
    }
    
# ---------------- FORGOT PASSWORD ----------------
class ForgotPasswordRequest(BaseModel):
    email: str
    new_password: str

@app.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(email=request.email).first()
    
    print("Forgot password endpoint hit")
    print(request)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = hash_password(request.new_password)
    db.commit()

    db.add(models.AuditLog(
        user_name=user.email,
        action="Password Reset",
        related_user=user.email,
        company_id=user.company_id
    ))
    db.commit()

    crud.create_notification(
        db=db,
        message=f"Password reset for {user.email}",
        recipient_email=user.email,
        company_id=user.company_id
    )

    return {"message": "Password reset successful"}