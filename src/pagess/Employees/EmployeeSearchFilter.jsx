import React, { useState } from "react";

export default function EmployeeSearchFilter({ onSearch, onFilter }) {
  const [search, setSearch] = useState("");
  const [department, setDepartment] = useState("");

  return (
    <div className="search-filter">
      <input
        type="text"
        placeholder="Search by name..."
        value={search}
        onChange={(e) => {
          setSearch(e.target.value);
          onSearch(e.target.value);
        }}
      />
      <select
        value={department}
        onChange={(e) => {
          setDepartment(e.target.value);
          onFilter(e.target.value);
        }}
      >
        <option value="">All Departments</option>
        <option value="IT">IT</option>
        <option value="HR">HR</option>
        <option value="Finance">Finance</option>
      </select>
    </div>
  );
}


