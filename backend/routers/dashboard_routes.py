from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import crud, database
from auth import get_current_user
from models import Employee, RoleChangeRequest, RoleChangeStatus, StatusEnum

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
    active_employees = len([e for e in employees if e.status == StatusEnum.active])

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

    # ---------------- Extra Analytics ----------------
    # Employee Role Distribution
    role_distribution = (
        db.query(Employee.role, func.count(Employee.id))
        .filter(Employee.company_id == company_id)
        .group_by(Employee.role)
        .all()
    )
    role_data = [{"role": r, "count": c} for r, c in role_distribution]

    # Employee Status Overview

    active_count = db.query(Employee).filter(
        Employee.company_id == company_id,
        Employee.status == StatusEnum.active
        ).count()

    inactive_count = db.query(Employee).filter(
        Employee.company_id == company_id,
        Employee.status == StatusEnum.inactive
        ).count()
    
    leave_count = db.query(Employee).filter(
        Employee.company_id == company_id,
        Employee.status == StatusEnum.onleave
        ).count()

    status_data = [
        {"status": "active", "count": active_count},
        {"status": "inactive", "count": inactive_count},
        {"status": "onleave", "count": leave_count},
        ]
    
    # Pending Role Requests
    pending_requests = (
        db.query(RoleChangeRequest)
        .filter(
            RoleChangeRequest.company_id == company_id,
            RoleChangeRequest.status == RoleChangeStatus.pending
        )
        .count()
    )

    return {
        "total_employees": total_employees,
        "active_employees": active_employees,
        "departments": total_departments,
        "attendance_percentage": attendance_percentage,
        "role_distribution": role_data,
        "status_overview": status_data,
        "pending_requests": pending_requests,
    }
