import React, { useEffect, useState } from "react";
import Skeleton from "react-loading-skeleton";
import "react-loading-skeleton/dist/skeleton.css";
import toast from "react-hot-toast";
import DashboardLayout from "../../components/layout/DashboardLayout";
import AddEmployeeForm from "./AddEmployeeForm";
import EditEmployeeForm from "./EditEmployeeForm";
import {fetchEmployees,fetchDepartments,transferDepartment,updateEmployee,
  deleteEmployee,suspendUser,reinstateUser} from "../../services/api";
import "./Employees.css";
//import EmployeeProfile from "./EmployeeProfile";

const Employees = () => {
  const [employees, setEmployees] = useState([]);
  const [filteredEmployees, setFilteredEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [searchTerm, setSearchTerm] = useState("");
  const [departmentFilter, setDepartmentFilter] = useState("All");

  const [showAddForm, setShowAddForm] = useState(false);
  const [editEmployee, setEditEmployee] = useState(null);

  // Department Transfer
  const [departments, setDepartments] = useState([]);
  const [showTransferModal, setShowTransferModal] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [selectedDepartment, setSelectedDepartment] = useState("");
  const [transferReason, setTransferReason] = useState("");

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

  /* ---------------- FETCH DEPARTMENTS ---------------- */
  useEffect(() => {
    const loadDepartments = async () => {
      try {
        const data = await fetchDepartments();
        setDepartments(data);
      } catch (err) {
        console.error(err);
        toast.error("Failed to load departments");
      }
    };
    loadDepartments();
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
      if (!emp) {
        toast.error("Employee not found");
        return;
      }

      const payload = {
        name: emp.name,
        email: emp.email,
        role: emp.role,
        department_name: emp.department_name,
        joined_date: emp.joined_date?.slice(0, 10),
        status: newStatus,
      };
      await updateEmployee(id, payload);

      const data = await fetchEmployees();

      setEmployees(data);
      setFilteredEmployees(data);

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
  const handleAddEmployee = async () => {
    const data = await fetchEmployees();

    setEmployees(data);
    setFilteredEmployees(data);

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
      const data = await fetchEmployees();
      setEmployees(data);
      setFilteredEmployees(data);
      toast.success("Employee updated");
      setEditEmployee(null);
    } catch (err) {
      console.error(err);
      toast.error("Update failed");
    }
  };

  /* ---------------- TRANSFER DEPARTMENT ---------------- */
  const handleTransferDepartment = async () => {
    try {
      if (!selectedDepartment) {
        toast.error("Please select a department");
        return;
      }
      await transferDepartment(
        selectedEmployee.id,
        Number(selectedDepartment),
        transferReason
      );
      // Refresh employee list
      const data = await fetchEmployees();
      setEmployees(data);
      setFilteredEmployees(data);
      toast.success("Department transferred successfully");
      setShowTransferModal(false);
      setSelectedEmployee(null);
      setSelectedDepartment("");
      setTransferReason("");
    } catch (err) {
      console.error(err);
      toast.error(
        err.response?.data?.detail || "Department transfer failed"
      );
    }
  };

//--------------- Suspend Employee--------------
const handleSuspend = async (userId) => {
  console.log("Suspend clicked");
  console.log("Suspending user:", userId);
  
  const reason = prompt("Enter suspension reason");

  if (!reason) return;

  try {
    await suspendUser(userId, reason);

    toast.success("User suspended");
  } catch (err) {
    console.error(err);
    toast.error("Suspension failed");
  }
};

//----------------Reinstate Employee---------------------
const handleReinstate = async (userId) => {
  try {
    await reinstateUser(userId);

    const updated = employees.map((emp) =>
      emp.id === userId
        ? { ...emp, status: "active" }
        : emp
    );

    setEmployees(updated);
    setFilteredEmployees(updated);

    toast.success("User reinstated");
  } catch (err) {
    console.error(err);
    toast.error("Reinstatement failed");
  }
};  

  /* ---------------- PAGINATION ---------------- */
  const indexOfLast = currentPage * employeesPerPage;
  const indexOfFirst = indexOfLast - employeesPerPage;
  const currentEmployees = filteredEmployees.slice(indexOfFirst, indexOfLast);

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

          <input type="text" placeholder="Search..."
           value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)}/>

          <select value={departmentFilter}
           onChange={(e) => setDepartmentFilter(e.target.value)}>
            {uniqueDepartments.map((d, i) => (
              <option key={i} value={d}>
                {d}
              </option>
            ))}
          </select>

          <button onClick={() => setShowAddForm(true)}>
            + Add Employee
          </button>

          <select value={employeesPerPage}
            onChange={(e) => {
              setEmployeesPerPage(Number(e.target.value));
              setCurrentPage(1);
            }}>
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
                  {/*<th>Profile</th>*/}
                  <th>Status</th>
                  <th>Joined</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {currentEmployees.map((emp) => (
                  <tr key={emp.id} className={
                    (emp.profile_completion?.completion_percentage ?? 0) < 70
                    ? "low-profile-row" : ""}>
                    <td>
                      <b>{emp.name}</b>
                      <div>{emp.email}</div>
                    </td>
                    <td>{emp.role}</td>
                    <td>{emp.department_name || "N/A"}</td>
                      {/*<td>
                         <EmployeeProfile profile={emp.profile_completion}/>
                      </td>*/}

                    <td>
                      <select value={emp.status}
                        onChange={(e) => handleStatusChange(emp.id, e.target.value)}>
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

                      <button onClick={() => {
                        setSelectedEmployee(emp);
                        setSelectedDepartment("");
                        setTransferReason("");
                        setShowTransferModal(true);
                      }}>
                       Transfer
                      </button>
                      {emp.status !== "suspended" ? (
                      <button onClick={() => {
                        console.log("EMP:", emp);
                        handleSuspend(emp.id);
                        }}>
                        Suspend
                      </button>
                      ) : (
                      <button className="reinstate-btn"
                       onClick={() => handleReinstate(emp.id)}>
                        Reinstate
                      </button>
                    )}

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
            onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))
            }>
            Prev
          </button>

          {Array.from({ length: totalPages }, (_, i) => (
            <button key={i} className={currentPage === i + 1 ? "active" : ""}
              onClick={() => setCurrentPage(i + 1)}>
              {i + 1}
            </button>
          ))}

          <button disabled={currentPage === totalPages}
            onClick={() => setCurrentPage((p) =>
                Math.min(p + 1, totalPages)
              )}>
            Next
          </button>
        </div>

        {/* MODALS */}
        {showAddForm && (
          <AddEmployeeForm onAdd={handleAddEmployee}
            onClose={() => setShowAddForm(false)}/>
        )}

        {editEmployee && (
          <EditEmployeeForm employee={editEmployee} onSave={handleEditEmployee}
            onClose={() => setEditEmployee(null)}/>
        )}

        {/* ---------------- TRANSFER DEPARTMENT MODAL ---------------- */}

        {showTransferModal && (
          <div className="modal-overlay">
            <div className="modal">

              <h3>Transfer Department</h3>
              <p><strong>Employee:</strong> {selectedEmployee?.name}</p>
              <label>New Department</label>
              
              <select value={selectedDepartment}
              onChange={(e) =>setSelectedDepartment(e.target.value)}>
                
              <option value="">Select Department</option>
              {departments.filter((dept) =>
              dept.name !== selectedEmployee?.department_name
            )
            .map((dept) => (
            <option key={dept.id} value={dept.id}>
              {dept.name}
            </option>))}
              </select>
              <label>Reason (Optional)</label>
              <textarea rows="3" value={transferReason}
              onChange={(e) => setTransferReason(e.target.value)}/>

          <div className="modal-buttons">
            <button onClick={handleTransferDepartment}>
             Transfer
            </button>

           <button onClick={() => {
             setShowTransferModal(false);
             setSelectedEmployee(null);
            }}>
            Cancel
           </button>
          </div>
    </div>
  </div>
)}
      </div>
    </DashboardLayout>
  );
};

export default Employees;