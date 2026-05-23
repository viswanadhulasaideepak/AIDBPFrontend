import { useEffect, useState } from "react";

const Departments = () => {
  const [departments, setDepartments] = useState([]);

  useEffect(() => {
    fetch("https://jsonplaceholder.typicode.com/users")
      .then((res) => res.json())
      .then((data) => {
        const uniqueDepartments = [...new Set(data.map(emp => emp.company.name))];
        setDepartments(uniqueDepartments);
      });
  }, []);

  return (
    <div>
      <h2>Departments</h2>
      <ul>
        {departments.map((dept, idx) => (
          <li key={idx}>{dept}</li>
        ))}
      </ul>
    </div>
  );
};

export default Departments;
