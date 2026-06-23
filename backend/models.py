from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum

# Define allowed statuses
class StatusEnum(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    onleave = "onleave"

#-------------DepartmentModel--------
class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", back_populates="departments")
    employees = relationship("Employee", back_populates="department_rel")
    
#------------DepartmentTransfer-----------------    
class DepartmentTransfer(Base):
    __tablename__ = "department_transfers"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    old_department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    new_department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    transferred_by = Column(String, nullable=False)
    transferred_at = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    reason = Column(String, nullable=True)
    employee = relationship("Employee")
    old_department = relationship("Department",foreign_keys=[old_department_id])
    new_department = relationship("Department",foreign_keys=[new_department_id])
    company = relationship("Company")

#-------------EmployeeModel-----------
class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    joined_date = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(StatusEnum), default=StatusEnum.active, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    department_rel = relationship("Department", back_populates="employees")
    company = relationship("Company", back_populates="employees") 
    
# ---------------- User Status ----------------
class UserStatus(str, enum.Enum):
    active = "active"
    deactivated = "deactivated"    

#-------------UserModel-----------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")
    status = Column(Enum(UserStatus), default=UserStatus.active, nullable=False)
    deactivated_by = Column(String, nullable=True) 
    deactivated_reason = Column(String, nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", back_populates="users")
    activity = relationship("UserActivity", back_populates="user", uselist=False, cascade="all, delete-orphan")

#---------------New User Model Activity-------------

class UserActivity(Base):
    __tablename__ = "user_activity"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    last_login = Column(DateTime, nullable=True)
    last_logout = Column(DateTime, nullable=True)
    last_activity = Column(DateTime)
    login_count = Column(Integer, default=0)
    is_online = Column(Boolean, default=False)
    browser = Column(String(255), nullable=True)
    ip_address = Column(String(100), nullable=True)
    device_hash = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="activity")
    company = relationship("Company", back_populates="activities")
    
#------------------AttendanceModel------------------    
class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, nullable=False)
    check_in = Column(DateTime, nullable=True)
    check_out = Column(DateTime, nullable=True)
    working_hours = Column(String, nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", backref="attendance_records")
    
 #---------AttendanceAccessRequest------------   
    
class AttendanceAccessStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    
class AttendanceAccessRequest(Base):
    __tablename__ = "attendance_access_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    admin_email = Column(String, nullable=False)
    status = Column(Enum(AttendanceAccessStatus),default=AttendanceAccessStatus.pending,
        nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(String, nullable=True)
    user = relationship("User", backref="attendance_requests")   
    
# ---------------- Leave Management ----------------

class LeaveType(str, enum.Enum):
    casual = "casual"
    sick = "sick"
    earned = "earned"
    unpaid = "unpaid"

class LeaveStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    leave_type = Column( Enum(LeaveType), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    reason = Column(String, nullable=False)
    status = Column( Enum(LeaveStatus), default=LeaveStatus.pending, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime)
    reviewed_by = Column(String)
    user = relationship("User", backref="leave_requests")
    company = relationship("Company", back_populates="leave_requests")             

#-----------------Notifications-----------------    
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String)
    recipient_email = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", back_populates="notifications")
    request_id = Column(Integer, nullable=True)
    type = Column(String, nullable=True)

#----------------------RoleChangeRequestModel-------------------
class RoleChangeStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class RoleChangeRequest(Base):
    __tablename__ = "role_change_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    admin_email = Column(String, nullable=False)
    status = Column(Enum(RoleChangeStatus), default=RoleChangeStatus.pending, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    user = relationship("User", backref="role_requests")

#------------------CompanyModel---------    
class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    domain = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    invitations = relationship("Invitation", back_populates="company")
    departments = relationship("Department", back_populates="company")
    notifications = relationship("Notification", back_populates="company")
    employees = relationship("Employee", back_populates="company")
    users = relationship("User", back_populates="company")
    leave_requests = relationship("LeaveRequest", back_populates="company")
    activities = relationship("UserActivity", back_populates="company")
    export_history = relationship("ExportHistory", back_populates="company",cascade="all, delete-orphan")

#--------------------AuditLog--------------------
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, nullable=False)
    action = Column(String, nullable=False)
    related_user = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    target_employee_id = Column(Integer, ForeignKey("employees.id"))
    target_employee = relationship("Employee")
    company = relationship("Company", backref="audit_logs")
    performed_by = Column(String)
    ip_address = Column(String(100), nullable=True)
    browser = Column(String(255), nullable=True)
    is_new_device = Column(Boolean, default=False)
    is_new_ip = Column(Boolean, default=False)
    details = Column(Text, nullable=True)
# ---------------- Invitation Status ----------------
class InvitationStatus(str, enum.Enum):
    pending = "pending"
    revoked = "revoked"
    accepted = "accepted"

class Invitation(Base):
    __tablename__ = "invitations"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    role = Column(String, nullable=False)
    is_used = Column(Boolean, default=False)
    token = Column(String, unique=True, nullable=False)
    status = Column(Enum(InvitationStatus), default=InvitationStatus.pending, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", back_populates="invitations")

# ---------------- Reactivation Request ----------------
class ReactivationStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class ReactivationRequest(Base):
    __tablename__ = "reactivation_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    admin_email = Column(String, nullable=False)
    message = Column(String, nullable=True)
    reviewed_at = Column(DateTime)
    reviewed_by = Column(String)
    admin_comment = Column(String)
    status = Column(Enum(ReactivationStatus), default=ReactivationStatus.pending, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    user = relationship("User", backref="reactivation_requests")

# -------------------Export History-----------------------

class ExportHistory(Base):
    __tablename__ = "export_history"

    id = Column(Integer, primary_key=True, index=True)
    exported_by = Column(String, nullable=False)
    data_type = Column(String, nullable=False)
    export_format = Column(String, nullable=False)
    exported_at = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", back_populates="export_history")