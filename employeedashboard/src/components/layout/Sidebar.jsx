import React, { useContext } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import "./Sidebar.css";
import { AuthContext } from "../../auth/AuthContext";

const Sidebar = () => {
  const { user, logout } = useContext(AuthContext);
  const isSuspended = user?.status === "suspended";
  const isDeactivated = user?.status === "deactivated";
  
  const navigate = useNavigate();

  if (isDeactivated) {
  return (
    <aside className="sidebar">
      <h2 className="sidebar-title">EEMS</h2>
      <p style={{ color: "red", padding: "10px" }}>
        Account Deactivated
      </p>
    </aside>
  );
}

  const handleLogout = () => {
    logout();               
    navigate("/login");     
  };

  const menuItems = [
    { id: "myprofile", label: "👤 My Profile", path: "/my-profile", roles: ["user"]},
    { id: "logindevices", label: "💻 Login Devices", path: "/login-devices", roles: ["admin", "user"]},
    { id: "dashboard", label: "📊 Dashboard", path: "/dashboard", roles: ["admin", "user"] },
    { id: "employees", label: "👥 Employees", path: "/employees", roles: ["admin"] },
    { id: "departments", label: "🏢 Departments", path: "/departments", roles: ["admin"] },
    { id: "attendance", label: "📅 Attendance", path: "/attendance", roles: ["admin", "user"] },
    { id: "skills", label: "🛠 Skills", path: "/skills", roles: ["admin", "user"] },
    { id: "certifications", label: "🎓 Certifications", path: "/certifications", roles: ["admin", "user"] },
    { id: "holidaycalendar", label: "🎉 Holiday Calendar", path: "/holiday-calendar", roles: ["admin", "user"] },
    { id: "auditlogs", label: "📜 Audit Logs", path: "/audit-logs", roles: ["admin"] },
    { id: "activity", label: "🟢 User Activity", path: "/activity", roles: ["admin"] },
    { id: "devicemonitor", label: "🖥 Device Monitoring", path: "/admin/login-devices", roles: ["admin"] },
    { id: "dataexport", label: "📤 Data Export Center", path: "/data-export", roles: ["admin"] },
    { id: "invitations", label: "📩 Invitations", path: "/invitations", roles: ["admin"] },
    { id: "settings", label: "⚙️ Settings", path: "/settings", roles: ["admin", "user"] }
  ];

  return (
  <aside className="sidebar">
    <h2 className="sidebar-title">EEMS</h2>

    {isSuspended ? (
      <ul className="sidebar-links">
        <li>
          <NavLink to="/account-suspended"
            className={({ isActive }) => (isActive ? "active" : "")}>
            🚫 Account Suspended
          </NavLink>
        </li>
      </ul>
    ) : (
      <ul className="sidebar-links">
        {menuItems
          .filter((item) => item.roles.includes(user?.role))
          .map((item) => (
            <li key={item.id}>
              <NavLink to={item.path}
                className={({ isActive }) => (isActive ? "active" : "")}>
                {item.label}
              </NavLink>
            </li>
          ))}
      </ul>
    )}

    <button className="logout-btn" onClick={handleLogout}>
      🚪 Logout
    </button>
  </aside>
);
};

export default Sidebar;
