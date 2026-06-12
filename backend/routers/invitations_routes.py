from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
import crud, schema, models

router = APIRouter(prefix="/invitations", tags=["Invitations"])

@router.post("/", response_model=schema.InvitationOut)
def create_invitation(
    request: schema.InvitationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    existing = crud.get_invitations(db, current_user["company_id"])
    
    for inv in existing:
        
        if inv.email == request.email and inv.status.value == "pending":
            raise HTTPException(
            status_code=400,
            detail="Pending invitation already exists"
        )
            
    invitation = crud.create_invitation(
        db, 
        request.email, 
        current_user["company_id"], 
        request.expires_at
        )
    
    crud.create_audit_log(
        db, 
        current_user["email"], 
        "Invitation Created", 
        request.email, 
        current_user["company_id"]
        )
    
    return invitation

@router.get("/", response_model=list[schema.InvitationOut])
def list_invitations(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
    ):
    
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )

    return crud.get_invitations(
        db,
        current_user["company_id"]
    )

@router.delete("/{id}")
def revoke_invitation(
    id: int, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
    ):
    if current_user["role"] != "admin":
        raise HTTPException(
        status_code=403,
        detail="Not authorized"
    )
    invitation = db.query(models.Invitation).filter(
        models.Invitation.id == id,
        models.Invitation.company_id == current_user["company_id"]
        ).first()
    if not invitation:
        raise HTTPException(
            status_code=404,
            detail="Invitation not found"
            )
    if invitation.status.value == "revoked":\
        raise HTTPException(
            status_code=400,
            detail="Invitation already revoked"
            )
        
    crud.revoke_invitation(
        db,
        id,
        current_user["company_id"]
        )   
    
    crud.create_audit_log(
        db, 
        current_user["email"], 
        "Invitation Revoked", 
        invitation.email, 
        current_user["company_id"]
        )
    return {"message": "Invitation revoked"}
