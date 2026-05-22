import React, { useState } from "react";
import DashboardLayout from "../../components/layout/DashboardLayout";
import EmployeeSearchFilter from "./EmployeeSearchFilter";
import EmployeeTable from "./EmployeeTable";

export default function Employees() {
  const [searchTerm, setSearchTerm] = useState("");
  const [departmentFilter, setDepartmentFilter] = useState("");

  return (
    <DashboardLayout>
      <EmployeeSearchFilter onSearch={setSearchTerm} onFilter={setDepartmentFilter} />
      <EmployeeTable searchTerm={searchTerm} departmentFilter={departmentFilter} />

      <div className="card">
        <h3>Employee Details</h3>
        <p>Preview employee profile here.</p>
      </div>

      <div className="card">
        <h3>Department Section</h3>
        <p>Placeholder for department management.</p>
      </div>

      <div className="card">
        <h3>Attendance Section</h3>
        <p>Placeholder for attendance tracking.</p>
      </div>
    </DashboardLayout>
  );
}
