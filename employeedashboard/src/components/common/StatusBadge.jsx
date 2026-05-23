const StatusBadge = ({ isActive }) => {
  return (
    <span className={`status-badge ${isActive ? "active" : "inactive"}`}>
      {isActive ? "Active" : "Inactive"}
    </span>
  );
};

export default StatusBadge;
