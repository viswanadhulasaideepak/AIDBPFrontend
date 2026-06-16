from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io
from datetime import datetime
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from auth import get_current_user
from database import get_db
import crud,models
from models import AuditLog

router = APIRouter(prefix="/attendance", tags=["Attendance"])

# ---------------- GET ATTENDANCE ----------------
@router.get("/access-status")
def attendance_access_status(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    print("Current User:", current_user)

    request = crud.get_attendance_access_request(
        db,
        current_user["id"]
    )

    print("Request Before:", request)

    if request is None:
        print("Creating Request...")
        request = crud.create_attendance_access_request(
            db=db,
            user_id=current_user["id"],
            admin_email=current_user["email"],
            company_id=current_user["company_id"]
        )

        print("Request After Create:", request)

    print("Final Request:", request)

    if request is None:
        return {"error": "REQUEST IS NONE"}

    return {
        "status": request.status.value,
        "submitted_on": request.created_at
    }
# ---------------- ADD ATTENDANCE ----------------
@router.post("/")
def add_attendance(
    status: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
    ):
    
    if not current_user.get("company_id"):
        raise HTTPException(status_code=401, detail="Company not found in token")
    
    if not crud.is_attendance_access_approved(
        db,
        current_user["id"]
        ):
        raise HTTPException(
        status_code=403,
        detail="Attendance access pending approval."
    )

    record = crud.create_attendance(
        db=db,
        employee_email=current_user["email"],
        date=datetime.utcnow(),
        status=status.lower(),  # normalize status
        company_id=current_user["company_id"]
    )
    
    return {
        "id": record.id,
        "employee_id": record.employee_id,
        "date": record.date.strftime("%Y-%m-%d"),
        "status": record.status,
        "company_id": record.company_id
    }
    
@router.get("/access-requests")
def get_pending_requests(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admin can view attendance requests."
        )

    requests = crud.get_pending_attendance_access_requests(
        db,
        current_user["company_id"]
    )

    return requests    
# ---------------- APPROVE / REJECT ATTENDANCE ACCESS ----------------
@router.put("/access-request/{request_id}")
def update_attendance_access(
    request_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admin can approve attendance requests."
        )

    if status not in ["approved", "rejected"]:
        raise HTTPException(
            status_code=400,
            detail="Status must be approved or rejected."
        )

    request = crud.update_attendance_access_request(
        db=db,
        request_id=request_id,
        status=status,
        company_id=current_user["company_id"],
        approved_by=current_user["email"]
    )

    if request is None:
        raise HTTPException(
            status_code=404,
            detail="Attendance request not found."
        )

    return {
        "message": f"Attendance request {status}.",
        "request": request
    }        
    
# ---------------- CHECK IN ----------------
@router.post("/check-in")
def check_in(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if not crud.is_attendance_access_approved(
        db,
        current_user["id"]
    ):
        raise HTTPException(
            status_code=403,
            detail="Attendance access pending approval."
        )
        
    print("Looking for employee...")
    print("Email:", current_user["email"])
    print("Company:", current_user["company_id"])    
    
    employee = db.query(models.Employee).filter(
        models.Employee.email == current_user["email"],
        models.Employee.company_id == current_user["company_id"]
        ).first()
    
    print("Employee Found:", employee)
    
    if employee is None:
        raise HTTPException(
        status_code=404,
        detail="Employee profile not found."
    )
    
    print("========== CHECK IN ==========")
    print("Current User:", current_user)
    print("Employee:", employee)
    print("Approved:", crud.is_attendance_access_approved(
    db,
    current_user["id"]
    ))    
        
    attendance = crud.check_in(
    db=db,
    employee_id=employee.id,
    company_id=current_user["company_id"]
    )
    
    if attendance is None:
        raise HTTPException(
        status_code=400,
        detail="Already checked in."
    )

    return {
    "id": attendance.id,
    "check_in": attendance.check_in,
    "check_out": attendance.check_out,
    "working_hours": attendance.working_hours
    }
# ---------------- CHECK OUT ----------------
@router.post("/check-out")
def check_out(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if not crud.is_attendance_access_approved(
        db,
        current_user["id"]
    ):
        raise HTTPException(
            status_code=403,
            detail="Attendance access pending approval."
        )

    employee = db.query(models.Employee).filter(
        models.Employee.email == current_user["email"],
        models.Employee.company_id == current_user["company_id"]
        ).first()
    
    if employee is None:
        raise HTTPException(
        status_code=404,
        detail="Employee profile not found."
    )
    
    attendance = crud.check_out(
    db=db,
    employee_id=employee.id,
    company_id=current_user["company_id"]
    )
    
    if attendance is None:
        raise HTTPException(
        status_code=400,
        detail="Please Check In."
    )

    return attendance

# ---------------- TODAY ----------------
@router.get("/today")
def today(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if not crud.is_attendance_access_approved(
        db,
        current_user["id"]
    ):
        raise HTTPException(
            status_code=403,
            detail="Attendance access pending approval."
        )

    employee = db.query(models.Employee).filter(
        models.Employee.email == current_user["email"],
        models.Employee.company_id == current_user["company_id"]
        ).first()
    
    if employee is None:
        raise HTTPException(
        status_code=404,
        detail="Employee profile not found."
    )

    attendance = crud.get_today_attendance(
        db=db,
        employee_id=employee.id,
        company_id=current_user["company_id"]
        )

    if attendance is None:
        return {
            "check_in": None,
            "check_out": None,
            "working_hours": None
        }

    return attendance

# ---------------- HISTORY ----------------

@router.get("/history")
def history(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if not crud.is_attendance_access_approved(
        db,
        current_user["id"]
    ):
        raise HTTPException(
            status_code=403,
            detail="Attendance access pending approval."
        )

    employee = db.query(models.Employee).filter(
        models.Employee.email == current_user["email"],
        models.Employee.company_id == current_user["company_id"]
        ).first()
    
    if employee is None:
        raise HTTPException(
        status_code=404,
        detail="Employee profile not found."
    )

    return crud.get_recent_attendance(
        db=db,
        employee_id=employee.id,
        company_id=current_user["company_id"]
        )
    
# ---------------- REPORT (JSON for Analytics) ----------------

@router.get("/report")
def get_attendance_report(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if not current_user.get("company_id"):
        raise HTTPException(status_code=401, detail="Company not found in token")
    
    if current_user["role"] != "admin":
        if not crud.is_attendance_access_approved(
            db,
            current_user["id"]
            ):
            raise HTTPException(
            status_code=403,
            detail="Attendance access pending approval."
        )

    records = crud.get_attendance(db, current_user["company_id"])

    report = {}
    for rec in records:
        date_str = rec.date.strftime("%Y-%m-%d")
        if date_str not in report:
            report[date_str] = {"present": 0, "leave": 0, "absent": 0}
        status = rec.status.lower()
        if status in report[date_str]:
            report[date_str][status] += 1

    dates = sorted(report.keys())

    return {
        "dates": dates,
        "present": [report[d]["present"] for d in dates],
        "leave": [report[d]["leave"] for d in dates],
        "absent": [report[d]["absent"] for d in dates],
    }

# ---------------- REPORT (EXCEL) ----------------

@router.get("/report/excel")
def get_attendance_report_excel(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not crud.is_attendance_access_approved(
    db,
    current_user["id"]
    ):
        raise HTTPException(
        status_code=403,
        detail="Attendance access pending approval."
    )

    records = crud.get_attendance(db, current_user["company_id"])
    records = sorted(records, key=lambda r: r.date)

    wb = Workbook()
    ws = wb.active
    ws.title = "Attendance Report"
    ws.append(["Date", "Employee ID", "Status"])

    for rec in records:
        ws.append([rec.date.strftime("%Y-%m-%d"), rec.employee_id, rec.status])

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)

    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=attendance_report.xlsx"}
    )

# ---------------- REPORT (PDF) ----------------

@router.get("/report/pdf")
def get_attendance_report_pdf(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not crud.is_attendance_access_approved(
    db,
    current_user["id"]
    ):
        raise HTTPException(
        status_code=403,
        detail="Attendance access pending approval."
    )

    records = crud.get_attendance(db, current_user["company_id"])
    records = sorted(records, key=lambda r: r.date)

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(200, 750, "Attendance Report")

    c.setFont("Helvetica", 12)
    y = 700
    c.drawString(50, y, "Date")
    c.drawString(150, y, "Employee ID")
    c.drawString(300, y, "Status")

    y -= 20
    for rec in records:
        c.drawString(50, y, rec.date.strftime("%Y-%m-%d"))
        c.drawString(150, y, str(rec.employee_id))
        c.drawString(300, y, rec.status)
        y -= 20

    c.save()
    buffer.seek(0)

    # Audit log
    audit = AuditLog(
        user_name=current_user["email"],
        action="Attendance Report Exported (PDF)",
        related_user=None,
        company_id=current_user["company_id"]
    )
    db.add(audit)
    db.commit()

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=attendance_report.pdf"}
    )
