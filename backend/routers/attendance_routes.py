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
import crud
from models import AuditLog

router = APIRouter(prefix="/attendance", tags=["Attendance"])

# ---------------- GET ATTENDANCE ----------------
@router.get("/")
def get_attendance(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    records = crud.get_attendance(db, current_user["company_id"])

    # Audit log
    audit = AuditLog(
        user_name=current_user["email"],
        action="Attendance Viewed",
        related_user=None,
        company_id=current_user["company_id"]
    )
    db.add(audit)
    db.commit()

    return [
        {
            "id": rec.id,
            "employee_id": rec.employee_id,
            "date": rec.date.strftime("%Y-%m-%d"),
            "status": rec.status,
            "company_id": rec.company_id
        }
        for rec in records
    ]

# ---------------- ADD ATTENDANCE ----------------
@router.post("/")
def add_attendance(
    employee_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if not current_user.get("company_id"):
        raise HTTPException(status_code=401, detail="Company not found in token")

    record = crud.create_attendance(
        db=db,
        employee_id=employee_id,
        date=datetime.utcnow(),
        status=status.lower(),  # normalize status
        company_id=current_user["company_id"]
    )

    # Audit log
    audit = AuditLog(
        user_name=current_user["email"],
        action=f"Attendance Added ({status})",
        related_user=str(employee_id),
        company_id=current_user["company_id"]
    )
    db.add(audit)
    db.commit()

    return {
        "id": record.id,
        "employee_id": record.employee_id,
        "date": record.date.strftime("%Y-%m-%d"),
        "status": record.status,
        "company_id": record.company_id
    }

# ---------------- REPORT (JSON for Analytics) ----------------
@router.get("/report")
def get_attendance_report(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if not current_user.get("company_id"):
        raise HTTPException(status_code=401, detail="Company not found in token")

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

    # Audit log
    audit = AuditLog(
        user_name=current_user["email"],
        action="Attendance Report Viewed (Analytics)",
        related_user=None,
        company_id=current_user["company_id"]
    )
    db.add(audit)
    db.commit()

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

    # Audit log
    audit = AuditLog(
        user_name=current_user["email"],
        action="Attendance Report Exported (Excel)",
        related_user=None,
        company_id=current_user["company_id"]
    )
    db.add(audit)
    db.commit()

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
