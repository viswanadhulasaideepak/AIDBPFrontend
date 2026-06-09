from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
from models import AuditLog

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])

@router.get("/")
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    logs = (
        db.query(AuditLog)
        .filter(AuditLog.company_id == current_user["company_id"])
        .order_by(AuditLog.timestamp.desc())
        .all()
    )

    return [
        {
            "id": log.id,
            "user_name": log.user_name,
            "action": log.action,
            "related_user": log.related_user,
            "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S"), 
            "company_id": log.company_id
        }
        for log in logs
    ]
