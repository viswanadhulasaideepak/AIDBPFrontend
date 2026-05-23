import StatusBadge from "../../components/common/StatusBadge";

const EmployeeProfile = ({ employee, onClose }) => {
  if (!employee) return null;

  return (
    <div className="profile-panel">
      <button className="close-btn" onClick={onClose}>X</button>
      <h3>{employee.name}</h3>
      <p><strong>Email:</strong> {employee.email}</p>
      <p><strong>Department:</strong> {employee.company?.name}</p>
      <p><strong>Status:</strong> {employee.id % 2 === 0 ? "Active" : "Inactive"}</p>
    </div>
  );
};

export default EmployeeProfile;