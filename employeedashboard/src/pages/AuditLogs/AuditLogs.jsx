import React, { useEffect, useState } from "react";
import DashboardLayout from "../../components/layout/DashboardLayout";
import { fetchAuditLogs } from "../../services/api";
import "./AuditLogs.css"

const AuditLogs = () => {
  const [logs, setLogs] = useState([]);

  const [currentPage, setCurrentPage] = useState(1);
  const rowsPerPage = 10;

  useEffect(() => {
    loadLogs();
  }, []);

  const loadLogs = async () => {
    try {
      const data = await fetchAuditLogs();
      setLogs(data);
      setCurrentPage(1);
    } catch (err) {
      console.error(err);
    }
  };
  // Pagination
const totalPages = Math.ceil(logs.length / rowsPerPage);

const startIndex = (currentPage - 1) * rowsPerPage;

const currentLogs = logs.slice(
  startIndex,
  startIndex + rowsPerPage
);

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
        {currentLogs.map((log) => (
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
    <div className="pagination">

  <button disabled={currentPage === 1}
    onClick={() => setCurrentPage(currentPage - 1)}>
    Previous
  </button>

  {[...Array(totalPages)].map((_, index) => (
    <button key={index} className={currentPage === index + 1 ? "active-page" : ""}
      onClick={() => setCurrentPage(index + 1)}>
      {index + 1}
    </button>
  ))}

  <button disabled={currentPage === totalPages || totalPages === 0}
    onClick={() => setCurrentPage(currentPage + 1)}>
    Next
  </button>

</div>
    </div>
  </DashboardLayout>
  )
};

export default AuditLogs;