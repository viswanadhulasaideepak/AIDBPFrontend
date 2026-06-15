import React, { useEffect, useState, useContext } from "react";
import toast from "react-hot-toast";
import Skeleton from "react-loading-skeleton";
import "react-loading-skeleton/dist/skeleton.css";
import DashboardLayout from "../../components/layout/DashboardLayout";
import { AuthContext } from "../../auth/AuthContext";
import {getAttendanceAccessStatus, getTodayAttendance, getAttendanceHistory, checkIn,
  checkOut, downloadAttendanceReportExcel, downloadAttendanceReportPDF,
} from "../../services/api";
import { FaFileExcel, FaFilePdf } from "react-icons/fa";
import "./Attendance.css";

const Attendance = () => {
  const { user } = useContext(AuthContext);

  const [accessStatus, setAccessStatus] = useState(null);
  const [today, setToday] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAttendance();
  }, []);

  const loadAttendance = async () => {
    try {
      const access = await getAttendanceAccessStatus();
      setAccessStatus(access);

      if (access.status === "approved") {
        const todayData = await getTodayAttendance();
        setToday(todayData);

        const historyData = await getAttendanceHistory();
        setHistory(historyData);
      }
    } catch (err) {
      toast.error("Failed to load attendance");
    } finally {
      setLoading(false);
    }
  };

  const handleCheckIn = async () => {
    try {
      await checkIn();

      toast.success("Checked In");

      loadAttendance();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Check In failed");
    }
  };

  const handleCheckOut = async () => {
    try {
      await checkOut();

      toast.success("Checked Out");

      loadAttendance();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Check Out failed");
    }
  };

  if (loading) {
    return <Skeleton count={6} height={40} />;
  }

  return (
    <DashboardLayout>
      <div className="attendance-container">
        <h2>Attendance</h2>
        {/* ---------------- Pending ---------------- */}
        {accessStatus?.status === "pending" && (
          <div className="attendance-pending">
            <h3>Attendance Access Pending</h3>
            <p>
              Your request has been sent to your company administrator.
            </p>
            <p>
              Submitted :
              {" "}
              {new Date(accessStatus.submitted_on).toLocaleString()}
            </p>
          </div>
        )}
        {/* ---------------- Rejected ---------------- */}
        {accessStatus?.status === "rejected" && (
          <div className="attendance-pending">
            <h3>Attendance Access Rejected</h3>
            <p>Please contact your administrator.</p>
          </div>
        )}
        {/* ---------------- Approved ---------------- */}
        {accessStatus?.status === "approved" && (
          <>
            <div className="attendance-actions">

              {!today?.check_in && (
                <button onClick={handleCheckIn}>
                  Check In
                </button>
              )}
              {today?.check_in && !today?.check_out && (
                <button onClick={handleCheckOut}>
                  Check Out
                </button>
              )}
            </div>
            <div className="attendance-card">
              <h3>Today's Attendance</h3>
              <p>
                Check In :
                {" "}
                {today?.check_in || "-"}
              </p>
              <p>
                Check Out :
                {" "}
                {today?.check_out || "-"}
              </p>
              <p>
                Working Hours :
                {" "}
                {today?.working_hours || "-"}
              </p>
            </div>
            <div className="attendance-card">
              <h3>Attendance History</h3>
              <table className="attendance-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Check In</th>
                    <th>Check Out</th>
                    <th>Hours</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((item) => (
                    <tr key={item.id}>
                      <td>{item.date}</td>
                      <td>{item.check_in || "-"}</td>
                      <td>{item.check_out || "-"}</td>
                      <td>{item.working_hours || "-"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {user?.role === "admin" && (
              <div className="download-actions">
                <button onClick={downloadAttendanceReportExcel}>
                  <FaFileExcel />
                  {" "}
                  Excel
                </button>
                <button onClick={downloadAttendanceReportPDF}>
                  <FaFilePdf />
                  {" "}
                  PDF
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </DashboardLayout>
  );
};
export default Attendance;