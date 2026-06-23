import React, { useEffect, useState } from "react";
import { fetchEmployees, addEmployee, updateEmployeeStatus } from "../../services/api";
import toast from "react-hot-toast";
import Skeleton from "react-loading-skeleton";
import "react-loading-skeleton/dist/skeleton.css";
import "./EmployeeDashboard.css";

const EmployeeDashboard = () => {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("all");
  const [newEmp, setNewEmp] = useState({ name: "", email: "", department_id: "" });

  const loadEmployees = async () => {
    try {
      const data = await fetchEmployees();
      setEmployees(data);
    } catch (err) {
      const message = err.response?.data?.detail || err.message;
      setError(message);
      toast.error("Failed to load employees");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEmployees();
  }, []);

  const handleAddEmployee = async (e) => {
    e.preventDefault();
    try {
      await addEmployee(newEmp);
      toast.success("Employee added!");
      setNewEmp({ name: "", email: "", department_id: "" });
      loadEmployees();
    } catch {
      toast.error("Failed to add employee");
    }
  };

  const handleUpdateStatus = async (id, status) => {
    try {
      await updateEmployeeStatus(id, { status });
      toast.success("Status updated!");
      loadEmployees();
    } catch {
      toast.error("Failed to update status");
    }
  };

  const filteredEmployees =
    filter === "all" ? employees : employees.filter((e) => e.status === filter);

  if (loading) return <Skeleton count={6} height={40} />;
  if (error) return <p className="error-text">{error}</p>;

  return (
    <div className="employee-dashboard">
      <h2 className="employee-title">👥 Employee Dashboard</h2>

      {/* Filter */}
      <div className="filter-buttons">
        <button onClick={() => setFilter("all")}>All</button>
        <button onClick={() => setFilter("active")}>Active</button>
        <button onClick={() => setFilter("inactive")}>Inactive</button>
      </div>

      {/* Add Employee Form */}
      <form className="add-employee-form" onSubmit={handleAddEmployee}>
        <input type="text" placeholder="Name"
          value={newEmp.name} onChange={(e) => setNewEmp({ ...newEmp, name: e.target.value })}/>
        <input type="email" placeholder="Email"
          value={newEmp.email} onChange={(e) => setNewEmp({ ...newEmp, email: e.target.value })}/>
        <input type="text" placeholder="Department ID"
          value={newEmp.department_id} onChange={(e) => setNewEmp({ ...newEmp, department_id: e.target.value })}/>
        <button type="submit">Add Employee</button>
      </form>

      {/* Employee Table */}
      <div className="employee-card">
        <table className="employee-table">
          <thead>
            <tr>
              <th>ID</th><th>Name</th><th>Email</th><th>Department</th><th>Status</th><th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredEmployees.map((emp) => (
              <tr key={emp.id}>
                <td>{emp.id}</td>
                <td>{emp.name}</td>
                <td>{emp.email}</td>
                <td>{emp.department_name || "N/A"}</td>
                <td>{emp.status}</td>
                <td>
                  <button onClick={() => handleUpdateStatus(emp.id, "active")}>Activate</button>
                  <button onClick={() => handleUpdateStatus(emp.id, "inactive")}>Deactivate</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default EmployeeDashboard;
