import React, { useEffect, useState } from "react";
import toast from "react-hot-toast";
import {
  getAttendanceAccessRequests,
  updateAttendanceAccessRequest,
  getCompanyLeaveRequests,
  updateLeaveRequest,
  downloadAttendanceReportExcel,
  downloadAttendanceReportPDF,
} from "../../services/api";

import { FaFileExcel, FaFilePdf } from "react-icons/fa";

const AttendanceAdminPanel = () => {
  const [requests, setRequests] = useState([]);
  const [leaveRequests, setLeaveRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processingId, setProcessingId] = useState(null);

  /* ---------------- LOAD DATA ---------------- */

  const loadAdminData = async () => {
    try {
      setLoading(true);

      const pendingRequests = await getAttendanceAccessRequests();
      const leaveData = await getCompanyLeaveRequests();

      setRequests(pendingRequests);
      setLeaveRequests(leaveData);
    } catch (err) {
      toast.error(
        err.response?.data?.detail ||
          "Failed to load admin data."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAdminData();
  }, []);

  /* ---------------- APPROVE ACCESS ---------------- */

  const approveRequest = async (id) => {
    try {
      setProcessingId(id);
      await updateAttendanceAccessRequest(id, "approved");
      toast.success("Attendance access approved.");
      loadAdminData();
    } catch (err) {
      toast.error(
        err.response?.data?.detail ||
          "Failed to approve request."
      );
    } finally {
      setProcessingId(null);
    }
  };

  /* ---------------- REJECT ACCESS ---------------- */

  const rejectRequest = async (id) => {
    try {
      setProcessingId(id);
      await updateAttendanceAccessRequest(id, "rejected");
      toast.success("Attendance access rejected.");
      loadAdminData();
    } catch (err) {
      toast.error(
        err.response?.data?.detail ||
          "Failed to reject request."
      );
    } finally {
      setProcessingId(null);
    }
  };

  /* ---------------- LEAVE ACTION ---------------- */

  const handleLeaveUpdate = async (id, status) => {
    try {
      setProcessingId(id);
      await updateLeaveRequest(id, status);
      toast.success(`Leave ${status} successfully.`);
      loadAdminData();
    } catch (err) {
      toast.error(
        err.response?.data?.detail ||
          "Failed to update leave request."
      );
    } finally {
      setProcessingId(null);
    }
  };

  /* ---------------- DOWNLOADS ---------------- */

  const handleExcelDownload = async () => {
    try {
      await downloadAttendanceReportExcel();
      toast.success("Excel report downloaded.");
    } catch {
      toast.error("Failed to download Excel report.");
    }
  };

  const handlePDFDownload = async () => {
    try {
      await downloadAttendanceReportPDF();
      toast.success("PDF report downloaded.");
    } catch {
      toast.error("Failed to download PDF report.");
    }
  };

  if (loading) {
    return <p>Loading admin data...</p>;
  }

  return (
    <>
      {/* --------------------- ACCESS REQUESTS ------------------- */}

      <div className="attendance-card">
        <h3>Attendance Access Requests</h3>

        {requests.length === 0 ? (
          <p>No pending attendance access requests.</p>
        ) : (
          <table className="attendance-table">
            <thead>
              <tr>
                <th>User</th>
                <th>Email</th>
                <th>Status</th>
                <th width="220">Action</th>
              </tr>
            </thead>

            <tbody>
              {requests.map((req) => (
                <tr key={req.id}>
                  <td>{req.user?.username}</td>
                  <td>{req.user?.email}</td>
                  <td>{req.status}</td>

                  <td>
                    <button disabled={processingId === req.id}
                      onClick={() => approveRequest(req.id)}>
                      Approve
                    </button>

                    <button disabled={processingId === req.id}
                      onClick={() => rejectRequest(req.id)}>
                      Reject
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* -------------------- LEAVE REQUESTS -------------------- */}

      <div className="leave-card">
        <h3>Company Leave Requests</h3>

        {leaveRequests.length === 0 ? (
          <p>No leave requests found.</p>
        ) : (
          <table className="leave-table">
            <thead>
              <tr>
                <th>Employee</th>
                <th>Type</th>
                <th>Start</th>
                <th>End</th>
                <th>Reason</th>
                <th>Status</th>
                <th width="220">Action</th>
              </tr>
            </thead>

            <tbody>
              {leaveRequests.map((req) => (
                <tr key={req.id}>
                  <td>{req.user?.username || "-"}</td>
                  <td>{req.leave_type}</td>

                  <td>
                    {new Date(req.start_date).toLocaleDateString()}
                  </td>

                  <td>
                    {new Date(req.end_date).toLocaleDateString()}
                  </td>

                  <td>{req.reason}</td>

                  <td>{req.status}</td>

                  <td>
                    {req.status === "pending" ? (
                      <>
                        <button disabled={processingId === req.id}
                          onClick={() => handleLeaveUpdate(req.id, "approved")}>
                          Approve
                        </button>

                        <button disabled={processingId === req.id}
                          onClick={() => handleLeaveUpdate(req.id, "rejected")}>
                          Reject
                        </button>
                      </>
                    ) : (
                      <span>{req.status}</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* ----------------- DOWNLOAD REPORTS ---------------- */}

      <div className="download-actions">
        <button onClick={handleExcelDownload}>
          <FaFileExcel /> Download Excel
        </button>

        <button onClick={handlePDFDownload}>
          <FaFilePdf /> Download PDF
        </button>
      </div>
    </>
  );
};

export default AttendanceAdminPanel;