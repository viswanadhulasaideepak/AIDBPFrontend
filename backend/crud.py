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
def create_notification(
    db: Session, 
    message: str, 
    recipient_email: str, 
    company_id: int, 
    request_id: int | None = None
    ):
    
    note = Notification(
        message=message,
        recipient_email=recipient_email,
        is_read=False,
        company_id=company_id,
        request_id=request_id
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
    
def get_attendance_access_request(db: Session, user_id: int):
    return db.query(models.AttendanceAccessRequest).filter(
        models.AttendanceAccessRequest.user_id == user_id
    ).first()
    
def create_attendance_access_request(
    db: Session,
    user_id: int,
    admin_email: str,
    company_id: int
):
    existing = get_attendance_access_request(db, user_id)

    if existing:
        return existing

    request = models.AttendanceAccessRequest(
        user_id=user_id,
        admin_email=admin_email,
        company_id=company_id,
        status=models.AttendanceAccessStatus.pending
    )

    db.add(request)
    db.commit()
    db.refresh(request)
    
    # Notify all admins of this company

    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()
    
    admins = db.query(User).filter(
        User.company_id == company_id,
        User.role == "admin").all()
    
    for admin in admins:
        create_notification(
            db=db,
            message=f"{user.username} ({user.email}) requested attendance access.",
            recipient_email=admin.email,
            company_id=company_id
    )


    create_audit_log(
        db=db,
        user_name=admin_email,
        action="Attendance Access Request Submitted",
        related_user=None,
        company_id=company_id
    )
    
    return request     

  #------------Update Attendance_access_request-------------
  
def update_attendance_access_request(
    db: Session,
    request_id: int,
    status: models.AttendanceAccessStatus,
    company_id: int,
    approved_by: str
    ):
    request = db.query(models.AttendanceAccessRequest).filter(
        models.AttendanceAccessRequest.id == request_id,
        models.AttendanceAccessRequest.company_id == company_id
    ).first()

    if not request:
        return None

    request.status = status
    request.approved_at = datetime.utcnow()
    request.approved_by = approved_by

    user = db.query(models.User).filter(
        models.User.id == request.user_id
    ).first()

    if isinstance(status, str):
        status = models.AttendanceAccessStatus(status)

        create_notification(
            db=db,
            message="Your attendance access request has been approved.",
            recipient_email=user.email,
            company_id=company_id
        )

        create_audit_log(
            db=db,
            user_name=user.email,
            action="Attendance Access Approved",
            related_user=user.email,
            company_id=company_id
        )

    elif status == models.AttendanceAccessStatus.rejected:

        create_notification(
            db=db,
            message="Your attendance access request has been rejected.",
            recipient_email=user.email,
            company_id=company_id
        )

        create_audit_log(
            db=db,
            user_name=user.email,
            action="Attendance Access Rejected",
            related_user=user.email,
            company_id=company_id
        )

    db.commit()
    db.refresh(request)

    return request
    

#----------Attendance Approval--------------

def is_attendance_access_approved(
    db: Session,
    user_id: int
):
   request = db.query(models.AttendanceAccessRequest).filter(
        models.AttendanceAccessRequest.user_id == user_id,
        models.AttendanceAccessRequest.status == models.AttendanceAccessStatus.approved
    ).first()
   
   return request is not None

# =====================================================
# ATTENDANCE CHECK-IN / CHECK-OUT
# =====================================================

def calculate_working_hours(check_in: datetime, check_out: datetime):
    """
    Calculate total working hours between check-in and check-out.
    Returns result in HH:MM format.
    """

    total_seconds = (check_out - check_in).total_seconds()

    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)

    return f"{hours:02}:{minutes:02}"


def check_in(
    db: Session,
    employee_id: int,
    company_id: int
):
    """
    Employee Check-In
    """

    today = datetime.utcnow().date()

    attendance = db.query(models.Attendance).filter(
        models.Attendance.employee_id == employee_id,
        models.Attendance.company_id == company_id,
        models.Attendance.date >= datetime.combine(today, datetime.min.time()),
        models.Attendance.date <= datetime.combine(today, datetime.max.time())
    ).first()

    if attendance:

        if attendance.check_in:
            return None

        attendance.check_in = datetime.utcnow()
        attendance.status = "Present"

    else:

        attendance = models.Attendance(
            employee_id=employee_id,
            company_id=company_id,
            date=datetime.utcnow(),
            status="Present",
            check_in=datetime.utcnow()
        )

        db.add(attendance)

    db.commit()
    db.refresh(attendance)

    return attendance


def check_out(
    db: Session,
    employee_id: int,
    company_id: int
):
    """
    Employee Check-Out
    """

    today = datetime.utcnow().date()

    attendance = db.query(models.Attendance).filter(
        models.Attendance.employee_id == employee_id,
        models.Attendance.company_id == company_id,
        models.Attendance.date >= datetime.combine(today, datetime.min.time()),
        models.Attendance.date <= datetime.combine(today, datetime.max.time())
    ).first()

    if not attendance:
        return None

    if attendance.check_in is None:
        return None

    if attendance.check_out:
        return attendance

    attendance.check_out = datetime.utcnow()

    attendance.working_hours = calculate_working_hours(
        attendance.check_in,
        attendance.check_out
    )

    db.commit()
    db.refresh(attendance)

    return attendance

# =====================================================
# TODAY'S ATTENDANCE
# =====================================================

def get_today_attendance(
    db: Session,
    employee_id: int,
    company_id: int
):
    """
    Returns today's attendance for the employee.
    """

    today = datetime.utcnow().date()

    attendance = db.query(models.Attendance).filter(
        models.Attendance.employee_id == employee_id,
        models.Attendance.company_id == company_id,
        models.Attendance.date >= datetime.combine(today, datetime.min.time()),
        models.Attendance.date <= datetime.combine(today, datetime.max.time())
    ).first()

    return attendance


# =====================================================
# RECENT ATTENDANCE HISTORY
# =====================================================

def get_recent_attendance(
    db: Session,
    employee_id: int,
    company_id: int,
    limit: int = 10
):
    """
    Returns recent attendance history.
    """

    attendance = (
        db.query(models.Attendance)
        .filter(
            models.Attendance.employee_id == employee_id,
            models.Attendance.company_id == company_id
        )
        .order_by(models.Attendance.date.desc())
        .limit(limit)
        .all()
    )
    return attendance

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
def create_invitation(
    db: Session, 
    email: str, 
    company_id: int, 
    role: str,
    expires_at:  None
    ):
    token = str(uuid.uuid4())
    invitation = Invitation(
        email=email,
        token=token,
        role=role,
        status=InvitationStatus.pending,
        created_at=datetime.utcnow(),
        expires_at=expires_at,
        company_id=company_id
    )
    
    existing = db.query(Invitation).filter(
        Invitation.email == email,
        Invitation.company_id == company_id,
        Invitation.status == InvitationStatus.pending,
        
        ).first()
    
    if existing:
        return None
    
    db.add(invitation)
    
    db.commit()
    db.refresh(invitation)
    
    create_audit_log(db, user_name=email, action="Invitation Created",
                 related_user=None, company_id=company_id)

    return invitation

def get_invitations(db: Session, company_id: int):
    return db.query(Invitation).filter(Invitation.company_id == company_id).all()

def revoke_invitation(db: Session, invitation_id: int, company_id: int, performed_by: str):
    invitation = db.query(Invitation).filter(
        Invitation.id == invitation_id,
        Invitation.company_id == company_id,
        Invitation.status == InvitationStatus.pending
    ).first()
    
    if not invitation:
        return None
    
    invitation.status = InvitationStatus.revoked
    db.commit()
    db.refresh(invitation)
    
    create_audit_log(db, user_name=invitation.email, action="Invitation Revoked",
                    related_user=None, company_id=company_id)
    
    return invitation

# ---------------- MEMBERS ----------------
def get_members(db: Session, company_id: int):
    return db.query(User).filter(
        User.company_id == company_id,
        User.status == UserStatus.active
    ).all()

def deactivate_user(db: Session, user_id: int, company_id: int, admin_email: str):
    user = db.query(User).filter(User.id == user_id, User.company_id == company_id).first()
    if user:
        user.status = UserStatus.deactivated
        user.deactivated_by = admin_email
        db.commit()
        db.refresh(user)
        
    create_audit_log(db, user_name=user.email, action="User Deactivated",
                     related_user=None, company_id=company_id)
    create_notification(
        db=db,
        message="Your account has been deactivated by the administrator.",
        recipient_email=user.email,
        company_id=company_id
        )
    return user

def reactivate_user(db: Session, user_id: int, company_id: int):
    user = db.query(User).filter(User.id == user_id, User.company_id == company_id).first()
    if user:
        user.status = UserStatus.active
        user.deactivated_by = None
        db.commit()
        db.refresh(user)
    return user

# ---------------- REACTIVATION REQUESTS ----------------
def create_reactivation_request(
    db: Session, 
    user_id: int,
    message:str | None,
    admin_email: str, 
    company_id: int
    ):
    
    existing = db.query(ReactivationRequest).filter(
        ReactivationRequest.user_id == user_id,
        ReactivationRequest.status == ReactivationStatus.pending
        ).first()
    
    if existing:
        return None
    
    request = ReactivationRequest(
        user_id=user_id,
        admin_email=admin_email,
        message=message,
        status=ReactivationStatus.pending,
        company_id=company_id
    ) 
    db.add(request)
    db.commit()
    db.refresh(request)
    
    create_audit_log(db, user_name=str(user_id), action="Reactivation Request Submitted",
                 related_user=None, company_id=company_id)
    
    create_notification(
        db=db,
        message=f"New reactivation request from {admin_email}",
        recipient_email=admin_email, 
        request_id=request.id,
        company_id=company_id
        )

    return request

def get_reactivation_requests(db: Session, company_id: int):
    return db.query(ReactivationRequest).filter(ReactivationRequest.company_id == company_id).all()

# ---------------- UPDATE REACTIVATION REQUEST ----------------
def update_reactivation_request(
    db: Session,
    request_id: int,
    status: ReactivationStatus,
    company_id: int
):
    req = db.query(ReactivationRequest).filter(
        ReactivationRequest.id == request_id,
        ReactivationRequest.company_id == company_id
    ).first()

    if not req:
        return None

    # Update request status
    req.status = status

    # Get the user
    user = db.query(User).filter(
        User.id == req.user_id,
        User.company_id == company_id
    ).first()

    # ---------------- APPROVED ----------------
    if status == ReactivationStatus.approved and user:
        user.status = UserStatus.active

        create_audit_log(
            db=db,
            user_name=user.email,
            action="User Reactivated",
            related_user=user.email,
            company_id=company_id
        )

        create_notification(
            db=db,
            message="Your account has been reactivated by the administrator.",
            recipient_email=user.email,
            company_id=company_id
        )

    # ---------------- REJECTED ----------------
    elif status == ReactivationStatus.rejected and user:

        create_audit_log(
            db=db,
            user_name=user.email,
            action="Reactivation Request Rejected",
            related_user=user.email,
            company_id=company_id
        )

        create_notification(
            db=db,
            message="Your reactivation request has been rejected.",
            recipient_email=user.email,
            company_id=company_id
        )

    db.commit()
    db.refresh(req)

    return req
