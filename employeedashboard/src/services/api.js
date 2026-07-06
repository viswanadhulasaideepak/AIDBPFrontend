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
      localStorage.removeItem("token");
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

// Update employee
export const updateEmployee = async (id, employee) =>
  (await api.put(`/employees/${id}`, employee)).data;

// Delete employee
export const deleteEmployee = async (id) =>
  (await api.delete(`/employees/${id}`)).data;

// Suspend
export const suspendUser = async (userId, reason) => {
  const res = await api.post(`/suspension/${userId}/suspend`, {reason,});
  return res.data;
};

// ---------------- Suspension ----------------

// Get suspension details
export const fetchAccountStatus = async () =>
  (await api.get("/suspension/account-status")).data;

// Submit reinstatement request
export const submitReinstatementRequest = async (reason) =>
  (await api.post("/suspension/reinstatement/request", {
      reason,
    })
  ).data;

// Get my reinstatement request
export const fetchMyReinstatementRequest = async () =>
  (await api.get("/suspension/reinstatement/my-request")
  ).data;

// Admin - Get all requests
export const fetchReinstatementRequests = async () =>
  (await api.get("/suspension/reinstatement/requests")
  ).data;

// Approve
export const approveReinstatement = async (id,admin_comment) =>
  (await api.post(`/suspension/reinstatement/${id}/approve`,
      { admin_comment })
  ).data;

// Reject
export const rejectReinstatement = async (id,admin_comment) =>
  (await api.post(`/suspension/reinstatement/${id}/reject`,
      { admin_comment })
  ).data;

// Reinstate
export const reinstateUser = async (userId) => {
  const res = await api.post(`/suspension/${userId}/reinstate`);
  return res.data;
};
//-------------Employee Profile--------------

// Get single employee profile completion
export const fetchEmployeeProfileCompletion = async (employeeId) =>
  (await api.get(`/employees/${employeeId}/profile-completion`)).data;

// Get all employees profile completion (admin view)
export const fetchCompanyProfileCompletion = async () =>
  (await api.get("/employees/profile-completion/all")).data;

// Employees below threshold
export const fetchEmployeesBelowThreshold = async (threshold = 80) =>
  (await api.get(`/employees/profile-completion/below-threshold?threshold=${threshold}`)).data;

// Get unread notifications only (if backend supports filtering)
export const fetchUnreadNotifications = async () =>
  (await api.get("/notifications?unread=true")).data;

// Departments
export const fetchDepartments = async () =>
  (await api.get("/departments")).data;

export const addDepartment = async (department) =>
  (await api.post("/departments", department)).data;

// ---------------- Department Transfer ----------------

// Transfer an employee to another department
export const transferDepartment = async (
  employeeId,
  newDepartmentId,
  reason = ""
) =>
  (
    await api.put(`/employees/${employeeId}/transfer`, {
      new_department_id: newDepartmentId,
      reason,
    })
  ).data;

// Get department transfer history
export const fetchDepartmentTransferHistory = async () =>
  (await api.get("/employees/transfer/history")).data;

// Attendance records (array)
export const fetchAttendanceRecords = async () =>
  (await api.get("/attendance")).data;

// Attendance analytics (object)
export const fetchAttendanceReport = async () =>
  (await api.get("/attendance/report")).data;

// Notifications
export const fetchNotifications = async () =>
  (await api.get("/notifications")).data;

// Mark one notification as read
export const markNotificationRead = async (id) =>
  (await api.put(`/notifications/${id}/read`)).data;

// Mark all notifications as read
export const markAllNotificationsRead = async () =>
  (await api.put("/notifications/read-all")).data;

// Audit Logs
export const fetchAuditLogs = async () =>
  (await api.get("/audit-logs")).data;

// ---------------- Activity ----------------

// Current user activity (last login/logout, browser, IP, etc.)
export const fetchUserActivity = async () =>
  (await api.get("/activity/users")).data;

// Complete activity history (audit logs)
export const fetchActivityHistory = async () =>
  (await api.get("/activity/history")).data;

export const getAttendanceAccessStatus = async () => {
    const response = await api.get("/attendance/access-status");
    return response.data;
};

export const updateAttendanceAccessRequest = async (id, status) =>
  (
    await api.put(`/attendance/access-request/${id}?status=${status}`, {
      status,
    })
  ).data;

export const checkIn = async () =>
  (await api.post("/attendance/check-in")).data;

export const checkOut = async () =>
  (await api.post("/attendance/check-out")).data;

export const getTodayAttendance = async () =>
  (await api.get("/attendance/today")).data;

export const getAttendanceHistory = async () =>
  (await api.get("/attendance/history")).data;

export const getAttendanceAccessRequests = async () =>
  (await api.get("/attendance/access-requests")).data;  


// Submit a new leave request
export const submitLeaveRequest = async (leaveForm) =>
  (await api.post("/leave/request", {
    leave_type: leaveForm.leave_type,
    start_date: leaveForm.start_date,
    end_date: leaveForm.end_date,
    reason: leaveForm.reason,
  })).data;

// Get current user's leave requests
export const getMyLeaveRequests = async () =>
  (await api.get("/leave/my")).data;

// Get all company leave requests (admin only)
export const getCompanyLeaveRequests = async () =>
  (await api.get("/leave/company")).data;

// Approve/Reject a leave request (admin only)
export const updateLeaveRequest = async (id, status) =>
  (await api.put(`/leave/${id}`, { status })).data;

/* ---------------- HOLIDAY MANAGEMENT ---------------- */

// Get all holidays
export const fetchHolidays = async () =>
  (await api.get("/holidays")).data;

// Get single holiday
export const fetchHolidayById = async (id) =>
  (await api.get(`/holidays/${id}`)).data;

// Create holiday (Admin)
export const createHoliday = async (holiday) =>
  (await api.post("/holidays", holiday)).data;

// Update holiday (Admin)
export const updateHoliday = async (id, holiday) =>
  (await api.put(`/holidays/${id}`, holiday)).data;

// Delete holiday (Admin)
export const deleteHoliday = async (id) =>
  (await api.delete(`/holidays/${id}`)).data;


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
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email,
      new_password: newPassword,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Password reset failed");
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

// ---------------- COMPANY ----------------

// Get current company details
export const fetchCompanyDetails = async () =>
  (await api.get("/companies/me")).data;

// Get all members of current company
export const fetchCompanyMembers = async () =>
  (await api.get("/companies/members")).data;

//----------------Members-----------------------
export const getMembers = async () =>
  (await api.get("/members")).data;

export const deactivateMember = async (id) =>
  (await api.put(`/members/${id}/deactivate`)).data;

export const reactivateMember = async (id) =>
  (await api.put(`/members/${id}/reactivate`)).data;

//----------------Reactivation-----------------
export const submitReactivationRequest = async (message) =>
(
    await api.post("/reactivation/request", {
        message
    })
).data;

export const getReactivationRequests = async () =>
  (await api.get("/reactivation")).data;

export const updateReactivationRequest = async (id, status) =>
  (await api.put(`/reactivation/${id}`, null, { params: { status } })).data;

export const getMyReactivationRequest = async () =>
  (await api.get("/reactivation/my-request")).data;

/* ---------------- DATA EXPORT CENTER ---------------- */

// Download any export
export const downloadExport = async (dataType, format) => {
  const response = await api.get(
    `/exports/${dataType}/${format}`,
    {
      responseType: "blob",
    }
  );

  const blob = new Blob([response.data]);
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  let extension = format;

  if (format === "excel") {
    extension = "xlsx";
  }

  link.setAttribute(
    "download",
    `${dataType}.${extension}`
  );

  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

// Export History
export const fetchExportHistory = async () =>
  (await api.get("/exports/history")).data;

// ---------------- USER PROFILE ----------------

// Get logged-in user's profile
export const fetchMyProfile = async () =>
  (await api.get("/employees/me/profile")).data;

// Update logged-in user's profile
export const updateMyProfile = async (profile) =>
  (await api.put("/employees/me/profile", profile)).data;

// Logged-in user's completion
export const fetchMyProfileCompletion = async () =>
  (await api.get("/employees/me/profile-completion")).data;

// Profile dashboard summary
export const fetchProfileDashboard = async () =>
  (await api.get("/employees/me/profile")).data;

// ---------------- LOGIN DEVICE MANAGEMENT ---------------- 

// -------------------- USER -----------------

// Get all my login devices
export const fetchMyLoginDevices = async () =>
  (await api.get("/login-devices")).data;

// Rename trusted device
export const renameTrustedDevice = async (
  sessionId,
  deviceName
) =>
  (
    await api.patch(`/login-devices/${sessionId}/rename`, {
      device_name: deviceName,
    })
  ).data;

// Remove trusted device
export const removeTrustedDevice = async (sessionId) =>
  (
    await api.delete(`/login-devices/${sessionId}/trusted`)
  ).data;

// Logout selected device
export const logoutDevice = async (sessionId) =>
  (
    await api.post(`/login-devices/${sessionId}/logout`)
  ).data;

// Logout every device except current
export const logoutAllDevices = async () =>
  (
    await api.post("/login-devices/logout-all")
  ).data;


// ----------------- ADMIN ------------------

// View all company sessions
export const fetchCompanyLoginSessions = async () =>
  (
    await api.get("/admin/login-devices")
  ).data;

// Force logout
export const forceLogoutSession = async (sessionId) =>
  (
    await api.post(
      `/admin/login-devices/${sessionId}/force-logout`
    )
  ).data;

// Revoke session
export const revokeLoginSession = async (sessionId) =>
  (
    await api.post(
      `/admin/login-devices/${sessionId}/revoke`
    )
  ).data;

export default api;