import React, { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import { Chart as ChartJS } from "chart.js/auto";
import { fetchAttendance } from "../../services/api";
import toast from "react-hot-toast";
import Skeleton from "react-loading-skeleton";
import "react-loading-skeleton/dist/skeleton.css";
import "./AttendanceDashboard.css";

const AttendanceDashboard = () => {
  const [attendanceData, setAttendanceData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadAttendance = async () => {
      try {
        const data = await fetchAttendance();
        setAttendanceData({
          labels: data.dates,
          datasets: [
            { label: "Present", data: data.present, borderColor: "#4caf50", fill: false },
            { label: "On Leave", data: data.leave, borderColor: "#ff9800", fill: false },
            { label: "Absent", data: data.absent, borderColor: "#f44336", fill: false },
          ],
        });
        toast.success("Attendance data loaded!");
      } catch (err) {
        const message = err.response?.data?.detail || err.message;
        setError(message);
        toast.error("Failed to load attendance");
      } finally {
        setLoading(false);
      }
    };
    loadAttendance();
  }, []);

  if (loading) return <Skeleton count={4} height={40} />;
  if (error) return <p className="error-text">{error}</p>;
  if (!attendanceData) return <p>No attendance data found.</p>;

  // 🔹 Calculate overall attendance percentage
  const totalPresent = attendanceData.datasets[0].data.reduce((a, b) => a + b, 0);
  const totalDays = attendanceData.labels.length;
  const totalEmployees = Math.max(...attendanceData.datasets[0].data) +
                         Math.max(...attendanceData.datasets[1].data) +
                         Math.max(...attendanceData.datasets[2].data);
  const attendancePercentage = totalEmployees > 0
    ? Math.round((totalPresent / (totalEmployees * totalDays)) * 100)
    : 0;

  return (
    <div className="attendance-dashboard">
      <h2 className="attendance-title">📅 Attendance Dashboard</h2>

      {/* 🔹 Attendance Percentage */}
      <p className="attendance-percentage">
        Overall Attendance: <strong>{attendancePercentage}%</strong>
      </p>

      {/* 🔹 Chart */}
      <div className="attendance-card">
        <Line data={attendanceData} options={{ maintainAspectRatio: false }} />
      </div>

      {/* 🔹 Table */}
      <table className="attendance-table">
        <thead>
          <tr>
            <th>Date</th><th>Present</th><th>On Leave</th><th>Absent</th>
          </tr>
        </thead>
        <tbody>
          {attendanceData.labels.map((date, idx) => (
            <tr key={date}>
              <td>{date}</td>
              <td>{attendanceData.datasets[0].data[idx]}</td>
              <td>{attendanceData.datasets[1].data[idx]}</td>
              <td>{attendanceData.datasets[2].data[idx]}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AttendanceDashboard;
