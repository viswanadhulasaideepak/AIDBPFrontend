import React, { useState, useEffect } from "react";
import toast from "react-hot-toast";
import {
  getReactivationRequests,
  updateReactivationRequest,
} from "../../services/api";
import "./ReactivationsTab.css";

function ReactivationTab() {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(null);

  useEffect(() => {
    loadRequests();
  }, []);

  const loadRequests = async () => {
    try {
      setLoading(true);
      const data = await getReactivationRequests();
      setRequests(data);
    } catch (err) {
      console.error(err);
      toast.error("Failed to load requests");
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async (id, status) => {
    const confirmAction = window.confirm(
      `Are you sure you want to ${status} this request?`
    );

    if (!confirmAction) return;
    try {
      setProcessing(id);
      await updateReactivationRequest(id, status);
      toast.success(
        status === "approved"
          ? "User reactivated successfully"
          : "Request rejected"
      );

      loadRequests();
    } catch (err) {
      console.error(err);
      toast.error("Operation failed");
    } finally {
      setProcessing(null);
    }
  };

  if (loading) {
    return <h3>Loading Reactivation Requests...</h3>;
  }

  return (
    <div className="reactivation-container">
      <div className="page-header">
        <h2>Reactivation Requests</h2>
        <span>{requests.length} Requests</span>
      </div>
      <table className="reactivation-table">
        <thead>
          <tr>
            <th>User ID</th>
            <th>Admin Email</th>
            <th>Status</th>
            <th>Requested On</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {requests.length === 0 ? (
            <tr>
              <td colSpan="5" className="empty">
                No Reactivation Requests
              </td>
            </tr>
          ) : (
            requests.map((req) => (
              <tr key={req.id}>
                <td>{req.user_id}</td>
                <td>{req.admin_email}</td>
                <td>
                  <span className={`status ${req.status}`}>
                    {req.status}
                  </span>
                </td>
                <td>
                  {new Date(req.created_at).toLocaleString()}
                </td>
                <td>
                  {req.status === "pending" ? (
                    <>
                      <button disabled={processing === req.id}
                        className="approve-btn" onClick={() =>
                          handleUpdate(req.id, "approved")}>
                        Approve
                      </button>
                      <button disabled={processing === req.id}
                        className="reject-btn" onClick={() =>
                          handleUpdate(req.id, "rejected")
                        }>
                        Reject
                      </button>
                    </>
                  ) : (
                    <span className="completed">
                      Completed
                    </span>
                  )}
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
export default ReactivationTab;