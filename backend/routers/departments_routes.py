from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import crud, models
from auth import get_current_user
from pydantic import BaseModel
from database import get_db

router = APIRouter(prefix="/departments", tags=["Departments"])

# ---------------- GET DEPARTMENTS ----------------

class DepartmentRequest(BaseModel):
    name: str

@router.get("/")
def read_departments(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    departments = crud.get_departments(db, current_user["company_id"])

    return [
        {
            "id": dept.id,
            "name": dept.name,
            "employee_count": len(dept.employees or [])
        }
        for dept in departments
    ]

# ---------------- ADD DEPARTMENT ----------------

@router.post("/")
def add_department(
    request: DepartmentRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    return crud.create_department(db, request.name, current_user["company_id"])


# ---------------- LIST DEPARTMENTS ----------------

@router.get("/list")
def list_departments(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    departments = crud.get_departments(db, current_user["company_id"])

    return [{"id": d.id, "name": d.name} for d in departments]

# ---------------- DEPARTMENT TRANSFER HISTORY ----------------

@router.get("/transfer-history")
def get_department_transfer_history(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )

    history = (
        db.query(models.DepartmentTransfer)
        .filter(
            models.DepartmentTransfer.company_id == current_user["company_id"]
        )
        .order_by(models.DepartmentTransfer.transferred_at.desc())
        .all()
    )

    return [
        {
            "id": record.id,
            "employee_name": record.employee.name,
            "old_department": record.old_department.name,
            "new_department": record.new_department.name,
            "transferred_by": record.transferred_by,
            "reason": record.reason,
            "transferred_at": record.transferred_at,
        }
        for record in history
    ]