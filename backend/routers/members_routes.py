from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
import crud, schema

router = APIRouter(prefix="/members", tags=["Members"])

@router.get("/", response_model=list[schema.UserOut])
def list_members(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )

    return crud.get_members(
        db,
        current_user["company_id"]
    )

@router.put("/{id}/deactivate", response_model=schema.UserOut)
def deactivate_member(
    id: int, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
    ):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if id == current_user["id"]:
        raise HTTPException(status_code=400, detail="You cannot deactivate your own account.")
    
    user = crud.deactivate_user(
        db, 
        id, 
        current_user["company_id"],
        current_user["email"]
        )
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    crud.create_audit_log(
        db, 
        current_user["email"], 
        "User Deactivated", 
        user.email, 
        current_user["company_id"]
        )
    
    crud.create_notification(
        db=db,
        message="Your account has been deactivated by administrator.",
        recipient_email=user.email,
        company_id=current_user["company_id"]
        )
    
    return user

@router.put("/{id}/reactivate")
def reactivate_member(
    id: int, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
    ):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if id == current_user["id"]:
        raise HTTPException(
            status_code=400,
            detail="You cannot deactivate your own account."
            )
    
    user = crud.reactivate_user(
        db, 
        id, 
        current_user["company_id"])
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    crud.create_audit_log(
        db, 
        current_user["email"], 
        "User Activated", 
        user.email, 
        current_user["company_id"]
        )
    return user