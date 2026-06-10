from pydantic import BaseModel, EmailStr
from enum import Enum
from datetime import datetime


class StatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"
    onleave = "onleave"
    
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role:str
    company_name: str

class EmployeeBase(BaseModel):
    name: str
    email: str
    role: str
    status: StatusEnum = StatusEnum.active

class EmployeeCreate(EmployeeBase):
    company_id: int
    
    class Config:
        orm_mode = True


class EmployeeUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    role: str | None = None
    department_name: str | None = None
    joined_date: datetime | None = None
    status: StatusEnum | None = None


# Role change request status
class RoleChangeStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

# User submits a role change request
class RoleChangeRequestCreate(BaseModel):
    current_password: str
    admin_email: EmailStr

# Admin updates (approve/reject)
class RoleChangeRequestUpdate(BaseModel):
    status: RoleChangeStatus

# Response model for requests
class RoleChangeRequestOut(BaseModel):
    id: int
    user_id: int
    admin_email: EmailStr
    status: RoleChangeStatus
    created_at: datetime

    class Config:
        orm_mode = True

class EmployeeCreate(EmployeeBase):
    company_id: int   # ensure employees are tied to a company

class EmployeeOut(EmployeeBase):
    id: int
    company_id: int

    class Config:
        orm_mode = True

class NotificationOut(BaseModel):
    id: int
    message: str
    recipient_email: EmailStr
    is_read: bool
    created_at: datetime
    company_id: int

    class Config:
        orm_mode = True

class AuditLogOut(BaseModel):
    id: int
    user_name: str
    action: str
    related_user: str | None
    timestamp: datetime
    company_id: int

    class Config:
        orm_mode = True

class AttendanceCreate(BaseModel):
    employee_id: int
    date: datetime
    status: str
    company_id: int

class AttendanceOut(BaseModel):
    id: int
    employee_id: int
    date: datetime
    status: str
    company_id: int

    class Config:
        orm_mode = True

class DepartmentOut(BaseModel):
    id: int
    name: str
    company_id: int

    class Config:
        orm_mode = True

class DashboardStatsOut(BaseModel):
    total_employees: int
    active_employees: int
    departments: int
    attendance_percentage: int
    role_distribution: list[dict]
    status_overview: list[dict]
    pending_requests: int
