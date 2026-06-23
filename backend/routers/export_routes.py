from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
import csv
import io
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import models
import database
from auth import get_current_user
from models import (Employee, Attendance, LeaveRequest,
    Notification, AuditLog, ExportHistory)

router = APIRouter( prefix="/exports", tags=["Data Export Center"])

# AUTHORIZATION

def admin_only(current_user: dict):

    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only Admin can access Data Export Center."
        )

    if not current_user.get("company_id"):
        raise HTTPException(
            status_code=401,
            detail="Company not found."
        )

    return current_user["company_id"]

#-------------- EXPORT HISTORY--------------

def log_export(db: Session, current_user: dict, data_type: str, export_format: str,):

    history = ExportHistory(
        exported_by=current_user["email"],
        data_type=data_type,
        export_format=export_format,
        company_id=current_user["company_id"]
    )

    db.add(history)
    db.commit()

#----------- CSV----------------

def csv_stream(headers, rows):
    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)

    output = io.BytesIO()
    output.write(stream.getvalue().encode())
    output.seek(0)

    return output

#-------------- EXCEL---------------

def excel_stream(title, headers, rows):
    wb = Workbook()
    ws = wb.active
    ws.title = title
    ws.append(headers)

    for row in rows:
        ws.append(row)

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)

    return stream

#------------ PDF-----------------

def pdf_stream(title, headers, rows):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(220, 760, title)
    y = 720
    pdf.setFont("Helvetica-Bold", 11)
    x_positions = [40, 130, 250, 380, 500]

    for i, h in enumerate(headers):
        if i < len(x_positions):
            pdf.drawString(x_positions[i], y, str(h))

    y -= 20
    pdf.setFont("Helvetica", 10)

    for row in rows:

        if y < 60:
            pdf.showPage()
            y = 760

        for i, value in enumerate(row):

            if i < len(x_positions):
                pdf.drawString(
                    x_positions[i],
                    y,
                    str(value)
                )

        y -= 18

    pdf.save()
    buffer.seek(0)

    return buffer

#--------------- EMPLOYEES CSV----------------

@router.get("/employees/csv")
def export_employees_csv(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(get_current_user)
):
    company_id = admin_only(current_user)
    employees = (
        db.query(Employee)
        .filter(Employee.company_id == company_id)
        .all()
    )

    rows = []
    for emp in employees:
        department = ""

        if emp.department_rel:
            department = emp.department_rel.name

        rows.append([
            emp.id,
            emp.name,
            emp.email,
            emp.role,
            department,
            emp.status.value,
            emp.joined_date.strftime("%Y-%m-%d")
        ])

    headers = [
        "ID",
        "Name",
        "Email",
        "Role",
        "Department",
        "Status",
        "Joined Date"
    ]

    file = csv_stream(headers, rows)
    log_export(db, current_user, "Employees", "CSV")

    return StreamingResponse(
        file,
        media_type="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=employees.csv"
        }
    )
    
#-------------- EMPLOYEES EXCEL -------------------

@router.get("/employees/excel")
def export_employees_excel(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(get_current_user)
):
    company_id = admin_only(current_user)
    employees = (
        db.query(Employee)
        .filter(Employee.company_id == company_id)
        .all()
    )
    rows = []
    for emp in employees:
        department = ""

        if emp.department_rel:
            department = emp.department_rel.name

        rows.append([
            emp.id,
            emp.name,
            emp.email,
            emp.role,
            department,
            emp.status.value,
            emp.joined_date.strftime("%Y-%m-%d")
        ])

    headers = [
        "ID",
        "Name",
        "Email",
        "Role",
        "Department",
        "Status",
        "Joined Date"
    ]

    file = excel_stream( "Employees", headers, rows)

    log_export(db, current_user, "Employees", "Excel")

    return StreamingResponse(
        file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition":
            "attachment; filename=employees.xlsx"
        }
    )

#----------------- EMPLOYEES PDF----------------

@router.get("/employees/pdf")
def export_employees_pdf(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(get_current_user)
):
    company_id = admin_only(current_user)
    employees = (
        db.query(Employee)
        .filter(Employee.company_id == company_id)
        .all()
    )

    rows = []
    for emp in employees:
        department = ""

        if emp.department_rel:
            department = emp.department_rel.name

        rows.append([emp.id, emp.name, emp.email, emp.role, department])

    headers = ["ID", "Name", "Email", "Role", "Department"]

    file = pdf_stream( "Employees Report", headers, rows)
    log_export( db, current_user, "Employees", "PDF")

    return StreamingResponse(
        file,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            "attachment; filename=employees.pdf"
        }
    )

#----------------- ATTENDANCE CSV----------------------

@router.get("/attendance/csv")
def export_attendance_csv(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(get_current_user)
):
    company_id = admin_only(current_user)
    attendance = (
        db.query(Attendance)
        .filter(
            Attendance.company_id == company_id
        )
        .order_by(Attendance.date.desc())
        .all()
    )

    rows = []
    for record in attendance:

        rows.append([
            record.id,
            record.employee_id,
            record.date.strftime("%Y-%m-%d"),
            record.status,
            record.check_in.strftime("%H:%M") if record.check_in else "",
            record.check_out.strftime("%H:%M") if record.check_out else "",
            record.working_hours or ""
        ])

    headers = ["ID","Employee ID","Date","Status","Check In","Check Out","Working Hours"]
    file = csv_stream( headers, rows )
    log_export( db, current_user, "Attendance", "CSV")

    return StreamingResponse(
        file,
        media_type="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=attendance.csv"
        }
    )    
    
#----------------- ATTENDANCE EXCEL------------------

@router.get("/attendance/excel")
def export_attendance_excel(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(get_current_user)
):

    company_id = admin_only(current_user)
    attendance = (
        db.query(Attendance)
        .filter(Attendance.company_id == company_id)
        .order_by(Attendance.date.desc())
        .all()
    )

    rows = []

    for record in attendance:
        rows.append([
            record.id,
            record.employee_id,
            record.date.strftime("%Y-%m-%d"),
            record.status,
            record.check_in.strftime("%H:%M") if record.check_in else "",
            record.check_out.strftime("%H:%M") if record.check_out else "",
            record.working_hours or ""
        ])

    headers = [
        "ID",
        "Employee ID",
        "Date",
        "Status",
        "Check In",
        "Check Out",
        "Working Hours"
    ]

    file = excel_stream( "Attendance", headers, rows)
    log_export( db, current_user, "Attendance", "Excel")

    return StreamingResponse(
        file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition":
            "attachment; filename=attendance.xlsx"
        }
    )

#------------------ ATTENDANCE PDF----------------------

@router.get("/attendance/pdf")
def export_attendance_pdf(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(get_current_user)
):

    company_id = admin_only(current_user)
    attendance = (
        db.query(Attendance)
        .filter(Attendance.company_id == company_id)
        .order_by(Attendance.date.desc())
        .all()
    )

    rows = []

    for record in attendance:
        rows.append([
            record.employee_id,
            record.date.strftime("%Y-%m-%d"),
            record.status,
            record.working_hours or ""
        ])

    headers = [ "Employee", "Date", "Status", "Hours"]
    file = pdf_stream( "Attendance Report", headers, rows)
    log_export( db, current_user, "Attendance", "PDF")

    return StreamingResponse(
        file,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            "attachment; filename=attendance.pdf"
        }
    )

#---------------------- LEAVE REQUESTS CSV--------------------

@router.get("/leave/csv")
def export_leave_csv(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(get_current_user)
):

    company_id = admin_only(current_user)
    leaves = (
        db.query(LeaveRequest)
        .filter(LeaveRequest.company_id == company_id)
        .order_by(LeaveRequest.created_at.desc())
        .all()
    )

    rows = []
    for leave in leaves:

        rows.append([
            leave.id,
            leave.user_id,
            leave.leave_type.value,
            leave.start_date.strftime("%Y-%m-%d"),
            leave.end_date.strftime("%Y-%m-%d"),
            leave.status.value,
            leave.reason
        ])

    headers = [
        "ID",
        "User",
        "Leave Type",
        "Start Date",
        "End Date",
        "Status",
        "Reason"
    ]

    file = csv_stream( headers, rows)
    log_export( db, current_user, "Leave Requests", "CSV")

    return StreamingResponse(
        file,
        media_type="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=leave_requests.csv"
        }
    )    
    
#--------------------- LEAVE REQUESTS EXCEL--------------------------

@router.get("/leave/excel")
def export_leave_excel(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(get_current_user)
):

    company_id = admin_only(current_user)
    leaves = (
        db.query(LeaveRequest)
        .filter(
            LeaveRequest.company_id == company_id
        )
        .order_by(
            LeaveRequest.created_at.desc()
        )
        .all()
    )

    rows = []
    for leave in leaves:

        rows.append([
            leave.id,
            leave.user_id,
            leave.leave_type.value,
            leave.start_date.strftime("%Y-%m-%d"),
            leave.end_date.strftime("%Y-%m-%d"),
            leave.status.value,
            leave.reason
        ])

    headers = ["ID","User","Leave Type","Start Date","End Date","Status","Reason"]

    file = excel_stream( "Leave Requests", headers, rows)
    log_export( db, current_user, "Leave Requests", "Excel")

    return StreamingResponse(
        file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition":
            "attachment; filename=leave_requests.xlsx"
        }
    )

# -----------------------LEAVE REQUESTS PDF-----------------------

@router.get("/leave/pdf")
def export_leave_pdf(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(get_current_user)
):
    company_id = admin_only(current_user)
    leaves = (
        db.query(LeaveRequest)
        .filter(
            LeaveRequest.company_id == company_id
        )
        .order_by(
            LeaveRequest.created_at.desc()
        )
        .all()
    )
    rows = []
    for leave in leaves:

        rows.append([
            leave.user_id,
            leave.leave_type.value,
            leave.start_date.strftime("%Y-%m-%d"),
            leave.end_date.strftime("%Y-%m-%d"),
            leave.status.value
        ])

    headers = [ "User", "Type", "Start", "End", "Status"]
    file = pdf_stream( "Leave Requests", headers, rows)
    log_export( db, current_user, "Leave Requests", "PDF")

    return StreamingResponse(
        file,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            "attachment; filename=leave_requests.pdf"
        }
    )

#-------------------- AUDIT LOGS CSV-------------------------

@router.get("/audit/csv")
def export_audit_csv(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(get_current_user)
):

    company_id = admin_only(current_user)
    logs = (
        db.query(AuditLog)
        .filter(
            AuditLog.company_id == company_id
        )
        .order_by(
            AuditLog.timestamp.desc()
        )
        .all()
    )
    rows = []

    for log in logs:

        rows.append([
            log.id,
            log.user_name,
            log.action,
            log.related_user or "",
            log.timestamp.strftime("%Y-%m-%d %H:%M"),
            log.performed_by or "",
            log.browser or "",
            log.ip_address or ""
        ])

    headers = [
        "ID",
        "User",
        "Action",
        "Related User",
        "Timestamp",
        "Performed By",
        "Browser",
        "IP Address"
    ]

    file = csv_stream( headers, rows)
    log_export( db, current_user, "Audit Logs", "CSV")
    return StreamingResponse(
        file,
        media_type="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=audit_logs.csv"
        }
    )    
    
#------------------- AUDIT LOGS EXCEL--------------------

@router.get("/audit/excel")
def export_audit_excel(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(get_current_user)
):

    company_id = admin_only(current_user)
    logs = (
        db.query(AuditLog)
        .filter(AuditLog.company_id == company_id)
        .order_by(AuditLog.timestamp.desc())
        .all()
    )

    rows = []

    for log in logs:

        rows.append([
            log.id,
            log.user_name,
            log.action,
            log.related_user or "",
            log.timestamp.strftime("%Y-%m-%d %H:%M"),
            log.performed_by or "",
            log.browser or "",
            log.ip_address or "",
            log.details or ""
        ])

    headers = [
        "ID",
        "User",
        "Action",
        "Related User",
        "Timestamp",
        "Performed By",
        "Browser",
        "IP Address",
        "Details"
    ]

    file = excel_stream( "Audit Logs", headers, rows)
    log_export( db,current_user, "Audit Logs", "Excel")

    return StreamingResponse(
        file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition":
            "attachment; filename=audit_logs.xlsx"
        }
    )

#------------------ AUDIT LOGS PDF-------------------

@router.get("/audit/pdf")
def export_audit_pdf(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(get_current_user)
):

    company_id = admin_only(current_user)

    logs = (
        db.query(AuditLog)
        .filter(AuditLog.company_id == company_id)
        .order_by(AuditLog.timestamp.desc())
        .all()
    )

    rows = []

    for log in logs:

        rows.append([
            log.user_name,
            log.action,
            log.timestamp.strftime("%Y-%m-%d"),
            log.browser or ""
        ])

    headers = [ "User", "Action", "Date", "Browser"]
    file = pdf_stream( "Audit Logs Report", headers, rows)
    log_export( db, current_user, "Audit Logs", "PDF")

    return StreamingResponse(
        file,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            "attachment; filename=audit_logs.pdf"
        }
    )

# --------------------NOTIFICATIONS CSV----------------------------

@router.get("/notifications/csv")
def export_notifications_csv(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(get_current_user)
):

    company_id = admin_only(current_user)
    notifications = (
        db.query(Notification)
        .filter(Notification.company_id == company_id)
        .order_by(Notification.created_at.desc())
        .all()
    )

    rows = []

    for notification in notifications:

        rows.append([
            notification.id,
            notification.recipient_email,
            notification.message,
            "Read" if notification.is_read else "Unread",
            notification.created_at.strftime("%Y-%m-%d %H:%M")
        ])

    headers = [ "ID", "Recipient", "Message", "Status", "Created At"]

    file = csv_stream( headers, rows)
    log_export( db, current_user, "Notifications", "CSV")

    return StreamingResponse(
        file,
        media_type="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=notifications.csv"
        }
    )    
    
# ---------------NOTIFICATIONS EXCEL---------------------

@router.get("/notifications/excel")
def export_notifications_excel(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(get_current_user)
):

    company_id = admin_only(current_user)
    notifications = (
        db.query(Notification)
        .filter(Notification.company_id == company_id)
        .order_by(Notification.created_at.desc())
        .all()
    )

    rows = []

    for n in notifications:
        rows.append([
            n.id,
            n.recipient_email,
            n.message,
            "Read" if n.is_read else "Unread",
            n.created_at.strftime("%Y-%m-%d %H:%M")
        ])

    headers = [ "ID", "Recipient", "Message", "Status", "Created At"]
    file = excel_stream("Notifications",headers,rows)
    log_export( db, current_user, "Notifications", "Excel")

    return StreamingResponse(
        file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition":
            "attachment; filename=notifications.xlsx"
        }
    )

# --------------------NOTIFICATIONS PDF-----------------------

@router.get("/notifications/pdf")
def export_notifications_pdf(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(get_current_user)
):

    company_id = admin_only(current_user)
    notifications = (
        db.query(Notification)
        .filter(Notification.company_id == company_id)
        .order_by(Notification.created_at.desc())
        .all()
    )

    rows = []

    for n in notifications:
        rows.append([
            n.recipient_email,
            n.message[:40],
            "Read" if n.is_read else "Unread"
        ])

    headers = [ "Recipient", "Message", "Status" ]

    file = pdf_stream( "Notifications Report", headers, rows )

    log_export( db, current_user, "Notifications", "PDF")

    return StreamingResponse(
        file,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            "attachment; filename=notifications.pdf"
        }
    )

#---------------- ANALYTICS PDF---------------------


@router.get("/analytics/pdf")
def export_analytics_pdf(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(get_current_user)
):

    company_id = admin_only(current_user)

    total_employees = (
        db.query(Employee)
        .filter(Employee.company_id == company_id)
        .count()
    )

    active = (
        db.query(Employee)
        .filter(
            Employee.company_id == company_id,
            Employee.status == models.StatusEnum.active
        )
        .count()
    )

    inactive = (
        db.query(Employee)
        .filter(
            Employee.company_id == company_id,
            Employee.status == models.StatusEnum.inactive
        )
        .count()
    )

    onleave = (
        db.query(Employee)
        .filter(
            Employee.company_id == company_id,
            Employee.status == models.StatusEnum.onleave
        )
        .count()
    )

    departments = (
        db.query(func.count(models.Department.id))
        .filter(models.Department.company_id == company_id)
        .scalar()
    )

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(170, 760, "Company Analytics Report")

    pdf.setFont("Helvetica", 12)
    y = 700

    pdf.drawString(80, y, f"Total Employees : {total_employees}")
    y -= 30

    pdf.drawString(80, y, f"Active Employees : {active}")
    y -= 30

    pdf.drawString(80, y, f"Inactive Employees : {inactive}")
    y -= 30

    pdf.drawString(80, y, f"Employees On Leave : {onleave}")
    y -= 30

    pdf.drawString(80, y, f"Departments : {departments}")
    pdf.save()
    buffer.seek(0)

    log_export(db, current_user, "Analytics", "PDF")

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            "attachment; filename=analytics.pdf"
        }
    )

#------------------- EXPORT HISTORY--------------------

@router.get("/history")
def export_history(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(get_current_user)
):

    company_id = admin_only(current_user)
    history = (
        db.query(ExportHistory)
        .filter(
            ExportHistory.company_id == company_id
        )
        .order_by(
            ExportHistory.exported_at.desc()
        )
        .all()
    )

    return [
        {
            "id": h.id,
            "exported_by": h.exported_by,
            "data_type": h.data_type,
            "export_format": h.export_format,
            "exported_at": h.exported_at,
            "company_id": h.company_id
        }
        for h in history
    ]