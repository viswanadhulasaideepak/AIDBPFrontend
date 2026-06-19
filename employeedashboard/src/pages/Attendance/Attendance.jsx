import React, { useContext } from "react";
import DashboardLayout from "../../components/layout/DashboardLayout";
import { AuthContext } from "../../auth/AuthContext";
import AttendanceAdminPanel from "./AttendanceAdminPanel";
import AttendanceUserPanel from "./AttendanceUserPanel";

const Attendance = () => {
  const { user } = useContext(AuthContext);

  return (
    <DashboardLayout>
      <div className="attendance-container">
        <h2>Attendance</h2>

        {user?.role === "admin" ? (
          <AttendanceAdminPanel />
        ) : (
          <AttendanceUserPanel />
        )}
      </div>
    </DashboardLayout>
  );
};

export default Attendance;