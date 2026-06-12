import React, { useState, useEffect } from "react";
import { submitReactivationRequest, getReactivationRequests } from "../services/api";
import "./AccountDeactivated.css"

function AccountDeactivated({ currentUser }) {
  const [request, setRequest] = useState(null);

  useEffect(() => {
    // Load any existing reactivation request for this user
    const loadRequest = async () => {
      const allRequests = await getReactivationRequests();
      const myReq = allRequests.find(r => r.user_id === currentUser.id);
      setRequest(myReq || null);
    };
    loadRequest();
  }, [currentUser]);

  const handleSubmit = async () => {
    const newReq = await submitReactivationRequest();
    setRequest(newReq);
  };

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h2>Your Account is Deactivated</h2>
      <p>Please submit a reactivation request to regain access.</p>

      {request ? (
        <p>Request Status: <strong>{request.status}</strong></p>
      ) : (
        <button onClick={handleSubmit}>Submit Reactivation Request</button>
      )}
    </div>
  );
}

export default AccountDeactivated;
