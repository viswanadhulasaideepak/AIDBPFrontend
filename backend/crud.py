from sqlalchemy.orm import Session
from datetime import datetime
import models
from models import Notification, InvitationStatus, UserStatus, ReactivationStatus
import uuid
from models import Invitation, User, ReactivationRequest

# ---------------- EMPLOYEES ----------------
def get_employees(db: Session, company_id: int):
    return db.query(models.Employee).filter(
        models.Employee.company_id == company_id
    ).all()

def get_employee_by_id(db: Session, id: int, company_id: int):
    return db.query(models.Employee).filter(
        models.Employee.id == id,
        models.Employee.company_id == company_id
    ).first()

def create_employee(
    db: Session,
    name: str,
    department_id: int,
    email: str,
    role: str,
    company_id: int,
    joined_date: datetime | None = None,
    status: str = "active"
):
    new_emp = models.Employee(
        name=name,
        email=email,
        department_id=department_id,
        role=role,
        joined_date=joined_date or datetime.utcnow(),
        status=status,
        company_id=company_id
    )
    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)
    return new_emp

def update_employee(
    db: Session,
    id: int,
    name: str,
    email: str,
    role: str,
    department_id: int,
    company_id: int,
    joined_date: datetime | None = None,
    status: str = "active"
):
    emp = get_employee_by_id(db, id, company_id)
    if not emp:
        return None

    emp.name = name
    emp.email = email
    emp.role = role
    emp.department_id = department_id
    emp.joined_date = joined_date or emp.joined_date
    emp.status = status

    db.commit()
    db.refresh(emp)
    return emp

def delete_employee(db: Session, id: int, company_id: int):
    emp = get_employee_by_id(db, id, company_id)
    if not emp:
        return None
    db.delete(emp)
    db.commit()
    return emp

# ---------------- DEPARTMENTS ----------------
def get_departments(db: Session, company_id: int):
    return db.query(models.Department).filter(
        models.Department.company_id == company_id
    ).all()

def create_department(db: Session, name: str, company_id: int):
    new_dept = models.Department(name=name, company_id=company_id)
    db.add(new_dept)
    db.commit()
    db.refresh(new_dept)
    return new_dept

# ---------------- NOTIFICATIONS ----------------
def create_notification(db: Session, message: str, recipient_email: str, company_id: int):
    note = Notification(
        message=message,
        recipient_email=recipient_email,
        is_read=False,
        company_id=company_id
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

# ---------------- ATTENDANCE ----------------
def create_attendance(db: Session, employee_id: int, date: datetime, status: str, company_id: int):
    record = models.Attendance(
        employee_id=employee_id,
        date=date,
        status=status,
        company_id=company_id
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def get_attendance(db: Session, company_id: int):
    return db.query(models.Attendance).filter(
        models.Attendance.company_id == company_id
    ).all()

# ---------------- AUDIT LOGS ----------------
def create_audit_log(db: Session, user_name: str, action: str, related_user: str | None, company_id: int):
    log = models.AuditLog(
        user_name=user_name,
        action=action,
        related_user=related_user,
        company_id=company_id
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

def get_audit_logs(db: Session, company_id: int):
    return db.query(models.AuditLog).filter(
        models.AuditLog.company_id == company_id
    ).all()

def get_pending_role_requests(db: Session, company_id: int):
    return db.query(models.RoleChangeRequest).filter(
        models.RoleChangeRequest.company_id == company_id,
        models.RoleChangeRequest.status == models.RoleChangeStatus.pending
    ).count()

# ---------------- INVITATIONS ----------------
def create_invitation(db: Session, email: str, company_id: int, expires_at: datetime | None = None):
    token = str(uuid.uuid4())
    invitation = Invitation(
        email=email,
        token=token,
        status=InvitationStatus.pending,
        created_at=datetime.utcnow(),
        expires_at=expires_at,
        company_id=company_id
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    return invitation

def get_invitations(db: Session, company_id: int):
    return db.query(Invitation).filter(Invitation.company_id == company_id).all()

def revoke_invitation(db: Session, invitation_id: int, company_id: int):
    invitation = db.query(Invitation).filter(
        Invitation.id == invitation_id,
        Invitation.company_id == company_id
    ).first()
    if invitation:
        invitation.status = InvitationStatus.revoked
        db.commit()
        db.refresh(invitation)
    return invitation

# ---------------- MEMBERS ----------------
def get_members(db: Session, company_id: int):
    return db.query(User).filter(
        User.company_id == company_id,
        User.status == UserStatus.active
    ).all()

def deactivate_user(db: Session, user_id: int, company_id: int):
    user = db.query(User).filter(User.id == user_id, User.company_id == company_id).first()
    if user:
        user.status = UserStatus.deactivated
        db.commit()
        db.refresh(user)
    return user

def reactivate_user(db: Session, user_id: int, company_id: int):
    user = db.query(User).filter(User.id == user_id, User.company_id == company_id).first()
    if user:
        user.status = UserStatus.active
        db.commit()
        db.refresh(user)
    return user

# ---------------- REACTIVATION REQUESTS ----------------
def create_reactivation_request(db: Session, user_id: int, admin_email: str, company_id: int):
    request = ReactivationRequest(
        user_id=user_id,
        admin_email=admin_email,
        status=ReactivationStatus.pending,
        created_at=datetime.utcnow(),
        company_id=company_id
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request

def get_reactivation_requests(db: Session, company_id: int):
    return db.query(ReactivationRequest).filter(ReactivationRequest.company_id == company_id).all()

def update_reactivation_request(db: Session, request_id: int, status: ReactivationStatus, company_id: int):
    req = db.query(ReactivationRequest).filter(
        ReactivationRequest.id == request_id,
        ReactivationRequest.company_id == company_id
    ).first()
    if req:
        req.status = status
        db.commit()
        db.refresh(req)
    return req
