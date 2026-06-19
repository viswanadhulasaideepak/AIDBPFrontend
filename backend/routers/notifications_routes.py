from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from database import get_db
from models import Notification, AuditLog
from pydantic import BaseModel
from auth import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])

# ---------------- GET NOTIFICATIONS ----------------
@router.get("/")
def get_notifications(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    notes = (
    db.query(Notification)
    .filter(
        Notification.company_id == current_user["company_id"],
        Notification.recipient_email == current_user["email"]
    )
    .order_by(Notification.created_at.desc())
    .all()
)

    result = []
    
    for n in notes:
        
        item = {
        "id": n.id,
        "message": n.message,
        "recipient_email": n.recipient_email,
        "is_read": n.is_read,
        "created_at": n.created_at,
        "company_id": n.company_id,
        "type": n.type,
        "request_id": n.request_id
        }

        if n.type == "attendance" and n.request_id:
            
            req = db.query(models.AttendanceAccessRequest).filter(
                models.AttendanceAccessRequest.id == n.request_id
                ).first()
        
            if req:
                user = db.query(models.User).filter(
                    models.User.id == req.user_id
                    ).first()
            
                if user:
                    item["user_name"] = user.username
                    item["user_email"] = user.email
                    item["request_timestamp"] = req.created_at
                    item["status"] = req.status
                    
        result.append(item)
                
    return result

# ---------------- MARK AS READ ----------------
@router.put("/{id}/read")
def mark_notification_as_read(
    id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    note = db.query(Notification).filter(
        Notification.id == id,
        Notification.company_id == current_user["company_id"]
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Notification not found")

    if note.is_read:
        return {"message": "Already read"}
    
    note.is_read = True
    db.commit()

    # Audit log entry
    audit = AuditLog(
        user_name=current_user["email"],
        action="Notification Marked as Read",
        related_user=note.recipient_email,
        company_id=current_user["company_id"]
    )
    db.add(audit)
    db.commit()

    return {"message": "Notification marked as read"}

# ---------------- ADD NOTIFICATION (API) ----------------
class NotificationCreate(BaseModel):
    message: str
    recipient_email: str

@router.post("/")
def add_notification(
    request: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    note = Notification(
        message=request.message,
        recipient_email=request.recipient_email,
        is_read=False,
        company_id=current_user["company_id"]
    )
    db.add(note)
    db.commit()
    db.refresh(note)

    # Audit log entry
    audit = AuditLog(
        user_name=current_user["email"],
        action="Notification Created (API)",
        related_user=request.recipient_email,
        company_id=current_user["company_id"]
    )
    db.add(audit)
    db.commit()

    return {
        "id": note.id,
        "message": note.message,
        "recipient_email": note.recipient_email,
        "is_read": note.is_read,
        "created_at": note.created_at,
        "company_id": note.company_id
    }