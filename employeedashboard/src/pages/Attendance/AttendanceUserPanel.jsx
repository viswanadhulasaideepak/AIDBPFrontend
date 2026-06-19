import React, { useEffect, useState } from "react";
import toast from "react-hot-toast";
import {
  getAttendanceAccessStatus,
  getTodayAttendance,
  getAttendanceHistory,
  checkIn,
  checkOut,
  submitLeaveRequest,
  getMyLeaveRequests,
} from "../../services/api";

const AttendanceUserPanel = () => {
  const [accessStatus, setAccessStatus] = useState(null);
  const [today, setToday] = useState(null);
  const [history, setHistory] = useState([]);
  const [leaveRequests, setLeaveRequests] = useState([]);

  const [leaveForm, setLeaveForm] = useState({
    leave_type: "casual",
    start_date: "",
    end_date: "",
    reason: "",
  });

  const formatDate = (date) =>
    date ? new Date(date).toLocaleDateString() : "-";

  const formatTime = (date) =>
    date ? new Date(date).toLocaleTimeString() : "-";

  const loadUserData = async () => {
    try {
      const access = await getAttendanceAccessStatus();
      setAccessStatus(access);

      if (access.status === "approved") {
        const todayData = await getTodayAttendance();
        const historyData = await getAttendanceHistory();
        const leaveData = await getMyLeaveRequests();

        setToday(todayData);
        setHistory(historyData);
        setLeaveRequests(leaveData);
      }
    } catch (err) {
      toast.error(
        err.response?.data?.detail ||
          "Failed to load attendance information."
      );
    }
  };

  useEffect(() => {
    loadUserData();
  }, []);

  /* ---------------- CHECK IN ---------------- */

  const handleCheckIn = async () => {
    try {
      await checkIn();
      toast.success("Checked In Successfully");
      loadUserData();
    } catch (err) {
      toast.error(
        err.response?.data?.detail ||
          "Unable to check in."
      );
    }
  };

  /* ---------------- CHECK OUT ---------------- */

  const handleCheckOut = async () => {
    try {
      await checkOut();
      toast.success("Checked Out Successfully");
      loadUserData();
    } catch (err) {
      toast.error(
        err.response?.data?.detail ||
          "Unable to check out."
      );
    }
  };

  /* ---------------- LEAVE SUBMIT ---------------- */

  const handleLeaveSubmit = async (e) => {
    e.preventDefault();

    if (
      !leaveForm.start_date ||
      !leaveForm.end_date ||
      !leaveForm.reason.trim()
    ) {
      toast.error("Please fill all fields.");
      return;
    }

    if (leaveForm.end_date < leaveForm.start_date) {
      toast.error("End date cannot be before start date.");
      return;
    }

    try {
      await submitLeaveRequest(leaveForm);

      toast.success("Leave request submitted.");

      setLeaveForm({
        leave_type: "casual",
        start_date: "",
        end_date: "",
        reason: "",
      });

      loadUserData();
    } catch (err) {
      toast.error(
        err.response?.data?.detail ||
          "Failed to submit leave request."
      );
    }
  };

  /* ---------------- ACCESS STATUS ---------------- */

  if (accessStatus?.status === "pending") {
    return <p>Attendance access request is pending approval.</p>;
  }

  if (accessStatus?.status === "rejected") {
    return <p>Your attendance access request was rejected.</p>;
  }

  return (
    <>
      {/* CHECK IN / OUT */}
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

      {/* TODAY */}
      <div className="attendance-card">
        <h3>Today's Attendance</h3>

        <p>
          <strong>Check In:</strong>{" "}
          {formatTime(today?.check_in)}
        </p>

        <p>
          <strong>Check Out:</strong>{" "}
          {formatTime(today?.check_out)}
        </p>

        <p>
          <strong>Working Hours:</strong>{" "}
          {today?.working_hours || "-"}
        </p>
      </div>

      {/* HISTORY */}
      <div className="attendance-card">
        <h3>Attendance History</h3>

        {history.length === 0 ? (
          <p>No attendance history found.</p>
        ) : (
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
                  <td>{formatDate(item.date)}</td>
                  <td>{formatTime(item.check_in)}</td>
                  <td>{formatTime(item.check_out)}</td>
                  <td>{item.working_hours || "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* LEAVE */}
      <div className="leave-card">
        <h3>My Leave Requests</h3>

        <form onSubmit={handleLeaveSubmit}>
          <select
            value={leaveForm.leave_type}
            onChange={(e) =>
              setLeaveForm({
                ...leaveForm,
                leave_type: e.target.value,
              })
            }
          >
            <option value="casual">Casual</option>
            <option value="sick">Sick</option>
            <option value="earned">Earned</option>
            <option value="unpaid">Unpaid</option>
          </select>

          <input
            type="date"
            value={leaveForm.start_date}
            onChange={(e) =>
              setLeaveForm({
                ...leaveForm,
                start_date: e.target.value,
              })
            }
          />

          <input
            type="date"
            value={leaveForm.end_date}
            onChange={(e) =>
              setLeaveForm({
                ...leaveForm,
                end_date: e.target.value,
              })
            }
          />

          <textarea
            placeholder="Reason"
            value={leaveForm.reason}
            onChange={(e) =>
              setLeaveForm({
                ...leaveForm,
                reason: e.target.value,
              })
            }
          />

          <button type="submit">
            Submit Leave Request
          </button>
        </form>

        {leaveRequests.length === 0 ? (
          <p>No leave requests found.</p>
        ) : (
          <table className="leave-table">
            <thead>
              <tr>
                <th>Type</th>
                <th>Start Date</th>
                <th>End Date</th>
                <th>Reason</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              {leaveRequests.map((req) => (
                <tr key={req.id}>
                  <td>{req.leave_type}</td>
                  <td>{formatDate(req.start_date)}</td>
                  <td>{formatDate(req.end_date)}</td>
                  <td>{req.reason}</td>
                  <td>{req.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
};

export default AttendanceUserPanel;