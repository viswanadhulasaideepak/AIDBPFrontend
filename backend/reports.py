from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io, csv
from openpyxl import Workbook
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from auth import get_current_user
from database import get_db
import crud
from models import AuditLog

router = APIRouter(prefix="/attendance/report", tags=["Reports"])

# ---------------- CSV REPORT ----------------
@router.get("/csv")
def get_csv(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    records = crud.get_attendance(db, current_user["company_id"])

    # Aggregate counts per date
    report = {}
    for rec in records:
        date_str = rec.date.strftime("%Y-%m-%d")
        if date_str not in report:
            report[date_str] = {"present": 0, "leave": 0, "absent": 0}
        if rec.status in report[date_str]:
            report[date_str][rec.status] += 1

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Present", "Leave", "Absent"])
    for date, stats in report.items():
        writer.writerow([date, stats["present"], stats["leave"], stats["absent"]])
    output.seek(0)

    # Audit log
    audit = AuditLog(
        user_name=current_user["username"],
        action="Attendance Report Exported (CSV)",
        related_user=None,
        company_id=current_user["company_id"]
    )
    db.add(audit)
    db.commit()

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=attendance_report.csv"}
    )

# ---------------- EXCEL REPORT ----------------
@router.get("/excel")
def get_excel(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    records = crud.get_attendance(db, current_user["company_id"])

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
        user_name=current_user["username"],
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

# ---------------- PDF REPORT ----------------
@router.get("/pdf")
def get_pdf(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    records = crud.get_attendance(db, current_user["company_id"])

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
        user_name=current_user["username"],
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
