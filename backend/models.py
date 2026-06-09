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

#-------------UserModel-----------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")

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
