import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";

/* ---------------- AXIOS INSTANCE ---------------- */
const api = axios.create({
  baseURL: API_BASE,
});

/* ---------------- TOKEN ATTACH ---------------- */
api.interceptors.request.use((config) => {
  const user = JSON.parse(localStorage.getItem("user"));
  if (user?.token) {
    config.headers.Authorization = `Bearer ${user.token}`;
  }
  return config;
});

/* ---------------- 401 HANDLER ---------------- */
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

/* ---------------- API CALLS ---------------- */

// Dashboard
export const fetchDashboardStats = async () =>
  (await api.get("/dashboard/stats")).data;

// Employees
export const fetchEmployees = async () =>
  (await api.get("/employees")).data;

export const addEmployee = async (employee) =>
  (await api.post("/employees", employee)).data;

export const updateEmployeeStatus = async (id, employee) =>
  (await api.put(`/employees/${id}`, employee)).data;

// Departments
export const fetchDepartments = async () =>
  (await api.get("/departments")).data;

export const addDepartment = async (department) =>
  (await api.post("/departments", department)).data;

// Attendance
export const fetchAttendance = async () =>
  (await api.get("/attendance")).data;

// Notifications
export const fetchNotifications = async () =>
  (await api.get("/notifications")).data;

// Audit Logs
export const fetchAuditLogs = async () =>
  (await api.get("/audit-logs")).data;

/* ---------------- LOGIN ---------------- */
export const loginUser = async (email, password, role) => {
  console.log("LOGIN REQUEST", {
    email,
    password,
    role
  });
 
  const response = await fetch(`${API_BASE}/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      username: email,
      password: password,
      role: role,
    }),
  });
 
  const data = await response.json();
 
  console.log("LOGIN RESPONSE", data);
 
  if (!response.ok) {
    throw new Error(data.detail || "Login failed");
  }
 
  return data;
};
/* ---------------- SIGNUP ---------------- */
export const signupUser = async (email, password, role, CompanyName) => {
  const response = await fetch(`${API_BASE}/signup`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      username: email,   
      email,
      password,
      role,
      company_name: CompanyName
    }),
  });

  const data = await response.json();
  console.log("SIGNUP RESPONSE:", data);

  if (!response.ok) {
    throw new Error(data.detail || "Signup failed");
  }

  return data;
};;

/* ---------------- PASSWORD RESET ---------------- */
export const resetPassword = async (email, newPassword) => {
  const response = await fetch(`${API_BASE}/forgot-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, new_password: newPassword }),
  });

  if (!response.ok) {
    throw new Error("Password reset failed");
  }

  return response.json(); // { message: "Password reset successful" }
};
/* ---------------- REPORT DOWNLOADS ---------------- */
export const downloadAttendanceReportCSV = async () => {
  const response = await api.get("/attendance/report/csv", {
    responseType: "blob",
  });
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", "attendance_report.csv");
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

export const downloadAttendanceReportExcel = async () => {
  const response = await api.get("/attendance/report/excel", {
    responseType: "blob",
  });
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", "attendance_report.xlsx");
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

export const downloadAttendanceReportPDF = async () => {
  const response = await api.get("/attendance/report/pdf", {
    responseType: "blob",
  });
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", "attendance_report.pdf");
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

export default api;
