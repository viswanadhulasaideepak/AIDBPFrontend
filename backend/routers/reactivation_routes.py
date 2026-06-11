from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
import crud, schema

router = APIRouter(prefix="/reactivation", tags=["Reactivation"])

@router.post("/request", response_model=schema.ReactivationRequestOut)
def submit_reactivation_request(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    request = crud.create_reactivation_request(db, current_user["id"], current_user["email"], current_user["company_id"])
    crud.create_audit_log(db, current_user["email"], "Reactivation Request Submitted", current_user["email"], current_user["company_id"])
    return request

@router.get("/", response_model=list[schema.ReactivationRequestOut])
def list_reactivation_requests(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return crud.get_reactivation_requests(db, current_user["company_id"])

@router.put("/{id}")
def update_reactivation_request(id: int, status: schema.ReactivationStatus, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    req = crud.update_reactivation_request(db, id, status, current_user["company_id"])
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    action = "Reactivation Approved" if status == schema.ReactivationStatus.approved else "Reactivation Rejected"
    crud.create_audit_log(db, current_user["email"], action, req.user.email, current_user["company_id"])
    return {"message": f"Reactivation {status}"}
