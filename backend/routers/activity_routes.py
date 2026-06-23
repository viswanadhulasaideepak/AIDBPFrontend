from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import crud
import database
import schema
from auth import get_current_user

router = APIRouter(
    prefix="/activity",
    tags=["Activity"]
)

# -------------------Company User Activity-----------------

@router.get(
    "/users",
    response_model=list[schema.UserActivityAdminOut]
)
def company_user_activity(
    db: Session = Depends(database.get_db),
    current_user=Depends(get_current_user),
):
    return crud.get_company_user_activity(
        db=db,
        company_id=current_user["company_id"]
    )

#----------- Activity History--------------

@router.get(
    "/history",
    response_model=list[schema.ActivityHistoryOut]
)
def activity_history(
    db: Session = Depends(database.get_db),
    current_user=Depends(get_current_user),
):
    return crud.get_user_activity_history(
        db=db,
        company_id=current_user["company_id"]
    )