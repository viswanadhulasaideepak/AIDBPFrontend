import React from "react";
import { NavLink } from "react-router-dom";
import { FaTachometerAlt, FaUsers, FaBuilding, FaCalendarCheck, FaCog, FaSignOutAlt } from "react-icons/fa";

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">👤</div>
        <h2>EEMS</h2>
      </div>

      <nav className="sidebar-nav">
        <NavLink to="/dashboard" className="nav-item">
          <FaTachometerAlt /> Dashboard
        </NavLink>
        <NavLink to="/employees" className="nav-item">
          <FaUsers /> Employees
        </NavLink>
        <NavLink to="/departments" className="nav-item">
          <FaBuilding /> Departments
        </NavLink>
        <NavLink to="/attendance" className="nav-item">
          <FaCalendarCheck /> Attendance
        </NavLink>
        <NavLink to="/settings" className="nav-item">
          <FaCog /> Settings
        </NavLink>
      </nav>

      <div className="sidebar-footer">
        <button className="logout-btn">
          <FaSignOutAlt /> Logout
        </button>
        <div className="user-info">
          <p className="username">Mohammad Muzafar</p>
          <small>khgfb</small>
        </div>
      </div>
    </aside>
  );
}

