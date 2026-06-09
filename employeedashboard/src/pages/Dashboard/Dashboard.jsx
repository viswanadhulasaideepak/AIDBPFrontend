import React, { useEffect, useState, useContext } from "react";
import { Bar, Line } from "react-chartjs-2";
import { Chart as ChartJS } from "chart.js/auto";
import {
  fetchDepartments,
  fetchAttendance,
  fetchEmployees,
  fetchDashboardStats,   
  downloadAttendanceReportExcel,
  downloadAttendanceReportPDF  
} from "../../services/api";
import toast from "react-hot-toast";
import "./Dashboard.css";
import DashboardLayout from "../../components/layout/DashboardLayout";
import { AuthContext } from "../../auth/AuthContext";

const Dashboard = () => {
  const [departments, setDepartments] = useState([]);
  const [attendanceData, setAttendanceData] = useState({
    labels: [],
    datasets: [],
  });
  const [employees, setEmployees] = useState([]);
  const [stats, setStats] = useState(null);

  const { user } = useContext(AuthContext);

  // Load departments
  useEffect(() => {
    const loadDepartments = async () => {
      try {
        const data = await fetchDepartments();   
        const validData = data.map((d) => ({
          name: d.name || d.department,
          employee_count: Number(d.employee_count || d.count || 0),
        }));
        console.log("DEPARTMENTS API:", data);
        setDepartments(validData);
      } catch {
        toast.error("Failed to load departments");
      }
    };
    loadDepartments();
  }, []);

  // Load attendance
  useEffect(() => {
    const loadAttendance = async () => {
      try {
        const data = await fetchAttendance();
        if (data && !Array.isArray(data) && data.dates) {
          setAttendanceData({
            labels: data.dates,
            datasets: [
              { label: "Present", data: data.present || [], borderColor: "#4caf50" },
              { label: "On Leave", data: data.leave || [], borderColor: "#ff9800" },
              { label: "Absent", data: data.absent || [], borderColor: "#f44336" },
            ],
          });
        } else {
          setAttendanceData({ labels: [], datasets: [] });
        }
        console.log("ATTENDANCE API:", data);
      } catch {
        toast.error("Failed to load attendance");
      }
    };
    loadAttendance();
  }, []);

  // Load employees
  useEffect(() => {
    const loadEmployees = async () => {
      try {
        const data = await fetchEmployees();
        console.log("EMPLOYEES API:", data);
        setEmployees(data);
      } catch {
        toast.error("Failed to load employees");
      }
    };
    loadEmployees();
  }, []);

  // Load stats
  useEffect(() => {
    const loadStats = async () => {
      try {
        const data = await fetchDashboardStats();
        setStats(data);
      } catch {
        toast.error("Failed to load stats");
      }
    };
    loadStats();
  }, []);

  // Department chart data
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

  // Attendance percentage
  const totalEmployees = employees.length;
  const totalDays = attendanceData?.labels.length || 0;
  const totalPossible = totalEmployees * totalDays;

  const totalPresent =
    attendanceData?.datasets?.[0]?.data?.reduce((sum, val) => sum + val, 0) || 0;

  const attendancePercentage =
    totalPossible > 0 ? Math.round((totalPresent / totalPossible) * 100) : 0;

  // Sort employees by join date (latest first)
  const sortedEmployees = [...employees].sort(
    (a, b) => new Date(b.joined_date) - new Date(a.joined_date)
  );

  return (
    <DashboardLayout>
      <div className="dashboard-page">
        <h2 className="dashboard-title">
          {user?.company_name || "Company"} Dashboard
        </h2>
        <p className="dashboard-subtitle">
          Welcome back, {user?.role === "admin" ? "Admin" : "User"} 👋
        </p>
        <p className="company-label">🏢 {user?.company_name}</p>

        {/* Stats row */}
        <div className="stats-row">
          <div className="stat-card">
            <div className="stat-icon">👥</div>
            <h4>Total Employees</h4>
            <p>{stats?.total_employees}</p>
          </div>
          <div className="stat-card">
            <div className="stat-icon">✅</div>
            <h4>Active Employees</h4>
            <p>{stats?.active_employees}</p>
          </div>
          {user?.role === "admin" && (
            <div className="stat-card">
              <div className="stat-icon">🏢</div>
              <h4>Departments</h4>
              <p>{stats?.departments}</p>
            </div>
          )}
          <div className="stat-card">
            <div className="stat-icon">📊</div>
            <h4>Attendance</h4>
            <p>{stats?.attendance_percentage || attendancePercentage}%</p>
          </div>
        </div>

        {/* Charts */}
        <div className="dashboard-grid">
          <div className="chart-card large-chart">
            <h3>Employee Activity Overview</h3>
            {employees.length > 0 ? (
              <div className="chart-container">
                <Bar
                  data={{
                    labels: ["Active", "Inactive"],
                    datasets: [
                      {
                        label: "Employees",
                        data: [
                          employees.filter((e) => e.status === "active").length,
                          employees.filter((e) => e.status !== "active").length,
                        ],
                        backgroundColor: ["#4caf50", "#f44336"],
                      },
                    ],
                  }}
                  options={{ maintainAspectRatio: false }}
                />
              </div>
            ) : (
              <p>Loading employees...</p>
            )}
          </div>

          <div className="chart-card large-chart">
            <h3>Attendance Analytics</h3>
            {attendanceData?.labels?.length > 0 ? (
              <div className="chart-container">
                <Line data={attendanceData} options={{ maintainAspectRatio: false }} />
              </div>
            ) : (
              <p>Loading attendance...</p>
            )}
            {user?.role === "admin" && (
              <div className="download-actions">
                <button
                  className="dashboard-btn"
                  onClick={downloadAttendanceReportExcel}
                  style={{ marginTop: "15px" }}
                >
                  Download Excel Report
                </button>
                <button
                  className="dashboard-btn"
                  onClick={downloadAttendanceReportPDF}
                  style={{ marginTop: "15px" }}
                >
                  Download PDF Report
                </button>
              </div>
            )}
          </div>

          {/* Admin-only Department Distribution + Recent Employees */}
          {user?.role === "admin" && (
            <div className="chart-row">
              {/* Department Distribution */}
              <div className="chart-card large-chart">
                <h3>Department Distribution</h3>
                {departments.length > 0 ? (
                  <div className="chart-container">
                    <Bar data={departmentData} options={{ maintainAspectRatio: false }} />
                  </div>
                ) : (
                  <p>Loading departments...</p>
                )}
              </div>

              {/* Recent Employees */}
              <div className="chart-card recent-employees">
                <h3>Recent Employees</h3>
                {sortedEmployees.length > 0 ? (
                  <ul className="recent-list">
                    {sortedEmployees.slice(0, 5).map((emp) => (
                      <li key={emp.id} className="recent-item">
                        <div className="avatar">
                          {emp.name.charAt(0).toUpperCase()}
                        </div>
                        <div className="emp-info">
                          <strong>{emp.name}</strong>
                          <span>{emp.role}</span>
                          <small>{emp.joined_date}</small>
                        </div>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p>No recent employees found.</p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Dashboard;
