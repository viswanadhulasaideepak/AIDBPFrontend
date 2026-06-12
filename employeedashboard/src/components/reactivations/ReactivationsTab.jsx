import React, { useState, useEffect } from "react";
import { getReactivationRequests, updateReactivationRequest } from "../../services/api";
import "./ReactivationsTab.css"

function ReactivationTab() {
  const [requests, setRequests] = useState([]);

  useEffect(() => {
    refreshRequests();
  }, []);

  const refreshRequests = async () => {
    const data = await getReactivationRequests();
    setRequests(data);
  };

  const handleUpdate = async (id, status) => {
    await updateReactivationRequest(id, status);
    refreshRequests();
  };

  return (
    <div>
      <h2>Reactivation Requests</h2>
      <table>
        <thead>
          <tr>
            <th>User ID</th>
            <th>Admin Email</th>
            <th>Status</th>
            <th>Created At</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {requests.map((req) => (
            <tr key={req.id}>
              <td>{req.user_id}</td>
              <td>{req.admin_email}</td>
              <td>{req.status}</td>
              <td>{new Date(req.created_at).toLocaleString()}</td>
              <td>
                {req.status === "pending" && (
                  <>
                    <button onClick={() => handleUpdate(req.id, "approved")}>
                      Approve
                    </button>
                    <button onClick={() => handleUpdate(req.id, "rejected")}>
                      Reject
                    </button>
                  </>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default ReactivationTab;
