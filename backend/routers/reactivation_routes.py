from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
import crud, schema
from models import User

router = APIRouter(prefix="/reactivation", tags=["Reactivation"])

@router.post("/request", response_model=schema.ReactivationRequestOut)
def submit_reactivation_request(
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
    ):
    request = crud.create_reactivation_request(
        db,
        user_id=current_user["id"],
        deactivated_by="system",  # or track actual admin later
        admin_email="admin@company.com",  # placeholder until linked
        company_id=current_user["company_id"]
        )
    
    admin = db.query(User).filter(
        User.company_id == current_user["company_id"],
        User.role == "admin"
        ).first()
    
    if admin:
        crud.create_notification(
            db=db,
            message=f"Reactivation request submitted by {current_user['email']}",
            recipient_email=admin.email,
            company_id=current_user["company_id"]
            )
    
    crud.create_audit_log(
        db, 
        current_user["email"], 
        "Reactivation Request Submitted", 
        None,
        current_user["company_id"])
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
    
    # If approved, reactivate user
    if status == schema.ReactivationStatus.approved:
        crud.reactivate_user(
            db,
            req.user_id,
            current_user["company_id"]
            )
           
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