import React, { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { fetchDepartments, fetchDepartmentTransferHistory } from "../../services/api";
import Skeleton from "react-loading-skeleton";
import "react-loading-skeleton/dist/skeleton.css";
import DashboardLayout from "../../components/layout/DashboardLayout";  
import "./Departments.css";

const Departments = () => {
  const [departments, setDepartments] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadDepartments = async () => {
  try {
    setLoading(true);
    const [departmentData, historyData] = await Promise.all([
    fetchDepartments(),
    fetchDepartmentTransferHistory()
  ]);
  setDepartments(departmentData);
  setHistory(historyData);
  setError("");

  } catch (err) {
    console.error(err);
    const message = err.response?.data?.detail || err.message;
    setError(message);
    toast.error("Failed to load departments");

  } finally {
    setLoading(false);
  }
};

useEffect(() => {
  loadDepartments();
}, []);

  if (loading) return <Skeleton count={4} height={40} />;
  if (error) return <p className="error-text">{error}</p>;
  if (!loading && departments.length === 0)
    return (
        <DashboardLayout>
            <div className="departments-container">
                <h2>No Departments Found</h2>
            </div>
        </DashboardLayout>
    );

  return (
  <DashboardLayout>
    <div className="departments-container">

      {/* Page Header */}
      <div className="departments-header">
        <div>
          <h2 className="departments-title">Departments</h2>
          <p>Manage all company departments</p>
        </div>
      </div>

      {/* Departments Table */}
      <div className="departments-card">

        <div className="table-header">
          <h3>Department List</h3>

          <button
            className="refresh-btn"
            onClick={loadDepartments}
          >
            Refresh
          </button>
        </div>

        <table className="departments-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Employee Count</th>
            </tr>
          </thead>

          <tbody>
            {departments.map((dept) => (
              <tr key={dept.id}>
                <td>{dept.id}</td>

                <td>{dept.name}</td>

                <td>
                  <span className="employee-count-badge">
                    {dept.employee_count}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

      </div>

      {/* Department Transfer History */}
      <div className="departments-card">
        <div className="table-header">
          <h3>Department Transfer History</h3>
        </div>

       {history.length === 0 ? (

    <div className="empty-history">
        No transfer history available.
    </div>
    ) : (
    <table className="departments-table">
      <thead>
        <tr>
            <th>Employee</th>
            <th>Old Department</th>
            <th>New Department</th>
            <th>Transferred By</th>
            <th>Reason</th>
            <th>Date</th>
        </tr>
     </thead>

     <tbody>
      {history.map((item) => (
        <tr key={item.id}>
          
          <td>{item.employee}</td>
          <td>{item.old_department}</td>
          <td>{item.new_department}</td>
          <td>{item.transferred_by}</td>
          <td>{item.reason || "-"}</td>
          <td>
            {new Date(item.transferred_at).toLocaleString()}
          </td>

        </tr>
      ))}
     </tbody>
    </table>
  )}
  </div>
  </div>
  </DashboardLayout>
);
};

export default Departments;