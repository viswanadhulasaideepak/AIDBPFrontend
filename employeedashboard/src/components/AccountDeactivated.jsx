import React, { useState, useEffect } from "react";
import toast from "react-hot-toast";
import {
  submitReactivationRequest,
  getMyReactivationRequest,
} from "../services/api";
import { useNavigate } from "react-router-dom";
import "./AccountDeactivated.css";

function AccountDeactivated({ currentUser }) {
  const [request, setRequest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState("");

  // ✅ Correct
  const navigate = useNavigate();

  useEffect(() => {
    if (!currentUser) {
      setLoading(false);
      return;
    }

    loadRequest();
  }, [currentUser]);

  const loadRequest = async () => {
    try {
      const data = await getMyReactivationRequest();
      setRequest(data);
    } catch (err) {
      console.error(err);

      if (err.response?.status !== 404) {
        toast.error("Failed to load reactivation request.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    try {
      setSubmitting(true);

      const newRequest = await submitReactivationRequest(message);

      setRequest(newRequest);

      toast.success("Reactivation request submitted successfully.");
    } catch (err) {
      console.error(err);

      toast.error(
        err.response?.data?.detail ||
          "Unable to submit reactivation request."
      );
    } finally {
      setSubmitting(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    localStorage.removeItem("role");
    localStorage.removeItem("company_id");

    toast.success("Logged out");

    navigate("/login");
  };

  if (loading) {
    return (
      <div className="deactivated-container">
        <h2>Loading...</h2>
      </div>
    );
  }

  return (
    <div className="deactivated-container">
      <div className="deactivated-card">
        <h1>Account Deactivated</h1>

        <p>
          Your account has been deactivated by your administrator.
        </p>

        <p>
          You can submit a reactivation request below. The administrator
          will review it.
        </p>

        {!request && (
          <>
            <h3>Additional Details (Optional)</h3>

            <textarea
              placeholder="Example: Please reactivate my account. I need access to continue working on my assigned tasks."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              rows={5}
            />

            <button
              className="submit-btn"
              onClick={handleSubmit}
              disabled={submitting}
            >
              {submitting
                ? "Submitting..."
                : "Submit Reactivation Request"}
            </button>
          </>
        )}

        {request && (
          <div className="status-section">
            <h3>Request Status</h3>

            <span className={`status-badge ${request.status}`}>
              {request.status.toUpperCase()}
            </span>

            {request.message && (
              <>
                <h4>Your Message</h4>
                <p>{request.message}</p>
              </>
            )}

            {request.status === "pending" && (
              <p>
                Your request has been submitted and is awaiting administrator
                approval.
              </p>
            )}

            {request.status === "approved" && (
              <p>
                Your account has been reactivated.
                Please logout and login again.
              </p>
            )}

            {request.status === "rejected" && (
              <p>
                Your request has been rejected by the administrator.
              </p>
            )}
          </div>
        )}

        <button className="logout-btn" onClick={handleLogout}>
          Logout
        </button>
      </div>
    </div>
  );
}

export default AccountDeactivated;