import React, { useEffect, useState } from "react";
import { downloadExport, fetchExportHistory,} from "../../services/api";
import DashboardLayout from "../../components/layout/DashboardLayout";
import toast from "react-hot-toast";
import "./DataExportCenter.css";

const DataExportCenter = () => {
  const [selectedData, setSelectedData] = useState("employees");
  const [selectedFormat, setSelectedFormat] = useState("csv");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadHistory = async () => {
    try {
      const data = await fetchExportHistory();
      setHistory(data);
    } catch (err) {
      console.error(err);
      toast.error("Failed to load export history");
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleExport = async () => {
    try {
      setLoading(true);

      await downloadExport(
        selectedData,
        selectedFormat
      );

      toast.success("Export completed");
      loadHistory();
    } catch (err) {
      console.error(err);
      toast.error("Export failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>

      <div className="export-container">
        <h1>Data Export Center</h1>
        <div className="export-card">
          <div className="section">
            <h2>Export Data</h2>
            <label>Select Data</label>
            <select value={selectedData}
              onChange={(e) =>
                setSelectedData(e.target.value)}>

              <option value="employees">
                Employees
              </option>
              <option value="attendance">
                Attendance
              </option>
              <option value="leave">
                Leave Requests
              </option>
              <option value="audit">
                Audit Logs
              </option>
              <option value="notifications">
                Notifications
              </option>
              <option value="analytics">
                Analytics
              </option>
            </select>
            <label>Format</label>
            <select value={selectedFormat}
              onChange={(e) =>
                setSelectedFormat(e.target.value)}>
              <option value="csv">
                CSV
              </option>
              <option value="excel">
                Excel
              </option>
              <option value="pdf">
                PDF
              </option>
            </select>
            <button onClick={handleExport} disabled={loading}>
              {loading ? "Exporting...": "Export"}
            </button>
          </div>
          <div className="section history-section">
            <h2>Export History</h2>
            <table className="history-table">
              <thead>
                <tr>
                  <th>Who Exported</th>
                  <th>When</th>
                  <th>What Data</th>
                  <th>Format</th>
                </tr>
              </thead>
              <tbody>
                {history.length === 0 ? (
                  <tr>
                    <td colSpan="4">
                      No export history found.
                    </td>
                  </tr>
                ) : (
                  history.map((item) => (
                    <tr key={item.id}>
                      <td>{item.exported_by}</td>
                      <td>
                        {new Date(
                          item.exported_at
                        ).toLocaleString()}
                      </td>
                      <td>{item.data_type}</td>
                      <td>
                        {item.export_format}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default DataExportCenter;