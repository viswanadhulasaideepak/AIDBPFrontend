from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, Boolean
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

#------------------AttendanceModel------------------    
class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, nullable=False)

    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", backref="attendance_records")

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

#--------------------AuditLog--------------------
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, nullable=False)
    action = Column(String, nullable=False)
    related_user = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    performed_by = Column(String)

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
