from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import RoleChangeRequest, RoleChangeStatus, User, AuditLog
from schema import RoleChangeRequestCreate, RoleChangeRequestOut, RoleChangeRequestUpdate
from auth import verify_user_identity, get_current_user
from typing import List

router = APIRouter(prefix="/role-change-request", tags=["Role Change Requests"])

# ---------------- User submits a role change request ----------------
@router.post("/", response_model=RoleChangeRequestOut)
def submit_role_change_request(
    request: RoleChangeRequestCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Only Users can request role change
    user = db.query(User).filter(User.email == current_user["email"]).first()
    if not user or user.role != "user":
        raise HTTPException(status_code=403, detail="Only User accounts can request role change")

    # Verify password
    verify_user_identity(db, user.email, request.current_password)

    # Create request entry
    role_request = RoleChangeRequest(
        user_id=user.id,
        admin_email=request.admin_email,
        status=RoleChangeStatus.pending
    )
    db.add(role_request)
    db.commit()
    db.refresh(role_request)
    
    #  Audit log only
    audit = AuditLog(
        user_name=user.email,
        action="Role Change Requested",
        related_user=user.email,
        company_id=user.company_id
    )
    db.add(audit)
    db.commit()

    return role_request


# ---------------- Admin views pending requests ----------------
@router.get("/", response_model=List[RoleChangeRequestOut])
def get_role_change_requests(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Only Admins can view requests
    admin = db.query(User).filter(User.email == current_user["email"]).first()
    if not admin or admin.role != "admin":
        raise HTTPException(status_code=403, detail="Only Admin accounts can view requests")

    requests = db.query(RoleChangeRequest).filter(RoleChangeRequest.status == RoleChangeStatus.pending).all()
    return requests


# ---------------- Admin approves/rejects a request ----------------
@router.put("/{request_id}", response_model=RoleChangeRequestOut)
def update_role_change_request(
    request_id: int,
    update: RoleChangeRequestUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Only Admins can approve/reject
    admin = db.query(User).filter(User.email == current_user["email"]).first()
    if not admin or admin.role != "admin":
        raise HTTPException(status_code=403, detail="Only Admin accounts can approve/reject requests")

    role_request = db.query(RoleChangeRequest).filter(RoleChangeRequest.id == request_id).first()
    if not role_request:
        raise HTTPException(status_code=404, detail="Request not found")

    role_request.status = update.status
    db.commit()
    db.refresh(role_request)

    # If approved → update user role
    if update.status == RoleChangeStatus.approved:
        user = db.query(User).filter(User.id == role_request.user_id).first()
        if user:
            user.role = "admin"
            db.commit()
            db.refresh(user)

            # Audit log only
            audit = AuditLog(
                user_name=admin.email,
                action="Role Change Approved",
                related_user=user.email,
                company_id=user.company_id
            )
            db.add(audit)
            db.commit()

    elif update.status == RoleChangeStatus.rejected:
        user = db.query(User).filter(User.id == role_request.user_id).first()
        if user:
            # Audit log only
            audit = AuditLog(
                user_name=admin.email,
                action="Role Change Rejected",
                related_user=user.email,
                company_id=user.company_id
            )
            db.add(audit)
            db.commit()

    return role_request
