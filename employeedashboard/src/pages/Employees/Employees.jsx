import React, { useEffect, useState } from "react";
import Skeleton from "react-loading-skeleton";
import "react-loading-skeleton/dist/skeleton.css";
import toast from "react-hot-toast";
import { fetchEmployees } from "../../services/api";
import DashboardLayout from "../../components/layout/DashboardLayout";
import AddEmployeeForm from "./AddEmployeeForm";
import EditEmployeeForm from "./EditEmployeeForm";
import { getEmployees, addEmployee, updateEmployee, deleteEmployee } from "../../services/api";
import "./Employees.css";

const Employees = () => {
  const [employees, setEmployees] = useState([]);
  const [filteredEmployees, setFilteredEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [showAddForm, setShowAddForm] = useState(false);
  const [departmentFilter, setDepartmentFilter] = useState("All");
  const [editEmployee, setEditEmployee] = useState(null);

  //  Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [employeesPerPage, setEmployeesPerPage] = useState(5); // default 5

  //  Helper to generate random dates
  const randomDate = () => {
    const start = new Date(2023, 0, 1);
    const end = new Date();
    const date = new Date(
      start.getTime() + Math.random() * (end.getTime() - start.getTime())
    );
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  //  Load employees from backend
  useEffect(() => {
    const loadEmployees = async () => {
      try {
        const data = await fetchEmployees();

        // Assign random joined_date if missing
        const employeesWithDates = data.map(emp => ({
          ...emp,
          joined_date: emp.joined_date || randomDate()
        }));

        setEmployees(employeesWithDates);
        setFilteredEmployees(employeesWithDates);
        toast.success("Employees loaded successfully!");
      } catch (err) {
        const message = err.response?.data?.detail || err.message;
        setError(message);
        toast.error("Failed to load employees");
      } finally {
        setLoading(false);
      }
    };
    loadEmployees();
  }, []);

  //  Build dynamic department list
  const uniqueDepartments = [
    "All",
    ...new Set(employees.map(emp => emp.department_name).filter(Boolean))
  ];

  //  Search + Filter logic
  useEffect(() => {
    const term = searchTerm.toLowerCase();

    const results = employees.filter((emp) => {
      const matchesSearch =
        emp.name.toLowerCase().includes(term) ||
        emp.email.toLowerCase().includes(term) ||
        (emp.role && emp.role.toLowerCase().includes(term));

      const matchesDepartment =
        departmentFilter === "All" ||
        (emp.department_name &&
          emp.department_name.toLowerCase() === departmentFilter.toLowerCase());

      return matchesSearch && matchesDepartment;
    });

    setFilteredEmployees(results);
    setCurrentPage(1); // reset to first page when filters change
  }, [searchTerm, departmentFilter, employees]);

const handleStatusChange = async (id, newStatus) => {
  try {
    console.log("STATUS FUNCTION CALLED");
    console.log("Employee ID:", id);
    console.log("New Status:", newStatus);

    const user = JSON.parse(localStorage.getItem("user"));
    const token = user?.token;

    // Find the full employee object from state
    const emp = employees.find(e => e.id === id);

    const response = await fetch(`http://127.0.0.1:8000/employees/${id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        name: emp.name,
        email: emp.email,
        role: emp.role,
        department_id: emp.department_id,
        joined_date: emp.joined_date,
        status: newStatus,
      }),
    });

    console.log("Response Status:", response.status);
    const data = await response.json();

    if (!response.ok) {
      console.log("Status Update Error:", data);
      toast.error(data.detail || "Failed to update status");
      return;
    }

    // Update Employees State
    setEmployees(prev =>
      prev.map(e => e.id === id ? { ...e, status: newStatus } : e)
    );

    // Update Filtered Employees State
    setFilteredEmployees(prev =>
      prev.map(e => e.id === id ? { ...e, status: newStatus } : e)
    );

    //  Notification API
    try {
      console.log("Creating notification...");
      await fetch("http://127.0.0.1:8000/notifications", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: `Employee ${emp.name} status changed to ${newStatus}`,
          recipient_email: emp.email,
        }),
      });
    } catch (notificationError) {
      console.log("Notification error:", notificationError);
    }

    toast.success(`Employee status updated to ${newStatus}`);
  } catch (err) {
    console.error("Error updating status:", err);
    toast.error("Error updating status");
  }
};

  // ------ Add Employee----
  const handleAddEmployee = (newEmp) => {
    const updatedList = [...employees, { ...newEmp, joined_date: newEmp.joined_date || randomDate() }];
    setEmployees(updatedList);
    setFilteredEmployees(updatedList);
    toast.success("Employee added successfully!");
  };


  // ----Delete Employee------
  const handleDeleteEmployee = async (id) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/employees/${id}`, {
        method: "DELETE",
      });
      if (!response.ok) {
        const data = await response.json();
        toast.error(data.detail || "Failed to delete employee");
        return;
      }
      const updatedList = employees.filter(emp => emp.id !== id);
      setEmployees(updatedList);
      setFilteredEmployees(updatedList);
      toast.success("Employee deleted successfully!");
    } catch (error) {
      console.error("Error deleting employee:", error);
      toast.error("Unable to connect to backend");
    }
  };

  // Edit Employee
  const handleEditEmployee = async (updatedEmp) => {
  try {
    const token = localStorage.getItem("token");

    const response = await fetch(
      `http://127.0.0.1:8000/employees/${updatedEmp.id}`,
      {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: updatedEmp.name,
          email: updatedEmp.email,
          role: updatedEmp.role,
          department_name: updatedEmp.department_name,
          joined_date: updatedEmp.joined_date,
        }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      toast.error(data.detail || "Failed to update employee");
      return;
    }

    const updatedList = employees.map((emp) =>
      emp.id === updatedEmp.id ? data : emp
    );

    setEmployees(updatedList);
    setFilteredEmployees(updatedList);

    toast.success("Employee updated successfully!");
    setEditEmployee(null);
  } catch (error) {
    console.error("Error updating employee:", error);
    toast.error("Unable to connect to backend");
  }
};

  //  Pagination calculations
  const indexOfLastEmployee = currentPage * employeesPerPage;
  const indexOfFirstEmployee = indexOfLastEmployee - employeesPerPage;
  const currentEmployees = filteredEmployees.slice(indexOfFirstEmployee, indexOfLastEmployee);
  const totalPages = Math.ceil(filteredEmployees.length / employeesPerPage);

  if (loading) return <Skeleton count={6} height={40} />;
  if (error) return <p className="error-text">{error}</p>;

  return (
    <DashboardLayout>
      <div className="employees-container">
        <div className="employees-header">
          <h2 className="employees-title">Employees</h2>
          <p className="employees-subtitle">
            Manage your team members, search, and filter by department.
          </p>
        </div>

        {/* Search and Filter Controls */}
        <div className="employees-actions">
          <input
            type="text"
            placeholder="Search employees..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-bar"
          />
          <select
            value={departmentFilter}
            onChange={(e) => setDepartmentFilter(e.target.value)}
            className="filter-dropdown"
          >
            {uniqueDepartments.map((dept) => (
              <option key={dept} value={dept}>
                {dept}
              </option>
            ))}
          </select>
          <button className="add-btn" onClick={() => setShowAddForm(true)}>
            + Add Employee
          </button>
          <select value={employeesPerPage} onChange={(e) => { 
            setEmployeesPerPage(Number(e.target.value));
            setCurrentPage(1); // reset to first page when size changes
            }}
            className="page-size-dropdown">
              <option value={5}>5 per page</option>
              <option value={10}>10 per page</option>
              <option value={20}>20 per page</option>
              </select>

        </div>

        {/*  Employee Table */}
        <div className="employees-card">
          {currentEmployees.length === 0 ? (
            <p className="no-results">No employees match your search or filter.</p>
          ) : (
            <table className="employees-table">
              <thead>
                <tr>
                  <th>Employee</th>
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
                    <td className="employee-cell">
                      <div className="avatar">
                        {emp.name.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <div className="emp-name">{emp.name}</div>
                        <div className="emp-email">{emp.email}</div>
                      </div>
                    </td>
                    <td>{emp.role || "N/A"}</td>
                    <td>{emp.department_name || "N/A"}</td>
                    <td>
                      <select className={`status-select ${emp.status}`}
                      value={emp.status}
                      onChange={(e) => handleStatusChange(emp.id, e.target.value)}>
                        <option value="active">Active</option>
                        <option value="inactive">Inactive</option>
                        <option value="onleave">On Leave</option>
                        </select>
                        </td>


                    <td>{emp.joined_date}</td>
                    <td>
                      <button className="action-btn edit" onClick={() => setEditEmployee(emp)}>Edit</button>
                      <button className="action-btn delete" onClick={() => handleDeleteEmployee(emp.id)}>Delete</button>
                    
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          {/*  Pagination Controls */}
          {totalPages > 1 && (
            <div className="pagination">
              <button onClick={() => 
              setCurrentPage(prev => Math.max(prev - 1, 1))}
              className="page-btn" disabled={currentPage === 1}>
                Previous
                </button>
                {Array.from({ length: totalPages }, (_, i) => (
                  <button key={i + 1} onClick={() => setCurrentPage(i + 1)}
                  className={`page-btn ${currentPage === i + 1 ? "active" : ""}`}>
                    {i + 1}
                  </button>
                ))}
              <button onClick={() => 
              setCurrentPage(prev => Math.min(prev + 1, totalPages))}
              className="page-btn" disabled={currentPage === totalPages}>
                Next
                </button>
                </div>
              )}
              </div>
              </div>

      {/*  Add Employee Modal */}
      {showAddForm && (
        <AddEmployeeForm
          onAdd={handleAddEmployee}
          onClose={() => setShowAddForm(false)}
        />
      )}
      {/*  Edit Employee Modal */}
      {editEmployee && (
        <EditEmployeeForm
        employee={editEmployee}
        onSave={handleEditEmployee}
        onClose={() => setEditEmployee(null)}/>
        )}

    </DashboardLayout>
  );
};

export default Employees;
