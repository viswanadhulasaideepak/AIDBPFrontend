from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import crud, models
import traceback
from database import get_db
from auth import (
    get_current_user,
    require_active_user,
    require_admin
)
from models import Department, AuditLog, Attendance
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from schema import (DepartmentTransferRequest,DepartmentTransferResponse)

router = APIRouter(prefix="/employees", tags=["Employees"])

#------------------ REQUEST MODELS ------------------

class EmployeeRequest(BaseModel):
    name: str
    email: str
    department_name: str
    role: str

    employee_code: Optional[str] = None

    joined_date: Optional[str] = None
    status: str = "active"

class EmployeeUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    department_name: Optional[str] = None
    role: Optional[str] = None
    joined_date: Optional[str] = None
    status: Optional[str] = None
    
    phone_number: Optional[str] = None
    address: Optional[str] = None
    designation: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    employee_code: Optional[str] = None
    profile_picture: Optional[str] = None

#------------------ READ EMPLOYEES ------------------

@router.get("/")
def read_employees(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_active_user)
    ):
    
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
            "company_id": emp.company_id,
            "profile_completion": crud.calculate_profile_completion(emp)
            }
        for emp in employees
        ]

#------------------ ADD EMPLOYEE ------------------

@router.post("/")
def add_employee(
    request: EmployeeRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_active_user)
    ):
    
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
    
        
    joined_date = None
    
    if request.joined_date:
        try:
            joined_date = datetime.strptime(request.joined_date,"%Y-%m-%d")
            
        except Exception:
            joined_date = None
                        
    new_emp = crud.create_employee(
        db=db,
        name=request.name,
        department_id=department.id,
        email=request.email,
        role=request.role,
        joined_date=joined_date,   
        status=request.status,
        employee_code=request.employee_code,
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

# Audit log only (no notification)

    audit = AuditLog(
        user_name=current_user["email"],
        action="Employee Created", 
        related_user=new_emp.email,
        company_id=current_user["company_id"]
        )
    db.add(audit)
    db.commit()
    
    # After creating new_emp and audit log
    crud.create_notification(
    db=db,
    message=f"New employee {new_emp.name} ({new_emp.email}) was added.",
    recipient_email=current_user["email"],   # or notify admins
    company_id=current_user["company_id"],
    request_id=new_emp.id,
    type="employee"
)
    
    return {
            "id": new_emp.id,
            "name": new_emp.name,
            "email": new_emp.email,
            "role": new_emp.role,
            "status": new_emp.status,
            "department_name": department.name,
            "company_id": new_emp.company_id,
            "profile_completion": crud.calculate_profile_completion(new_emp)
            }

#------------------ UPDATE EMPLOYEE ------------------

@router.put("/{id}")
def update_employee(
    id: int,
    request: EmployeeUpdateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_active_user)
    ):
    PROFILE_COMPLETION_THRESHOLD = 70
    
    emp = crud.get_employee_by_id(db, id, current_user["company_id"])
    
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    old_score = crud.calculate_profile_completion(emp)
    
    # ... update fields ...
    if request.name is not None:
        emp.name = request.name
    
    if request.email is not None:
        emp.email = request.email

    if request.role is not None:
        emp.role = request.role

    if request.status is not None:
        emp.status = request.status
        
    if request.first_name is not None:
        emp.first_name = request.first_name

    if request.last_name is not None:
        emp.last_name = request.last_name

    if request.phone_number is not None:
        emp.phone_number = request.phone_number

    if request.address is not None:
        emp.address = request.address

    if request.designation is not None:
        emp.designation = request.designation

    if request.profile_picture is not None:
        emp.profile_picture = request.profile_picture

    if request.employee_code is not None:
        emp.employee_code = request.employee_code        
    
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

    if department:
        emp.department_id = department.id
    
    db.flush()
    
    new_score = crud.calculate_profile_completion(emp)  
    
    emp.profile_completion = new_score["completion_percentage"]  
    db.commit()
    db.refresh(emp)
    
    crud.create_audit_log(
    db=db,
    user_name=current_user["email"],
    action="Profile Updated",
    related_user=emp.email,
    company_id=current_user["company_id"]
)

    if new_score["completion_percentage"] == 100:
        
        crud.create_notification(
            db=db,
            message="Congratulations! Your profile is now 100% complete.",
            recipient_email=emp.email,
            company_id=emp.company_id,
            type="profile"
            )
        
        if old_score["completion_percentage"] != new_score["completion_percentage"]:
            crud.create_audit_log(
                db=db,
                user_name=current_user["email"],
                action="Profile Completion Score Changed ",
                details=f"{old_score['completion_percentage']}% → {new_score['completion_percentage']}%",
                related_user=emp.email,
                company_id=current_user["company_id"]
                )

    elif new_score["completion_percentage"] < PROFILE_COMPLETION_THRESHOLD:
        crud.create_notification(
            db=db,
            message="Please complete your profile.",
            recipient_email=emp.email,
            company_id=emp.company_id,
            type="profile"
        )
        
# Audit log
    audit = AuditLog(
        user_name=current_user["email"],
        action="Employee Updated",
        related_user=emp.email,
        company_id=current_user["company_id"]
        )
    db.add(audit)
    db.commit()
    
    crud.create_notification(
    db=db,
    message=f"Employee {emp.name} ({emp.email}) was updated.",
    recipient_email=current_user["email"],   
    company_id=current_user["company_id"],
    request_id=emp.id,
    type="employee"
)

    return { 
            "id": emp.id,
            "name": emp.name,
            "email": emp.email,
            "role": emp.role,
            "status": emp.status,
            "department_name": emp.department_rel.name if emp.department_rel else None,
            "joined_date": emp.joined_date,
            "company_id": emp.company_id,
            "profile_completion": new_score
            }

#------------------ DELETE EMPLOYEE ------------------

@router.delete("/{id}")
def delete_employee(
    id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_active_user)
    ):
    
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
    
    crud.create_notification(
    db=db,
    message=f"Employee {emp.name} ({emp.email}) was deleted.",
    recipient_email=current_user["email"],   # or notify admins
    company_id=current_user["company_id"],
    request_id=emp.id,
    type="employee"
)

    return {"message": "Employee deleted successfully"} 

# ---------------- Transfer Department ----------------

@router.put("/{employee_id}/transfer")
def transfer_department(
    employee_id: int,
    transfer: DepartmentTransferRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    print("DATABASE PATH:", db.bind.url.database)

    # ---------------- GET EMPLOYEE ----------------
    employee = crud.get_employee_by_id(
        db=db,
        id=employee_id,
        company_id=current_user["company_id"]
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found."
        )

    # ---------------- CALL CRUD ----------------
    try:
        result = crud.transfer_employee_department(
            db=db,
            employee=employee,
            new_department_id=transfer.new_department_id,
            performed_by=current_user["email"],
            company_id=current_user["company_id"],
            reason=transfer.reason
        )

        db.commit()
        db.refresh(employee)

        return result
    except Exception as e:
        db.rollback()
        traceback.print_exc()  
        raise HTTPException(status_code=400, detail=str(e))
    
    # ---------------- DEPARTMENT TRANSFER HISTORY ----------------

@router.get("/transfer/history")
def get_department_transfer_history(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_active_user)
    ):

    transfers = (
        db.query(models.DepartmentTransfer)
        .filter(
            models.DepartmentTransfer.company_id == current_user["company_id"]
        )
        .order_by(models.DepartmentTransfer.transferred_at.desc())
        .all()
    )

    history = []
    for transfer in transfers:

        employee = db.query(models.Employee).filter(
            models.Employee.id == transfer.employee_id
        ).first()

        old_department = db.query(models.Department).filter(
            models.Department.id == transfer.old_department_id
        ).first()

        new_department = db.query(models.Department).filter(
            models.Department.id == transfer.new_department_id
        ).first()

        history.append({
            "id": transfer.id,
            "employee": employee.name if employee else "-",
            "old_department": old_department.name if old_department else "-",
            "new_department": new_department.name if new_department else "-",
            "transferred_by": transfer.transferred_by,
            "reason": transfer.reason,
            "transferred_at": transfer.transferred_at
        })

    return history
    
# ---------------- USER PROFILE COMPLETION ----------------    
@router.get("/me/profile")
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    emp = db.query(models.Employee).filter(
        models.Employee.email == current_user["email"],
        models.Employee.company_id == current_user["company_id"]
    ).first()

    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    score = crud.calculate_profile_completion(emp)

    return {
        "id": emp.id,
        "first_name": emp.first_name,
        "last_name": emp.last_name,
        "email": emp.email,
        "phone_number": emp.phone_number,
        "department_name": emp.department_rel.name if emp.department_rel else None,
        "designation": emp.designation,
        "profile_picture": emp.profile_picture,
        "address": emp.address,
        "joined_date": emp.joined_date.strftime("%Y-%m-%d") if emp.joined_date else "",
        "employee_code": emp.employee_code,
    }
    
@router.put("/me/profile")
def update_my_profile(
    request: EmployeeUpdateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    print("===== UPDATE PROFILE =====")
    print(request)
    print(request.dict())

    emp = db.query(models.Employee).filter(
        models.Employee.email == current_user["email"],
        models.Employee.company_id == current_user["company_id"]
    ).first()

    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    if request.first_name is not None:
        emp.first_name = request.first_name

    if request.last_name is not None:
        emp.last_name = request.last_name

    if request.email is not None:
        emp.email = request.email

    if request.department_name:
        dept = db.query(Department).filter(
            Department.name == request.department_name,
            Department.company_id == current_user["company_id"]
        ).first()

        if dept:
            emp.department_id = dept.id

    if request.phone_number is not None:
        emp.phone_number = request.phone_number

    if request.designation is not None:
        emp.designation = request.designation

    if request.address is not None:
        emp.address = request.address

    if request.profile_picture is not None:
        emp.profile_picture = request.profile_picture

    db.commit()
    db.refresh(emp)

    score = crud.calculate_profile_completion(emp)

    emp.profile_completion = score["completion_percentage"]
    
    if request.joined_date:
        try:
            emp.joined_date = datetime.strptime(
                request.joined_date,
                "%Y-%m-%d"
                )
        except Exception:
            pass
    
    print("Before Commit")
    print(emp.first_name)
    print(emp.last_name)
    print(emp.phone_number)
    print(emp.designation)
    print(emp.address)

    db.commit()
    db.refresh(emp)

    return {
        "message": "Profile updated successfully",
        "profile_completion": score["completion_percentage"],
        **{k: v for k, v in score.items() if k != "completion_percentage"}
    }    
    
@router.get("/me/profile-completion")
def user_profile_completion(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_active_user)
):
    emp = db.query(models.Employee).filter(
        models.Employee.email == current_user["email"],
        models.Employee.company_id == current_user["company_id"]
    ).first()

    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    return crud.calculate_profile_completion(emp)    

#-----------------Profile admin view-------------------

@router.get("/{employee_id}/profile-completion")
def get_profile_completion(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_active_user)
):
    """
    Returns the profile completion percentage and missing fields
    for the requested employee.
    """

    result = crud.get_employee_profile_completion(
        db=db,
        employee_id=employee_id,
        company_id=current_user["company_id"]
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return result

@router.get("/profile-completion/below-threshold")
def employees_below_threshold(
    threshold: int = 80,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_active_user)
):
    return crud.get_profile_completion_below_threshold(
        db=db,
        company_id=current_user["company_id"],
        threshold=threshold
    )

@router.get("/profile-completion/all")
def company_profile_completion(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_active_user)
):
    return crud.get_company_profile_completion(
        db=db,
        company_id=current_user["company_id"]
    )