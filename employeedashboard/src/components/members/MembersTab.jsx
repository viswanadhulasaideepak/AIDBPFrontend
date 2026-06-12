import React, { useState, useEffect } from "react";
import { getMembers, deactivateMember, reactivateMember } from "../../services/api";
import "./MembersTab.css"

function MembersTab() {
  const [members, setMembers] = useState([]);

  useEffect(() => {
    refreshMembers();
  }, []);

  const refreshMembers = async () => {
    const data = await getMembers();
    setMembers(data);
  };

  const handleDeactivate = async (id) => {
    await deactivateMember(id);
    refreshMembers();
  };

  const handleReactivate = async (id) => {
    await reactivateMember(id);
    refreshMembers();
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
