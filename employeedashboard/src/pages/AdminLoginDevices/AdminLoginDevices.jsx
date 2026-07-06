import React, { useEffect, useState } from "react";
import toast from "react-hot-toast";
import DashboardLayout from "../../components/layout/DashboardLayout";
import {fetchCompanyLoginSessions,forceLogoutSession,revokeLoginSession,} from "../../services/api";
import "./AdminLoginDevices.css";

const AdminLoginDevices = () => {

  const [sessions, setSessions] = useState([]);
  const [filteredSessions, setFilteredSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");
  const [browserFilter, setBrowserFilter] = useState("All");
  const [loginDateFilter, setLoginDateFilter] = useState("");

  const loadSessions = async () => {
    try {
      setLoading(true);
      const data = await fetchCompanyLoginSessions();
      setSessions(data);
      setFilteredSessions(data);

    } catch (err) {
      toast.error("Unable to load sessions.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSessions();
  }, []);

  useEffect(() => {
    let data = [...sessions];
    if (search.trim()) {
        data = data.filter(session =>
            session.user_name
                ?.toLowerCase()
                .includes(search.toLowerCase())
        );
    }

    if (statusFilter !== "All") {
        data = data.filter(
            session => session.status === statusFilter
        );

    }

    if (browserFilter !== "All") {
        data = data.filter(session =>
            session.browser
                ?.toLowerCase()
                .includes(browserFilter.toLowerCase())
        );
    }

    if (loginDateFilter) {

        data = data.filter(session => {
            return (
                new Date(session.login_time)
                    .toISOString()
                    .slice(0,10)
                === loginDateFilter
            );
        });
    }
    setFilteredSessions(data);

},[
    search,
    statusFilter,
    browserFilter,
    loginDateFilter,
    sessions
]);

  const handleForceLogout = async (id) => {
    if (!window.confirm("Force logout this session?")) return;
    try {
      await forceLogoutSession(id);
      toast.success("Session logged out.");
      loadSessions();
    } catch {
      toast.error("Operation failed.");
    }

  };

  const handleRevoke = async (id) => {
    if (!window.confirm("Revoke this session?")) return;
    try {
      await revokeLoginSession(id);
      toast.success("Session revoked.");
      loadSessions();
    } catch {
      toast.error("Operation failed.");
    }

  };

  return (
    <DashboardLayout>
      <div className="admin-device-page">
        <h2>Device Monitoring</h2>

        <div className="session-summary">
          <div className="summary-card">
            <h3>Active</h3>
            <p>{sessions.filter(s=>s.status==="active").length}</p>
          </div>
          <div className="summary-card">
           <h3>Logged Out</h3>
           <p>{sessions.filter(s=>s.status==="logged_out").length}</p>
          </div>

          <div className="summary-card">
           <h3>Revoked</h3>
           <p>{sessions.filter(s=>s.status==="revoked").length}</p>
          </div>

          <div className="summary-card">
            <h3>Expired</h3>
            <p>{sessions.filter(s=>s.status==="expired").length}</p>
          </div>

      </div>

        <div className="admin-device-toolbar">
          <input type="text" placeholder="Search User..." 
          value={search} onChange={(e)=>setSearch(e.target.value)}/>
          
          <select value={browserFilter} 
          onChange={(e)=>setBrowserFilter(e.target.value)}>
            <option>All</option>
            <option>Chrome</option>
            <option>Firefox</option>
            <option>Edge</option>
            <option>Safari</option>
          </select>

          <select value={statusFilter}
          onChange={(e)=>setStatusFilter(e.target.value)}>
            <option>All</option>
            <option>active</option>
            <option>logged_out</option>
            <option>revoked</option>
            <option>expired</option>
          </select>
          
          <input type="date" value={loginDateFilter}
           onChange={(e)=>setLoginDateFilter(e.target.value)}/>
        </div>
        {loading ? (
          <p>Loading...</p>

        ) : (

          <table className="admin-device-table">
            <thead>
              <tr>
                <th>User</th>
                <th>Device</th>
                <th>Browser</th>
                <th>IP</th>
                <th>Login</th>
                <th>Last Activity</th>
                <th>Status</th>
                <th>Termination</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>
              {filteredSessions.map((session) => (
                <tr key={session.id}>
                  <td>{session.user_name}</td>
                  <td>
                    <div>{session.device_name}
                      {session.is_current && (
                        <span className="badge current">
                          Current
                        </span>
                      )}
                      {session.is_trusted && (
                        <span className="badge trusted">
                          Trusted
                        </span>
                      )}
                    </div>
                  </td>
                  <td>{session.browser}</td>
                  <td>{session.ip_address}</td>
                  <td>{new Date(session.login_time).toLocaleString()}</td>
                  <td>{new Date(session.last_activity).toLocaleString()}</td>
                  <td>
                    <span className={`status ${session.status}`}>
                      {session.status}
                    </span>
                  </td>
                  <td>{session.termination_reason ? session.termination_reason : "-"}</td>
                  <td>

                    {session.status === "active" && (

                      <>

                        <button onClick={() => handleForceLogout(session.id)}>
                          Force Logout
                        </button>

                        <button onClick={() => handleRevoke(session.id)}>
                          Revoke
                        </button>
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </DashboardLayout>
  );
};

export default AdminLoginDevices;