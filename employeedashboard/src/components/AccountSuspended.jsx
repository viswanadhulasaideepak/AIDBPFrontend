import React, { useEffect, useState } from "react";
import toast from "react-hot-toast";
import DashboardLayout from "./layout/DashboardLayout";
import "./AccountDeactivated.css"

import {
  fetchAccountStatus,
  submitReinstatementRequest,
  fetchMyReinstatementRequest,
} from "../services/api";

const AccountSuspended = () => {
  const [account, setAccount] = useState(null);
  const [request, setRequest] = useState(null);
  const [reason, setReason] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);

      const accountData = await fetchAccountStatus();
      setAccount(accountData);

      try {
        const requestData = await fetchMyReinstatementRequest();
        setRequest(requestData);
      } catch (err) {
        setRequest(null);
      }
    } catch (err) {
      toast.error("Failed to load suspension details.");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!reason.trim()) {
      toast.error("Please enter a reason.");
      return;
    }

    try {
      setSubmitting(true);

      await submitReinstatementRequest(reason);

      toast.success("Reinstatement request submitted.");

      setReason("");

      loadData();
    } catch (err) {
      toast.error(
        err?.response?.data?.detail ||
          "Unable to submit request."
      );
    } finally {
      setSubmitting(false);
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    window.location.href = "/login";
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div
          style={{
            padding: 50,
            textAlign: "center",
          }}
        >
          Loading...
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div
        style={{
          maxWidth: 700,
          margin: "40px auto",
          background: "#fff",
          padding: 30,
          borderRadius: 10,
          boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
        }}
      >
        <h1 style={{ color: "red" }}>
          🚫 Account Suspended
        </h1>

        <p>
          Your account has been suspended by your company
          administrator.
        </p>

        <hr />

        <h3>Suspension Details</h3>

        <p>
          <strong>Status :</strong>{" "}
          {account?.status}
        </p>

        <p>
          <strong>Suspended On :</strong>{" "}
          {account?.suspended_at
            ? new Date(
                account.suspended_at
              ).toLocaleString()
            : "-"}
        </p>

        <p>
          <strong>Suspended By :</strong>{" "}
          {account?.suspended_by || "-"}
        </p>

        <p>
          <strong>Reason :</strong>{" "}
          {account?.suspension_reason || "-"}
        </p>

        <hr />

        {request ? (
          <>
            <h3>Reinstatement Request</h3>

            <p>
              <strong>Status :</strong>{" "}
              {request.status}
            </p>

            <p>
              <strong>Your Reason :</strong>
              <br />
              {request.reason}
            </p>

            {request.admin_comment && (
              <p>
                <strong>Admin Comment :</strong>
                <br />
                {request.admin_comment}
              </p>
            )}

            {request.reviewed_at && (
              <p>
                <strong>Reviewed On :</strong>{" "}
                {new Date(
                  request.reviewed_at
                ).toLocaleString()}
              </p>
            )}
          </>
        ) : (
          <>
            <h3>Request Reinstatement</h3>

            <textarea
              rows={5}
              value={reason}
              onChange={(e) =>
                setReason(e.target.value)
              }
              placeholder="Explain why your account should be reinstated..."
              style={{
                width: "100%",
                padding: 10,
                marginTop: 10,
              }}
            />

            <button
              onClick={handleSubmit}
              disabled={submitting}
              style={{
                marginTop: 15,
                padding: "10px 20px",
                cursor: "pointer",
              }}
            >
              {submitting
                ? "Submitting..."
                : "Submit Reinstatement Request"}
            </button>
          </>
        )}

        <hr />

        <button
          onClick={handleLogout}
          style={{
            marginTop: 15,
            padding: "10px 20px",
          }}
        >
          Logout
        </button>
      </div>
    </DashboardLayout>
  );
};

export default AccountSuspended;