from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import models
from schema import DepartmentTransferCreate
from auth import get_current_user
from datetime import datetime

router = APIRouter()

@router.post("/department/transfer")
def transfer_department(
    request: DepartmentTransferCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # 1. Get employee
    employee = db.query(models.Employee).filter(
        models.Employee.id == request.employee_id
    ).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    old_department_id = employee.department_id

    # 2. Validate department change
    if old_department_id == request.new_department_id:
        raise HTTPException(
            status_code=400,
            detail="Employee already in this department"
        )

    # 3. Validate new department exists
    new_department = db.query(models.Department).filter(
        models.Department.id == request.new_department_id
    ).first()

    if not new_department:
        raise HTTPException(status_code=404, detail="New department not found")

    # 4. Update employee department
    employee.department_id = request.new_department_id

    # 5. Save transfer record
    transfer = models.DepartmentTransfer(
        employee_id=employee.id,
        old_department_id=old_department_id,
        new_department_id=request.new_department_id,
        transferred_by=current_user.id,
        company_id=employee.company_id,
        reason=request.reason
    )
    db.add(transfer)

    # 6. Notification (to employee)
    notification = models.Notification(
        user_id=employee.user_id if hasattr(employee, "user_id") else employee.id,
        message=f"Your department has been changed to {new_department.name}"
    )
    db.add(notification)

    # 7. Audit log (if you have audit_logs table)
    audit = models.AuditLog(
        action="DEPARTMENT_TRANSFER",
        performed_by=current_user.id,
        target_employee_id=employee.id,
        metadata={
            "old_department_id": old_department_id,
            "new_department_id": request.new_department_id,
            "company_id": employee.company_id,
            "reason": request.reason
        }
    )
    db.add(audit)

    db.commit()
    db.refresh(employee)

    return {
        "message": "Department transferred successfully",
        "employee_id": employee.id,
        "old_department_id": old_department_id,
        "new_department_id": request.new_department_id
    }