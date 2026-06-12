import React, { useContext } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import "./Sidebar.css";
import { AuthContext } from "../../auth/AuthContext";

const Sidebar = () => {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();               // clears localStorage + resets context
    navigate("/login");     // redirect to login
  };

  const menuItems = [
    { id: "dashboard", label: "📊 Dashboard", path: "/dashboard", roles: ["admin", "user"] },
    { id: "employees", label: "👥 Employees", path: "/employees", roles: ["admin"] },
    { id: "departments", label: "🏢 Departments", path: "/departments", roles: ["admin"] },
    { id: "attendance", label: "📅 Attendance", path: "/attendance", roles: ["admin", "user"] },
    { id: "auditlogs", label: "📜 Audit Logs", path: "/audit-logs", roles: ["admin"] },

    { id: "invitations", label: "📩 Invitations", path: "/invitations", roles: ["admin"] },

    { id: "settings", label: "⚙️ Settings", path: "/settings", roles: ["admin", "user"] },
  ];

  return (
    <aside className="sidebar">
      <h2 className="sidebar-title">EEMS</h2>
      <ul className="sidebar-links">
        {menuItems
          .filter((item) => item.roles.includes(user?.role))
          .map((item) => (
            <li key={item.id}>
              <NavLink
                to={item.path}
                className={({ isActive }) => (isActive ? "active" : "")}
              >
                {item.label}
              </NavLink>
            </li>
          ))}
      </ul>

      {/* Fixed logout button */}
      <button className="logout-btn" onClick={handleLogout}>
        🚪 Logout
      </button>
    </aside>
  );
};

export default Sidebar;
