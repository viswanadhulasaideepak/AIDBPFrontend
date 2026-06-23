import React, { useEffect, useState } from "react";
import DashboardLayout from "../../components/layout/DashboardLayout";
import { fetchAuditLogs } from "../../services/api";
import "./AuditLogs.css"

const AuditLogs = () => {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    loadLogs();
  }, []);

  const loadLogs = async () => {
    try {
      const data = await fetchAuditLogs();
      setLogs(data);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <DashboardLayout>
      <div className="audit-container">
        <h2 className="audit-title">📜 Audit Logs</h2>

    <table className="audit-table">
      <thead>
        <tr>
          <th>User</th>
          <th>Action</th>
          <th>Related User</th>
          <th>Timestamp</th>
        </tr>
      </thead>

      <tbody>
        {logs.map((log) => (
          <tr key={log.id}>
            <td className="audit-user">{log.user_name}</td>
            <td className="audit-action">{log.action}</td>
            <td>{log.related_user}</td>
            <td className="audit-time">
              {new Date(log.timestamp).toLocaleString()}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
    </div>
  </DashboardLayout>
  )
};

export default AuditLogs;