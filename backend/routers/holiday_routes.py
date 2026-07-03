from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import crud
import schema
import models

from database import get_db
from auth import get_current_user

router = APIRouter(
    prefix="/holidays",
    tags=["Holiday Management"]
)


# ---------------- CREATE HOLIDAY ----------------

@router.post("/", response_model=schema.HolidayOut)
def create_holiday(
    holiday: schema.HolidayCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user["role"].lower() != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admin can create holidays."
        )
    
    existing = (
    db.query(models.Holiday)
    .filter(
        models.Holiday.company_id == current_user["company_id"],
        models.Holiday.holiday_date == holiday.holiday_date
    )
    .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Holiday already exists for this date."
            )    
    
    print(current_user)    

    return crud.create_holiday(
        db=db,
        name=holiday.name,
        description=holiday.description,
        holiday_date=holiday.holiday_date,
        holiday_type=holiday.holiday_type,
        recurring=holiday.recurring,
        company_id=current_user["company_id"],
        created_by=current_user.get("email", current_user["email"])
    )


# ---------------- GET ALL HOLIDAYS ----------------

@router.get("/", response_model=list[schema.HolidayOut])
def get_holidays(
    db: Session =Depends(get_db),
    current_user=Depends(get_current_user)
):
    return crud.get_holidays(
        db=db,
        company_id=current_user["company_id"]
    )


# ---------------- GET SINGLE HOLIDAY ----------------

@router.get("/{holiday_id}", response_model=schema.HolidayOut)
def get_holiday(
    holiday_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    holiday = crud.get_holiday(
        db=db,
        holiday_id=holiday_id,
        company_id=current_user["company_id"]
    )

    if not holiday:
        raise HTTPException(
            status_code=404,
            detail="Holiday not found."
        )

    return holiday


# ---------------- UPDATE HOLIDAY ----------------

@router.put("/{holiday_id}", response_model=schema.HolidayOut)
def update_holiday(
    holiday_id: int,
    holiday: schema.HolidayUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user["role"].lower() != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admin can update holidays."
        )
        
    existing = (
        db.query(models.Holiday)
        .filter(
            models.Holiday.company_id == current_user["company_id"],
            models.Holiday.holiday_date == holiday.holiday_date,
            models.Holiday.id != holiday_id
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Another holiday already exists on this date."
            )    

    updated = crud.update_holiday(
    db=db,
    holiday_id=holiday_id,
    company_id=current_user["company_id"],
    updated_by=current_user["email"],
    name=holiday.name,
    description=holiday.description,
    holiday_date=holiday.holiday_date,
    holiday_type=holiday.holiday_type,
    recurring=holiday.recurring
)

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Holiday not found."
        )

    return updated


# ---------------- DELETE HOLIDAY ----------------

@router.delete("/{holiday_id}")
def delete_holiday(
    holiday_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user["role"].lower() != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admin can delete holidays."
        )

    deleted = crud.delete_holiday(
        db=db,
        holiday_id=holiday_id,
        company_id=current_user["company_id"],
        deleted_by=current_user["email"]
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Holiday not found."
        )

    return {
        "message": "Holiday deleted successfully."
    }