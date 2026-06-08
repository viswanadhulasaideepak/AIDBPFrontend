import React, { useState, useEffect } from "react";
import "./Employees.css";

const EditEmployeeForm = ({ employee, onSave, onClose }) => {
  const [formData, setFormData] = useState({
    id: employee.id,
    name: employee.name,
    email: employee.email,
    role: employee.role || "HR",
    department_name: employee.department_name || "",
    joined_date: employee.joined_date || "",
  });

  const [errors, setErrors] = useState({});

  // Validation logic
  const validate = () => {
    const newErrors = {};
    if (!formData.name.trim()) newErrors.name = "Name is required";
    if (!formData.email.trim()) newErrors.email = "Email is required";
    else if (!/\S+@\S+\.\S+/.test(formData.email))
      newErrors.email = "Invalid email format";
    if (!formData.role.trim()) newErrors.role = "Role is required";
    if (!formData.department_name.trim())
      newErrors.department_name = "Department is required";
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!validate()) return;
    onSave(formData);
  };

  const isValid =
    formData.name.trim() !== "" &&
    formData.email.trim() !== "" &&
    formData.role.trim() !== "" &&
    formData.department_name.trim() !== "";

  return (
    <div className="modal-overlay">
      <div className="modal">
        <h2>Edit Employee</h2>
        <form onSubmit={handleSubmit} className="employee-form">
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            placeholder="Name"
            required
          />
          {errors.name && <span className="error">{errors.name}</span>}

          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="Email"
            required
          />
          {errors.email && <span className="error">{errors.email}</span>}

          <select
            name="role"
            value={formData.role}
            onChange={handleChange}
            required
          >
            <option value="HR">HR</option>
            <option value="Finance">Finance</option>
            <option value="IT">IT</option>
            <option value="Sales">Sales</option>
          </select>

          <input
            type="text"
            name="department_name"
            value={formData.department_name}
            onChange={handleChange}
            placeholder="Department Name"
            required
          />
          {errors.department_name && (
            <span className="error">{errors.department_name}</span>
          )}

          <input
            type="text"
            name="joined_date"
            value={formData.joined_date}
            onChange={handleChange}
            placeholder="Joined Date"
          />

          <div className="form-actions">
            <button type="submit" className="save-btn" disabled={!isValid}>
              Save
            </button>
            <button type="button" className="cancel-btn" onClick={onClose}>
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EditEmployeeForm;
