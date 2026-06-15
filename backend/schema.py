from pydantic import BaseModel, EmailStr, ConfigDict
from enum import Enum
from datetime import datetime

model_config = ConfigDict(from_attributes=True)

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
    
    #class Config:
    #    orm_mode = True


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

# ---------------- Invitation Status ----------------
class InvitationStatus(str, Enum):
    pending = "pending"
    revoked = "revoked"
    accepted = "accepted"

class InvitationCreate(BaseModel):
    email: EmailStr
    role: str
    expires_at: datetime | None = None

class InvitationOut(BaseModel):
    id: int
    email: EmailStr
    token: str
    status: InvitationStatus
    created_at: datetime
    expires_at: datetime | None
    company_id: int
    is_used: bool

    class Config:
        orm_mode = True

# ---------------- User Status ----------------
class UserStatus(str, Enum):
    active = "active"
    deactivated = "deactivated"

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    status: UserStatus
    company_id: int

    class Config:
        orm_mode = True
        
class InvitationSignupRequest(BaseModel):
    token: str
    username: str
    password: str
# ---------------- Reactivation Request ----------------
class ReactivationStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class ReactivationRequestCreate(BaseModel):
    message: str | None=None

class ReactivationRequestOut(BaseModel):
    id: int
    user_id: int
    admin_email: EmailStr
    message: str | None
    status: ReactivationStatus
    created_at: datetime
    reviewed_at: datetime | None
    reviewed_by: str | None
    admin_comment: str | None
    company_id: int

    class Config:
        orm_mode = True

class AttendanceAccessStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    
class AttendanceAccessRequestCreate(BaseModel):
    pass

class AttendanceAccessRequestUpdate(BaseModel):
    status: AttendanceAccessStatus
    
class AttendanceAccessRequestOut(BaseModel):
    id: int
    user_id: int
    admin_email: EmailStr
    status: AttendanceAccessStatus
    created_at: datetime
    approved_at: datetime | None = None
    approved_by: str | None = None
    company_id: int

    class Config:
        orm_mode = True        
        
class AttendanceAccessStatusOut(BaseModel):
    status: AttendanceAccessStatus
    submitted_on: datetime        
    
# ---------------- Attendance Check In ----------------

class AttendanceCheckIn(BaseModel):
    employee_id: int


# ---------------- Attendance Check Out ----------------

class AttendanceCheckOut(BaseModel):
    employee_id: int


# ---------------- Today's Attendance ----------------

class AttendanceTodayOut(BaseModel):
    employee_id: int
    date: datetime
    check_in: datetime | None = None
    check_out: datetime | None = None
    working_hours: str | None = None
    status: str

    class Config:
        orm_mode = True


# ---------------- Attendance History ----------------

class AttendanceHistoryOut(BaseModel):
    id: int
    employee_id: int
    date: datetime
    check_in: datetime | None = None
    check_out: datetime | None = None
    working_hours: str | None = None
    status: str

    class Config:
        orm_mode = True    
        
# ---------------- Leave Management ----------------

class LeaveType(str, Enum):
    casual = "casual"
    sick = "sick"
    earned = "earned"
    unpaid = "unpaid"


class LeaveStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class LeaveRequestCreate(BaseModel):
    leave_type: LeaveType
    start_date: datetime
    end_date: datetime
    reason: str


class LeaveRequestUpdate(BaseModel):
    status: LeaveStatus


class LeaveRequestOut(BaseModel):
    id: int
    user_id: int
    company_id: int
    leave_type: LeaveType
    start_date: datetime
    end_date: datetime
    reason: str
    status: LeaveStatus
    created_at: datetime
    reviewed_at: datetime | None = None
    reviewed_by: str | None = None

    class Config:
        orm_mode = True        