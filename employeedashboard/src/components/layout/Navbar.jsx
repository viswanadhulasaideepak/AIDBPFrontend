import React, { useContext, useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { ThemeContext } from "../../context/ThemeContext";
import api from "../../services/api";
import "./Navbar.css";

const Navbar = () => {
  const { theme, toggleTheme } = useContext(ThemeContext);
  const [notifications, setNotifications] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);

  const storedUser = JSON.parse(localStorage.getItem("user"));
  const userName = storedUser?.fullName || "Admin User";
  const initials = userName.charAt(0).toUpperCase();

  // Fetch notifications safely
  useEffect(() => {
  const loadNotifications = async () => {
    try {
      const response = await api.get("/notifications/");
      setNotifications(response.data || []);
    } catch (error) {
      console.error("Error fetching notifications:", error);
      setNotifications([]);
    }
  };

  loadNotifications();
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

  // Mark all as read
 /* const markAllAsRead = async () => {
    await Promise.all(
      notifications.map((n) =>
        fetch(`http://127.0.0.1:8000/notifications/${n.id}/read`, {
          method: "PUT",
        })
      )
    );
    setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
  };*/

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
                  <p
                    key={n.id}
                    className={n.is_read ? "read" : "unread"}
                    onClick={() => markAsRead(n.id)}
                  >
                    {n.message}
                  </p>
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
