import React, { useState, useEffect } from "react";
import { getMembers, deactivateMember, reactivateMember } from "../../services/api";
import "./MembersTab.css"

function MembersTab() {
  const [members, setMembers] = useState([]);

  useEffect(() => {
    refreshMembers();
  }, []);

  const refreshMembers = async () => {
    try {
        const data = await getMembers();
        setMembers(data);
    } catch (err) {
        console.error(err);
    }
};

  const handleDeactivate = async (id) => {
    if (!window.confirm("Deactivate this member?")) return;

    try {
        await deactivateMember(id);
        alert("Member deactivated successfully.");
        refreshMembers();
    } catch (err) {
        console.error(err);
        alert("Failed to deactivate member.");
    }
};

  const handleReactivate = async (id) => {
    if (!window.confirm("Reactivate this member?")) return;

    try {
        await reactivateMember(id);
        alert("Member reactivated successfully.");
        refreshMembers();
    } catch (err) {
        console.error(err);
        alert("Failed to reactivate member.");
    }
};

  return (
    <div>
      <h2>Members</h2>
      <table>
        <thead>
          <tr>
            <th>Username</th>
            <th>Email</th>
            <th>Role</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {members.map((m) => (
            <tr key={m.id}>
              <td>{m.username}</td>
              <td>{m.email}</td>
              <td>{m.role}</td>
              <td>{m.status}</td>
              <td>
                {m.status === "active" ? (
                  <button onClick={() => handleDeactivate(m.id)}>Deactivate</button>
                ) : (
                  <button onClick={() => handleReactivate(m.id)}>Reactivate</button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default MembersTab;
