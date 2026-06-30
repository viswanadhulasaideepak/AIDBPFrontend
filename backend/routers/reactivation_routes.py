from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_user, require_admin
import crud, schema
from models import User, ReactivationRequest, UserStatus

router = APIRouter(
    prefix="/reactivation",
    tags=["Reactivation"]
)

# ---------------- SUBMIT REACTIVATION REQUEST ----------------

@router.post(
    "/request",
    response_model=schema.ReactivationRequestOut
)
def submit_reactivation_request(
    request: schema.ReactivationRequestCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    user = db.query(User).filter(
        User.id == current_user["id"]
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.status not in [
        UserStatus.suspended,
        UserStatus.deactivated
    ]:
        raise HTTPException(
            status_code=400,
            detail="Only suspended or deactivated users can request reinstatement."
        )

    admin_email = (
        user.suspended_by
        if user.status == UserStatus.suspended
        else user.deactivated_by
    )

    req = crud.create_reactivation_request(
        db=db,
        user_id=user.id,
        message=request.message,
        admin_email=admin_email,
        company_id=user.company_id
    )

    if not req:
        raise HTTPException(
            status_code=400,
            detail="A pending request already exists."
        )

    return req


# ---------------- LIST REQUESTS ----------------

@router.get(
    "/",
    response_model=list[schema.ReactivationRequestOut]
)
def list_reactivation_requests(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):

    return crud.get_reactivation_requests(
        db,
        current_user["company_id"]
    )


# ---------------- APPROVE / REJECT ----------------

@router.put(
    "/{id}",
    response_model=schema.ReactivationRequestOut
)
def update_reactivation_request(
    id: int,
    status: schema.ReactivationStatus,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):

    req = crud.update_reactivation_request(
        db=db,
        request_id=id,
        status=status,
        company_id=current_user["company_id"]
    )

    if not req:
        raise HTTPException(
            status_code=404,
            detail="Request not found"
        )

    user = db.query(User).filter(
    User.id == req.user_id
    ).first()

    if user.company_id != current_user["company_id"]:
        raise HTTPException(
        status_code=403,
        detail="Access denied"
    )

    action = (
        "Reactivation Approved"
        if status == schema.ReactivationStatus.approved
        else "Reactivation Rejected"
    )

    crud.create_audit_log(
        db=db,
        user_name=current_user["email"],
        action=action,
        related_user=req.user.email,
        company_id=current_user["company_id"]
    )

    return req


# ---------------- MY REQUEST ----------------

@router.get(
    "/my-request",
    response_model=schema.ReactivationRequestOut
)
def get_my_request(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    req = (
        db.query(ReactivationRequest)
        .filter(
            ReactivationRequest.user_id ==
            current_user["id"]
        )
        .order_by(
            ReactivationRequest.created_at.desc()
        )
        .first()
    )

    if not req:
        raise HTTPException(
            status_code=404,
            detail="No reactivation request found"
        )

    return req