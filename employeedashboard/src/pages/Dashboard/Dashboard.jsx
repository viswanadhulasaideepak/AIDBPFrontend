import { useEffect, useState } from "react";

const Dashboard = () => {
  const [employees, setEmployees] = useState([]);

  useEffect(() => {
    fetch("https://jsonplaceholder.typicode.com/users")
      .then((res) => res.json())
      .then((data) => setEmployees(data));
  }, []);

  const totalEmployees = employees.length;
  const activeEmployees = employees.filter((emp) => emp.id % 2 === 0).length;
  const inactiveEmployees = employees.filter((emp) => emp.id % 2 !== 0).length;
  const departments = new Set(employees.map((emp) => emp.company.name)).size;

  return (
    <div className="dashboard-container">
      <h2>Dashboard</h2>
      <div className="dashboard-cards">
        <div className="card">
          <h3>Total Employees</h3>
          <p>{totalEmployees}</p>
        </div>
        <div className="card">
          <h3>Active Employees</h3>
          <p>{activeEmployees}</p>
        </div>
        <div className="card">
          <h3>Inactive Employees</h3>
          <p>{inactiveEmployees}</p>
        </div>
        <div className="card">
          <h3>Departments</h3>
          <p>{departments}</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
