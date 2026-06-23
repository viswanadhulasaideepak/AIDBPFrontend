import React, { useEffect, useState } from "react";
import { fetchUserActivity, fetchActivityHistory } from "../../services/api";
import DashboardLayout from "../../components/layout/DashboardLayout";
import "./Activity.css";

const Activity = () => {
  const [activities, setActivities] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  const loadData = async () => {
    try {
      setLoading(true);
      const [activityData, historyData] = await Promise.all([
        fetchUserActivity(),
        fetchActivityHistory(),
      ]);
      setActivities(activityData || []);
      setHistory(historyData || []);
    } catch (err) {
      console.error(err);
      alert("Failed to load activity.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const filteredActivities = activities.filter((item) => {
    const value = search.toLowerCase();
    return (
      item.user?.username?.toLowerCase().includes(value) ||
      item.user?.email?.toLowerCase().includes(value) ||
      item.browser?.toLowerCase().includes(value) ||
      item.ip_address?.toLowerCase().includes(value)
    );
  });

  const formatDate = (date) => {
    if (!date) return "-";
    return new Date(date).toLocaleString();
  };

  return (
    <DashboardLayout>
    <div className="activity-layout">
      <div className="activity-container">
        <div className="activity-header">
          <div>
            <h1>User Activity</h1>
            <p>Monitor employee login sessions and device activity.</p>
          </div>
          <button className="refresh-btn" onClick={loadData}>
            Refresh
          </button>
        </div>
        <div className="summary-cards">
          <div className="summary-card">
            <h2>{activities.length}</h2>
            <span>Total Users</span>
          </div>
          <div className="summary-card">
            <h2>
              {
                activities.filter(
                  (a) => a.last_login
                ).length
              }
            </h2>
            <span>Logged In</span>
          </div>
          <div className="summary-card">
            <h2>
              {activities.filter(
                  (a) => a.last_logout
                ).length}
            </h2>
            <span>Logged Out</span>
          </div>
          <div className="summary-card">
            <h2>{history.length}</h2>
            <span>Activity Logs</span>
          </div>
        </div>
        <div className="activity-toolbar">
          <input type="text" placeholder="Search by user, browser or IP..."
            value={search} onChange={(e) => setSearch(e.target.value)}/>
        </div>
        <div className="activity-table">
          {loading ? (
            <div className="loading">
              Loading...
            </div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>User</th>
                  <th>Email</th>
                  <th>Browser</th>
                  <th>IP Address</th>
                  <th>Last Login</th>
                  <th>Last Logout</th>
                  
                </tr>
              </thead>
              <tbody>
                {filteredActivities.length === 0 ? (
                  <tr>
                    <td colSpan="8" style={{ textAlign: "center", padding: "40px",}}>
                      No activity found.
                    </td>
                  </tr>
                ) : (
                  filteredActivities.map((item) => (
                    <tr key={item.id}>
                      <td>
                        {item.username || "-"}
                      </td>
                      <td>
                        {item.email || "-"}
                      </td>
                      <td>
                        {item.browser || "-"}
                      </td>
                      <td>
                        {item.ip_address || "-"}
                      </td>
                      <td>
                        {formatDate(item.last_login)}
                      </td>
                      <td>
                        {formatDate(item.last_logout)}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          )}
        </div>
        <div className="history-section">
          <h2>Recent Activity History</h2>
          <table>
            <thead>
              <tr>
                <th>User</th>
                <th>Action</th>
                <th>Browser</th>
                <th>IP Address</th>
                <th>New Device</th>
                <th>New IP</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {history.length === 0 ? (
                <tr>
                  <td colSpan="5" style={{ textAlign: "center", padding: "40px",}}>
                    No history available.
                  </td>
                </tr>
              ) : (
                history.map((log) => (
                  <tr key={log.id}>
                    <td>
                      {log.user_name}
                    </td>
                    <td>
                      {log.action}
                    </td>
                    <td>
                      {log.browser || "-"}
                    </td>
                    <td>
                      {log.ip_address || "-"}
                    </td>
                    <td>
                        {log.is_new_device ? (
                            <span className="badge new-device">
                              Yes
                            </span>
                            ) : (
                            <span className="badge success">
                              No
                            </span>
                        )}
                    </td>
                    <td>
                        {log.is_new_ip ? (
                            <span className="badge new-ip">
                              Yes
                            </span>
                            ) : (
                            <span className="badge success">
                              No
                            </span>
                        )}
                    </td>
                    <td>
                        {formatDate(log.timestamp)}
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

export default Activity;