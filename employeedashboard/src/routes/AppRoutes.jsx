import { Routes, Route, Navigate, useNavigate } from "react-router-dom";
import { useContext, useEffect } from "react";

import Login from "../pages/Login/Login";
import Dashboard from "../pages/Dashboard/Dashboard";
import Employees from "../pages/Employees/Employees";
import Departments from "../pages/Departments/Departments";
import Attendance from "../pages/Attendance/Attendance";
import Settings from "../pages/Settings/Settings";
import AuditLogs from "../pages/AuditLogs/AuditLogs";
import Activity from "../pages/Activity/Activity";
import DataExportCenter from "../pages/DataExportCenter/DataExportCenter";

import InvitationsPage from "../components/invitations/InvitationsPage";
import AccountDeactivated from "../components/AccountDeactivated";
import AccountSuspended from "../components/AccountSuspended";
import Profile from "../pages/Profile/Profile";
import Company from "../pages/Company/Company";

import { AuthContext } from "../auth/AuthContext";

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

  const isSuspended = user?.status === "suspended";
  const isDeactivated = user?.status === "deactivated";

  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<Navigate to="/login" />} />
      <Route path="/login" element={<Login />} />
      <Route path="/logout" element={<Logout />} />

      {/* Dashboard */}
      <Route
        path="/dashboard"
        element={
          !user ? (
            <Navigate to="/login" />
          ) : isDeactivated ? (
            <Navigate to="/account-deactivated" />
          ) : isSuspended ? (
            <Navigate to="/account-suspended" />
          ) : (
            <Dashboard />
          )
        }
      />
      {/* Profile */}
      <Route
        path="/my-profile"
        element={
          !user ? (
          <Navigate to="/login" />
        ) : isDeactivated ? (
          <Navigate to="/account-deactivated" />
        ) : isSuspended ? (
          <Navigate to="/account-suspended" />
        ) : (
          <Profile />
        )
      }
     />
      {/* Company */}
      <Route
        path="/company"
        element={
          !user ? (
          <Navigate to="/login" />
        ) : isDeactivated ? (
          <Navigate to="/account-deactivated" />
        ) : isSuspended ? (
          <Navigate to="/account-suspended" />
        ) : (
          <Company />
       )
     }
     />

      {/* Employees */}
      <Route
        path="/employees"
        element={
          !user ? (
            <Navigate to="/login" />
          ) : isDeactivated ? (
            <Navigate to="/account-deactivated" />
          ) : isSuspended ? (
            <Navigate to="/account-suspended" />
          ) : user.role === "admin" ? (
            <Employees />
          ) : (
            <Navigate to="/dashboard" />
          )
        }
      />

      {/* Departments */}
      <Route
        path="/departments"
        element={
          !user ? (
            <Navigate to="/login" />
          ) : isDeactivated ? (
            <Navigate to="/account-deactivated" />
          ) : isSuspended ? (
            <Navigate to="/account-suspended" />
          ) : user.role === "admin" ? (
            <Departments />
          ) : (
            <Navigate to="/dashboard" />
          )
        }
      />

      {/* Attendance */}
      <Route
        path="/attendance"
        element={
          !user ? (
            <Navigate to="/login" />
          ) : isDeactivated ? (
            <Navigate to="/account-deactivated" />
          ) : isSuspended ? (
            <Navigate to="/account-suspended" />
          ) : (
            <Attendance />
          )
        }
      />

      {/* Settings */}
      <Route
        path="/settings"
        element={
          !user ? (
            <Navigate to="/login" />
          ) : isDeactivated ? (
            <Navigate to="/account-deactivated" />
          ) : isSuspended ? (
            <Navigate to="/account-suspended" />
          ) : (
            <Settings />
          )
        }
      />

      {/* Invitations */}
      <Route
        path="/invitations"
        element={
          !user ? (
            <Navigate to="/login" />
          ) : isDeactivated ? (
            <Navigate to="/account-deactivated" />
          ) : isSuspended ? (
            <Navigate to="/account-suspended" />
          ) : user.role === "admin" ? (
            <InvitationsPage />
          ) : (
            <Navigate to="/dashboard" />
          )
        }
      />

      {/* Audit Logs */}
      <Route
        path="/audit-logs"
        element={
          !user ? (
            <Navigate to="/login" />
          ) : isDeactivated ? (
            <Navigate to="/account-deactivated" />
          ) : isSuspended ? (
            <Navigate to="/account-suspended" />
          ) : user.role === "admin" ? (
            <AuditLogs />
          ) : (
            <Navigate to="/dashboard" />
          )
        }
      />

      {/* Activity */}
      <Route
        path="/activity"
        element={
          !user ? (
            <Navigate to="/login" />
          ) : isDeactivated ? (
            <Navigate to="/account-deactivated" />
          ) : isSuspended ? (
            <Navigate to="/account-suspended" />
          ) : user.role === "admin" ? (
            <Activity />
          ) : (
            <Navigate to="/dashboard" />
          )
        }
      />

      {/* Data Export */}
      <Route
        path="/data-export"
        element={
          !user ? (
            <Navigate to="/login" />
          ) : isDeactivated ? (
            <Navigate to="/account-deactivated" />
          ) : isSuspended ? (
            <Navigate to="/account-suspended" />
          ) : user.role === "admin" ? (
            <DataExportCenter />
          ) : (
            <Navigate to="/dashboard" />
          )
        }
      />

      {/* Status Pages */}
      <Route
        path="/account-deactivated"
        element={<AccountDeactivated currentUser={user} />}
      />

      <Route
        path="/account-suspended"
        element={<AccountSuspended />}
      />

      {/* Catch All */}
      <Route
        path="*"
        element={
          !user ? (
            <Navigate to="/login" />
          ) : isDeactivated ? (
            <Navigate to="/account-deactivated" />
          ) : isSuspended ? (
            <Navigate to="/account-suspended" />
          ) : (
            <Navigate to="/dashboard" />
          )
        }
      />
    </Routes>
  );
};

export default AppRoutes;