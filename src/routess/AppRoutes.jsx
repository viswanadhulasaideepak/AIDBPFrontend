import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "../pagess/Login/Login";
import Dashboard from "../pagess/Dashboard/Dashboard";
import Employees from "../pagess/Employees/Employees";
import Departments from "../pagess/Departments/Departments";
import Attendance from "../pagess/Attendance/Attendance";
import Settings from "../pagess/Settings/Settings";

export default function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/employees" element={<Employees />} />
        <Route path="/departments" element={<Departments />} />
        <Route path="/attendance" element={<Attendance />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/employees" element={<Employees />} />
      </Routes>
    </BrowserRouter>
  );
}
