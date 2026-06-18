import React, { useContext, useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import toast from "react-hot-toast";
import { ThemeContext } from "../../context/ThemeContext";
import api, { updateAttendanceAccessRequest, updateLeaveRequest} from "../../services/api";
import "./Navbar.css";

const Navbar = () => {
  const { theme, toggleTheme } = useContext(ThemeContext);
  const [notifications, setNotifications] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);

  const storedUser = JSON.parse(localStorage.getItem("user"));
  const userName = storedUser?.fullName || "Admin User";
  const initials = userName.charAt(0).toUpperCase();

  // Fetch notifications
const loadNotifications = async () => {
  try {
    const response = await api.get("/notifications/");
    setNotifications(response.data || []);
  } catch (error) {
    console.error("Error fetching notifications:", error);
    setNotifications([]);
  }
};

useEffect(() => {
  // Initial load
  loadNotifications();

  // Refresh every 3 seconds
  const interval = setInterval(() => {
    loadNotifications();
  }, 3000);

  return () => clearInterval(interval);
}, []);

 // Mark a single notification as read
  const markAsRead = async (id) => {
  try {
    await api.put(`/notifications/${id}/read`);
    setNotifications((prev) =>
      prev.map((n) =>
        n.id === id
          ? { ...n, is_read: true }
          : n
      )
    );
  } catch (error) {
    console.error("Error marking notification as read:", error);
  }
};

  // Mark single notification as read
  const markAllAsRead = async () => {
  try {
    await Promise.all(
      notifications.map((n) =>
        api.put(`/notifications/${n.id}/read`)
      )
    );

    setNotifications((prev) =>
      prev.map((n) => ({ ...n, is_read: true }))
    );
  } catch (error) {
    console.error("Error marking all notifications as read:", error);
  }
};
  const approveAttendance = async (requestId) => {
  try {
    await updateAttendanceAccessRequest(requestId, "approved");
    toast.success("Attendance Approved");
    await loadNotifications();
  } catch (err) {
    toast.error("Approval failed");
  }
};

const rejectAttendance = async (requestId) => {
  try {
    await updateAttendanceAccessRequest(requestId,"rejected");
    toast.success("Attendance Access Rejected");
    const response = await api.get("/notifications");
    await loadNotifications();
  } catch (err) {
    toast.error("Request failed");
  }
};
const approveLeave = async (requestId) => {
    try {
        await updateLeaveRequest(requestId,"approved");
        toast.success("Leave Approved");
        const response = await api.get("/notifications");
        await loadNotifications();
    } catch {
        toast.error("Failed");
    }
};
const rejectLeave = async (requestId) => {
    try {
        await updateLeaveRequest(requestId,"rejected");
        toast.success("Leave Rejected");
        const response = await api.get("/notifications");
        await loadNotifications();
    } catch {
        toast.error("Failed");
    }
};

  return (
    <div className="navbar">
      <h2 className="navbar-title">Enterprise Employee Management System</h2>

      <div className="navbar-links">
        <NavLink to="/employees" className="nav-item">Employees</NavLink>
        <NavLink to="/departments" className="nav-item">Departments</NavLink>
        <NavLink to="/attendance" className="nav-item">Attendance</NavLink>
      </div>

      <div className="navbar-actions">
        {/* 🔔 Notification Bell */}
        <div className="notification-bell" onClick={() => setShowDropdown(!showDropdown)}>
          🔔
          {Array.isArray(notifications) &&
            notifications.filter((n) => !n.is_read).length > 0 && (
              <span className="badge">
                {notifications.filter((n) => !n.is_read).length}
              </span>
            )}
        </div>
        {showDropdown && (
          <div className="notification-dropdown">
            {notifications.length === 0 ? (
              <p>No notifications</p>
            ) : (
              <>
                <button className="mark-all-btn" onClick={markAllAsRead}>
                  ✔️ Mark All as Read
                </button>
                {notifications.map((n) => (
                  <div key={n.id} className={n.is_read ? "read" : "unread"}>
                    <p>{n.message}</p>
                    {storedUser?.role === "admin" &&
                    n.type === "attendance" && !n.is_read && (
                      <div className="notification-actions">
                      <button className="approve-btn"
                      onClick={() => approveAttendance(n.request_id)}>
                        ✓ Approve
                      </button>
                     <button className="reject-btn"
                     onClick={() => rejectAttendance(n.request_id)}>
                      ✗ Reject
                     </button>
                     </div>)}
                {storedUser?.role === "admin" &&
                n.type === "leave" && (
                  <div className="notification-actions">
                    <button onClick={() => approveLeave(n.request_id)}>
                      Approve
                    </button>
                    <button onClick={() => rejectLeave(n.request_id)}>
                      Reject
                    </button>
                  </div>)}
                    <button onClick={() => markAsRead(n.id)}>
                     Mark Read
                    </button>
                  </div>))}
              </>
            )}
          </div>
        )}
        {/* 🌙 Theme Toggle */}
        <button className="theme-toggle" onClick={toggleTheme}>
          {theme === "dark" ? "☀️" : "🌙"}
        </button>
        {/* 👤 User Info */}
        <div className="user-info">
          <span className="user-name">{userName}</span>
          <div className="user-avatar">
            <img
              src="https://placehold.co"
              alt="User Avatar"
              onError={(e) => {
                e.target.style.display = "none";
                e.target.nextSibling.style.display = "flex";
              }}
            />
            <div className="avatar-fallback">{initials}</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Navbar;
