import axios from "axios";

const API_BASE = "http://localhost:8000";

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

// Attendance (FIXED to use /report)
//export const fetchAttendance = async () =>
 // (await api.get("/attendance/report")).data;

// Attendance records (array)
export const fetchAttendanceRecords = async () =>
  (await api.get("/attendance")).data;

// Attendance analytics (object)
export const fetchAttendanceReport = async () =>
  (await api.get("/attendance/report")).data;

// Notifications
export const fetchNotifications = async () =>
  (await api.get("/notifications")).data;

// Audit Logs
export const fetchAuditLogs = async () =>
  (await api.get("/audit-logs")).data;

/* ---------------- LOGIN ---------------- */
export const loginUser = async (email, password, role) => {
  const response = await fetch(`${API_BASE}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      username: email,
      password: password,
      role: role,
    }),
  });

  const data = await response.json();
  if (!response.ok) {
  console.log(data);
  throw new Error(JSON.stringify(data));
}
  localStorage.setItem("user", JSON.stringify(data));
  return data;
};

/* ---------------- SIGNUP ---------------- */
// ---------------- NORMAL SIGNUP ----------------
export const signupUser = async (
  email,
  password,
  role,
  companyName
) => {
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
      company_name: companyName,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    console.log("Signup Error:", data);
    throw new Error(data.detail || "Signup failed");
  }

  return data;
};

// ---------------- INVITATION SIGNUP ----------------
export const signupWithInvitation = async (
  token,
  username,
  password
) => {
  const response = await fetch(`${API_BASE}/signup/invitation`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      token,
      username,
      password,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Invitation signup failed");
  }

  return data;
};

// ---------------- VALIDATE INVITATION ----------------

export const validateInvitation = async (token) => {
  const response = await fetch(`${API_BASE}/invitation/${token}`);

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Invalid invitation");
  }

  return data;
};

/* ---------------- PASSWORD RESET ---------------- */
export const resetPassword = async (email, newPassword) => {
  const response = await fetch(`${API_BASE}/forgot-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, new_password: newPassword }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error("Password reset failed");
  }
  return data;
};

/* ---------------- REPORT DOWNLOADS ---------------- */
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

//----------------Invitations-----------------
export const createInvitation = async (email, role, expiresAt) =>
  (
    await api.post("/invitations", {
      email,
      role,
      expires_at: expiresAt || null,
    })
  ).data;

export const getInvitations = async () =>
  (await api.get("/invitations")).data;

export const revokeInvitation = async (id) =>
  (await api.delete(`/invitations/${id}`)).data;

//----------------Members-----------------------
export const getMembers = async () =>
  (await api.get("/members")).data;

export const deactivateMember = async (id) =>
  (await api.put(`/members/${id}/deactivate`)).data;

export const reactivateMember = async (id) =>
  (await api.put(`/members/${id}/reactivate`)).data;

//----------------Reactivation-----------------
export const submitReactivationRequest = async () =>
  (await api.post("/reactivation/request")).data;

export const getReactivationRequests = async () =>
  (await api.get("/reactivation")).data;

export const updateReactivationRequest = async (id, status) =>
  (await api.put(`/reactivation/${id}`, null, { params: { status } })).data;

export const getMyReactivationRequest = async () =>
  (await api.get("/reactivation/my-request")).data;

export default api;
