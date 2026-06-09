import { useState, useEffect } from "react";
import "./AddEmployeeForm.css";

const AddEmployeeForm = ({ onAdd, onClose }) => {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("HR");
  const [departmentId, setDepartmentId] = useState("");
  const [departmentName, setDepartmentName] = useState("");
  const [errors, setErrors] = useState({}); //stores validation error
  const [status, setStatus] = useState("active");

  //  Generate random joined date
  const randomDate = () => {
    const start = new Date(2023, 0, 1);
    const end = new Date();
    const date = new Date(
      start.getTime() + Math.random() * (end.getTime() - start.getTime())
    );
    return date.toISOString().split("T")[0];
  };

  //  Validation logic
  const validate = () => {
    const newErrors = {};
    if (!name.trim()) newErrors.name = "Name is required";
    if (!email.trim()) newErrors.email = "Email is required";
    else if (!/\S+@\S+\.\S+/.test(email))
      newErrors.email = "Invalid email format";
    if (!role.trim()) newErrors.role = "Role is required";
    if (!departmentName.trim()) {
      newErrors.departmentName = "Department is required";
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  //  Handle form submission with token
  const handleSubmit = async (e) => {
    e.preventDefault();

    const newEmployee = {
      name: name.trim(),
      email: email.trim(),
      role,
      department_name: departmentName.trim(),
      joined_date: randomDate(),
      status, 
    };

    try {
      const user = JSON.parse(localStorage.getItem("user"));
      const token = user?.token;
      console.log("Sending employee:", newEmployee);
      console.log("Token:", token);

      const response = await fetch("http://localhost:8000/employees", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(newEmployee),
      });

      const data = await response.json();

      if (!response.ok) {
        console.log("FULL ERROR RESPONSE:", data);
        alert(JSON.stringify(data, null, 2));
        return;
      }

      onAdd(data);
      onClose();

      // Reset form
      setName("");
      setEmail("");
      setRole("HR");
      setDepartmentName("");;
      setStatus("active");
    } catch (error) {
      console.error("Error adding employee:", error);
      alert("Unable to connect to backend. Check if FastAPI is running and CORS allows your frontend port.");
    }
  };

  // Validation check
  const isValid =
    name.trim() !== "" &&
    email.trim() !== "" &&
    role.trim() !== "" &&
    departmentName.trim() !== "";

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h3 className="modal-title">➕ Add Employee</h3>
        <form onSubmit={handleSubmit} className="employee-form">
          <input
            type="text"
            placeholder="Full Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
           {errors.name && <span className="error">{errors.name}</span>}
          <input
            type="email"
            placeholder="Email Address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          {errors.email && <span className="error">{errors.email}</span>}
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            required
          >
            <option value="HR">HR</option>
            <option value="Finance">Finance</option>
            <option value="IT">IT</option>
            <option value="Sales">Sales</option>
          </select>

          <input type="text" placeholder="Department Name" value={departmentName}
             onChange={(e) => setDepartmentName(e.target.value)} required/>

          {errors.departmentName && (
            <span className="error">{errors.departmentName}</span>
          )}
          {/* Status Dropdown */}
          <select value={status} onChange={(e) => setStatus(e.target.value)} required>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="onleave">On Leave</option>
          </select>
          <div className="form-actions">
            <button
              type="submit"
              className="btn-primary"
              disabled={!isValid}
            >
              Add
            </button>
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddEmployeeForm;
