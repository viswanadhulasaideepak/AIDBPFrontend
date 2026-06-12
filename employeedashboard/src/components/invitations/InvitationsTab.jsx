import React, { useState, useEffect } from "react";
import { createInvitation, getInvitations, revokeInvitation } from "../../services/api";
import "./InvitationsTab.css"

function InvitationsTab() {
  const [invitations, setInvitations] = useState([]);
  const [email, setEmail] = useState("");
  const [expiresAt, setExpiresAt] = useState("");

  // Load invitations on mount
  useEffect(() => {
    refreshInvitations();
  }, []);

  const refreshInvitations = async () => {
    const data = await getInvitations();
    setInvitations(data);
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    await createInvitation(email, expiresAt || null);
    setEmail("");
    setExpiresAt("");
    refreshInvitations();
  };

  const handleRevoke = async (id) => {
    await revokeInvitation(id);
    refreshInvitations();
  };

  const handleCopyLink = (token) => {
    const link = `${window.location.origin}/signup?token=${token}`;
    navigator.clipboard.writeText(link);
    alert("Invitation link copied!");
  };

  return (
    <div>
      <h2>Invitations</h2>

      {/* Create Invitation Form */}
      <form onSubmit={handleCreate}>
        <input
          type="email"
          placeholder="User email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="date"
          value={expiresAt}
          onChange={(e) => setExpiresAt(e.target.value)}
        />
        <button type="submit">Create Invitation</button>
      </form>

      {/* Invitations List */}
      <table>
        <thead>
          <tr>
            <th>Email</th>
            <th>Status</th>
            <th>Created At</th>
            <th>Expires At</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {invitations.map((inv) => (
            <tr key={inv.id}>
              <td>{inv.email}</td>
              <td>{inv.status}</td>
              <td>{new Date(inv.created_at).toLocaleString()}</td>
              <td>{inv.expires_at ? new Date(inv.expires_at).toLocaleDateString() : "—"}</td>
              <td>
                <button onClick={() => handleCopyLink(inv.token)}>Copy Link</button>
                {inv.status === "pending" && (
                  <button onClick={() => handleRevoke(inv.id)}>Revoke</button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default InvitationsTab;
