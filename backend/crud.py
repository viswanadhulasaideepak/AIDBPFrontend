from sqlalchemy.orm import Session
from datetime import datetime
import models
from models import Notification, InvitationStatus, UserStatus, ReactivationStatus,LeaveRequest,LeaveStatus,LeaveType
import uuid
from models import Invitation, User, ReactivationRequest

# ---------------- EMPLOYEES ----------------
def get_employees(db: Session, company_id: int):
    return db.query(models.Employee).filter(
        models.Employee.company_id == company_id
    ).all()

def get_employee_by_id(db: Session,id: int, company_id: int):
    return db.query(models.Employee).filter(
        models.Employee.id == id,
        models.Employee.company_id == company_id
    ).first()
    
def get_employee(db: Session, employee_id: int, company_id: int):
    return db.query(models.Employee).filter(
        models.Employee.id == employee_id,
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
    
    admins = db.query(models.User).filter(
        models.User.company_id == company_id,
       models.User.role == "admin"
       ).all()
    
    for admin in admins:
        
        create_notification(
            db=db,
            message=f"New employee added: {new_emp.name}",
            recipient_email=admin.email,
            company_id=company_id,
            type="employee"
            )
        
        create_audit_log(
            db=db,
            user_name=new_emp.name,
            action="Employee Added",
            related_user=new_emp.email,
            company_id=company_id
            )
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

    admins = db.query(models.User).filter(
    models.User.company_id == emp.company_id,
    models.User.role == "admin"
    ).all()
    
    for admin in admins:
        create_notification(
            db=db,
            message=f"Employee updated: {emp.name}",
            recipient_email=admin.email,
            company_id=emp.company_id,
            type="employee"
            )

        create_audit_log(
            db=db,
            user_name=emp.name,
            action="Employee Updated",
            related_user=emp.email,
            company_id=emp.company_id
            )
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

# ---------------- Department Transfer ----------------

def transfer_employee_department(
    db: Session,
    employee,
    new_department_id: int,
    performed_by: str,
    company_id: int,
    reason: str | None = None
):

    old_department = db.query(models.Department).filter(
        models.Department.id == employee.department_id
    ).first()

    new_department = db.query(models.Department).filter(
        models.Department.id == new_department_id,
        models.Department.company_id == company_id
    ).first()

    if not new_department:
        raise Exception("Department not found.")

    if employee.department_id == new_department_id:
        raise Exception("Employee is already in this department.")

    transfer = models.DepartmentTransfer(
        employee_id=employee.id,
        old_department_id=employee.department_id,
        new_department_id=new_department_id,
        transferred_by=performed_by,
        company_id=company_id,
        reason=reason
    )

    db.add(transfer)

    employee.department_id = new_department_id

    db.flush()

    create_notification(
        db=db,
        message=f"Your department has been changed from '{old_department.name}' to '{new_department.name}'.",
        recipient_email=employee.email,
        company_id=company_id,
        request_id=employee.id,
        type="department_transfer"
    )

    create_audit_log(
        db=db,
        user_name=performed_by,
        action=f"Department transferred from '{old_department.name}' to '{new_department.name}'",
        related_user=employee.email,
        company_id=company_id
    )

    return {
        "message": "Department transferred successfully.",
        "employee_id": employee.id,
        "old_department": old_department.name,
        "new_department": new_department.name
    }

# ---------------- NOTIFICATIONS ----------------
def create_notification(
    db: Session, 
    message: str, 
    recipient_email: str, 
    company_id: int, 
    request_id: int | None = None,
    type: str = "general"
    ):
    
    note = Notification(
        message=message,
        recipient_email=recipient_email,
        company_id=company_id,
        request_id=request_id,
        type=type,
        is_read=False
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
    
def get_attendance_access_request(db, user_id):

    request = db.query(
        models.AttendanceAccessRequest
    ).filter(
        models.AttendanceAccessRequest.user_id == user_id
    ).first()

    print("========== SEARCH REQUEST ==========")
    print("User:", user_id)
    print("Result:", request)
    print("===================================")

    return request
    
def create_attendance_access_request(
    db,
    user_id,
    admin_email,
    company_id
):
    print("FUNCTION STARTED")
    existing = get_attendance_access_request(db, user_id)
    print("Existing:", existing)
    if existing:
        print("Already Exists")
        return existing

    print("Creating...")

    request = models.AttendanceAccessRequest(
        user_id=user_id,
        admin_email=admin_email,
        company_id=company_id,
        status=models.AttendanceAccessStatus.pending
    )
    db.add(request)
    print("Before Commit")
    db.commit()
    print("After Commit")
    db.refresh(request)
    print("Request ID:", request.id)
    
    # Notify all admins about the new attendance request
    admins = db.query(models.User).filter(
        models.User.company_id == company_id,
        models.User.role == "admin").all()

    user = db.query(models.User).filter(
        models.User.id == user_id).first()

    for admin in admins:
        create_notification(
            db=db,
            message=f"{user.username} requested attendance access.",
            recipient_email=admin.email,
            company_id=company_id,
            request_id=request.id,
            type="attendance"
            )

    return request     

def update_attendance_access_request(
    db: Session,
    request_id: int,
    status: models.AttendanceAccessStatus,
    company_id: int,
    approved_by: str
):
    # Convert string to enum if needed
    if isinstance(status, str):
        status = models.AttendanceAccessStatus(status)

    request = db.query(models.AttendanceAccessRequest).filter(
        models.AttendanceAccessRequest.id == request_id,
        models.AttendanceAccessRequest.company_id == company_id
    ).first()

    if not request:
        return None
    
    print("========== APPROVING ==========")
    print("Request ID:", request_id)
    print("Status:", status)
    print("Company:", company_id)

    request.status = status
    request.approved_at = datetime.utcnow()
    request.approved_by = approved_by
    
    admins = db.query(models.User).filter(
    models.User.company_id == company_id,
    models.User.role == "admin"
    ).all()

    user = db.query(models.User).filter(
        models.User.id == request.user_id
    ).first()

    # ---------------- APPROVED ----------------
    if status == models.AttendanceAccessStatus.approved:
        
        create_audit_log(
            db=db,
            user_name=approved_by,
            action="Attendance Access Approved",
            related_user=user.email,
            company_id=company_id
            )

        create_notification(
            db=db,
            message="Your attendance access request has been approved.",
            recipient_email=user.email,
            request_id=request.id,
            company_id=company_id
            )
        
        for admin in admins:
            create_notification(
            db=db,
            message=f"{user.username} attendance request approved.",
            recipient_email=admin.email,
            company_id=company_id,
            request_id=request.id,
            type="attendance"
            )


    # ---------------- REJECTED ----------------
    elif status == models.AttendanceAccessStatus.rejected:
        
        create_audit_log(
            db=db,
            user_name=approved_by,
            action="Attendance Access Rejected",
            related_user=user.email,
            company_id=company_id
            )

        create_notification(
            db=db,
            message="Your attendance access request has been rejected.",
            recipient_email=user.email,
            request_id=request.id,
            company_id=company_id
        )
        
        for admin in admins:
            create_notification(
                db=db,
                message=f"{user.username} attendance request rejected.",
                recipient_email=admin.email,
                company_id=company_id,
                request_id=request.id,
                type="attendance"
                )

    db.commit()
    print("Approved Successfully")
    db.refresh(request)
    print("After Commit:", request.status)
    

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

# ----------ATTENDANCE CHECK-IN / CHECK-OUT--------------
def calculate_working_hours(check_in: datetime, check_out: datetime):
    """
    Calculate total working hours between check-in and check-out.
    Returns result in HH:MM format.
    """

    total_seconds = (check_out - check_in).total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)

    return f"{hours:02}:{minutes:02}"

#-----------Check In---------------
def check_in(db: Session, employee_id: int, company_id: int):

    today = datetime.utcnow().date()

    attendance = db.query(models.Attendance).filter(
        models.Attendance.employee_id == employee_id,
        models.Attendance.company_id == company_id,
        models.Attendance.date >= datetime.combine(today, datetime.min.time()),
        models.Attendance.date <= datetime.combine(today, datetime.max.time())
    ).first()
    
    print("DB PATH:", db.bind.url.database)

    print("Attendance Found:", attendance)

    if attendance:
        print("Attendance ID:", attendance.id)
        print("Attendance Date:", attendance.date)
        print("Check In:", attendance.check_in)
        print("Check Out:", attendance.check_out)
        
        if attendance.check_in:
            print("Already Checked In")
            return None

        attendance.check_in = datetime.utcnow()
        attendance.status = "Present"

        db.commit()
        db.refresh(attendance)

        print("Updated Attendance")

        return attendance

    print("Creating New Attendance")

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

    print("Created Attendance:", attendance.id)

    return attendance

#--------------CheckOut----------------
def check_out(db: Session, employee_id: int, company_id: int):
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
    
    employee = db.query(models.Employee).filter(
    models.Employee.id == employee_id).first()
    
    create_audit_log(
        db=db,
        user_name=employee.email,
        action="Check-Out",
        related_user=None,
        company_id=company_id
        )

    return attendance

# --------TODAY'S ATTENDANCE-------------
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

# ----------RECENT ATTENDANCE HISTORY-------------------
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

#------------ LEAVE MANAGEMENT----------------
def create_leave_request(
    db: Session,
    user_id: int,
    company_id: int,
    leave_type: str,
    start_date: datetime,
    end_date: datetime,
    reason: str
):

    leave = LeaveRequest(
        user_id=user_id,
        company_id=company_id,
        leave_type=LeaveType(leave_type),
        start_date=start_date,
        end_date=end_date,
        reason=reason,
        status=LeaveStatus.pending
    )

    db.add(leave)
    db.commit()
    db.refresh(leave)

    # Notify all admins
    admins = db.query(User).filter(
        User.company_id == company_id,
        User.role == "admin"
    ).all()

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    for admin in admins:

        create_notification(
            db=db,
            recipient_email=admin.email,
            company_id=company_id,
            message=(
                f"Leave request from "
                f"{user.username} ({user.email}) "
                f"submitted on "
                f"{leave.created_at.strftime('%Y-%m-%d %H:%M')}"
            ),
            request_id=leave.id,
            type="leave"
        )

    create_audit_log(
        db=db,
        user_name=user.email,
        action="Leave Request Submitted",
        related_user=user.email,
        company_id=company_id
    )

    return leave

def get_my_leave_requests(
    db: Session,
    user_id: int
):

    return db.query( LeaveRequest ).filter(
        LeaveRequest.user_id == user_id).order_by(
        LeaveRequest.created_at.desc()).all()
    
def get_company_leave_requests(
    db: Session,
    company_id: int
):

    return db.query( LeaveRequest).filter( 
        LeaveRequest.company_id == company_id).order_by(
        LeaveRequest.created_at.desc()).all()
        
#------update leave requests-----------    
def update_leave_request(
    db: Session,
    request_id: int,
    status: str,
    company_id: int,
    reviewed_by: str
):

    request = db.query(LeaveRequest).filter(
        LeaveRequest.id == request_id,
        LeaveRequest.company_id == company_id
    ).first()

    if request is None:
        return None

    request.status = LeaveStatus(status)
    request.reviewed_at = datetime.utcnow()
    request.reviewed_by = reviewed_by
    
    db.commit()
    db.refresh(request)

    user = db.query(User).filter(
        User.id == request.user_id
    ).first()

    create_notification(
        db=db,
        recipient_email=user.email,
        company_id=company_id,
        message=f"Your leave request has been {status}.",
        request_id=request.id,
        type="leave"
    )

    create_audit_log(
        db=db,
        user_name=reviewed_by,
        action=f"Leave Request {status.capitalize()}",
        related_user=user.email,
        company_id=company_id
    )

    return request
        
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

def get_pending_attendance_access_requests(
    db: Session,
    company_id: int
):
    print("========== ADMIN FETCHING REQUESTS ==========")
    print("Company:", company_id)

    requests = (
        db.query(models.AttendanceAccessRequest)
        .filter(
            models.AttendanceAccessRequest.company_id == company_id,
            models.AttendanceAccessRequest.status == models.AttendanceAccessStatus.pending
        )
        .all()
    )
    print("Pending Requests:", len(requests))
    for r in requests:
        print(
            r.id,
            r.user_id,
            r.company_id,
            r.status
        )
    print("==========================================")
    return requests

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
        
    create_audit_log(db=db, user_name=user.email, action="User Deactivated",
                     related_user=user.email, company_id=user.company_id)
    create_notification(
        db=db,
        message="Your account has been deactivated.",
        recipient_email=admin_email,
        company_id=user.company_id,
        type="user"
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
        company_id=company_id,
        type="user"
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