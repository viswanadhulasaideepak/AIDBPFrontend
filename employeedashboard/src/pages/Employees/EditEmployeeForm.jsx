import React, { useState } from "react";
import "./Employees.css";

const EditEmployeeForm = ({ employee, onSave, onClose }) => {
  const [role, setRole] = useState("HR");
  const [formData, setFormData] = useState({
    id: employee.id,
    name: employee.name || "",
    email: employee.email || "", 
    role: employee.role || "employee",
    department_name: employee.department_name || "",
    joined_date: employee.joined_date
      ? employee.joined_date.slice(0, 10)
      : "",
    status: employee.status || "active",
  });

  const [errors, setErrors] = useState({});

  /* ---------------- VALIDATION ---------------- */
  const validate = () => {
    const newErrors = {};

    if (!formData.name.trim()) newErrors.name = "Name is required";

    if (!formData.email.trim()) {
      newErrors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Invalid email format";
    }

    if (!formData.role) newErrors.role = "Role is required";

    if (!formData.department_name.trim()) {
      newErrors.department_name = "Department is required";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /* ---------------- HANDLE CHANGE ---------------- */
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  /* ---------------- SUBMIT ---------------- */
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!validate()) return;

    onSave(formData); // backend update handled in parent
  };

  return (
    <div className="modal-overlay">
      <div className="modal">

        <h2>Edit Employee</h2>

        <form onSubmit={handleSubmit} className="employee-form">

          {/* NAME */}
          <label>Name</label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            placeholder="Enter name"
          />
          {errors.name && <span className="error">{errors.name}</span>}

          {/* EMAIL */}
          <label>Email</label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="Enter email"
          />
          {errors.email && <span className="error">{errors.email}</span>}

          {/* ROLE */}
          <label>Role</label>
          <select
            name="role"
            value={formData.role}
            onChange={handleChange}
          >
            <option value="HR">HR</option>
            <option value="Finance">Finance</option>
            <option value="IT">IT</option>
            <option value="Sales">Sales</option>
          </select>
          {errors.role && <span className="error">{errors.role}</span>}

          {/* DEPARTMENT (TRANSFER FEATURE) */}
          <label>Department (Transfer)</label>
          <input
            type="text"
            name="department_name"
            value={formData.department_name}
            onChange={handleChange}
            placeholder="Change department"
          />
          {errors.department_name && (
            <span className="error">{errors.department_name}</span>
          )}

          <small style={{ color: "gray" }}>
            Changing department will transfer the employee.
          </small>

          {/* JOINED DATE */}
          <label>Joined Date</label>
          <input
            type="date"
            name="joined_date"
            value={formData.joined_date}
            onChange={handleChange}
          />

          {/* STATUS */}
          <label>Status</label>
          <select
            name="status"
            value={formData.status}
            onChange={handleChange}
          >
            <option value="active">Active</option>
            <option value="onleave">On Leave</option>
            <option value="inactive">Inactive</option>
          </select>

          {/* ACTIONS */}
          <div className="form-actions">
            <button type="submit" className="save-btn">
              Save Changes
            </button>

            <button
              type="button"
              className="cancel-btn"
              onClick={onClose}
            >
              Cancel
            </button>
          </div>

        </form>
      </div>
    </div>
  );
};

export default EditEmployeeForm;