import { Routes, Route, Navigate, useNavigate } from "react-router-dom";
import { useContext, useEffect } from "react";
import Login from "../pages/Login/Login";
import Dashboard from "../pages/Dashboard/Dashboard";
import Employees from "../pages/Employees/Employees";
import Departments from "../pages/Departments/Departments";   
import Attendance from "../pages/Attendance/Attendance";       
import Settings from "../pages/Settings/Settings";
import { AuthContext } from "../auth/AuthContext"; 
import AuditLogs from "../pages/AuditLogs/AuditLogs";
import InvitationsPage from "../components/invitations/InvitationsPage";
import AccountDeactivated from "../components/AccountDeactivated";
import Activity from "../pages/Activity/Activity";

const Logout = () => {
  const { logout } = useContext(AuthContext);
  const navigate = useNavigate();

  useEffect(() => {
    logout();
    navigate("/login");
  }, [logout, navigate]);

  return null;
};

const AppRoutes = () => {
  const { user } = useContext(AuthContext);

  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" />} />
      <Route path="/login" element={<Login />} />
      <Route path="/logout" element={<Logout />} />

      {/* Protected routes */}
      <Route
        path="/dashboard"
        element={
          user
            ? user.status === "deactivated"
              ? <Navigate to="/account-deactivated" />
              : <Dashboard />
            : <Navigate to="/login" />
        }
      />
      <Route
        path="/employees"
        element={user?.role === "admin" ? <Employees /> : <Navigate to="/dashboard" />}
      />
      <Route
        path="/departments"
        element={user?.role === "admin" ? <Departments /> : <Navigate to="/dashboard" />}
      />
      <Route
        path="/attendance"
        element={user ? <Attendance /> : <Navigate to="/login" />}
      />
      <Route
        path="/settings"
        element={user ? <Settings /> : <Navigate to="/login" />}
      />
      <Route
        path="/invitations"
        element={user?.role === "admin" ? <InvitationsPage /> : <Navigate to="/dashboard" />}
      />
      <Route
        path="/account-deactivated"
        element={<AccountDeactivated currentUser={user} />}
      />
      <Route
        path="/audit-logs"
        element={user?.role === "admin" ? <AuditLogs /> : <Navigate to="/dashboard" />}
      />

      <Route
       path="/activity" 
       element={user?.role === "admin" ? <Activity /> : <Navigate to="/dashboard" />}
       />

      {/* Catch-all */}
      <Route
        path="*"
        element={user ? <Navigate to="/dashboard" /> : <Navigate to="/login" />}
      />
    </Routes>
  );
};

export default AppRoutes;
