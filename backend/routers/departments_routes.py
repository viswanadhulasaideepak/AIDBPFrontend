from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import crud, models
from auth import get_current_user, require_admin
from pydantic import BaseModel
from database import get_db

router = APIRouter(prefix="/departments", tags=["Departments"])

# ---------------- GET DEPARTMENTS ----------------

class DepartmentRequest(BaseModel):
    name: str

@router.get("/")
def read_departments(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):

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
    current_user: dict = Depends(require_admin)
):
    
    existing = db.query(models.Department).filter(
    models.Department.name == request.name.strip(),
    models.Department.company_id == current_user["company_id"]
    ).first()
    
    if existing:
        raise HTTPException(
        status_code=400,
        detail="Department already exists"
        )

    return crud.create_department(db, request.name, current_user["company_id"])


# ---------------- LIST DEPARTMENTS ----------------

@router.get("/list")
def list_departments(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    departments = crud.get_departments(db, current_user["company_id"])

    return [{"id": d.id, "name": d.name} for d in departments]

# ---------------- DEPARTMENT TRANSFER HISTORY ----------------

@router.get("/transfer-history")
def get_department_transfer_history(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):

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
            "employee_name": (
                record.employee.name
                if record.employee
                else "Deleted Employee"),
            "old_department": (
                record.old_department.name
                if record.old_department
                else "Deleted Department"),
            "new_department": (
                record.new_department.name
                if record.new_department
                else "Deleted Department"),
            "transferred_by": record.transferred_by,
            "reason": record.reason,
            "transferred_at": record.transferred_at,
        }
        for record in history
    ]