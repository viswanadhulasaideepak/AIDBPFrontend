import React, { useEffect, useState, useContext } from "react";
import toast from "react-hot-toast";
import { FaFileCsv, FaFileExcel, FaFilePdf } from "react-icons/fa";
import { 
  fetchAttendance, 
  downloadAttendanceReportCSV, 
  downloadAttendanceReportExcel, 
  downloadAttendanceReportPDF 
} from "../../services/api";
import Skeleton from "react-loading-skeleton";
import "react-loading-skeleton/dist/skeleton.css";
import DashboardLayout from "../../components/layout/DashboardLayout";
import { AuthContext } from "../../auth/AuthContext"; 
import "./Attendance.css";

const Attendance = () => {
  const [attendance, setAttendance] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const { user } = useContext(AuthContext);

  useEffect(() => {
    const loadAttendance = async () => {
      try {
        const data = await fetchAttendance();
        setAttendance(data);
        toast.success("Attendance loaded successfully!");
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
  if (attendance.length === 0) return <p>No attendance records found.</p>;

  return (
    <DashboardLayout>
      <div className="attendance-container">
        <h2 className="attendance-title">📅 Attendance</h2>
        <div className="attendance-card">
          <table className="attendance-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Present</th>
                <th>On Leave</th>
                <th>Absent</th>
              </tr>
            </thead>
            <tbody>
              {attendance.map(rec => (
                <tr key={rec.id}>
                  <td>{rec.date}</td>
                  <td>{rec.employee_id}</td>
                  <td>{rec.status}</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>

        {/* Admin-only download buttons */}
        {user?.role === "admin" && (
          <div className="download-actions">
            <button onClick={downloadAttendanceReportCSV}>
              <FaFileCsv /> Download CSV
            </button>
            <button onClick={downloadAttendanceReportExcel}>
              <FaFileExcel /> Download Excel
            </button>
            <button onClick={downloadAttendanceReportPDF}>
              <FaFilePdf /> Download PDF
            </button>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default Attendance;
