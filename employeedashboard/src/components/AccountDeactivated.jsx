import React, { useState, useEffect } from "react";
import toast from "react-hot-toast";
import {
  submitReactivationRequest,
  getMyReactivationRequest,
} from "../services/api";
import "./AccountDeactivated.css";

function AccountDeactivated({ currentUser }) {
  const [request, setRequest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

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

      // No request yet is okay
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

      const newRequest = await submitReactivationRequest();

      setRequest(newRequest);

      toast.success("Reactivation request submitted successfully.");
    } catch (err) {
      console.error(err);

      toast.error(
        err.response?.data?.detail || "Unable to submit request."
      );
    } finally {
      setSubmitting(false);
    }
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
          You currently cannot access application features.
        </p>

        <p>
          You may submit a reactivation request below.
        </p>

        {request ? (
          <div className="status-section">
            <h3>Request Status</h3>

            <span className={`status-badge ${request.status}`}>
              {request.status.toUpperCase()}
            </span>

            {request.status === "pending" && (
              <p>
                Your request has been submitted and is waiting for admin
                approval.
              </p>
            )}

            {request.status === "approved" && (
              <p>
                Your account has been reactivated. Please login again.
              </p>
            )}

            {request.status === "rejected" && (
              <p>
                Your request was rejected by the administrator.
              </p>
            )}
          </div>
        ) : (
          <button
            className="submit-btn"
            onClick={handleSubmit}
            disabled={submitting}
          >
            {submitting
              ? "Submitting..."
              : "Submit Reactivation Request"}
          </button>
        )}
      </div>
    </div>
  );
}

export default AccountDeactivated;