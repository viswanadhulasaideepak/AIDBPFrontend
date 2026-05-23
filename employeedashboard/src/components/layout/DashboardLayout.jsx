import Sidebar from "./Sidebar";
import Navbar from "./Navbar";

const DashboardLayout = () => {
  return (
    <div className="dashboard-container">
      <Sidebar />
      <div className="dashboard-main">
        <Navbar />
        <div className="dashboard-content">
          <h2>Dashboard Content Area</h2>
        </div>
      </div>
    </div>
  );
};

export default DashboardLayout;
