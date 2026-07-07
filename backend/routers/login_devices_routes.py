from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import crud
import schema
import models

from database import get_db
from auth import require_active_user, require_admin

router = APIRouter(prefix="/login-devices",tags=["Login Devices"])

admin_router = APIRouter(prefix="/admin/login-devices",tags=["Admin Login Devices"])

#-----------------Get My Devices------------------
@router.get("/", response_model=list[schema.LoginSessionOut])
def get_my_devices(
    current_user=Depends(require_active_user),
    db: Session = Depends(get_db)
):
    return crud.get_user_sessions(
        db,
        current_user["id"]
    )
    
#-----------------Rename Trusted Device----------------    
@router.patch("/{session_id}/rename")
def rename_device(
    session_id: int,
    request: schema.RenameTrustedDeviceRequest,
    current_user=Depends(require_active_user),
    db: Session = Depends(get_db)
):

    session = crud.rename_trusted_device(
        db=db,
        session_id=session_id,
        user_id=current_user["id"],
        device_name=request.device_name
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Trusted device not found."
        )

    return {
        "message": "Trusted device renamed successfully."
    }
    
#-----------------Remove Trusted Device-----------------
    
@router.delete("/{session_id}/trusted")
def remove_trusted_device(
    session_id: int,
    current_user=Depends(require_active_user),
    db: Session = Depends(get_db)
):

    session = crud.remove_trusted_device(
        db=db,
        session_id=session_id,
        user_id=current_user["id"]
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Trusted device not found."
        )

    return {
        "message": "Trusted device removed."
    }

#-----------------Logout Selected Device-------------------

@router.post("/{session_id}/logout")
def logout_device(
    session_id: int,
    current_user=Depends(require_active_user),
    db: Session = Depends(get_db)
):

    db_session = (
        db.query(models.LoginSession)
        .filter(
            models.LoginSession.id == session_id,
            models.LoginSession.user_id == current_user["id"]
        )
        .first()
    )

    if not db_session:
        raise HTTPException(
            status_code=404,
            detail="Session not found."
        )

    session = crud.logout_session(
        db=db,
        session_identifier=db_session.session_identifier,
        user_id=current_user["id"]
    )

    if not session:
        raise HTTPException(
            status_code=400,
            detail="Session is already logged out or inactive."
        )

    return {
        "message": "Device logged out successfully."
    }
    
#--------------Logout All Devices Except Current Device-----------------    
    
@router.post("/logout-all")
def logout_all_devices(
    current_user=Depends(require_active_user),
    db: Session = Depends(get_db)
):

    count = crud.logout_other_sessions(
        db=db,
        user_id=current_user["id"],
        current_session_identifier=current_user["session_identifier"]
    )

    return {
        "message": f"{count} session(s) logged out."
    }           
    
#---------------Admin Sessions-----------------

@admin_router.get("/",response_model=list[schema.LoginSessionAdminOut])

def company_sessions(
    current_user=Depends(require_admin),
    db: Session = Depends(get_db)
):

    return crud.get_company_sessions(
        db=db,
        company_id=current_user["company_id"]
    )
    
#---------------Force Logout-----------------
@admin_router.post("/{session_id}/force-logout")
def force_logout(
    session_id: int,
    current_user=Depends(require_admin),
    db: Session = Depends(get_db)
):

    session = crud.force_logout_session(
        db=db,
        session_id=session_id,
        company_id=current_user["company_id"],
        performed_by=current_user["email"]
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found."
        )

    return {
        "message": "Session forcefully logged out."
    }
    
#-----------------Revoke Session-------------------

@admin_router.post("/{session_id}/revoke")
def revoke_session(
    session_id: int,
    current_user=Depends(require_admin),
    db: Session = Depends(get_db)
):

    session = crud.revoke_session(
        db=db,
        session_id=session_id,
        company_id=current_user["company_id"],
        performed_by=current_user["email"]
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found."
        )

    return {
        "message": "Session revoked successfully."
    }        
    
#-----------------Bulk Revoke Sessions-------------------

@admin_router.post("/bulk-revoke")
def bulk_revoke_sessions(
    request: schema.BulkRevokeRequest,
    current_user=Depends(require_admin),
    db: Session = Depends(get_db)
):

    count = crud.revoke_multiple_sessions(
        db=db,
        session_ids=request.session_ids,
        company_id=current_user["company_id"],
        performed_by=current_user["email"]
    )

    return {
        "message": f"{count} session(s) revoked successfully."
    }
   
#-------------------Trust Device-------------------                
    
@router.post("/{session_id}/trust")
def trust_device(
    session_id: int,
    current_user=Depends(require_active_user),
    db: Session = Depends(get_db)
):

    session = crud.trust_device(
        db=db,
        session_id=session_id,
        user_id=current_user["id"]
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Device not found."
        )

    return {
        "message": "Device marked as trusted."
    }    