import requests
from fastapi import FastAPI, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime
import schema, models, crud, database
from auth import verify_password, create_token, hash_password
from routers.analytics_routes import router as analytics_router
from routers.role_requests_routes import router as role_requests_router
from routers import (
    employees_routes, departments_routes, attendance_routes, dashboard_routes,
    notifications_routes, auditlogs_routes, invitations_routes,  members_routes, 
    reactivation_routes
)


app = FastAPI()

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

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
                    #"http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- SEED FUNCTION ----------------
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

    # Insert employees, departments, attendance, audit logs
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
            status=random.choice(["active", "onleave", "inactive"]),
            company_id=company.id
        )
        db.add(emp)
        db.flush()

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

    # 
    db.commit()
    db.close()
    print(" Seed completed successfully!")

# ---------------- STARTUP ----------------
@app.on_event("startup")
def startup_event():
    seed_data()

# ---------------- USERS ----------------
@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return [{"id": u.id, "email": u.email, "role": u.role} for u in users]

# ---------------- COMPANIES ----------------
@app.get("/companies")
def get_companies(db: Session = Depends(get_db)):
    return db.query(models.Company).all()

# ---------------- LOGIN ----------------
class TokenResponse(BaseModel):
    token: str
    role: str
    company_id: int

@app.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    role: str = Form(...)
):
    user = db.query(models.User).filter(
        models.User.email == form_data.username
    ).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token(user.email, user.role, user.company_id, user.status.value)

    audit = models.AuditLog(
        user_name=user.email,
        action="User Login",
        related_user=user.email,
        company_id=user.company_id
    )
    db.add(audit)
    db.commit()

    return {
        "token": token,
        "role": user.role,
        "company_id": user.company_id
    }

# ---------------- SIGNUP ----------------
@app.post("/signup")
def signup(user: schema.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter_by(email=user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    company = db.query(models.Company).filter_by(name=user.company_name).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

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

# ---------------- FORGOT PASSWORD ----------------
class ForgotPasswordRequest(BaseModel):
    email: str
    new_password: str

@app.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(email=request.email).first()
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
