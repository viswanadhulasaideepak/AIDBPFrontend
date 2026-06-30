from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import crud
from auth import get_current_user, require_active_user
from database import get_db
from auth import require_admin
from models import UserStatus
from schema import (LeaveRequestCreate, LeaveRequestUpdate)

router = APIRouter( prefix="/leave",tags=["Leave Management"])

def check_user_not_suspended(current_user):
    if current_user.get("status") == UserStatus.suspended:
        raise HTTPException(
            status_code=403,
            detail="Account suspended. Access denied."
        )

    if current_user.get("status") == UserStatus.deactivated:
        raise HTTPException(
            status_code=403,
            detail="Account deactivated. Access denied."
        )

#--------------- USER SUBMIT LEAVE REQUEST-------------------------

@router.post("/request")
def submit_leave_request(
    leave: LeaveRequestCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_active_user)
):
    check_user_not_suspended(current_user)

    request = crud.create_leave_request(
        db=db,
        user_id=current_user["id"],
        company_id=current_user["company_id"],
        leave_type=leave.leave_type.value,
        start_date=leave.start_date,
        end_date=leave.end_date,
        reason=leave.reason
    )
    
    

    return {
        "message": "Leave request submitted successfully.",
        "request": request
    }

#----------------- USER VIEW MY LEAVE REQUESTS----------------------

@router.get("/my")
def get_my_leave_requests(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_active_user)
):
    check_user_not_suspended(current_user)

    requests = crud.get_my_leave_requests(
        db=db,
        user_id=current_user["id"]
    )

    return requests

#------------ ADMIN VIEW ALL COMPANY LEAVE REQUESTS----------------

@router.get("/company")
def get_company_leave_requests(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    check_user_not_suspended(current_user)

    requests = crud.get_company_leave_requests(
        db=db,
        company_id=current_user["company_id"]
    )

    return requests

# --------------------ADMIN APPROVE / REJECT LEAVE-----------------------

@router.put("/{request_id}")
def update_leave_request(
    request_id: int,
    leave: LeaveRequestUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    check_user_not_suspended(current_user)

    request = crud.update_leave_request(
        db=db,
        request_id=request_id,
        status=leave.status.value,
        company_id=current_user["company_id"],
        reviewed_by=current_user["email"]
    )
    
    if request is None:
        raise HTTPException(
            status_code=404,
            detail="Leave request not found."
        )

    return {
        "message": f"Leave request {leave.status.value}.",
        "request": request
    }