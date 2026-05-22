import React, { useEffect, useState } from "react";

export default function EmployeeTable({ searchTerm, departmentFilter }) {
  const [employees, setEmployees] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/employees")
      .then((res) => res.json())
      .then((data) => setEmployees(data))
      .catch((err) => console.error("Error fetching employees:", err));
  }, []);

  const filteredEmployees = employees.filter((emp) => {
    const matchesName = emp.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesDept = departmentFilter ? emp.company === departmentFilter : true;
    return matchesName && matchesDept;
  });

  return (
    <div className="card">
      <h3>Employees</h3>
      <table className="employee-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Company</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {filteredEmployees.map((emp) => (
            <tr key={emp.id}>
              <td>{emp.name}</td>
              <td>{emp.email}</td>
              <td>{emp.company}</td>
              <td>
                <span className={`status-badge ${emp.id % 2 === 0 ? "active" : "inactive"}`}>
                  {emp.id % 2 === 0 ? "Active" : "Inactive"}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <button className="primary-btn">+ Add Employee</button>
    </div>
  );
}
