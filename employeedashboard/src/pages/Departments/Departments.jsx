import React, { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { fetchDepartments } from "../../services/api";
import Skeleton from "react-loading-skeleton";
import "react-loading-skeleton/dist/skeleton.css";
import DashboardLayout from "../../components/layout/DashboardLayout";  // ✅ added
import "./Departments.css";

const Departments = () => {
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadDepartments = async () => {
      try {
        const data = await fetchDepartments();
        setDepartments(data);
        toast.success("Departments loaded successfully!");
      } catch (err) {
        const message = err.response?.data?.detail || err.message;
        setError(message);
        toast.error("Failed to load departments");
      } finally {
        setLoading(false);
      }
    };
    loadDepartments();
  }, []);

  if (loading) return <Skeleton count={4} height={40} />;
  if (error) return <p className="error-text">{error}</p>;
  if (departments.length === 0) return <p>No departments found.</p>;

  return (
    <DashboardLayout>   {/* ✅ wrap content in layout */}
      <div className="departments-container">
        <h2 className="departments-title">🏢 Departments</h2>
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
                  <td>{dept.employee_count}</td>
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
