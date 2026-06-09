import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import { useContext, useEffect } from "react";
import Login from "../pages/Login/Login";
import Dashboard from "../pages/Dashboard/Dashboard";
import Employees from "../pages/Employees/Employees";
import Departments from "../pages/Departments/Departments";   
import Attendance from "../pages/Attendance/Attendance";       
import Settings from "../pages/Settings/Settings";
import { AuthContext } from "../auth/AuthContext"; 
import AuditLogs from "../pages/AuditLogs/AuditLogs";


const Logout = () => {
  const { logout } = useContext(AuthContext);
  const navigate = useNavigate();

  useEffect(() => {
    logout();            // clears localStorage + resets context
    navigate("/login");  // redirect to login
  }, [logout, navigate]);

  return null;
};

const AppRoutes = () => {
  const { user } = useContext(AuthContext);

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/login" />} />
        <Route path="/login" element={<Login />} />
        <Route path="/logout" element={<Logout />} /> 

        {/* Protected routes */}
        <Route
          path="/dashboard"
          element={user ? <Dashboard /> : <Navigate to="/login" />}
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
          path="/audit-logs"
          element={user?.role === "admin" ? <AuditLogs /> : <Navigate to="/dashboard" />}
        />

        {/* Catch-all */}
       <Route
          path="*"
          element={ user ? <Navigate to="/dashboard" /> : <Navigate to="/login" /> }
        />
      </Routes>
    </Router>
  );
};

export default AppRoutes;
