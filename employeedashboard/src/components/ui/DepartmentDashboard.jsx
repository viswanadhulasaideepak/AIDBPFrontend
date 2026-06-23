import React, { useEffect, useState } from "react";
import { Bar } from "react-chartjs-2";
import { Chart as ChartJS } from "chart.js/auto";
import { fetchDepartments, addDepartment } from "../../services/api";
import toast from "react-hot-toast";
import Skeleton from "react-loading-skeleton";
import "react-loading-skeleton/dist/skeleton.css";
import "./DepartmentDashboard.css";

const DepartmentsDashboard = () => {
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [newDept, setNewDept] = useState("");

  const loadDepartments = async () => {
    try {
      const data = await fetchDepartments();
      const validData = data.map((d) => ({
        name: d.name || "Unknown",
        employee_count: Number(d.employee_count) || 0,
      }));
      setDepartments(validData);
    } catch (err) {
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

  const handleAddDepartment = async (e) => {
    e.preventDefault();
    if (!newDept.trim()) return;
    try {
      await addDepartment({ name: newDept });
      toast.success("Department added!");
      setNewDept("");
      loadDepartments();
    } catch {
      toast.error("Failed to add department");
    }
  };

  if (loading) return <Skeleton count={4} height={40} />;
  if (error) return <p className="error-text">{error}</p>;

  const departmentData = {
    labels: departments.map((d) => d.name),
    datasets: [
      {
        label: "Employees per Department",
        data: departments.map((d) => d.employee_count),
        backgroundColor: "#2196f3",
      },
    ],
  };

  return (
    <div className="departments-dashboard">
      <h2 className="departments-title">🏢 Departments Dashboard</h2>

      {/* Add Department Form */}
      <form className="add-department-form" onSubmit={handleAddDepartment}>
        <input type="text" placeholder="Enter department name"
          value={newDept} onChange={(e) => setNewDept(e.target.value)}/>
        <button type="submit">Add Department</button>
      </form>

      {/* Department List */}
      <ul className="department-list">
        {departments.map((d, idx) => (
          <li key={idx}>
            <strong>{d.name}</strong> — {d.employee_count} employees
          </li>
        ))}
      </ul>

      {/* Chart */}
      <div className="departments-card">
        <div className="chart-container">
          <Bar data={departmentData} options={{ maintainAspectRatio: false }} />
        </div>
      </div>
    </div>
  );
};

export default DepartmentsDashboard;
