import React, { useState, useEffect } from "react";
import { createInvitation, getInvitations, revokeInvitation } from "../../services/api";
import toast from "react-hot-toast";
import "./InvitationsTab.css"

function InvitationsTab() {
  const [invitations, setInvitations] = useState([]);
  const [email, setEmail] = useState("");
  const [expiresAt, setExpiresAt] = useState("");
  const [role, setRole] = useState("user");

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

    try {
        await createInvitation(email,role, expiresAt || null);
        toast.success("Invitation created successfully!");
        setEmail("");
        setExpiresAt("");
        refreshInvitations();
    } catch (err) {
        toast.error(err.response?.data?.detail || "Unable to create invitation");
    }
  };

  const handleRevoke = async (id) => {
    try {
        await revokeInvitation(id);
        toast.success("Invitation revoked.");
        refreshInvitations();
    } catch (err) {
        toast.error("Unable to revoke invitation.");
    }
  };

  const handleCopyLink = (inv) => {
    const link = `${window.location.origin}/login?invite=${inv.token}`;

    navigator.clipboard.writeText(link);
    toast.success("Invitation link copied!");
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
        <select value={role} onChange={(e) => setRole(e.target.value)}>
          <option value="user">User</option>
          <option value="admin">Admin</option>
          </select>
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
                <button onClick={() => handleCopyLink(inv)}>Copy Link</button>
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
