import { FaHome, FaUsers, FaBuilding, FaCalendarCheck, FaCog } from "react-icons/fa";

const Sidebar = () => {
  return (
    <div className="sidebar">
      <h3 className="sidebar-title">EMS</h3>
      <ul>
        <li><FaHome /> Dashboard</li>
        <li><FaUsers /> Employees</li>
        <li><FaBuilding /> Departments</li>
        <li><FaCalendarCheck /> Attendance</li>
        <li><FaCog /> Settings</li>
      </ul>
    </div>
  );
};

export default Sidebar;
