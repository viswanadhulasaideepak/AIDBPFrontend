import React from "react";
import { FaBell, FaSearch } from "react-icons/fa";

export default function Navbar() {
  return (
    <header className="navbar">
      <div className="search-bar">
        <FaSearch />
        <input type="text" placeholder="Search here..." />
      </div>

      <div className="navbar-actions">
        <FaBell />
        <div className="profile-circle">K</div>
      </div>
    </header>
  );
}
