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
  const [selectedSessions,setSelectedSessions]=useState([]);

  // Pagination
const [currentPage, setCurrentPage] = useState(1);
const rowsPerPage = 10;

  const loadSessions = async () => {
    try {
      setLoading(true);
      const data = await fetchCompanyLoginSessions();
      console.log(data);
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

  const interval = setInterval(() => {
    loadSessions();
  }, 45000);

  return () => clearInterval(interval);

}, []);

  useEffect(() => {
    let data = [...sessions];
    if (search.trim()) {
        data = data.filter(session =>
    session.user_name
        ?.toLowerCase()
        .includes(search.toLowerCase()) ||

    session.user_email
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
    setCurrentPage(1);

},[
    search,
    statusFilter,
    browserFilter,
    loginDateFilter,
    sessions
]);

//-------------------Force Logout-----------------

  const handleForceLogout = async (id) => {
    if (!window.confirm("Force logout this session?")) return;
    try {
      await forceLogoutSession(id);
      toast.success("Session logged out.");
      setSelectedSessions([]);
      loadSessions();
    } catch {
      toast.error("Operation failed.");
    }

  };

  //-------------------HandleRevoke-----------------

  const handleRevoke = async (id) => {
    if (!window.confirm("Revoke this session?")) return;
    try {
      await revokeLoginSession(id);
      toast.success("Session revoked.");
      setSelectedSessions([]);
      loadSessions();
    } catch {
      toast.error("Operation failed.");
    }

  };

  // Pagination
const totalPages = Math.ceil(filteredSessions.length / rowsPerPage);

const startIndex = (currentPage - 1) * rowsPerPage;

const currentSessions = filteredSessions.slice(
    startIndex,
    startIndex + rowsPerPage
);

  //---------------Bulk Handle Revoke-----------------

  const handleBulkRevoke = async () => {

  if (selectedSessions.length === 0) {
    toast.error("No sessions selected");
    return;
  }

  if (!window.confirm("Revoke selected sessions?")) {
    return;
  }

  try {

    for (const id of selectedSessions) {
      await revokeLoginSession(id);
    }

    toast.success("Selected sessions revoked");

    setSelectedSessions([]);

    loadSessions();

  } catch {

    toast.error("Bulk revoke failed");

  }

};

  return (
    <DashboardLayout>
      <div className="admin-device-page">
        <h2>User Session Monitoring</h2>

        <div style={{ marginBottom: "15px" }}>
          <button className="bulk-revoke-btn"
           disabled={selectedSessions.length === 0}
           onClick={handleBulkRevoke}>
            Revoke Selected ({selectedSessions.length})
          </button>
        </div>

        <button className="refresh-btn" onClick={loadSessions}>
          Refresh
        </button>

        <div className="session-summary">
          <div className="summary-card">
            <h3>Total Sessions</h3>
            <p>{sessions.length}</p>
          </div>
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
          <div className="loading">
            Loading user sessions...
          </div>

        ) : (

          <table className="admin-device-table">
            <thead>
              <tr>
                <th>
                  <input type="checkbox"
                   checked={
                    filteredSessions.length > 0 &&
                    selectedSessions.length ===
                    filteredSessions.filter(
                       s => s.status === "active"
                      ).length
                    }
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedSessions(
                          filteredSessions.filter(s => s.status === "active").map(s => s.id));
                        } else {
                          setSelectedSessions([]);
                        }
                      }}/>
                </th>
                <th>User</th>
                <th>Email</th>
                <th>Device</th>
                <th>Browser</th>
                <th>IP</th>
                <th>Login</th>
                <th>Last Activity</th>
                <th>Status</th>
                <th>Termination</th>
                <th>Logged Out</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredSessions.length === 0 ? (
                <tr>
                  <td colSpan="12" style={{ textAlign: "center" }}>
                   No sessions found.
                  </td>
                </tr>
                ) : (
                  currentSessions.map((session) => (
                  <tr key={session.id}>
                    <td>
                      <input type="checkbox" disabled={session.status !== "active"}
                      checked={selectedSessions.includes(session.id)}
                       onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedSessions([
                            ...selectedSessions,
                            session.id,
                          ]);
                        } else {
                          setSelectedSessions(
                            selectedSessions.filter(
                              (id) => id !== session.id
                            )
                          );
                        }
                      }}/>
                    </td>

                    <td>{session.user_name}</td>
                    <td>{session.user_email}</td>
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

        <td>
          {new Date(session.login_time).toLocaleString()}
        </td>

        <td>
          {new Date(session.last_activity).toLocaleString()}
        </td>

        <td>
          <span className={`status ${session.status}`}>
           {session.status}
          </span>
        </td>

        <td>{session.termination_reason || "-"}</td>

        <td>
          {session.logged_out_at
            ? new Date(session.logged_out_at).toLocaleString()
            : "-"}
        </td>

        <td>
          {session.status === "active" ? (
            <>
              <button disabled={loading}
                onClick={() =>
                  handleForceLogout(session.id)}>
                Force Logout
              </button>

              <button disabled={loading}
                onClick={() =>
                  handleRevoke(session.id)}>
                Revoke
              </button>
            </>
          ) : (
            <span>No Actions</span>
          )}
        </td>
      </tr>
    ))
  )}
</tbody>
          </table>
        )}
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
  );
};

export default AdminLoginDevices;