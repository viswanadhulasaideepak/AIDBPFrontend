import React, { useEffect, useState, useContext } from "react";
import { Bar, Line } from "react-chartjs-2";
import { Chart as ChartJS } from "chart.js/auto";
import {
  fetchDepartments,
  fetchAttendanceReport,
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
  const [analytics, setAnalytics] = useState({
  totalEmployees: 0,
  activeEmployees: 0,
  totalDepartments: 0,
  pendingRequests: 0,
  byDepartment: [],
  byRole: [],
  byStatus: []
});


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

  // Load attendance (analytics report)
useEffect(() => {
  const loadAttendance = async () => {
    try {
      const data = await fetchAttendanceReport(); // 
      if (data && data.dates) {
        setAttendanceData({
          labels: data.dates,
          datasets: [
            {
              label: "Present",
              data: data.present || [],
              borderColor: "#4caf50",
              backgroundColor: "rgba(76, 175, 80, 0.2)",
              fill: true,
              tension: 0.3,
            },
            {
              label: "On Leave",
              data: data.leave || [],
              borderColor: "#ff9800",
              backgroundColor: "rgba(255, 152, 0, 0.2)",
              fill: true,
              tension: 0.3,
            },
            {
              label: "Absent",
              data: data.absent || [],
              borderColor: "#f44336",
              backgroundColor: "rgba(244, 67, 54, 0.2)",
              fill: true,
              tension: 0.3,
            },
          ],
        });
      } else {
        setAttendanceData({ labels: [], datasets: [] });
      }
      console.log("ATTENDANCE REPORT API:", data);
    } catch {
      toast.error("Failed to load attendance analytics");
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
    <div className="stat-icon">📋</div>
    <h4>Pending Requests</h4>
    <p>{stats?.pending_requests}</p>
  </div>
  {user?.role === "admin" && (
    <div className="stat-card">
      <div className="stat-icon">🏢</div>
      <h4>Departments</h4>
      <p>{stats?.departments}</p>
    </div>
  )}
  <div className="stat-card active">
  <div className="stat-icon">💼</div>
  <h4>Active Employees</h4>
  <p>{stats?.active_employees}</p>
</div>
</div>

{/* Charts */}
<div className="dashboard-grid">

  {/* Role Distribution */}
  <div className="chart-card large-chart">
    <h3>Employee Role Distribution</h3>
    {stats?.role_distribution?.length > 0 ? (
      <div className="chart-container">
        <Bar
          data={{
            labels: stats.role_distribution.map(r => r.role),
            datasets: [{
              label: "Employees by Role",
              data: stats.role_distribution.map(r => r.count),
              backgroundColor: "#2196f3"
            }]
          }}
          options={{ maintainAspectRatio: false }}
        />
      </div>
    ) : <p>Loading role distribution...</p>}
  </div>

  {/* Attendance Analytics */}
<div className="chart-card large-chart">
  <h3>Attendance Analytics</h3>
  {attendanceData?.labels?.length > 0 ? (
    <div className="chart-container">
      <Line
        data={attendanceData}
        options={{
          maintainAspectRatio: false,
          responsive: true,
          plugins: {
            legend: { position: "top" },
            tooltip: { mode: "index", intersect: false },
          },
          interaction: { mode: "nearest", axis: "x", intersect: false },
          scales: {
            x: { grid: { color: "#ddd" } },
            y: { grid: { color: "#ddd" }, beginAtZero: true },
          },
        }}
      />
    </div>
  ) : (
    <p>Loading attendance...</p>
  )}
  {user?.role === "admin" && (
    <div className="download-actions">
      <button className="dashboard-btn" onClick={downloadAttendanceReportExcel}>
        Download Excel Report
      </button>
      <button className="dashboard-btn" onClick={downloadAttendanceReportPDF}>
        Download PDF Report
      </button>
    </div>
  )}
</div>

  {/* Employee Status Overview */}
  <div className="chart-card large-chart status-overview">
    <h3>Employee Status Overview</h3>
    {stats?.status_overview?.length > 0 ? (
      <div className="chart-container">
        <Bar
          data={{
            labels: stats.status_overview.map(s => s.status),
            datasets: [{
              label: "Employees by Status",
              data: stats.status_overview.map(s => s.count),
              backgroundColor: ["#4caf50", "#f44336", "#ff9800"]
            }]
          }}
          options={{ maintainAspectRatio: false }}
        />
      </div>
    ) : <p>Loading status overview...</p>}
  </div>

  {/* Recent Employees BELOW Status Overview */}
  <div className="chart-card recent-employees below-status">
    <h3>Recent Employees</h3>
    {sortedEmployees.length > 0 ? (
      <ul className="recent-list">
        {sortedEmployees.slice(0, 5).map(emp => (
          <li key={emp.id} className="recent-item">
            <div className="avatar">{emp.name.charAt(0).toUpperCase()}</div>
            <div className="emp-info">
              <strong>{emp.name}</strong>
              <span>{emp.role}</span>
              <small>{emp.joined_date}</small>
            </div>
          </li>
        ))}
      </ul>
    ) : <p>No recent employees found.</p>}
  </div>

  {/* Department Distribution */}
  {user?.role === "admin" && (
    <div className="chart-card large-chart">
      <h3>Department Distribution</h3>
      {departments.length > 0 ? (
        <div className="chart-container">
          <Bar data={departmentData} options={{ maintainAspectRatio: false }} />
        </div>
      ) : <p>Loading departments...</p>}
    </div>
  )}
</div>

      </div>
    </DashboardLayout>
  );
};

export default Dashboard;
