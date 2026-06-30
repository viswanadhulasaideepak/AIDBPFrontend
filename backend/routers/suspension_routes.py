from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from auth import (
    require_admin,
    require_suspended_user,
    require_active_user,
    get_current_user
)

import crud
import schema

from models import UserStatus

router = APIRouter( prefix="/suspension", tags=["Suspension"])

@router.post("/{user_id}/suspend")
def suspend_user(
    user_id: int,
    request: schema.SuspensionRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    print("SUSPEND API HIT")
    print("User ID:", user_id)
    
    if user_id == current_user["id"]:
        raise HTTPException(
            status_code=400,
            detail="You cannot suspend yourself."
        )

    user = crud.suspend_user(
        db=db,
        user_id=user_id,
        company_id=current_user["company_id"],
        admin_email=current_user["email"],
        reason=request.reason
    )
    
    print("Looking for User ID:", user_id)
    print("User found:", user)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "message": "User suspended successfully."
    }
    
@router.get("/account-status")
def account_status(
    current_user: dict = Depends(get_current_user)
):
    user = current_user["user"]

    return {
        "status": user.status.value,
        "suspended_at": user.suspended_at,
        "suspended_by": user.suspended_by,
        "suspended_reason": user.suspended_reason,
        "deactivated_by": user.deactivated_by,
        "deactivated_reason": user.deactivated_reason
    }
    
@router.post("/reinstatement/request")
def submit_reinstatement_request(
    request: schema.ReinstatementRequestCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["user"].status != UserStatus.suspended:
        raise HTTPException(400, "Only suspended users can request reinstatement")

    return crud.create_reinstatement_request(
        db=db,
        user_id=current_user["id"],
        company_id=current_user["company_id"],
        reason=request.reason
    )
    
@router.get("/reinstatement/my-request")
def my_reinstatement_request(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_suspended_user)
):
    return crud.get_my_reinstatement_request(
        db,
        current_user["id"],
         company_id=current_user["company_id"]
    )    
    
@router.get("/reinstatement/requests")
def get_requests(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    return crud.get_reinstatement_requests(
        db,
        current_user["company_id"]
    )
    
@router.post("/reinstatement/{request_id}/approve")
def approve_reinstatement(
    request_id: int,
    review: schema.ReinstatementReview,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    return crud.approve_reinstatement(
        db=db,
        request_id=request_id,
        company_id=current_user["company_id"],
        approved_by=current_user["email"],
        comment=review.admin_comment
    )

@router.post("/reinstatement/{request_id}/reject")
def reject_reinstatement(
    request_id: int,
    review: schema.ReinstatementReview,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    return crud.reject_reinstatement(
        db=db,
        request_id=request_id,
        company_id=current_user["company_id"],
        rejected_by=current_user["email"],
        comment=review.admin_comment
    )            
            