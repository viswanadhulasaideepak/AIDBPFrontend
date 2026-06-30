from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import crud
import database
from auth import get_current_user, require_active_user,require_admin
from models import (Employee, RoleChangeRequest, RoleChangeStatus, StatusEnum)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(database.get_db),
    current_user: dict = Depends(require_admin)
    ):

    company_id = current_user.get("company_id")

    if not company_id:
        raise HTTPException(
            status_code=401,
            detail="Company not found in token"
        )

    # ---------------- Employees ----------------
    employees = crud.get_employees(db, company_id)

    total_employees = len(employees)
    active_employees = sum(
        1
    for emp in employees
    if (
        emp.status == StatusEnum.active
        or str(emp.status).lower() == "active"
        or getattr(emp.status, "value", "") == "active"
    )
)

    # ---------------- Departments ----------------
    departments = crud.get_departments(db, company_id)
    total_departments = len(departments)

    # ---------------- Attendance ----------------
    attendance_records = crud.get_attendance(db, company_id)
    attendance_by_date = {}

    for record in attendance_records:

        date = record.date.strftime("%Y-%m-%d")

        if date not in attendance_by_date:
            attendance_by_date[date] = {
                "present": 0,
                "leave": 0,
                "absent": 0,
            }
            
        status = record.status.lower()    

        if record.status in attendance_by_date[date]:
            attendance_by_date[date][status] += 1

    total_days = len(attendance_by_date)
    total_possible = total_days * total_employees

    total_present = sum(
        day["present"]
        for day in attendance_by_date.values()
    )

    attendance_percentage = (
        round((total_present / total_possible) * 100)
        if total_possible > 0
        else 0
    )

    # ---------------- Role Distribution ----------------
    role_distribution = (
        db.query(
            Employee.role,
            func.count(Employee.id)
        )
        .filter(Employee.company_id == company_id)
        .group_by(Employee.role)
        .all()
    )

    role_data = [
        {
            "role": role,
            "count": count,
        }
        for role, count in role_distribution
    ]

    # ---------------- Employee Status Overview ----------------
    status_distribution = (
        db.query(
            Employee.status,
            func.count(Employee.id)
        )
        .filter(Employee.company_id == company_id)
        .group_by(Employee.status)
        .all()
    )

    status_map = {}

    for status, count in status_distribution:
        key = (
            status.value
            if hasattr(status, "value")
            else str(status)
        )
        status_map[key] = count

    for status, count in status_distribution:

        key = (
            status.value
            if hasattr(status, "value")
            else str(status)
        )

        status_map[key] = count

    status_data = [
    {
        "status": k,
        "count": v
    }
    for k, v in status_map.items()
    ]

    # ---------------- Pending Role Requests ----------------
    pending_requests = (
        db.query(RoleChangeRequest)
        .filter(
            RoleChangeRequest.company_id == company_id,
            RoleChangeRequest.status == RoleChangeStatus.pending,
        )
        .count()
    )

    # ---------------- Response ----------------
    return {
        "total_employees": total_employees,
        "active_employees": active_employees,
        "departments": total_departments,
        "attendance_percentage": attendance_percentage,
        "role_distribution": role_data,
        "status_overview": status_data,
        "pending_requests": pending_requests,
    }