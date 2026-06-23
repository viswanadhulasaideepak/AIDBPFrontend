import React, { useEffect, useState } from "react";
import DashboardLayout from "../../components/layout/DashboardLayout";
import "./Settings.css";

const Settings = () => {
  const [user, setUser] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [roleRequests, setRoleRequests] = useState([]);

  // Load user safely
  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    if (storedUser) setUser(JSON.parse(storedUser));
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("user");
    window.location.href = "/login";
  };

  const toggleTheme = (mode) => {
    document.body.classList.toggle("dark-theme", mode === "dark");
  };

  //  Notifications fetch with token + localhost
  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        if (!user?.token) return;
        const res = await fetch("http://localhost:8000/notifications/", {
          headers: {
            Authorization: `Bearer ${user.token}`,
          },
        });
        if (!res.ok) throw new Error("Unauthorized or server error");
        const data = await res.json();

        if (Array.isArray(data)) {
          setNotifications(prev =>
            JSON.stringify(prev) !== JSON.stringify(data) ? data : prev
          );
        }
      } catch (err) {
        console.error("Error fetching notifications:", err);
      }
    };

    fetchNotifications();
    const interval = setInterval(fetchNotifications, 3000);
    return () => clearInterval(interval);
  }, [user]);

//----mark as read-----------
  const markAsRead = async (id) => {
    if (!user?.token) return;
    await fetch(`http://localhost:8000/notifications/${id}/read`, {
      method: "PUT",
      headers: { Authorization: `Bearer ${user.token}` },
    });
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
    );
  };

  const markAllAsRead = async () => {
    if (!user?.token) return;
    await Promise.all(
      notifications.map((n) =>
        fetch(`http://localhost:8000/notifications/${n.id}/read`, {
          method: "PUT",
          headers: { Authorization: `Bearer ${user.token}` },
        })
      )
    );
    setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
  };

  // Fetch Role Requests (Admin only)
  useEffect(() => {
    if (user?.role === "admin" && user?.token) {
      fetch("http://localhost:8000/role-change-request/", {
        headers: { Authorization: `Bearer ${user.token}` },
      })
        .then((res) => res.json())
        .then((data) => setRoleRequests(Array.isArray(data) ? data : []))
        .catch((err) => console.error("Error fetching role requests:", err));
    }
  }, [user]);

  // User sends role request
  const sendRoleRequest = async (e) => {
    e.preventDefault();
    const password = e.target.password.value;
    const adminEmail = e.target.adminEmail.value;

    try {
      if (!user?.token) return;
      const res = await fetch("http://localhost:8000/role-change-request/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${user.token}`,
        },
        body: JSON.stringify({
          current_password: password,
          admin_email: adminEmail,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        alert("Role request submitted successfully!");
        console.log("Response:", data);
        e.target.reset();
      } else {
        const err = await res.json();
        console.error("Request failed:", err);
        alert(JSON.stringify(err, null, 2));
      }
    } catch (error) {
      console.error("Error sending role request:", error);
      alert("Unable to connect to backend. Check if FastAPI is running and CORS allows your frontend port.");
    }
  };

  // Admin approves/rejects
  const updateRequest = async (id, status) => {
    try {
      if (!user?.token) return;
      const res = await fetch(`http://localhost:8000/role-change-request/${id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${user.token}`,
        },
        body: JSON.stringify({ status }),
      });

      if (res.ok) {
        setRoleRequests((prev) =>
          prev.map((r) => (r.id === id ? { ...r, status } : r))
        );
      } else {
        const err = await res.json();
        console.error("Update failed:", err);
        alert(JSON.stringify(err, null, 2));
      }
    } catch (error) {
      console.error("Error updating request:", error);
      alert("Unable to connect to backend. Check if FastAPI is running and CORS allows your frontend port.");
    }
  };

  return (
    <DashboardLayout>
      <div className="settings-container">
        <h2>⚙️ Settings</h2>

        {/* User Info */}
        <div className="settings-card">
          <h3>User Info</h3>
          <p>Role: {user?.role}</p>
          <button onClick={handleLogout}>🚪 Logout</button>
        </div>

        {/* User Role Request */}
        {user?.role === "user" && (
          <div className="settings-card">
            <h3>Request Role Change</h3>
            <form onSubmit={sendRoleRequest}>
              <input type="password" name="password" placeholder="Current Password" required />
              <input type="email" name="adminEmail" placeholder="Admin Email" required />
              <button type="submit">Send Request</button>
            </form>
          </div>
        )}

        {/* Admin Role Requests */}
        {user?.role === "admin" && (
          <div className="settings-card">
            <h3>📋 Role Requests</h3>
            {roleRequests.length === 0 ? (
              <p>No requests</p>
            ) : (
              roleRequests.map((req) => (
                <div key={req.id} className="role-request-item">
                  <p><b>{req.user_name}</b></p>
                  <p>Status: {req.status}</p>

                  {req.status === "pending" && (
                    <div className="request-actions">
                      <button className="approve-btn"
                        onClick={() => updateRequest(req.id, "approved")}>
                        ✅ Approve
                      </button>
                      <button className="reject-btn"
                        onClick={() => updateRequest(req.id, "rejected")}>
                        ❌ Reject
                      </button>
                    </div>
                  )}
                  {req.status === "approved" && <p className="approved-text">✅ Approved</p>}
                  {req.status === "rejected" && <p className="rejected-text">❌ Rejected</p>}
                </div>
              ))
            )}
          </div>
        )}

        {/* Notifications */}
        <div className="settings-card">
          <h3>Notifications</h3>
          <button onClick={markAllAsRead}>✔️ Mark All Read</button>
          {notifications.map((n) => (
            <p key={n.id} onClick={() => markAsRead(n.id)}
              style={{
                fontWeight: n.is_read ? "normal" : "bold",
                cursor: "pointer",
              }}>
              {n.message}
            </p>
          ))}
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Settings;
