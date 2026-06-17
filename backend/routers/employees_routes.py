from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import crud
from database import get_db
from auth import get_current_user
from models import Department, AuditLog, Attendance
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

router = APIRouter(prefix="/employees", tags=["Employees"])

#------------------ REQUEST MODELS ------------------

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

#------------------ READ EMPLOYEES ------------------

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

#------------------ ADD EMPLOYEE ------------------

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
        department = Department(
            name=request.department_name,
            company_id=current_user["company_id"]
            )
        db.add(department)
        db.commit()
        db.refresh(department)
    
        
    if request.joined_date:
        try:
            joined_date = datetime.strptime(request.joined_date, "%Y-%m-%d")

        except Exception:
            joined_date = None
                
    joined_date = None        
    new_emp = crud.create_employee(
        db=db,
        name=request.name,
        department_id=department.id,
        email=request.email,
        role=request.role,
        joined_date=joined_date,   
        status=request.status,
        company_id=current_user["company_id"]
        )
        
        # Attendance record for new employee
    attendance_status = "present"
    
    if new_emp.status.lower() == "active":
        attendance_status = "present"
        
    elif new_emp.status.lower() == "onleave":
        attendance_status = "leave"
        
    elif new_emp.status.lower() == "inactive":
        attendance_status = "absent"
        
    '''attendance = Attendance(
        employee_id=new_emp.id,
        date=datetime.utcnow(),
        status=attendance_status,
        company_id=new_emp.company_id
        )'''

# Audit log only (no notification)

    audit = AuditLog(
        user_name=current_user["email"],
        action="Employee Created", 
        related_user=new_emp.email,
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

#------------------ UPDATE EMPLOYEE ------------------

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
    
    # ... update fields ...
    if request.name is not None:
        emp.name = request.name
    
    if request.email is not None:
        emp.email = request.email

    if request.role is not None:
        emp.role = request.role

    if request.status is not None:
        emp.status = request.status
    
    if request.joined_date:
        try:
            emp.joined_date = datetime.strptime(
                request.joined_date,
                "%Y-%m-%d"
                )
        except Exception:
            pass
        
    department = None
    
    if request.department_name:
        department = db.query(Department).filter(
        Department.name == request.department_name,
        Department.company_id == current_user["company_id"]
    ).first()
        
        if not department:
            department = Department(
            name=request.department_name,
            company_id=current_user["company_id"]
            )
            db.add(department)
            db.commit()
            db.refresh(department)

    emp.department_id = department.id
    db.commit()
    db.refresh(emp)

# Audit log
    audit = AuditLog(
        user_name=current_user["email"],
        action="Employee Updated",
        related_user=emp.email,
        company_id=current_user["company_id"]
        )
    db.add(audit)
    db.commit()
        
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

#------------------ DELETE EMPLOYEE ------------------

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
    
    
    db.query(Attendance).filter(
        Attendance.employee_id == emp.id,
        Attendance.company_id == emp.company_id
        ).delete()

# Audit log

    audit = AuditLog(
        user_name=current_user["email"],
        action="Employee Deleted",
        related_user=emp.email,
        company_id=emp.company_id
        )
    db.add(audit)
    db.delete(emp)
    db.commit()
    
    return {"message": "Employee deleted successfully"} 