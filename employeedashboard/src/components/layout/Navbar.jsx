import React, { useContext, useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import toast from "react-hot-toast";
import { ThemeContext } from "../../context/ThemeContext";
import api, { updateAttendanceAccessRequest, updateLeaveRequest,approveReinstatement,
  rejectReinstatement,} from "../../services/api";
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
    console.log(response.data);
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
    toast.success("Notification marked as read");

    await loadNotifications();
  } catch (error) {
    console.error(error);
    toast.error("Unable to mark notification");
  }
};

  // Mark notification as read all
  const markAllAsRead = async () => {
  try {
    await api.put("/notifications/read-all");

    toast.success("All notifications marked as read");

    await loadNotifications();
  } catch (err) {
    console.error(err);
  }
};

//----Approve Attendance--------------
  const approveAttendance = async (requestId) => {
  try {
    await updateAttendanceAccessRequest(requestId, "approved");
    toast.success("Attendance Approved");
    await loadNotifications();
  } catch (err) {
    console.error(err);
    toast.error("Approval failed");
  }
};

// --Reject Attendance------------
  const rejectAttendance = async (requestId) => {
  try {
    await updateAttendanceAccessRequest(requestId, "rejected");
    toast.success("Attendance Rejected");
    await loadNotifications();
  } catch (err) {
    console.error(err);
    toast.error("Request failed");
  }
};

  //----Approve Leave----------------
  const approveLeave = async (requestId) => {
  try {
    await updateLeaveRequest(requestId, "approved");
    toast.success("Leave Approved");
    await loadNotifications();
  } catch (err) {
    console.error(err);
    toast.error("Approval failed");
  }
};

//--------Reject Leave----------------
  const rejectLeave = async (requestId) => {
  try {
    await updateLeaveRequest(requestId, "rejected");
    toast.success("Leave Rejected");
    await loadNotifications();
  } catch (err) {
    console.error(err);
    toast.error("Rejection failed");
  }
};

//--------------Approve Reinstatement-----------------
const approveReinstatementRequest = async (requestId) => {
  try {
    await approveReinstatement(requestId, "");
    toast.success("Reinstatement Approved");
    await loadNotifications();
  } catch (err) {
    console.error(err);
    toast.error("Approval failed");
  }
};

//------------------Rejct Reinstatement-----------------------
const rejectReinstatementRequest = async (requestId) => {
  try {
    await rejectReinstatement(requestId, "");
    toast.success("Reinstatement Rejected");
    await loadNotifications();
  } catch (err) {
    console.error(err);
    toast.error("Rejection failed");
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

            {/* Attendance */}
            {storedUser?.role === "admin" &&
              n.type === "attendance" &&
               n.status === "pending" && (
                <div className="notification-actions">
                  <button className="approve-btn"
                    onClick={() => approveAttendance(n.request_id)}>
                    ✓ Approve
                  </button>
                  <button className="reject-btn"
                    onClick={() => rejectAttendance(n.request_id)}>
                    ✗ Reject
                  </button>
                </div>
              )}

            {/* Leave */}
            {storedUser?.role === "admin" &&
              n.type === "leave" &&
               n.status === "pending" && (
                <div className="notification-actions">
                  <button className="approve-btn"
                    onClick={() => approveLeave(n.request_id)}>
                    ✓ Approve
                  </button>
                  <button className="reject-btn"
                    onClick={() => rejectLeave(n.request_id)}>
                    ✗ Reject
                  </button>
                </div>
              )}

            {/* Reinstatement */}
            {storedUser?.role === "admin" &&
              n.type === "reinstatement" &&
               n.status === "pending" && (
                <div className="notification-actions">
                  <button className="approve-btn"
                    onClick={() => approveReinstatementRequest(n.request_id)}>
                    ✓ Approve
                  </button>
                  <button className="reject-btn"
                    onClick={() => rejectReinstatementRequest(n.request_id)}>
                    ✗ Reject
                  </button>
                </div>
              )}
            <button onClick={() => markAsRead(n.id)}>
              Mark Read
            </button>
          </div>
        ))}
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
            <img src="https://placehold.co" alt="User Avatar" onError={(e) => {
                e.target.style.display = "none";
                e.target.nextSibling.style.display = "flex";}}/>
            <div className="avatar-fallback">{initials}</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Navbar;
