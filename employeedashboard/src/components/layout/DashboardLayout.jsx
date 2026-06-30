import React, { useContext } from "react";
import Sidebar from "./Sidebar";
import Navbar from "./Navbar";
import "./DashboardLayout.css";
import { AuthContext } from "../../auth/AuthContext";

const DashboardLayout = ({ children }) => {
  const { user } = useContext(AuthContext);

  const isSuspended = user?.status === "suspended";

  if (isSuspended) {
    return (
      <div className="dashboard-content">
        {children}
      </div>
    );
  }

  return (
    <div className="dashboard-layout">
      <Sidebar />
      <div className="dashboard-main">
        <Navbar />
        <div className="dashboard-content">
          {children}
        </div>
      </div>
    </div>
  );
};

export default DashboardLayout;