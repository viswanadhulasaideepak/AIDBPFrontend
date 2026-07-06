from pydantic import BaseModel, EmailStr, ConfigDict
from enum import Enum
from datetime import datetime
from typing import Optional

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
    first_name: str | None = None
    last_name: str | None = None

    email: EmailStr
    role: str

    phone_number: str | None = None
    designation: str | None = None
    profile_picture: str | None = None
    address: str | None = None

    status: StatusEnum = StatusEnum.active

class EmployeeCreate(EmployeeBase):
    company_id: int
    employee_code: str | None = None
    joined_date: datetime | None = None
     
class EmployeeOut(EmployeeBase):
    id: int
    company_id: int

    employee_code: str | None = None
    joined_date: datetime | None = None

    profile_completion: int = 0

    class Config:
        orm_mode = True

class EmployeeUpdate(BaseModel):
    name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    
    email: EmailStr | None = None
    role: str | None = None

    phone_number: str | None = None
    designation: str | None = None
    profile_picture: str | None = None
    address: str | None = None

    department_name: str | None = None
    joined_date: datetime | None = None
    status: StatusEnum | None = None
    employee_code: str | None = None
    
class ProfileCompletionOut(BaseModel):
    employee_id: int
    employee_name: str

    completion_percentage: int
    completed_fields: int
    total_fields: int

    missing_fields: list[str]
    recommendation: str
    
class EmployeeProfileCompletionOut(BaseModel):
    employee_id: int

    employee_name: str
    role: str

    company_id: int
    completion_percentage: int

    department: str | None = None
    designation: str | None = None        

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

    ip_address: str | None = None
    browser: str | None = None
    is_new_device: bool = False
    is_new_ip: bool = False
    details: str | None = None
    performed_by: str | None = None

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
        
class DepartmentTransferRequest(BaseModel):
    new_department_id: int
    reason: Optional[str] = None        
        
class DepartmentTransferResponse(BaseModel):
    message: str
    employee_id: int
    old_department: str
    new_department: str
    transferred_at: datetime        
    
class DepartmentTransferHistoryOut(BaseModel):
    id: int
    employee_id: int
    old_department: str
    new_department: str
    transferred_by: str
    reason: str | None = None
    transferred_at: datetime

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
    
    class Config:
        orm_mode = True

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
    suspended = "suspended"
    deactivated = "deactivated"

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    status: UserStatus
    company_id: int
    
    suspended_at: datetime | None = None
    suspended_by: str | None = None
    suspended_reason: str | None = None


    class Config:
        orm_mode = True
        
class SuspensionRequest(BaseModel):
    reason: str        
        
class UserActivityOut(BaseModel):
    user_id: int
    company_id: int

    last_login: datetime | None = None
    last_logout: datetime | None = None

    browser: str | None = None
    ip_address: str | None = None

    class Config:
        orm_mode = True    
        
class UserActivityAdminOut(BaseModel):
    username: str
    email: str

    last_login: datetime | None = None
    last_logout: datetime | None = None

    browser: str | None = None
    ip_address: str | None = None

    class Config:
        orm_mode = True         
        
class ActivityHistoryOut(BaseModel):
    user_name: str
    action: str
    related_user: str | None = None
    timestamp: datetime
    performed_by: str | None = None
    browser: str | None = None
    ip_address: str | None = None
    is_new_device: bool = False
    is_new_ip: bool = False
    details: str | None = None

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
        
 #-----------Reinstatement Request------------
 
class ReinstatementStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    
class ReinstatementRequestCreate(BaseModel):
    reason: str
    
class ReinstatementReview(BaseModel):
    admin_comment: str | None = None
    
class ReinstatementRequestOut(BaseModel):
    id: int
    user_id: int
    company_id: int

    request_reason: str
    
    status: ReinstatementStatus
    submitted_at: datetime
    reviewed_at: datetime | None = None

    reviewed_by: str | None = None
    admin_comment: str | None = None

    class Config:
        orm_mode = True     
        
#--------------Suspend User Request--------------------        
        
class SuspendUserRequest(BaseModel):
    reason: str        
        
  #--------Account Status Out------------
        
class AccountStatusOut(BaseModel):
    status: str

    suspended_at: datetime | None = None

    suspended_by: str | None = None
    suspensded_reason: str | None = None
    deactivated_by: str | None = None
    deactivated_reason: str | None = None           
                

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
        
#------ Data Export Center----------

class ExportFormat(str, Enum):
    csv = "csv"
    excel = "excel"
    pdf = "pdf"

class ExportDataType(str, Enum):
    employees = "employees"
    attendance = "attendance"
    leave_requests = "leave_requests"
    audit_logs = "audit_logs"
    notifications = "notifications"
    analytics = "analytics"

class ExportHistoryOut(BaseModel):
    id: int
    exported_by: str
    data_type: ExportDataType
    export_format: ExportFormat
    exported_at: datetime
    company_id: int

    class Config:
        orm_mode = True        
        
# ---------------- Holiday Management ----------------

class HolidayType(str, Enum):
    public = "Public Holiday"
    company = "Company Holiday"
    optional = "Optional Holiday"


class HolidayCreate(BaseModel):
    name: str
    holiday_date: datetime
    description: str | None = None
    holiday_type: HolidayType
    recurring: bool = False


class HolidayUpdate(BaseModel):
    name: str | None = None
    holiday_date: datetime | None = None
    description: str | None = None
    holiday_type: HolidayType | None = None
    recurring: bool | None = None


class HolidayOut(BaseModel):
    id: int
    name: str
    holiday_date: datetime
    description: str | None = None
    holiday_type: HolidayType
    recurring: bool
    company_id: int
    created_at: datetime

    class Config:
        orm_mode = True                    
        
# ---------------- Login Session ----------------

class SessionStatus(str, Enum):
    active = "active"
    logged_out = "logged_out"
    revoked = "revoked"
    expired = "expired"


class SessionTerminationReason(str, Enum):
    user_logout = "User Logout"
    force_logout = "Force Logout"
    session_expired = "Session Expired"
    revoked = "Revoked"        
    
class LoginSessionOut(BaseModel):
    id: int
    session_identifier: str
    
    user_email: str | None = None

    user_id: int
    company_id: int

    device_name: str
    browser: str | None = None
    ip_address: str | None = None

    login_time: datetime
    last_activity: datetime

    status: SessionStatus

    termination_reason: SessionTerminationReason | None = None

    is_trusted: bool
    is_current: bool

    logged_out_at: datetime | None = None
    revoked_at: datetime | None = None
    expires_at: datetime | None = None

    class Config:
        orm_mode = True
        
class LoginSessionAdminOut(BaseModel):
    id: int

    session_identifier: str

    username: str
    email: EmailStr

    company_id: int

    device_name: str
    browser: str | None = None
    ip_address: str | None = None

    login_time: datetime
    last_activity: datetime

    status: SessionStatus
    termination_reason: SessionTerminationReason | None = None

    is_trusted: bool
    is_current: bool

    class Config:
        orm_mode = True
        
class RenameTrustedDeviceRequest(BaseModel):
    device_name: str
    
class SessionActionRequest(BaseModel):
    pass                        