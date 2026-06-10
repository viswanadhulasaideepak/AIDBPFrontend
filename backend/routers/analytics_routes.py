from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from auth import get_current_user
from models import Employee, Department, RoleChangeRequest, RoleChangeStatus

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    company_id = current_user["company_id"]

    total_employees = db.query(Employee).filter(Employee.company_id == company_id).count()
    active_employees = db.query(Employee).filter(
        Employee.company_id == company_id,
        Employee.status == "active"
    ).count()
    total_departments = db.query(Department).filter(Department.company_id == company_id).count()
    pending_requests = db.query(RoleChangeRequest).filter(
        RoleChangeRequest.company_id == company_id,
        RoleChangeRequest.status == RoleChangeStatus.pending
    ).count()

    return {
        "total_employees": total_employees,
        "active_employees": active_employees,
        "total_departments": total_departments,
        "pending_requests": pending_requests
    }
