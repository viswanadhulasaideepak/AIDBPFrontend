import React, { useEffect, useState, useContext } from "react";
import toast from "react-hot-toast";
import Skeleton from "react-loading-skeleton";
import "react-loading-skeleton/dist/skeleton.css";
import DashboardLayout from "../../components/layout/DashboardLayout";
import { AuthContext } from "../../auth/AuthContext";
import {getAttendanceAccessStatus, getTodayAttendance, getAttendanceHistory, checkIn,
  checkOut, downloadAttendanceReportExcel, downloadAttendanceReportPDF,
  getAttendanceAccessRequests,  updateAttendanceAccessRequest,updateLeaveRequest,
  submitLeaveRequest,getMyLeaveRequests,getCompanyLeaveRequests} from "../../services/api";
import { FaFileExcel, FaFilePdf } from "react-icons/fa";
import "./Attendance.css";

const Attendance = () => {
  const { user } = useContext(AuthContext);
  const [accessStatus, setAccessStatus] = useState(null);
  const [today, setToday] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [requests, setRequests] = useState([]);
  const [leaveRequests, setLeaveRequests] = useState([]);
  const [leaveForm, setLeaveForm] = useState({
    leave_type: "casual",
    start_date: "",
    end_date: "",
    reason: ""
  });

  useEffect(() => {
    loadAttendance();
  }, []);

  const loadAttendance = async () => {
    try {
      // ---------------- ADMIN ----------------
      if (user?.role === "admin") {
        const pending = await getAttendanceAccessRequests();
        setRequests(pending);

        const companyLeaves = await getCompanyLeaveRequests();
        setLeaveRequests(companyLeaves);
        return;
      }

      // ---------------- USER ----------------
      const access = await getAttendanceAccessStatus();
      setAccessStatus(access);

      if (access.status === "approved" || access.status === "AttendanceAccessStatus.approved") {
        const todayData = await getTodayAttendance();
        setToday(todayData);

        const historyData = await getAttendanceHistory();
        setHistory(historyData);

        const myLeaves = await getMyLeaveRequests();
        setLeaveRequests(myLeaves);
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed loading attendance.");
    } finally {
      setLoading(false);
    }
  };

  const handleLeaveSubmit = async (e) => {
    e.preventDefault();
    try {
      await submitLeaveRequest(leaveForm);
      toast.success("Leave request submitted");
      loadAttendance();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Submission failed");
    }
  };

  const handleLeaveUpdate = async (id, status) => {
    try {
      await updateLeaveRequest(id, status);
      toast.success(`Leave ${status}`);
      loadAttendance();
    } catch (err) {
      toast.error("Update failed");
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
  };

  return (
  <DashboardLayout>
    <div className="attendance-container">
      <h2>Attendance</h2>

      {user?.role === "admin" ? (
        <>
          {/* ---------------- Admin Attendance Access Requests ---------------- */}
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
                        <button onClick={() => approveRequest(req.id)}>Approve</button>
                        <button onClick={() => rejectRequest(req.id)}>Reject</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          {/* ---------------- Admin Leave Requests ---------------- */}
          <div className="leave-card">
            <h3>Company Leave Requests</h3>
            <table className="leave-table"><thead>
    <tr>
      <th>Type</th>
      <th>Start</th>
      <th>End</th>
      <th>Reason</th>
      <th>Status</th>
      {user?.role === "admin" && <th>Action</th>}
    </tr>
    </thead>
    <tbody>
    {leaveRequests.map((req) => (
      <tr key={req.id}>
        <td>{req.leave_type}</td>
        <td>{req.start_date}</td>
        <td>{req.end_date}</td>
        <td>{req.reason}</td>
        <td>{req.status}</td>
        {user?.role === "admin" && (
          <td>
            {req.status === "pending" ? (
              <>
                <button onClick={() => handleLeaveUpdate(req.id, "approved")}>
                  Approve
                </button>
                <button onClick={() => handleLeaveUpdate(req.id, "rejected")}>
                  Reject
                </button>
              </>
            ) : (
              <span style={{ color: "gray" }}>{req.status}</span>
            )}
          </td>
        )}
      </tr>
    ))}
  </tbody>
</table>

          </div>

          {/* ---------------- Admin Report Downloads ---------------- */}
          <div className="download-actions">
            <button onClick={downloadAttendanceReportExcel}><FaFileExcel /> Excel</button>
            <button onClick={downloadAttendanceReportPDF}><FaFilePdf /> PDF</button>
          </div>
        </>
      ) : (
        <>
          {/* ---------------- User Access Status ---------------- */}
          {accessStatus?.status === "pending" && (
            <div className="attendance-pending">
              <h3>Attendance Access Pending</h3>
              <p>Your request has been sent to your company administrator.</p>
              <p>Submitted : {new Date(accessStatus.submitted_on).toLocaleString()}</p>
            </div>
          )}

          {accessStatus?.status === "rejected" && (
            <div className="attendance-pending">
              <h3>Attendance Access Rejected</h3>
              <p>Please contact your administrator.</p>
            </div>
          )}

          {accessStatus?.status === "approved" && (
            <>
              {/* ---------------- User Attendance Actions ---------------- */}
              <div className="attendance-actions">
                {!today?.check_in && <button onClick={handleCheckIn}>Check In</button>}
                {today?.check_in && !today?.check_out && <button onClick={handleCheckOut}>Check Out</button>}
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
                      <th>Date</th><th>Check In</th><th>Check Out</th><th>Hours</th>
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

              {/* ---------------- User Leave Requests ---------------- */}
              <div className="leave-card">
                <h3>My Leave Requests</h3>
                <form onSubmit={handleLeaveSubmit} className="leave-form">
                  <select value={leaveForm.leave_type}
                          onChange={(e) => setLeaveForm({ ...leaveForm, leave_type: e.target.value })}>
                    <option value="casual">Casual</option>
                    <option value="sick">Sick</option>
                    <option value="earned">Earned</option>
                    <option value="unpaid">Unpaid</option>
                  </select>
                  <input type="date" value={leaveForm.start_date}
                         onChange={(e) => setLeaveForm({ ...leaveForm, start_date: e.target.value })}/>
                  <input type="date" value={leaveForm.end_date}
                         onChange={(e) => setLeaveForm({ ...leaveForm, end_date: e.target.value })}/>
                  <textarea placeholder="Reason"
                            value={leaveForm.reason}
                            onChange={(e) => setLeaveForm({ ...leaveForm, reason: e.target.value })}/>
                  <button type="submit">Submit Leave Request</button>
                </form>

                <table className="leave-table">
                  <thead>
                    <tr>
                      <th>Type</th><th>Start</th><th>End</th><th>Reason</th><th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {leaveRequests.map((req) => (
                      <tr key={req.id}>
                        <td>{req.leave_type}</td>
                        <td>{req.start_date}</td>
                        <td>{req.end_date}</td>
                        <td>{req.reason}</td>
                        <td>{req.status}</td>
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