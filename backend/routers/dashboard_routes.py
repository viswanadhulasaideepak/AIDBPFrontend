from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import crud, database
from auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(get_current_user)
):
    # Authorization check
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    company_id = current_user.get("company_id")
    if not company_id:
        raise HTTPException(status_code=401, detail="Company not found in token")

    # Employees scoped by company
    employees = crud.get_employees(db, company_id)
    total_employees = len(employees)
    active_employees = len([e for e in employees if e.status == "active"])

    # Departments scoped by company
    departments = crud.get_departments(db, company_id)
    total_departments = len(departments)

    # Attendance scoped by company
    records = crud.get_attendance(db, company_id)
    report = {}
    for rec in records:
        date_str = rec.date.strftime("%Y-%m-%d")
        if date_str not in report:
            report[date_str] = {"present": 0, "leave": 0, "absent": 0}
        if rec.status in report[date_str]:
            report[date_str][rec.status] += 1

    total_days = len(report.keys())
    total_possible = total_employees * total_days
    total_present = sum([report[d]["present"] for d in report])

    attendance_percentage = round(
        (total_present / total_possible) * 100
    ) if total_possible > 0 else 0

    return {
        "total_employees": total_employees,
        "active_employees": active_employees,
        "departments": total_departments,
        "attendance_percentage": attendance_percentage,
    }
