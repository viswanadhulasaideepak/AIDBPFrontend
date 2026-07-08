from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
import models
from models import (Notification,InvitationStatus,UserStatus,ReactivationStatus,LeaveRequest,
    LeaveStatus,LeaveType,ReinstatementRequest,ReinstatementStatus,ExportHistory,LoginSession,
    SessionStatus,SessionTerminationReason)
import uuid
from models import Invitation, User, ReactivationRequest
from hashlib import sha256

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
    
def get_employee_by_email(
    db: Session,
    email: str,
    company_id: int
):
    return (
        db.query(models.Employee)
        .filter(
            models.Employee.email == email,
            models.Employee.company_id == company_id
        )
        .first()
    )    

def create_employee(
    db: Session,
    name: str,
    department_id: int,
    email: str,
    role: str,
    company_id: int,
    joined_date: datetime | None = None,
    status: str = "active",
    employee_code: str = None
):
    new_emp = models.Employee(
        name=name,
        email=email,
        department_id=department_id,
        role=role,
        joined_date=joined_date or datetime.utcnow(),
        status=status,
        employee_code=employee_code,
        company_id=company_id,
        profile_completion=0
    )
    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)
    
    new_emp.employee_code = f"EMP{new_emp.id:03d}"

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
    PROFILE_COMPLETION_THRESHOLD = 70
    emp = get_employee_by_id(db, id, company_id)
    if not emp:
        return None
    
    old_score = calculate_profile_completion(emp)

    emp.name = name
    emp.email = email
    emp.role = role
    emp.department_id = department_id
    emp.joined_date = joined_date or emp.joined_date
    emp.status = status
    
    emp.last_profile_update = datetime.utcnow()

    db.commit()
    db.refresh(emp)

    new_score = calculate_profile_completion(emp)
    
    emp.profile_completion = new_score["completion_percentage"]

    if old_score["completion_percentage"] != new_score["completion_percentage"]:
        create_audit_log(
            db=db,
            user_name=emp.name,
            action="Profile Completion Score Changed",
            related_user=emp.email,
            company_id=emp.company_id,
            details=f"{old_score['completion_percentage']}% -> {new_score['completion_percentage']}%"
    )

    admins = db.query(models.User).filter(
        models.User.company_id == emp.company_id,
        models.User.role == "admin"
    ).all()

    if new_score["completion_percentage"] == 100:
        for admin in admins:
            create_notification(
                db=db,
                message=f"{emp.name} completed their profile.",
                recipient_email=admin.email,
                company_id=emp.company_id,
                type="profile"
            )

        create_audit_log(
            db=db,
            user_name=emp.name,
            action="Profile Reached 100% Completion",
            related_user=emp.email,
            company_id=emp.company_id
        )

    elif new_score["completion_percentage"] < PROFILE_COMPLETION_THRESHOLD:
        create_notification(
            db=db,
            message="Your profile completion is below 70%. Please complete your profile.",
            recipient_email=emp.email,
            company_id=emp.company_id,
            type="profile"
        )

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

    # Don't create duplicate unread notification
    existing = db.query(Notification).filter(
        Notification.recipient_email == recipient_email,
        Notification.company_id == company_id,
        Notification.message == message,
        Notification.is_read == False
    ).first()

    if existing:
        return existing

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
    
    # Mark the admin notification as read
    db.query(models.Notification).filter(
        models.Notification.request_id == request.id,
        models.Notification.type == "attendance",
        models.Notification.recipient_email == approved_by
        ).update({"is_read": True})
    
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

# ---------------- HOLIDAY CHECK ----------------

def is_today_holiday(db: Session, company_id: int):
    today = datetime.utcnow().date()

    holiday = (
        db.query(models.Holiday)
        .filter(
            models.Holiday.company_id == company_id,
            models.Holiday.holiday_date >= datetime.combine(today, datetime.min.time()),
            models.Holiday.holiday_date <= datetime.combine(today, datetime.max.time())
        )
        .first()
    )

    return holiday

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

#---------------------Check In----------------------
def check_in(db: Session, employee_id: int, company_id: int):

    today = datetime.utcnow().date()
    
    holiday = is_today_holiday(db, company_id)

    if holiday:
        return {
            "holiday": True,
            "message": f"Today is '{holiday.name}'. Check-In is not required."
    }

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
    
    holiday = is_today_holiday(db, company_id)

    if holiday:
        return {
            "holiday": True,
            "message": f"Today is '{holiday.name}'. Check-Out is not required."
            }
    
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

# --------------------TODAY'S ATTENDANCE---------------
def get_today_attendance(
    db: Session,
    employee_id: int,
    company_id: int
):
    """
    Returns today's attendance for the employee.
    """

    today = datetime.utcnow().date()
    
    holiday = is_today_holiday(db, company_id)

    if holiday:
        return {
            "holiday": True,
            "holiday_name": holiday.name,
            "description": holiday.description
            }

    attendance = db.query(models.Attendance).filter(
        models.Attendance.employee_id == employee_id,
        models.Attendance.company_id == company_id,
        models.Attendance.date >= datetime.combine(today, datetime.min.time()),
        models.Attendance.date <= datetime.combine(today, datetime.max.time())
    ).first()

    return attendance

# -----------------RECENT ATTENDANCE HISTORY-------------------
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
        
#----------------update leave requests----------------
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
    
    # Mark the admin notification as read
    db.query(Notification).filter(
        Notification.request_id == request.id,
        Notification.type == "leave",
        Notification.recipient_email == reviewed_by,
        Notification.is_read == False
    ).update({"is_read": True})
    
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
def create_audit_log(
    db: Session,
    user_name: str,
    action: str,
    related_user: str | None,
    company_id: int,
    ip_address: str | None = None,
    browser: str | None = None,
    is_new_device: bool = False,
    is_new_ip: bool = False,
    details: str | None = None,
    performed_by: str | None = None,
):
    log = models.AuditLog(
        user_name=user_name,
        action=action,
        related_user=related_user,
        company_id=company_id,
        ip_address=ip_address,
        browser=browser,
        is_new_device=is_new_device,
        is_new_ip=is_new_ip,
        details=details,
        performed_by=performed_by,
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log

#-----------------Record User Login-------------------

def record_user_login(
    db: Session,
    user: models.User,
    ip_address: str,
    browser: str,
):

    device_hash = sha256(browser.encode()).hexdigest()
    activity = db.query(models.UserActivity).filter(
        models.UserActivity.user_id == user.id
    ).first()

    new_device = False
    new_ip = False

    if activity:

        if activity.device_hash != device_hash:
            new_device = True

        if activity.ip_address != ip_address:
            new_ip = True

        activity.last_login = datetime.utcnow()
        activity.browser = browser
        activity.ip_address = ip_address
        activity.device_hash = device_hash
        activity.last_activity = datetime.utcnow()
        activity.login_count += 1
        activity.is_online = True

    else:
        activity = models.UserActivity(
            user_id=user.id,
            company_id=user.company_id,
            last_login=datetime.utcnow(),
            last_logout=None,
            last_activity=datetime.utcnow(),
            login_count=1,
            is_online=True,
            browser=browser,
            ip_address=ip_address,
            device_hash=device_hash
            )

        db.add(activity)
        new_device = True
        new_ip = True

    db.commit()

    # Audit log (already correct, just reused)
    create_audit_log(
        db=db,
        user_name=user.email,
        action="User Login",
        related_user=user.email,
        company_id=user.company_id,
        ip_address=ip_address,
        browser=browser,
        is_new_device=new_device,
        is_new_ip=new_ip,
        details="User logged in."
    )
 #--------------Record User LogOut---------------------   
def record_user_logout(
    db: Session,
    user: models.User,
    ip_address: str,
    session_identifier: str,
    browser: str
):
    print("LOGOUT CALLED FOR:", user.email)

    activity = db.query(models.UserActivity).filter(
        models.UserActivity.user_id == user.id
    ).first()

    if activity:
        activity.last_logout = datetime.utcnow()
        activity.last_activity = datetime.utcnow()
        activity.is_online = False
        activity.browser = browser
        activity.ip_address = ip_address
        
        print("LAST LOGOUT SAVED:", activity.last_logout)
        
    session = (
    db.query(LoginSession)
    .filter(
        LoginSession.session_identifier == session_identifier,
        LoginSession.status == SessionStatus.active,
    ).first()
    )

    if session:
        session.status = SessionStatus.logged_out
        session.logged_out_at = datetime.utcnow()
        session.termination_reason = SessionTerminationReason.user_logout    

        
    db.commit()

    create_audit_log(
        db=db,
        user_name=user.email,
        action="User Logout",
        related_user=user.email,
        company_id=user.company_id,
        ip_address=ip_address,
        browser=browser,
        details="User logged out."
    )    
    
    #-----------Company User Activity---------------
def get_company_user_activity(
    db: Session,
    company_id: int
):

    results = (
        db.query(models.UserActivity, models.User)
        .join(models.User, models.User.id == models.UserActivity.user_id)
        .filter(models.User.company_id == company_id)
        .all()
    )

    response = []

    for activity, user in results:
        response.append({
            "username": user.username,
            "email": user.email,
            "last_login": activity.last_login,
            "last_logout": activity.last_logout,
            "browser": activity.browser,
            "ip_address": activity.ip_address,
        })

    return response

#-------------Activity History-------------------

def get_activity_history(
    db: Session,
    company_id: int
):

    logs = db.query(models.AuditLog).filter(
        models.AuditLog.company_id == company_id
    ).order_by(models.AuditLog.timestamp.desc()).all()

    response = []

    for log in logs:
        response.append({
            "user_name": log.user_name,
            "action": log.action,
            "timestamp": log.timestamp,
            "browser": log.browser,
            "ip_address": log.ip_address,
            "is_new_device": log.is_new_device,
            "is_new_ip": log.is_new_ip,
            "details": log.details
        })

    return response
#----------------User Self Activity-----------------
def get_user_activity(
    db: Session,
    user_id: int,
    company_id: int
):

    activity = db.query(models.UserActivity).filter(
        models.UserActivity.user_id == user_id,
        models.UserActivity.company_id == company_id
    ).first()

    return activity
    
    #------------Company User Activity History---------------
    
def get_user_activity_history(
    db: Session,
    company_id: int
):

    return (
        db.query(models.AuditLog)
        .filter(
            models.AuditLog.company_id == company_id
        )
        .order_by(models.AuditLog.timestamp.desc())
        .all()
    )    

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

#---------------Suspend User-----------------------

def suspend_user(
    db: Session,
    user_id: int,
    company_id: int,
    admin_email: str,
    reason: str
):
    print("======== SUSPEND DEBUG ========")
    print("User ID:", user_id)
    print("Company ID:", company_id)

    user = db.query(User).filter(
        User.id == user_id,
        User.company_id == company_id
    ).first()

    print("Found User:", user)

    if user:
        print("Email:", user.email)
        print("Role:", user.role)
        print("Company:", user.company_id)

    print("==============================")

    if not user:
        return None

    user.status = UserStatus.suspended
    user.suspended_by = admin_email
    user.suspended_reason = None
    user.suspended_at = datetime.utcnow()

    db.commit()
    db.refresh(user)

    # Notification to suspended user
    create_notification(
        db=db,
        message=f"Your account has been suspended. Reason: {reason}",
        recipient_email=user.email,
        company_id=company_id,
        type="suspension"
    )

    # Audit
    create_audit_log(
        db=db,
        user_name=admin_email,
        action=(
            "Admin Suspended"
            if user.role.lower() == "admin"
            else "User Suspended"
        ),
        related_user=user.email,
        company_id=company_id,
        details=reason
    )

    return user

#--------------------Reinstate User--------------------

def reinstate_user(
    db: Session,
    user_id: int,
    company_id: int,
    admin_email: str
):
    user = db.query(User).filter(
        User.id == user_id,
        User.company_id == company_id
    ).first()

    if not user:
        return None

    user.status = UserStatus.active

    user.suspended_by = None
    user.suspended_at = None
    user.suspended_reason = None

    db.commit()
    db.refresh(user)

    create_notification(
        db=db,
        message="Your account has been reinstated.",
        recipient_email=user.email,
        company_id=company_id,
        type="reinstatement"
    )

    create_audit_log(
        db=db,
        user_name=admin_email,
        action="User Reinstated",
        related_user=user.email,
        company_id=company_id
    )

    return user
#-----------------Reactivate User-------------------

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

#-------------Reinstatement Request------------------------

def create_reinstatement_request(
    db: Session,
    user_id: int,
    company_id: int,
    reason: str
):
    user = db.query(User).filter(
        User.id == user_id,
        User.company_id == company_id
    ).first()

    if not user:
        return None

    existing = db.query(
        ReinstatementRequest
    ).filter(
        ReinstatementRequest.user_id == user_id,
        ReinstatementRequest.status == ReinstatementStatus.pending
    ).first()

    if existing:
        return existing

    request = ReinstatementRequest(
        user_id=user_id,
        company_id=company_id,
        request_reason=reason,
        status=ReinstatementStatus.pending
    )

    db.add(request)
    db.commit()
    db.refresh(request)

    # Notify suspension admin
    admins = db.query(User).filter(
        User.company_id == company_id,
        User.role == "admin"
    ).all()

    for admin in admins:

        create_notification(
            db=db,
            message=(
                f"{user.username} submitted "
                f"a reinstatement request."
            ),
            recipient_email=admin.email,
            company_id=company_id,
            request_id=request.id,
            type="reinstatement"
        )

    create_audit_log(
        db=db,
        user_name=user.email,
        action="Reinstatement Request Submitted",
        related_user=user.email,
        company_id=company_id
    )

    return request

def get_reinstatement_requests(
    db: Session,
    company_id: int
):
   return (
    db.query(ReinstatementRequest)
    .filter(
        ReinstatementRequest.company_id == company_id,
        ReinstatementRequest.status == ReinstatementStatus.pending
    )
    .order_by(ReinstatementRequest.submitted_at.desc())
    .all()
)
   
#--------------Get My Reinstatement Request-------------------

def get_my_reinstatement_request(
    db: Session,
    user_id: int,
    company_id: int
):
    return (
        db.query(ReinstatementRequest)
        .filter(
            ReinstatementRequest.user_id == user_id,
            ReinstatementRequest.company_id == company_id
        )
        .order_by(ReinstatementRequest.submitted_at.desc())
        .first()
    )    
    
#--------------Update Reinstatement-------------------    
    
def update_reinstatement_request(
    db: Session,
    request_id: int,
    status: ReinstatementStatus,
    company_id: int,
    reviewed_by: str,
    admin_comment: str | None = None
):
    request = db.query(
        ReinstatementRequest
    ).filter(
        ReinstatementRequest.id == request_id,
        ReinstatementRequest.company_id == company_id
    ).first()

    if not request:
        return None

    request.status = status
    request.reviewed_at = datetime.utcnow()
    request.reviewed_by = reviewed_by
    request.admin_comment = admin_comment

    user = db.query(User).filter(
        User.id == request.user_id,
        User.company_id == company_id
    ).first()

    if not user:
        return None

    #----- APPROVE-----
    if status == ReinstatementStatus.approved:

        user.status = UserStatus.active
        user.suspended_by = None
        user.suspended_at = None
        user.suspended_reason = None

        create_audit_log(
            db=db,
            user_name=reviewed_by,
            action="Reinstatement Approved",
            related_user=user.email,
            company_id=company_id
        )

        create_notification(
            db=db,
            message="Your reinstatement request was approved.",
            recipient_email=user.email,
            company_id=company_id,
            type="reinstatement"
        )

    # --REJECT----
    elif status == ReinstatementStatus.rejected:

        create_audit_log(
            db=db,
            user_name=reviewed_by,
            action="Reinstatement Rejected",
            related_user=user.email,
            company_id=company_id
        )

        create_notification(
            db=db,
            message="Your reinstatement request was rejected.",
            recipient_email=user.email,
            company_id=company_id,
            type="reinstatement"
        )

    db.commit()
    db.refresh(request)

    return request

#-----------------Approve Reinstatement---------------

def approve_reinstatement(
    db: Session,
    request_id: int,
    company_id: int,
    approved_by: str,
    comment: str | None = None
):
    return update_reinstatement_request(
        db=db,
        request_id=request_id,
        status=ReinstatementStatus.approved,
        company_id=company_id,
        reviewed_by=approved_by,
        admin_comment=comment
    )

#-------------Reject Reinstatement---------------

def reject_reinstatement(
    db: Session,
    request_id: int,
    company_id: int,
    rejected_by: str,
    comment: str | None = None
):
    return update_reinstatement_request(
        db=db,
        request_id=request_id,
        status=ReinstatementStatus.rejected,
        company_id=company_id,
        reviewed_by=rejected_by,
        admin_comment=comment
    )

#----------------- DATA EXPORT CENTER--------------------------

def log_export(
    db: Session,
    exported_by: str,
    data_type: str,
    export_format: str,
    company_id: int,
):
    """
    Stores every successful export.
    """

    export = ExportHistory(
        exported_by=exported_by,
        data_type=data_type,
        export_format=export_format,
        company_id=company_id,
    )

    db.add(export)
    db.commit()
    db.refresh(export)

    return export


def get_export_history(
    db: Session,
    company_id: int,
):
    """
    Returns export history for the current company only.
    """

    return (
        db.query(ExportHistory)
        .filter(
            ExportHistory.company_id == company_id
        )
        .order_by(
            ExportHistory.exported_at.desc()
        )
        .all()
    )
    
# ----------------Export Employees ----------------

def get_export_employees(
    db: Session,
    company_id: int
):
    return (
        db.query(models.Employee)
        .filter(
            models.Employee.company_id == company_id
        )
        .all()
    )

# ----------------Export Attendance ----------------

def get_export_attendance(
    db: Session,
    company_id: int
):
    return (
        db.query(models.Attendance)
        .filter(
            models.Attendance.company_id == company_id
        )
        .all()
    )

# ----------------Export Leave Requests ----------------

def get_export_leave_requests(
    db: Session,
    company_id: int
):
    return (
        db.query(models.LeaveRequest)
        .filter(
            models.LeaveRequest.company_id == company_id
        )
        .all()
    )

# ----------------Export Audit Logs ----------------

def get_export_audit_logs(
    db: Session,
    company_id: int
):
    return (
        db.query(models.AuditLog)
        .filter(
            models.AuditLog.company_id == company_id
        )
        .order_by(models.AuditLog.timestamp.desc())
        .all()
    )

# ----------------Export Notifications ----------------

def get_export_notifications(
    db: Session,
    company_id: int
):
    return (
        db.query(models.Notification)
        .filter(
            models.Notification.company_id == company_id
        )
        .order_by(models.Notification.created_at.desc())
        .all()
    )    
    
#------------------Calculate Profile Completion-----------------------------------
    
def calculate_profile_completion(employee):
    """
    Calculates employee profile completion percentage.
    """

    required_fields = {
        "First Name": getattr(employee, "first_name", None),
        "Last Name": getattr(employee, "last_name", None),
        "Email": getattr(employee, "email", None),
        "Department": getattr(employee, "department_id", None),
        "Date of Joining": getattr(employee, "joined_date", None),
        "Employee ID": getattr(employee, "employee_code", None),
        "Phone Number": getattr(employee, "phone_number", None),
        "Designation": getattr(employee, "designation", None),
        "Profile Picture": getattr(employee, "profile_picture", None),
        "Address": getattr(employee, "address", None),
    }

    total_fields = len(required_fields)
    completed = 0
    missing_fields = []

    for field_name, value in required_fields.items():
        if value not in (None, "", []):
            completed += 1
        else:
            missing_fields.append(field_name)

    percentage = round((completed / total_fields) * 100)

    recommendation = (
    "Your profile is complete."
    if percentage == 100
    else "Complete your profile to improve account readiness."
    )

    return {
        "completion_percentage": percentage,
        "completed_fields": completed,
        "total_fields": total_fields,
        "missing_fields": missing_fields,
        "recommendation": recommendation,
        }    
    
def get_employee_profile_completion(
    db: Session,
    employee_id: int,
    company_id: int
):
    employee = db.query(models.Employee).filter(
        models.Employee.id == employee_id,
        models.Employee.company_id == company_id
    ).first()

    if not employee:
        return None

    score = calculate_profile_completion(employee)

    return {
        "employee_id": employee.id,
        "employee_name": employee.name,
        "completion_percentage": score["completion_percentage"],
        "completed_fields": score["completed_fields"],
        "total_fields": score["total_fields"],
        "missing_fields": score["missing_fields"],
        "recommendation": score["recommendation"],
        }

def get_company_profile_completion(
    db: Session,
    company_id: int,
    threshold: int | None = None
):
    employees = db.query(models.Employee).filter(
        models.Employee.company_id == company_id
    ).all()

    results = []

    for employee in employees:
        score = calculate_profile_completion(employee)
        
        print(employee.name, employee.role)

        if threshold is None or score["completion_percentage"] < threshold:
            results.append({
                "employee_id": employee.id,
                "employee_name": employee.name,
                "role": employee.role,
                "company_id": employee.company_id,
                "department": (
                    employee.department_rel.name
                    if employee.department_rel
                    else None
                    ),
                "designation": employee.designation,
                "completion_percentage": score["completion_percentage"],
                "missing_fields": score["missing_fields"],
                })

    admins = db.query(models.User).filter(
    models.User.company_id == company_id,
    models.User.role == "admin"
    ).count()

    users = db.query(models.User).filter(
        models.User.company_id == company_id,
    models.User.role == "user"
    ).count()

    return {
        "members": results,
        "admin_count": admins,
        "user_count": users
        }    


def get_profile_completion_below_threshold(
    db: Session,
    company_id: int,
    threshold: int
):
    employees = db.query(models.Employee).filter(
        models.Employee.company_id == company_id
    ).all()

    result = []

    for emp in employees:
        completion = calculate_profile_completion(emp)  

        if threshold is None or completion["completion_percentage"] < threshold:
            result.append({
                "employee_id": emp.id,
                "employee_name": emp.name,
                "email": emp.email,
                "completion_percentage": completion["completion_percentage"],
                "missing_fields": completion["missing_fields"]
            })

    return result

#---------------------Holidays Section---------------------

def create_holiday(
    db: Session,
    name: str,
    description: str,
    holiday_date: datetime,
    holiday_type: str,
    recurring: bool,
    company_id: int,
    created_by: str
):
    existing = (
        db.query(models.Holiday).filter(
            models.Holiday.company_id == company_id,
            models.Holiday.holiday_date == holiday_date
            ).first()
        )

    if existing:
        raise ValueError("Holiday already exists for this date.")
    
    holiday = models.Holiday(
        name=name,
        description=description,
        holiday_date=holiday_date,
        holiday_type=holiday_type,
        recurring=recurring,
        company_id=company_id,
        created_by=created_by
    )

    db.add(holiday)
    db.commit()
    db.refresh(holiday)

    create_audit_log(
        db=db,
        user_name=created_by,
        action="Holiday Created",
        related_user=None,
        company_id=company_id,
        details=name
    )

    return holiday

def get_holidays(
    db: Session,
    company_id: int
):
    return (
        db.query(models.Holiday)
        .filter(models.Holiday.company_id == company_id)
        .order_by(models.Holiday.holiday_date)
        .all()
    )
    
def update_holiday(
    db: Session,
    holiday_id: int,
    company_id: int,
    updated_by,
    **kwargs
):
    holiday = (
        db.query(models.Holiday).filter(
            models.Holiday.id == holiday_id,
            models.Holiday.company_id == company_id
        )
        .first()
    )

    if not holiday:
        return None
    
    new_date = kwargs.get("holiday_date")

    if new_date:
        duplicate = (
            db.query(models.Holiday).filter(
                models.Holiday.company_id == company_id,
                models.Holiday.holiday_date == new_date,
                models.Holiday.id != holiday_id
                ).first()
            )

    if duplicate:
        raise ValueError("Holiday already exists for this date.")

    for key, value in kwargs.items():
        if value is not None:
            setattr(holiday, key, value)

    db.commit()
    db.refresh(holiday)
    
    create_audit_log(
        db=db,
        user_name=updated_by,
        action="Holiday Updated",
        related_user=None,
        company_id=company_id,
        details=holiday.name
        )

    return holiday

def delete_holiday(
    db: Session,
    holiday_id: int,
    company_id: int,
    deleted_by : str
):
    holiday = (
        db.query(models.Holiday)
        .filter(
            models.Holiday.id == holiday_id,
            models.Holiday.company_id == company_id
        )
        .first()
    )

    if not holiday:
        return None

    create_audit_log(
        db=db,
        user_name=deleted_by,
        action="Holiday Deleted",
        related_user=None,
        company_id=company_id,
        details=holiday.name
        )

    db.delete(holiday)
    db.commit()
    return holiday    

def get_holiday(
    db: Session,
    holiday_id: int,
    company_id: int
):
    return (
        db.query(models.Holiday)
        .filter(
            models.Holiday.id == holiday_id,
            models.Holiday.company_id == company_id
        )
        .first()
    )
    
# -----------------------Login Device & Session Management------------------------------

def create_login_session(
    db: Session,
    user: models.User,
    session_identifier: str,
    device_name: str,
    browser: str,
    ip_address: str,
    is_current: bool = True,
):
    """
    Creates a new login session whenever a user logs in.
    """

    session = LoginSession(
        session_identifier=session_identifier,
        user_id=user.id,
        company_id=user.company_id,
        device_name=device_name,
        browser=browser,
        ip_address=ip_address,
        login_time=datetime.utcnow(),
        last_activity=datetime.utcnow(),
        status=SessionStatus.active,
        is_trusted=False,
        is_current=is_current,
    )

    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def update_session_activity(
    db: Session,
    session_identifier: str
):
    """
    Updates the last activity time for an active session.
    """

    session = (
        db.query(LoginSession)
        .filter(
            LoginSession.session_identifier == session_identifier,
            LoginSession.status == SessionStatus.active
        )
        .first()
    )

    if not session:
        return None

    session.last_activity = datetime.utcnow()

    db.commit()
    db.refresh(session)
    return session

def get_user_sessions(
    db: Session,
    user_id: int
):
    """
    Returns all login sessions for the current user.
    """

    return (
        db.query(LoginSession)
        .filter(
            LoginSession.user_id == user_id
        )
        .order_by(LoginSession.login_time.desc())
        .all()
    )
    
def rename_trusted_device(
    db: Session,
    session_id: int,
    user_id: int,
    device_name: str
):
    """
    Rename a trusted device.
    """

    session = (
        db.query(LoginSession)
        .filter(
            LoginSession.id == session_id,
            LoginSession.user_id == user_id,
            LoginSession.is_trusted == True
        )
        .first()
    )

    if not session:
        return None

    session.device_name = device_name

    db.commit()
    db.refresh(session)

    create_audit_log(
        db=db,
        user_name=str(user_id),
        action="Trusted Device Renamed",
        related_user=None,
        company_id=session.company_id,
        browser=session.browser,
        ip_address=session.ip_address,
        details=device_name
    )

    return session

def trust_device(
    db: Session,
    session_id: int,
    user_id: int
):
    """
    Mark a device as trusted.
    """

    session = (
        db.query(LoginSession)
        .filter(
            LoginSession.id == session_id,
            LoginSession.user_id == user_id
        )
        .first()
    )

    if not session:
        return None

    session.is_trusted = True

    db.commit()
    db.refresh(session)

    create_audit_log(
        db=db,
        user_name=str(user_id),
        action="Trusted Device Added",
        related_user=None,
        company_id=session.company_id,
        browser=session.browser,
        ip_address=session.ip_address,
        details=session.device_name,
    )

    return session

def remove_trusted_device(
    db: Session,
    session_id: int,
    user_id: int
):
    """
    Remove trusted device.
    """

    session = (
        db.query(LoginSession)
        .filter(
            LoginSession.id == session_id,
            LoginSession.user_id == user_id
        )
        .first()
    )

    if not session:
        return None

    session.is_trusted = False

    db.commit()
    db.refresh(session)

    create_audit_log(
        db=db,
        user_name=str(user_id),
        action="Trusted Device Removed",
        related_user=None,
        company_id=session.company_id,
        browser=session.browser,
        ip_address=session.ip_address,
        details=session.device_name,
    )

    return session

def logout_session(
    db: Session,
    session_identifier: str,
    user_id: int
):
    """
    Logout a single session belonging to the current user.
    """

    session = (
        db.query(LoginSession)
        .filter(
            LoginSession.session_identifier == session_identifier,
            LoginSession.user_id == user_id
        )
        .first()
    )

    if not session:
        return None

    if session.status != SessionStatus.active:
        return None

    session.status = SessionStatus.logged_out
    session.termination_reason = SessionTerminationReason.user_logout
    session.logged_out_at = datetime.utcnow()
    session.last_activity = datetime.utcnow()

    db.commit()
    db.refresh(session)

    create_audit_log(
        db=db,
        user_name=str(user_id),
        action="User Logout",
        related_user=None,
        company_id=session.company_id,
        browser=session.browser,
        ip_address=session.ip_address,
        details=session.device_name
    )

    return session

def logout_other_sessions(
    db: Session,
    user_id: int,
    current_session_identifier: str
):
    """
    Logout every session except the current one.
    """

    sessions = (
        db.query(LoginSession)
        .filter(
            LoginSession.user_id == user_id,
            LoginSession.status == SessionStatus.active,
            LoginSession.session_identifier != current_session_identifier
        )
        .all()
    )

    count = 0

    for session in sessions:

        session.status = SessionStatus.logged_out
        session.logged_out_at = datetime.utcnow()
        session.last_activity = datetime.utcnow()
        session.termination_reason = SessionTerminationReason.user_logout

        count += 1

    db.commit()
    return count

def get_company_sessions(
    db: Session,
    company_id: int
):
    """
    Returns every login session belonging only
    to the current company.
    Includes user information for admin monitoring.
    """

    sessions = (
        db.query(LoginSession, User)
        .join(User, User.id == LoginSession.user_id)
        .filter(
            User.company_id == company_id
        )
        .order_by(LoginSession.login_time.desc())
        .all()
    )

    result = []

    for session, user in sessions:

        result.append({
            "id": session.id,
            "session_identifier": session.session_identifier,
  
            "user_id": session.user_id,
            "company_id": session.company_id,

            "user_name": user.username,
            "user_email": user.email,

            "device_name": session.device_name,
            "browser": session.browser,
            "ip_address": session.ip_address,

            "login_time": session.login_time,
            "last_activity": session.last_activity,

            "status": session.status,

            "termination_reason": session.termination_reason,

            "is_trusted": session.is_trusted,
            "is_current": session.is_current,

            "logged_out_at": session.logged_out_at,
            "revoked_at": session.revoked_at,
            "expires_at": session.expires_at,
            })

    return result
    
def force_logout_session(
    db: Session,
    session_id: int,
    company_id: int,
    performed_by: str
):
    """
    Admin force logout.
    """

    session = (
        db.query(LoginSession)
        .filter(
            LoginSession.id == session_id,
            LoginSession.company_id == company_id
        )
        .first()
    )

    if not session:
        return None

    if session.status != SessionStatus.active:
        return None

    session.status = SessionStatus.revoked
    session.logged_out_at = datetime.utcnow()
    session.revoked_at = datetime.utcnow()
    session.termination_reason = SessionTerminationReason.force_logout

    db.commit()
    db.refresh(session)

    create_audit_log(
        db=db,
        user_name=performed_by,
        action="Force Logout Initiated",
        related_user=None,
        company_id=company_id,
        browser=session.browser,
        ip_address=session.ip_address,
        details=session.device_name,
        performed_by=performed_by
    )

    return session

def revoke_session(
    db: Session,
    session_id: int,
    company_id: int,
    performed_by: str
):
    """
    Permanently revoke a session.
    """

    session = (
        db.query(LoginSession)
        .filter(
            LoginSession.id == session_id,
            LoginSession.company_id == company_id
        )
        .first()
    )

    if not session:
        return None

    if session.status in (
        SessionStatus.revoked,
        SessionStatus.expired
    ):
        return None

    session.status = SessionStatus.revoked
    session.revoked_at = datetime.utcnow()
    session.termination_reason = SessionTerminationReason.revoked

    db.commit()
    db.refresh(session)

    create_audit_log(
        db=db,
        user_name=performed_by,
        action="Session Revoked",
        related_user=None,
        company_id=company_id,
        browser=session.browser,
        ip_address=session.ip_address,
        details=session.device_name,
        performed_by=performed_by
    )

    return session

def revoke_multiple_sessions(
    db: Session,
    session_ids: list[int],
    company_id: int,
    performed_by: str
):
    """
    Revoke multiple sessions belonging to the current company.
    """

    sessions = (
        db.query(LoginSession)
        .filter(
            LoginSession.id.in_(session_ids),
            LoginSession.company_id == company_id
        )
        .all()
    )

    count = 0

    for session in sessions:

        if session.status in (
            SessionStatus.revoked,
            SessionStatus.expired
        ):
            continue

        session.status = SessionStatus.revoked
        session.revoked_at = datetime.utcnow()
        session.logged_out_at = datetime.utcnow()
        session.termination_reason = SessionTerminationReason.revoked

        create_audit_log(
            db=db,
            user_name=performed_by,
            action="Session Revoked",
            related_user=None,
            company_id=company_id,
            browser=session.browser,
            ip_address=session.ip_address,
            details=session.device_name,
            performed_by=performed_by
        )

        count += 1

    db.commit()
    return count

def expire_inactive_sessions(
    db: Session,
    timeout_minutes: int = 30
):
    """
    Mark inactive sessions as expired.
    """

    expiry_time = datetime.utcnow() - timedelta(minutes=timeout_minutes)

    sessions = (
        db.query(LoginSession)
        .filter(
            LoginSession.status == SessionStatus.active,
            LoginSession.last_activity < expiry_time
        )
        .all()
    )

    for session in sessions:

        session.status = SessionStatus.expired
        session.termination_reason = SessionTerminationReason.session_expired
        session.logged_out_at = datetime.utcnow()

        create_audit_log(
            db=db,
            user_name=str(session.user_id),
            action="Session Expired",
            related_user=None,
            company_id=session.company_id,
            browser=session.browser,
            ip_address=session.ip_address,
            details=session.device_name,
        )

    db.commit()

    return len(sessions)            

#---------------------EMPLOYEE SKILLS & CERTIFICATIONS----------------------
#--------------EMPLOYEE SKILLS MANAGEMENT----------------

def get_employee_skills(
    db: Session,
    employee_id: int,
    company_id: int
):
    """
    Returns all skills for an employee.
    """
    return (
        db.query(models.EmployeeSkill)
        .filter(
            models.EmployeeSkill.employee_id == employee_id,
            models.EmployeeSkill.company_id == company_id
        )
        .order_by(
            models.EmployeeSkill.is_primary.desc(),
            models.EmployeeSkill.skill_name.asc()
        )
        .all()
    )


def get_employee_skill(
    db: Session,
    skill_id: int,
    company_id: int
):
    """
    Returns a single skill.
    """

    return (
        db.query(models.EmployeeSkill)
        .filter(
            models.EmployeeSkill.id == skill_id,
            models.EmployeeSkill.company_id == company_id
        )
        .first()
    )

def create_employee_skill(
    db: Session,
    employee_id: int,
    company_id: int,
    skill_name: str,
    proficiency,
    years_experience: float,
    is_primary: bool,
    performed_by: str
):
    """
    Add a new employee skill.
    """

    employee = db.query(models.Employee).filter(
        models.Employee.id == employee_id,
        models.Employee.company_id == company_id
    ).first()

    if not employee:
        return None

    skill_name = skill_name.strip()

    if not skill_name:
        raise ValueError("Skill name is required.")

    if years_experience < 0:
        raise ValueError("Years of experience cannot be negative.")

    duplicate = (
        db.query(models.EmployeeSkill)
        .filter(
            models.EmployeeSkill.employee_id == employee_id,
            models.EmployeeSkill.company_id == company_id,
            models.EmployeeSkill.skill_name.ilike(skill_name)
        )
        .first()
    )

    if duplicate:
        raise ValueError("Skill already exists.")

    if is_primary:
        db.query(models.EmployeeSkill).filter(
            models.EmployeeSkill.employee_id == employee_id
        ).update(
            {"is_primary": False},
            synchronize_session=False
        )

    skill = models.EmployeeSkill(
        employee_id=employee_id,
        company_id=company_id,
        skill_name=skill_name,
        proficiency=proficiency,
        years_experience=years_experience,
        is_primary=is_primary
    )

    db.add(skill)
    db.commit()
    db.refresh(skill)

    create_audit_log(
        db=db,
        user_name=employee.name,
        action="Skill Added",
        related_user=employee.email,
        company_id=company_id,
        details=skill.skill_name,
        performed_by=performed_by
    )

    return skill

def update_employee_skill(
    db: Session,
    skill_id: int,
    company_id: int,
    skill_name: str,
    proficiency,
    years_experience: float,
    is_primary: bool,
    performed_by: str
):
    """
    Update employee skill.
    """

    skill = get_employee_skill(db,skill_id,company_id)

    if not skill:
        return None

    if years_experience < 0:
        raise ValueError(
            "Years of experience cannot be negative."
        )

    skill_name = skill_name.strip() if skill_name else skill.skill_name

    duplicate = (
        db.query(models.EmployeeSkill)
        .filter(
            models.EmployeeSkill.employee_id == skill.employee_id,
            models.EmployeeSkill.company_id == company_id,
            models.EmployeeSkill.skill_name.ilike(skill_name),
            models.EmployeeSkill.id != skill_id
        )
        .first()
    )

    if duplicate:
        raise ValueError("Duplicate skill.")

    if is_primary:

        db.query(models.EmployeeSkill).filter(
            models.EmployeeSkill.employee_id == skill.employee_id
        ).update(
            {"is_primary": False},
            synchronize_session=False
        )

    skill.skill_name = skill_name
    skill.proficiency = proficiency
    skill.years_experience = years_experience
    skill.is_primary = is_primary

    db.commit()
    db.refresh(skill)

    employee = db.query(models.Employee).filter(
        models.Employee.id == skill.employee_id
    ).first()

    create_audit_log(
        db=db,
        user_name=employee.name,
        action="Skill Updated",
        related_user=employee.email,
        company_id=company_id,
        details=skill.skill_name,
        performed_by=performed_by
    )

    return skill

def delete_employee_skill(
    db: Session,
    skill_id: int,
    company_id: int,
    performed_by: str
):
    """
    Delete employee skill.
    """

    skill = get_employee_skill(db,skill_id,company_id)

    if not skill:
        return None

    employee = db.query(models.Employee).filter(
        models.Employee.id == skill.employee_id
    ).first()

    skill_name = skill.skill_name

    db.delete(skill)
    db.commit()

    create_audit_log(
        db=db,
        user_name=employee.name,
        action="Skill Deleted",
        related_user=employee.email,
        company_id=company_id,
        details=skill_name,
        performed_by=performed_by
    )

    return True

def get_primary_skills(
    db: Session,
    employee_id: int,
    company_id: int
):
    """
    Returns only primary/core skills.
    """

    return (
        db.query(models.EmployeeSkill)
        .filter(
            models.EmployeeSkill.employee_id == employee_id,
            models.EmployeeSkill.company_id == company_id,
            models.EmployeeSkill.is_primary == True
        )
        .all()
    )
    
#-----------------EMPLOYEE CERTIFICATIONS MANAGEMENT-----------------------

def get_employee_certifications(
    db: Session,
    employee_id: int,
    company_id: int
):
    """
    Returns all certifications for an employee.
    """

    return (
        db.query(models.EmployeeCertification)
        .filter(
            models.EmployeeCertification.employee_id == employee_id,
            models.EmployeeCertification.company_id == company_id
        )
        .order_by(
            models.EmployeeCertification.issue_date.desc()
        )
        .all()
    )


def get_employee_certification(
    db: Session,
    certification_id: int,
    company_id: int
):
    """
    Returns a single certification.
    """

    return (
        db.query(models.EmployeeCertification)
        .filter(
            models.EmployeeCertification.id == certification_id,
            models.EmployeeCertification.company_id == company_id
        )
        .first()
    )

def create_employee_certification(
    db: Session,
    employee_id: int,
    company_id: int,
    certification_name: str,
    issuing_organization: str,
    issue_date: date,
    expiry_date: date | None,
    document_path: str | None,
    performed_by: str
):
    """
    Add employee certification.
    """

    employee = (
        db.query(models.Employee)
        .filter(
            models.Employee.id == employee_id,
            models.Employee.company_id == company_id
        )
        .first()
    )

    if not employee:
        return None

    certification_name = certification_name.strip()
    issuing_organization = issuing_organization.strip()

    if not certification_name:
        raise ValueError("Certification name is required.")

    if not issuing_organization:
        raise ValueError("Issuing organization is required.")

    if expiry_date and expiry_date < issue_date:
        raise ValueError(
            "Expiry date cannot be earlier than issue date."
        )

    duplicate = (
        db.query(models.EmployeeCertification)
        .filter(
            models.EmployeeCertification.employee_id == employee_id,
            models.EmployeeCertification.company_id == company_id,
            models.EmployeeCertification.certification_name.ilike(certification_name),
            models.EmployeeCertification.issuing_organization.ilike(
                issuing_organization
            )
        )
        .first()
    )

    if duplicate:
        raise ValueError(
            "Certification already exists."
        )

    certification = models.EmployeeCertification(
        employee_id=employee_id,
        company_id=company_id,
        certification_name=certification_name,
        issuing_organization=issuing_organization,
        issue_date=issue_date,
        expiry_date=expiry_date,
        document_path=document_path
    )

    db.add(certification)
    db.commit()
    db.refresh(certification)

    create_audit_log(
        db=db,
        user_name=employee.name,
        action="Certification Added",
        related_user=employee.email,
        company_id=company_id,
        details=certification_name,
        performed_by=performed_by
    )

    return certification

def update_employee_certification(
    db: Session,
    certification_id: int,
    company_id: int,
    certification_name: str,
    issuing_organization: str,
    issue_date: date,
    expiry_date: date | None,
    document_path: str | None,
    performed_by: str
):
    """
    Update certification.
    """

    certification = get_employee_certification(db,certification_id,company_id)

    if not certification:
        return None

    certification_name = certification_name.strip()
    issuing_organization = issuing_organization.strip()

    if expiry_date and expiry_date < issue_date:
        raise ValueError(
            "Expiry date cannot be earlier than issue date."
        )

    duplicate = (
        db.query(models.EmployeeCertification)
        .filter(
            models.EmployeeCertification.employee_id == certification.employee_id,
            models.EmployeeCertification.company_id == company_id,
            models.EmployeeCertification.certification_name.ilike(certification_name),
            models.EmployeeCertification.issuing_organization.ilike(
                issuing_organization
            ),
            models.EmployeeCertification.id != certification_id
        )
        .first()
    )

    if duplicate:
        raise ValueError(
            "Duplicate certification."
        )

    certification.certification_name = certification_name
    certification.issuing_organization = issuing_organization
    certification.issue_date = issue_date
    certification.expiry_date = expiry_date

    if document_path is not None:
        certification.document_path = document_path

    db.commit()
    db.refresh(certification)

    employee = (
        db.query(models.Employee)
        .filter(
            models.Employee.id == certification.employee_id
        )
        .first()
    )

    create_audit_log(
        db=db,
        user_name=employee.name,
        action="Certification Updated",
        related_user=employee.email,
        company_id=company_id,
        details=certification_name,
        performed_by=performed_by
    )

    return certification

def delete_employee_certification(
    db: Session,
    certification_id: int,
    company_id: int,
    performed_by: str
):
    """
    Delete certification.
    """

    certification = get_employee_certification(db,certification_id,company_id)

    if not certification:
        return None

    employee = (
        db.query(models.Employee)
        .filter(
            models.Employee.id == certification.employee_id
        )
        .first()
    )

    cert_name = certification.certification_name

    db.delete(certification)
    db.commit()

    create_audit_log(
        db=db,
        user_name=employee.name,
        action="Certification Deleted",
        related_user=employee.email,
        company_id=company_id,
        details=cert_name,
        performed_by=performed_by
    )

    return True

#------------------CERTIFICATION STATUS HELPERS------------------

def get_active_certifications(
    db: Session,
    employee_id: int,
    company_id: int
):
    """
    Returns active certifications.
    """

    today = date.today()

    return (
        db.query(models.EmployeeCertification)
        .filter(
            models.EmployeeCertification.employee_id == employee_id,
            models.EmployeeCertification.company_id == company_id,
            (
                (models.EmployeeCertification.expiry_date == None)
                |
                (models.EmployeeCertification.expiry_date >= today)
            )
        )
        .all()
    )

def get_expired_certifications(
    db: Session,
    employee_id: int,
    company_id: int
):
    """
    Returns expired certifications.
    """
    today = date.today()

    return (
        db.query(models.EmployeeCertification)
        .filter(
            models.EmployeeCertification.employee_id == employee_id,
            models.EmployeeCertification.company_id == company_id,
            models.EmployeeCertification.expiry_date != None,
            models.EmployeeCertification.expiry_date < today
        )
        .all()
    )

def get_expiring_certifications(
    db: Session,
    company_id: int,
    days: int = 30
):
    """
    Returns certifications expiring within X days.
    """

    today = date.today()
    target = today + timedelta(days=days)

    return (
        db.query(models.EmployeeCertification)
        .filter(
            models.EmployeeCertification.company_id == company_id,
            models.EmployeeCertification.expiry_date != None,
            models.EmployeeCertification.expiry_date >= today,
            models.EmployeeCertification.expiry_date <= target
        )
        .all()
    )

def mark_expired_certifications(
    db: Session,
    company_id: int,
    performed_by="System"
):
    """
    Audit expired certifications.
    Intended for scheduled jobs.
    """

    today = date.today()

    certifications = (
        db.query(models.EmployeeCertification)
        .filter(
            models.EmployeeCertification.company_id == company_id,
            models.EmployeeCertification.expiry_date != None,
            models.EmployeeCertification.expiry_date < today
        )
        .all()
    )

    for cert in certifications:

        employee = (
            db.query(models.Employee)
            .filter(
                models.Employee.id == cert.employee_id
            )
            .first()
        )

        create_audit_log(
            db=db,
            user_name=employee.name,
            action="Certification Expired",
            related_user=employee.email,
            company_id=company_id,
            details=cert.certification_name,
            performed_by=performed_by
        )

    return len(certifications)    

#-----------------ADMIN SKILL / CERTIFICATION SEARCH-----------------------

def search_employees_by_skill(
    db: Session,
    company_id: int,
    skill_name: str
):
    """
    Search employees by skill.
    """

    return (
        db.query(models.Employee)
        .join(
            models.EmployeeSkill,
            models.Employee.id == models.EmployeeSkill.employee_id
        )
        .filter(
            models.Employee.company_id == company_id,
            models.EmployeeSkill.skill_name.ilike(f"%{skill_name}%")
        )
        .distinct()
        .all()
    )

def filter_employee_competencies(
    db: Session,
    company_id: int,
    skill: str | None = None,
    skill_level=None,
    min_years_experience: float | None = None,
    certification_name: str |None = None,
    certification_status: str | None = None,
):

    query = db.query(models.Employee).filter(
        models.Employee.company_id == company_id
    )

    if skill or skill_level or min_years_experience is not None:
        query = query.join(
            models.EmployeeSkill,
            models.Employee.id == models.EmployeeSkill.employee_id,
            isouter=True
        )

    if certification_name or certification_status:
        query = query.join(
            models.EmployeeCertification,
            models.Employee.id == models.EmployeeCertification.employee_id,
            isouter=True
        )

    if skill:
        query = query.filter(
            models.EmployeeSkill.skill_name.ilike(f"%{skill}%")
        )

    if skill_level:
        query = query.filter(
            models.EmployeeSkill.proficiency == skill_level
        )

    if min_years_experience is not None:
        query = query.filter(
            models.EmployeeSkill.years_experience >= min_years_experience
        )

    if certification_name:
        query = query.filter(
            models.EmployeeCertification.certification_name.ilike(
                f"%{certification_name}%"
            )
        )

    today = date.today()

    if certification_status == "Valid":
        query = query.filter(
            (models.EmployeeCertification.expiry_date == None) |
            (models.EmployeeCertification.expiry_date >= today)
        )

    elif certification_status == "Expired":
        query = query.filter(
            models.EmployeeCertification.expiry_date < today
        )

    elif certification_status == "Expiring Soon":
        limit = today + timedelta(days=30)

        query = query.filter(
            models.EmployeeCertification.expiry_date >= today,
            models.EmployeeCertification.expiry_date <= limit
        )

    employees = query.distinct().all()

    result = []

    for employee in employees:

        skills = employee.skills or []
        certifications = employee.certifications or []

        active_certifications = 0

        for cert in certifications:
            if cert.expiry_date is None or cert.expiry_date >= today:
                active_certifications += 1

        result.append({

            "employee": {
                "id": employee.id,
                "name": employee.name,
                "email": employee.email,
                "department_name":
                    employee.department_rel.name
                    if employee.department_rel else "-"
            },

            "summary": {
                "total_skills": len(skills),
                "active_certifications": active_certifications
            },

            "skills": [
                {
                    "id": s.id,
                    "skill_name": s.skill_name,
                    "proficiency":
                        s.proficiency.value
                        if hasattr(s.proficiency, "value")
                        else s.proficiency,
                    "years_experience": s.years_experience
                }
                for s in skills
            ],

            "certifications": [
                {
                    "id": c.id,
                    "certification_name": c.certification_name,
                    "issuing_organization": c.issuing_organization,
                    "expiry_date": c.expiry_date
                }
                for c in certifications
            ]

        })

    return result

#-------------------EMPLOYEE DASHBOARD SUMMARY-----------------

def get_employee_skill_summary(
    db: Session,
    employee_id: int,
    company_id: int
):
    """
    Dashboard statistics.
    """

    total_skills = (
        db.query(models.EmployeeSkill)
        .filter(
            models.EmployeeSkill.employee_id == employee_id,
            models.EmployeeSkill.company_id == company_id
        )
        .count()
    )

    primary_skills = (
        db.query(models.EmployeeSkill)
        .filter(
            models.EmployeeSkill.employee_id == employee_id,
            models.EmployeeSkill.company_id == company_id,
            models.EmployeeSkill.is_primary == True
        )
        .count()
    )

    today = date.today()

    active_certifications = (
        db.query(models.EmployeeCertification)
        .filter(
            models.EmployeeCertification.employee_id == employee_id,
            models.EmployeeCertification.company_id == company_id,
            (
                (models.EmployeeCertification.expiry_date == None)
                |
                (models.EmployeeCertification.expiry_date >= today)
            )
        )
        .count()
    )

    expired_certifications = (
        db.query(models.EmployeeCertification)
        .filter(
            models.EmployeeCertification.employee_id == employee_id,
            models.EmployeeCertification.company_id == company_id,
            models.EmployeeCertification.expiry_date != None,
            models.EmployeeCertification.expiry_date < today
        )
        .count()
    )

    profile = get_employee_profile_completion(db, employee_id, company_id)

    return {

        "total_skills": total_skills,
        "primary_skills": primary_skills,
        "active_certifications": active_certifications,
        "expired_certifications": expired_certifications,
        "profile_completion":
            profile["completion_percentage"]
            if profile
            else 0
    }
    
#---------------------EMPLOYEE COMPETENCY PROFILE------------------

def get_employee_competency_profile(
    db: Session,
    employee_id: int,
    company_id: int
):
    """
    Complete competency profile.
    """

    employee = (
        db.query(models.Employee)
        .filter(
            models.Employee.id == employee_id,
            models.Employee.company_id == company_id
        )
        .first()
    )

    if not employee:
        return None

    return {

        "employee": employee,
        "skills": get_employee_skills(db,employee_id,company_id),
        "certifications":
            get_employee_certifications(db,employee_id,company_id),
        "summary":
            get_employee_skill_summary(db,employee_id,company_id)
    }    
    
#----------------------EXPORT COMPETENCY REPORT------------------------

def get_competency_export(
    db: Session,
    company_id: int
):
    """
    Export employee competency report.
    """

    employees = (
        db.query(models.Employee)
        .filter(
            models.Employee.company_id == company_id
        )
        .all()
    )

    report = []

    for emp in employees:

        skills = get_employee_skills(db,emp.id,company_id)
        certifications = get_employee_certifications(db,emp.id,company_id)

        report.append({

            "employee_id": emp.id,
            "employee_name": emp.name,
            "email": emp.email,
            "department": (
                emp.department_rel.name
                if emp.department_rel
                else None
            ),

            "skills": [
                {
                    "skill": s.skill_name,
                    "level": s.proficiency,
                    "experience": s.years_experience,
                    "primary": s.is_primary
                }
                for s in skills
            ],

            "certifications": [
                {
                    "name": c.certification_name,
                    "organization": c.issuing_organization,
                    "issue_date": c.issue_date,
                    "expiry_date": c.expiry_date
                }
                for c in certifications
            ]
        })

    return report    