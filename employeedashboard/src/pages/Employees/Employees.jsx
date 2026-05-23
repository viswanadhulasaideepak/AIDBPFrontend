import { useEffect, useState } from "react";
import EmployeeProfile from "./EmployeeProfile";
import StatusBadge from "../../components/common/StatusBadge";
import AddEmployeeForm from "./AddEmployeeForm";
import EmployeeSections from "./EmployeeSections";

const Employees = () => {
  const [employees, setEmployees] = useState([]);
  const [search, setSearch] = useState("");
  const [departmentFilter, setDepartmentFilter] = useState("");
  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const employeesPerPage = 5;

  // Sorting
  const [sortField, setSortField] = useState("name");
  const [sortOrder, setSortOrder] = useState("asc");

  // Fetch employees from FakeAPI
  useEffect(() => {
    fetch("https://jsonplaceholder.typicode.com/users")
      .then((res) => res.json())
      .then((data) => setEmployees(data));
  }, []);

  const handleAddEmployee = async (newEmployee) => {
    const response = await fetch("https://jsonplaceholder.typicode.com/users", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(newEmployee),
    });
    const data = await response.json();
    setEmployees([...employees, data]);
  };

  // Filtering
  const filteredEmployees = employees.filter((emp) => {
    const matchesName = emp.name.toLowerCase().includes(search.toLowerCase());
    const matchesDept = departmentFilter
      ? emp.company.name.toLowerCase().includes(departmentFilter.toLowerCase())
      : true;
    return matchesName && matchesDept;
  });

  // Sorting
  const sortedEmployees = [...filteredEmployees].sort((a, b) => {
    const fieldA = a[sortField]?.toLowerCase?.() || a.company.name.toLowerCase();
    const fieldB = b[sortField]?.toLowerCase?.() || b.company.name.toLowerCase();
    if (fieldA < fieldB) return sortOrder === "asc" ? -1 : 1;
    if (fieldA > fieldB) return sortOrder === "asc" ? 1 : -1;
    return 0;
  });

  // Pagination
  const indexOfLast = currentPage * employeesPerPage;
  const indexOfFirst = indexOfLast - employeesPerPage;
  const currentEmployees = sortedEmployees.slice(indexOfFirst, indexOfLast);
  const totalPages = Math.ceil(sortedEmployees.length / employeesPerPage);

  const handleSort = (field) => {
    if (sortField === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortOrder("asc");
    }
  };

  return (
    <div className="employees-container">
      <h2>Employees</h2>

      {/* Actions */}
      <div className="employee-actions">
        <input
          type="text"
          placeholder="Search by name"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <input
          type="text"
          placeholder="Filter by department"
          value={departmentFilter}
          onChange={(e) => setDepartmentFilter(e.target.value)}
        />
        <button className="add-btn" onClick={() => setShowAddForm(true)}>+ Add Employee</button>
      </div>

      {/* Table */}
      <table className="employee-table">
        <thead>
          <tr>
            <th onClick={() => handleSort("name")}>Name</th>
            <th onClick={() => handleSort("email")}>Email</th>
            <th onClick={() => handleSort("company")}>Department</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {currentEmployees.map((emp) => (
            <tr key={emp.id} onClick={() => setSelectedEmployee(emp)}>
              <td>{emp.name}</td>
              <td>{emp.email}</td>
              <td>{emp.company.name}</td>
              <td>
                <StatusBadge isActive={emp.id % 2 === 0} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Pagination Controls */}
      <div className="pagination">
        <button disabled={currentPage === 1} onClick={() => setCurrentPage(currentPage - 1)}>
          Prev
        </button>
        <span>Page {currentPage} of {totalPages}</span>
        <button disabled={currentPage === totalPages} onClick={() => setCurrentPage(currentPage + 1)}>
          Next
        </button>
      </div>

      {/* Profile Preview */}
      <EmployeeProfile employee={selectedEmployee} onClose={() => setSelectedEmployee(null)} />

      {/* Add Employee Modal */}
      {showAddForm && (
        <AddEmployeeForm
          onAdd={handleAddEmployee}
          onClose={() => setShowAddForm(false)}
        />
      )}

      {/* Placeholder Sections */}
      <EmployeeSections />
    </div>
  );
};

export default Employees;
