import React, { useEffect, useState, useContext } from "react";
import toast from "react-hot-toast";
import Skeleton from "react-loading-skeleton";
import "react-loading-skeleton/dist/skeleton.css";
import DashboardLayout from "../../components/layout/DashboardLayout";
import { AuthContext } from "../../auth/AuthContext";
import {getAttendanceAccessStatus, getTodayAttendance, getAttendanceHistory, checkIn,
  checkOut, downloadAttendanceReportExcel, downloadAttendanceReportPDF,
  getAttendanceAccessRequests,  updateAttendanceAccessRequest} from "../../services/api";
import { FaFileExcel, FaFilePdf } from "react-icons/fa";
import "./Attendance.css";

const Attendance = () => {
  const { user } = useContext(AuthContext);
  const [accessStatus, setAccessStatus] = useState(null);
  const [today, setToday] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [requests, setRequests] = useState([]);

  useEffect(() => {
    loadAttendance();
  }, []);

  const loadAttendance = async () => {
  try {
    // ---------------- ADMIN ----------------
    if (user?.role === "admin") {
      const pending = await getAttendanceAccessRequests();
      setRequests(pending);
      return;
    }
    // ---------------- USER ----------------
    try {
      const access = await getAttendanceAccessStatus();
      console.log("Access from API:", access);
      setAccessStatus(access);
    } catch (err) {
      console.log("FULL ERROR:", err);
      console.log("ERROR RESPONSE:", err.response);
      console.log("ERROR DATA:", err.response?.data);
    }
    setAccessStatus(access);
    if (access.status === "approved" || access.status === "AttendanceAccessStatus.approved") {
      const todayData = await getTodayAttendance();
      console.log("TODAY DATA:", todayData);
      setToday(todayData);
      const historyData = await getAttendanceHistory();
      setHistory(historyData);
    }
  } catch (err) {
    console.log(err.response);
    toast.error(
        err.response?.data?.detail ||
        "Failed loading attendance."
    );
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

  const approveRequest = async (id) => {
  try {
    await updateAttendanceAccessRequest(id, "approved");
    toast.success("Attendance Approved");
    loadAttendance();
  } catch (err) {
    toast.error("Approval failed");
  }
};

const rejectRequest = async (id) => {
  try {
    await updateAttendanceAccessRequest(id, "rejected");
    toast.success("Attendance Rejected");
    loadAttendance();
  } catch (err) {
    toast.error("Rejection failed");
  }
  console.log("Access Status:", accessStatus);
  console.log("Today:", today);
  console.log("History:", history);
};

  return (
  <DashboardLayout>
    <div className="attendance-container">
      <h2>Attendance</h2>

      {user?.role === "admin" ? (
        <>
          <div className="attendance-card">
            <h3>Attendance Access Requests</h3>
            {requests.length === 0 ? (
              <p>No Pending Requests</p>
            ) : (
              <table className="attendance-table">
                <thead>
                  <tr>
                    <th>User</th>
                    <th>Email</th>
                    <th>Status</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {requests.map((req) => (
                    <tr key={req.id}>
                      <td>{req.user?.username}</td>
                      <td>{req.user?.email}</td>
                      <td>{req.status}</td>
                      <td>
                        <button onClick={() => approveRequest(req.id)}>
                          Approve
                        </button>
                        <button onClick={() => rejectRequest(req.id)}>
                          Reject
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          <div className="download-actions">
            <button onClick={downloadAttendanceReportExcel}>
              <FaFileExcel /> Excel
            </button>
            <button onClick={downloadAttendanceReportPDF}>
              <FaFilePdf /> PDF
            </button>
          </div>
        </>
      ) : (
        <>
          {/* ---------------- Pending ---------------- */}
          {accessStatus?.status === "pending" && (
            <div className="attendance-pending">
              <h3>Attendance Access Pending</h3>
              <p>Your request has been sent to your company administrator.</p>
              <p>
                Submitted :{" "}
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
                  <button onClick={handleCheckIn}>Check In</button>
                )}
                {today?.check_in && !today?.check_out && (
                  <button onClick={handleCheckOut}>Check Out</button>
                )}
              </div>

              <div className="attendance-card">
                <h3>Today's Attendance</h3>
                <p>Check In : {today?.check_in || "-"}</p>
                <p>Check Out : {today?.check_out || "-"}</p>
                <p>Working Hours : {today?.working_hours || "-"}</p>
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
            </>
          )}
        </>
      )}
    </div>
  </DashboardLayout>
);

};
export default Attendance;