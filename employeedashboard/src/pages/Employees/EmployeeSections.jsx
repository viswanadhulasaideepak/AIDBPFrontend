import React from "react";
import "./EmployeeSections.css";

const EmployeeSections = () => {
  return (
    <div className="employee-sections">
      <div className="section-card">
        <h3>👤 Employee Details</h3>
        <p>Manage employee profiles, roles, and personal information.</p>
      </div>

      <div className="section-card">
        <h3>🏢 Departments</h3>
        <p>View and organize departments, assign employees, and track teams.</p>
      </div>

      <div className="section-card">
        <h3>📅 Attendance</h3>
        <p>Monitor attendance records, leaves, and generate reports.</p>
      </div>
    </div>
  );
};

export default EmployeeSections;
