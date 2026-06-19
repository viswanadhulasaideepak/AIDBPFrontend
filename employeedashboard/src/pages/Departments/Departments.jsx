import React, { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { fetchDepartments } from "../../services/api";
import Skeleton from "react-loading-skeleton";
import "react-loading-skeleton/dist/skeleton.css";
import DashboardLayout from "../../components/layout/DashboardLayout";  
import "./Departments.css";

const Departments = () => {
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadDepartments = async () => {
  try {
    setLoading(true);
    const data = await fetchDepartments();
    setDepartments(data);
    setError("");
  } catch (err) {
    console.error(err);
    const message =
      err.response?.data?.detail || err.message;
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
    <DashboardLayout>   {/* wrap content in layout */}
      <div className="departments-container">

    <div className="departments-header">

        <div>

            <h2 className="departments-title">
                Departments
            </h2>

            <p>
                Manage all company departments
            </p>

        </div>

        <button
            className="refresh-btn"
            onClick={loadDepartments}
        >
            Refresh
        </button>

    </div>
        <div className="departments-header">
          <h2 className="departments-title">
            🏢 Departments
          </h2>

          <button className="refresh-btn" onClick={loadDepartments}>
           Refresh
          </button>
        </div>
        <div className="departments-card">
          <table className="departments-table">
            <thead>
              <tr>
                <th>ID</th><th>Name</th><th>Employee Count</th>
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
      </div>
    </DashboardLayout>
  );
};

export default Departments;