from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import crud
from database import get_db
from auth import get_current_user
from models import Department, AuditLog
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

router = APIRouter(prefix="/employees", tags=["Employees"])

# ------------------ REQUEST MODELS ------------------
class EmployeeRequest(BaseModel):
    name: str
    email: str
    department_name: str
    role: str
    joined_date: Optional[str] = None
    status: str = "active"

class EmployeeUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    department_name: Optional[str] = None
    role: Optional[str] = None
    joined_date: Optional[str] = None
    status: Optional[str] = None

# ------------------ READ EMPLOYEES ------------------
@router.get("/")
def read_employees(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    employees = crud.get_employees(db, current_user["company_id"])
    
    print("CURRENT USER:", current_user)

    return [
        {
            "id": emp.id,
            "name": emp.name,
            "email": emp.email,
            "role": emp.role,
            "status": emp.status,
            "department_name": emp.department_rel.name if emp.department_rel else None,
            "company_id": emp.company_id
        }
        for emp in employees
    ]

# ------------------ ADD EMPLOYEE ------------------
@router.post("/")
def add_employee(
    request: EmployeeRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    department = db.query(Department).filter(
        Department.name == request.department_name,
        Department.company_id == current_user["company_id"]
    ).first()

    if not department:
        department = Department(name=request.department_name,  
                                company_id=current_user["company_id"])
        
        db.add(department)
        db.commit()
        db.refresh(department)

    new_emp = crud.create_employee(
        db=db,
        name=request.name,
        department_id=department.id,
        email=request.email,
        role=request.role,
        joined_date=request.joined_date,
        status=request.status,
        company_id=current_user["company_id"]
    )

    # CRUD NOTIFICATION (OPTION A)
    crud.create_notification(
        db=db,
        message=f"New employee {new_emp.name} was added",
        recipient_email=new_emp.email,
        company_id=current_user["company_id"]
    )

    audit = AuditLog(
        user_name=current_user["username"],
        action="Employee Created",
        related_user=new_emp.name,
        company_id=current_user["company_id"]
    )
    db.add(audit)
    db.commit()

    return {
        "id": new_emp.id,
        "name": new_emp.name,
        "email": new_emp.email,
        "role": new_emp.role,
        "status": new_emp.status,
        "department_name": department.name,
        "company_id": new_emp.company_id
    }

# ------------------ UPDATE EMPLOYEE ------------------
@router.put("/{id}")
def update_employee(
    id: int,
    request: EmployeeUpdateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    emp = crud.get_employee_by_id(db, id, current_user["company_id"])
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    old_status = emp.status

    if request.name is not None:
        emp.name = request.name
    if request.email is not None:
        emp.email = request.email
    if request.role is not None:
        emp.role = request.role
    if request.department_name is not None:
        department = db.query(Department).filter(
            Department.name == request.department_name,
            Department.company_id == current_user["company_id"]
        ).first()
        if department:
            emp.department_id = department.id

    if request.joined_date:
        try:
            emp.joined_date = datetime.strptime(request.joined_date, "%Y-%m-%d")
        except Exception:
            pass

    if request.status is not None:
        emp.status = request.status

    db.commit()
    db.refresh(emp)

    audit = AuditLog(
        user_name=current_user["username"],
        action="Employee Updated",
        related_user=emp.name,
        company_id=current_user["company_id"]
    )
    db.add(audit)
    db.commit()

    # CRUD NOTIFICATION (OPTION A)
    if old_status != emp.status:
        crud.create_notification(
            db=db,
            message=f"Employee {emp.name} status changed from {old_status} to {emp.status}",
            recipient_email=emp.email,
            company_id=current_user["company_id"]
        )

    return {
        "id": emp.id,
        "name": emp.name,
        "email": emp.email,
        "role": emp.role,
        "status": emp.status,
        "department_name": emp.department_rel.name if emp.department_rel else None,
        "joined_date": emp.joined_date,
        "company_id": emp.company_id
    }

# ------------------ DELETE EMPLOYEE ------------------
@router.delete("/{id}")
def delete_employee(
    id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    emp = crud.get_employee_by_id(db, id, current_user["company_id"])
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    audit = AuditLog(
        user_name=current_user["username"],
        action="Employee Deleted",
        related_user=emp.name,
        company_id=current_user["company_id"]
    )
    db.add(audit)
    db.commit()

    db.delete(emp)
    db.commit()

    return {"message": "Employee deleted successfully"}