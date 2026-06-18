import React, { useEffect, useState } from "react";
import Skeleton from "react-loading-skeleton";
import "react-loading-skeleton/dist/skeleton.css";
import toast from "react-hot-toast";
import DashboardLayout from "../../components/layout/DashboardLayout";
import AddEmployeeForm from "./AddEmployeeForm";
import EditEmployeeForm from "./EditEmployeeForm";
import {
  fetchEmployees,
  updateEmployee,
  deleteEmployee,
} from "../../services/api";

import "./Employees.css";

const Employees = () => {
  const [employees, setEmployees] = useState([]);
  const [filteredEmployees, setFilteredEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [searchTerm, setSearchTerm] = useState("");
  const [departmentFilter, setDepartmentFilter] = useState("All");

  const [showAddForm, setShowAddForm] = useState(false);
  const [editEmployee, setEditEmployee] = useState(null);

  const [currentPage, setCurrentPage] = useState(1);
  const [employeesPerPage, setEmployeesPerPage] = useState(5);

  /* ---------------- FETCH EMPLOYEES ---------------- */
  useEffect(() => {
    const loadEmployees = async () => {
      try {
        const data = await fetchEmployees();

        const formatted = data.map((emp) => ({
          ...emp,
          joined_date: emp.joined_date || null,
        }));

        setEmployees(formatted);
        setFilteredEmployees(formatted);
      } catch (err) {
        console.error(err);
        setError("Failed to load employees");
        toast.error("Failed to load employees");
      } finally {
        setLoading(false);
      }
    };

    loadEmployees();
  }, []);

  /* ---------------- SEARCH + FILTER ---------------- */
  useEffect(() => {
    const term = searchTerm.toLowerCase();

    const filtered = employees.filter((emp) => {
      const matchesSearch =
        emp.name?.toLowerCase().includes(term) ||
        emp.email?.toLowerCase().includes(term) ||
        emp.role?.toLowerCase().includes(term);

      const matchesDept =
        departmentFilter === "All" ||
        emp.department_name === departmentFilter;

      return matchesSearch && matchesDept;
    });

    setFilteredEmployees(filtered);
    setCurrentPage(1);
  }, [searchTerm, departmentFilter, employees]);

  /* ---------------- STATUS UPDATE ---------------- */
  const handleStatusChange = async (id, newStatus) => {
    try {
      const emp = employees.find((e) => e.id === id);

      const payload = {
        name: emp.name,
        email: emp.email,
        role: emp.role,
        department_name: emp.department_name,
        joined_date: emp.joined_date?.slice(0, 10),
        status: newStatus,
      };

      await updateEmployee(id, payload);

      const updated = employees.map((e) =>
        e.id === id ? { ...e, status: newStatus } : e
      );

      setEmployees(updated);
      setFilteredEmployees(updated);

      toast.success("Status updated");
    } catch (err) {
      console.error(err);
      toast.error("Status update failed");
    }
  };

  /* ---------------- DELETE EMPLOYEE ---------------- */
  const handleDeleteEmployee = async (id) => {
    try {
      await deleteEmployee(id);

      const updated = employees.filter((e) => e.id !== id);

      setEmployees(updated);
      setFilteredEmployees(updated);

      toast.success("Employee deleted");
    } catch (err) {
      console.error(err);
      toast.error("Delete failed");
    }
  };

  /* ---------------- ADD EMPLOYEE ---------------- */
  const handleAddEmployee = (newEmp) => {
    const updated = [...employees, newEmp];
    setEmployees(updated);
    setFilteredEmployees(updated);
    toast.success("Employee added");
  };

  /* ---------------- EDIT EMPLOYEE ---------------- */
  const handleEditEmployee = async (updatedEmp) => {
    try {
      const payload = {
        name: updatedEmp.name,
        email: updatedEmp.email,
        role: updatedEmp.role,
        department_name: updatedEmp.department_name,
        joined_date: updatedEmp.joined_date?.slice(0, 10),
        status: updatedEmp.status,
      };

      await updateEmployee(updatedEmp.id, payload);

      const updated = employees.map((e) =>
        e.id === updatedEmp.id ? updatedEmp : e
      );

      setEmployees(updated);
      setFilteredEmployees(updated);

      toast.success("Employee updated");
      setEditEmployee(null);
    } catch (err) {
      console.error(err);
      toast.error("Update failed");
    }
  };

  /* ---------------- PAGINATION ---------------- */
  const indexOfLast = currentPage * employeesPerPage;
  const indexOfFirst = indexOfLast - employeesPerPage;
  const currentEmployees = filteredEmployees.slice(
    indexOfFirst,
    indexOfLast
  );

  const totalPages = Math.ceil(
    filteredEmployees.length / employeesPerPage
  );

  const uniqueDepartments = [
    "All",
    ...new Set(employees.map((e) => e.department_name).filter(Boolean)),
  ];

  if (loading)
    return <Skeleton count={6} height={40} />;

  if (error)
    return <p className="error-text">{error}</p>;

  return (
    <DashboardLayout>
      <div className="employees-container">

        {/* HEADER */}
        <div className="employees-header">
          <h2>Employees</h2>
          <p>Manage employees efficiently</p>
        </div>

        {/* CONTROLS */}
        <div className="employees-actions">

          <input
            type="text"
            placeholder="Search..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />

          <select
            value={departmentFilter}
            onChange={(e) => setDepartmentFilter(e.target.value)}
          >
            {uniqueDepartments.map((d, i) => (
              <option key={i} value={d}>
                {d}
              </option>
            ))}
          </select>

          <button onClick={() => setShowAddForm(true)}>
            + Add Employee
          </button>

          <select
            value={employeesPerPage}
            onChange={(e) => {
              setEmployeesPerPage(Number(e.target.value));
              setCurrentPage(1);
            }}
          >
            <option value={5}>5</option>
            <option value={10}>10</option>
            <option value={20}>20</option>
          </select>

        </div>

        {/* TABLE */}
        <div className="employees-card">

          {currentEmployees.length === 0 ? (
            <p>No employees found</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Role</th>
                  <th>Department</th>
                  <th>Status</th>
                  <th>Joined</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {currentEmployees.map((emp) => (
                  <tr key={emp.id}>

                    <td>
                      <b>{emp.name}</b>
                      <div>{emp.email}</div>
                    </td>

                    <td>{emp.role}</td>

                    <td>{emp.department_name}</td>

                    <td>
                      <select
                        value={emp.status}
                        onChange={(e) =>
                          handleStatusChange(emp.id, e.target.value)
                        }
                      >
                        <option value="active">Active</option>
                        <option value="inactive">Inactive</option>
                        <option value="onleave">On Leave</option>
                      </select>
                    </td>

                    <td>
                      {emp.joined_date
                        ? new Date(emp.joined_date).toLocaleDateString()
                        : "N/A"}
                    </td>

                    <td>
                      <button onClick={() => setEditEmployee(emp)}>
                        Edit
                      </button>

                      <button onClick={() => handleDeleteEmployee(emp.id)}>
                        Delete
                      </button>
                    </td>

                  </tr>
                ))}
              </tbody>
            </table>
          )}

        </div>

        {/* PAGINATION */}
        <div className="pagination">
          <button
            disabled={currentPage === 1}
            onClick={() =>
              setCurrentPage((p) => Math.max(p - 1, 1))
            }
          >
            Prev
          </button>

          {Array.from({ length: totalPages }, (_, i) => (
            <button
              key={i}
              className={currentPage === i + 1 ? "active" : ""}
              onClick={() => setCurrentPage(i + 1)}
            >
              {i + 1}
            </button>
          ))}

          <button
            disabled={currentPage === totalPages}
            onClick={() =>
              setCurrentPage((p) =>
                Math.min(p + 1, totalPages)
              )
            }
          >
            Next
          </button>
        </div>

        {/* MODALS */}
        {showAddForm && (
          <AddEmployeeForm
            onAdd={handleAddEmployee}
            onClose={() => setShowAddForm(false)}
          />
        )}

        {editEmployee && (
          <EditEmployeeForm
            employee={editEmployee}
            onSave={handleEditEmployee}
            onClose={() => setEditEmployee(null)}
          />
        )}

      </div>
    </DashboardLayout>
  );
};

export default Employees;