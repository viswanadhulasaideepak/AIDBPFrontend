from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
import crud, schema
from models import User, ReactivationRequest

router = APIRouter(prefix="/reactivation", tags=["Reactivation"])

@router.post("/request", response_model=schema.ReactivationRequestOut)
def submit_reactivation_request(
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
    ):
    # Get the current user from DB
    user = db.query(User).filter(
        User.id == current_user["id"]
        ).first()
    
    request = crud.create_reactivation_request(
        db,
        user_id=current_user["id"],
        deactivated_by=user.deactivated_by,
        admin_email=user.deactivated_by,
        company_id=current_user["company_id"]
        )
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return request

@router.get("/", response_model=list[schema.ReactivationRequestOut])
def list_reactivation_requests(
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
    ):
    
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return crud.get_reactivation_requests(db, current_user["company_id"])

@router.put("/{id}", response_model=schema.ReactivationRequestOut)
def update_reactivation_request(
    id: int, 
    status: schema.ReactivationStatus, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
    ):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    req = crud.update_reactivation_request(
        db, 
        id, 
        status, 
        current_user["company_id"]
        )
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
        
        
    action = (
        "Reactivation Approved"
        if status == schema.ReactivationStatus.approved
        else "Reactivation Rejected"
        )
        
    crud.create_audit_log(
        db, 
        current_user["email"], 
        action, 
        req.user.email, 
        current_user["company_id"]
        )
    
    crud.create_notification(
        db,
        f"Your reactivation request was {status.value}",
        req.user.email,
        current_user["company_id"]
    )

    return req

@router.get("/my-request", response_model=schema.ReactivationRequestOut)
def get_my_request(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    req = (
        db.query(ReactivationRequest)
        .filter(ReactivationRequest.user_id == current_user["id"])
        .order_by(ReactivationRequest.created_at.desc())
        .first()
    )

    if not req:
        raise HTTPException(
            status_code=404,
            detail="No reactivation request found"
        )

    return req