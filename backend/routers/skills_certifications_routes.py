from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import os
import shutil
from datetime import date as certification_date
import crud
import schema
import auth
from database import get_db
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
)

router = APIRouter(prefix="/skills",tags=["Employee Skills & Certifications"])

UPLOAD_FOLDER = "uploads/certifications"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- Allowed Certificate File Types ----------------

ALLOWED_CERTIFICATE_TYPES = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg"
}

#--------------------Get My Skills---------------------

@router.get(
    "/my-skills",
    response_model=list[schema.EmployeeSkillOut]
)
def get_my_skills(
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user)
):

    employee = crud.get_employee_by_email(
    db,
    current_user["email"],
    current_user["company_id"]
)
    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found."
        )

    return crud.get_employee_skills(
        db,
        employee.id,
        current_user["company_id"]
    )
    
#---------------------Add Skills-----------------
    
@router.post(
    "/my-skills",
    response_model=schema.EmployeeSkillOut
)
def add_skill(
    skill: schema.EmployeeSkillCreate,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user)
):

    employee = crud.get_employee_by_email(
    db,
    current_user["email"],
    current_user["company_id"]
)

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found."
        )

    try:

        return crud.create_employee_skill(
            db=db,
            employee_id=employee.id,
            company_id=current_user["company_id"],
            skill_name=skill.skill_name,
            proficiency=skill.proficiency,
            years_experience=skill.years_experience,
            is_primary=skill.is_primary,
            performed_by=current_user["email"]
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
        
#---------------------Update Skills---------------------        
        
@router.put(
    "/my-skills/{skill_id}",
    response_model=schema.EmployeeSkillOut
)
def update_skill(
    skill_id: int,
    skill: schema.EmployeeSkillCreate,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user)
):

    try:

        updated = crud.update_employee_skill(
            db=db,
            skill_id=skill_id,
            company_id=current_user["company_id"],
            skill_name=skill.skill_name,
            proficiency=skill.proficiency,
            years_experience=skill.years_experience,
            is_primary=skill.is_primary,
            performed_by=current_user["email"]
        )

        if not updated:
            raise HTTPException(
                status_code=404,
                detail="Skill not found."
            )

        return updated

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )          
        
#--------------------Delete Skills-----------------------

@router.delete("/my-skills/{skill_id}")
def delete_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user)
):

    deleted = crud.delete_employee_skill(
        db,
        skill_id,
        current_user["company_id"],
        current_user["email"]
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Skill not found."
        )

    return {
        "message": "Skill deleted successfully."
    }
    
#----------------------Get My Certifications----------------------
    
@router.get(
    "/my-certifications",
    response_model=list[schema.EmployeeCertificationOut]
)
def get_my_certifications(
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user)
):

    employee = crud.get_employee_by_email(
    db,
    current_user["email"],
    current_user["company_id"]
)

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found."
        )

    return crud.get_employee_certifications(
        db,
        employee.id,
        current_user["company_id"]
    )

#----------------Active Certifications--------------------
    
@router.get("/my-certifications/active")
def get_active_certifications(
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user)
):
    employee = crud.get_employee_by_email(
    db,
    current_user["email"],
    current_user["company_id"]
)

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found."
        )

    return crud.get_active_certifications(
        db,
        employee.id,
        current_user["company_id"]
    )
    
#----------------Expired Certifications-------------------    
    
@router.get("/my-certifications/expired")
def get_expired_certifications(
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user)
):
    employee = crud.get_employee_by_email(
    db,
    current_user["email"],
    current_user["company_id"]
)

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found."
        )

    return crud.get_expired_certifications(
        db,
        employee.id,
        current_user["company_id"]
    )        
    
#--------------------------Add Certifications-------------------------

@router.post(
    "/my-certifications",
    response_model=schema.EmployeeCertificationOut
)
def add_certification(
    certification_name: str = Form(...),
    issuing_organization: str = Form(...),
    issue_date: str = Form(...),
    expiry_date: str | None = Form(None),
    document: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user)
):

    employee = crud.get_employee_by_email(
        db,
        current_user["email"],
        current_user["company_id"]
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found."
        )

    file_path = None

    # Upload certificate (optional)
    if document:

        extension = os.path.splitext(document.filename)[1].lower()

        if extension not in ALLOWED_CERTIFICATE_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type."
            )

        filename = f"{employee.id}_{document.filename}"

        file_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(
                document.file,
                buffer
            )

    try:

        return crud.create_employee_certification(
            db=db,
            employee_id=employee.id,
            company_id=current_user["company_id"],
            certification_name=certification_name,
            issuing_organization=issuing_organization,
            issue_date=certification_date.fromisoformat(issue_date),
            expiry_date=(
                certification_date.fromisoformat(expiry_date)
                if expiry_date
                else None
            ),
            document_path=file_path,
            performed_by=current_user["email"]
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )    
                  
#--------------------Update Certifications--------------------

@router.put(
    "/my-certifications/{certification_id}",
    response_model=schema.EmployeeCertificationOut
)
def update_certification(
    certification_id: int,
    certification: schema.EmployeeCertificationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user)
):

    updated = crud.update_employee_certification(
        db=db,
        certification_id=certification_id,
        company_id=current_user["company_id"],
        certification_name=certification.certification_name,
        issuing_organization=certification.issuing_organization,
        issue_date=certification.issue_date,
        expiry_date=certification.expiry_date,
        document_path=None,
        performed_by=current_user["email"]
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Certification not found."
        )

    return updated              

#----------------------Delete Certifications-------------------

@router.delete(
    "/my-certifications/{certification_id}"
)
def delete_certification(
    certification_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user)
):

    deleted = crud.delete_employee_certification(
        db,
        certification_id,
        current_user["company_id"],
        current_user["email"]
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Certification not found."
        )

    return {
        "message": "Certification deleted successfully."
    }
    
#--------------Admin - Search Employees by Skill----------------

@router.get("/admin/search")
def search_employee_skill(
    skill: str,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_admin)
):

    return crud.search_employees_by_skill(
        db,
        current_user["company_id"],
        skill
    )
    
#--------------Admin Competency Filters--------------------

@router.post("/admin/filter-competencies")
def filter_competencies(
    filters: schema.CompetencyFilter,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_admin)
):

    return crud.filter_employee_competencies(
        db=db,
        company_id=current_user["company_id"],
        skill=filters.skill,
        skill_level=filters.skill_level,
        min_years_experience=filters.min_years_experience,
        certification_name=filters.certification_name,
        certification_status=filters.certification_status,
    )
    
#--------------Employee Competency Profile--------------------

@router.get("/admin/profile/{employee_id}")
def employee_competency_profile(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_admin)
):

    profile = crud.get_employee_competency_profile(
        db,
        employee_id,
        current_user["company_id"]
    )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Employee not found."
        )

    return profile

#---------------------Employee Dashboard Summary----------------

@router.get("/my-summary")
def my_summary(
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user)
):

    employee = crud.get_employee_by_email(
    db,
    current_user["email"],
    current_user["company_id"]
)

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found."
        )

    return crud.get_employee_skill_summary(
        db,
        employee.id,
        current_user["company_id"]
    )
    
#----------------Expiring Certifications only for Admins---------------
    
@router.get("/admin/expiring")
def get_expiring_certifications(
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_admin)
):
    return crud.get_expiring_certifications(
        db,
        current_user["company_id"]
    )    
    
#------------------Export Competency Report-----------------

@router.get("/admin/export")
def export_competency_report(
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_admin)
):

    return crud.get_competency_export(
        db,
        current_user["company_id"]
    )                    