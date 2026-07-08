import React, { useEffect, useState } from "react";
import toast from "react-hot-toast";
import DashboardLayout from "../../components/layout/DashboardLayout";
import {filterCompetencies,downloadCompetencyReport,fetchCompetencyProfile} from "../../services/api";
import "./AdminCompetencies.css";
const AdminCompetencies = () => {
const [employees,setEmployees]=useState([]);
const [loading,setLoading]=useState(true);

const [filters, setFilters] = useState({
    skill: null,
    skill_level: null,
    min_years_experience: null,
    certification_name: null,
    certification_status: null,
});

const [selectedEmployee,setSelectedEmployee]=useState(null);

const loadEmployees = async () => {
    try {
        setLoading(true);

        const cleanFilters = Object.fromEntries(
            Object.entries(filters).filter(
                ([, value]) => value !== null && value !== ""
            )
        );
        const data = await filterCompetencies(cleanFilters);
        console.log(data);
        setEmployees(data);
    } catch (err) {
        console.error(err);
        toast.error("Unable to load competencies.");
    } finally {
        setLoading(false);
    }
};

useEffect(()=>{
    loadEmployees();
},[]);

useEffect(()=>{
    loadEmployees();
},[filters]);

const handleChange = (e) => {
    const { name, value } = e.target;

    setFilters((prev) => ({
        ...prev,
        [name]:
            value === ""
                ? null
                : name === "min_years_experience"
                ? Number(value)
                : value,
    }));
};

const handleViewProfile = async (employeeId) => {
    try {
        const profile = await fetchCompetencyProfile(employeeId);
        console.log(profile);
        setSelectedEmployee(profile);
    } catch (err) {
        console.error(err);
        toast.error("Unable to load profile.");

    }
};

const handleExport=async()=>{
    try{
        await downloadCompetencyReport();
        toast.success("Report downloaded.");
    }catch{
        toast.error("Export failed.");
    }
};

return(
<DashboardLayout>
    <div className="competency-page">

        <h2>Employee Competencies</h2>

        <div className="toolbar">

            <input placeholder="Skill" name="skill"
            value={filters.skill ?? ""} onChange={handleChange}/>

            <select name="skill_level" value={filters.skill_level ?? ""}
               onChange={handleChange}>
                <option value="">All Levels</option>
                <option>Beginner</option>
                <option>Intermediate</option>
                <option>Advanced</option>
                <option>Expert</option>
            </select>

            <input type="number" placeholder="Minimum Experience"
            name="min_years_experience" value={filters.min_years_experience ?? ""}
            onChange={handleChange}/>

            <input placeholder="Certification" name="certification_name"
            value={filters.certification_name ?? ""} onChange={handleChange}/>

            <select name="certification_status" value={filters.certification_status ?? ""}
               onChange={handleChange}>
                <option value="">All Status</option>
                <option>Valid</option>
                <option>Expired</option>
                <option>Expiring Soon</option>
            </select>

            <button onClick={handleExport}>
                Export
            </button>

        </div>
        {loading? (
            <div className="loading">
                Loading...
            </div>
            
        ):(
        
        <table className="competency-table">
            <thead>
                <tr>
                    <th>Employee</th>
                    <th>Email</th>
                    <th>Department</th>
                    <th>Skills</th>
                    <th>Certifications</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                {employees.length===0? (
                    <tr>
                        <td colSpan="6">
                            No Employees Found
                        </td>
                    </tr>
                    
                ):(

                    employees.map((emp , index)=>(
                    <tr key={emp.employee?.id || index}>
                        <td>{emp.employee?.name || "-"}</td>
                        <td>{emp.employee?.email || "-"}</td>
                        <td>{emp.employee?.department_name || "-"}</td>
                        <td>{emp.summary?.total_skills || 0}</td>
                        <td>{emp.summary?.active_certifications || 0}</td>
                        <td>
                            <button onClick={() => handleViewProfile(emp.employee.id)}>
                                View Profile
                            </button>
                        </td>
                    </tr>
                ))
                )}
            </tbody>
        </table>
    )}
    {selectedEmployee && (
        <div className="modal-overlay">
            <div className="profile-modal">
                <h3>{selectedEmployee.employee?.name || selectedEmployee.name}</h3>
                <p>
                    <strong>Email:</strong>
                    {" "}
                    {selectedEmployee.employee?.email || selectedEmployee.email}
                </p>
                <h4>Skills</h4>
                <ul>
                    {(selectedEmployee.skills || []).map(skill=>(
                        <li key={skill.id}>
                           {skill.skill_name} - {skill.proficiency}
                           {" ("}
                           {skill.years_experience}
                           {" yrs)"}
                        </li>
                    ))}
                </ul>
                <h4>Certifications</h4>
                <ul>
                    {(selectedEmployee.certifications || []).map(cert=>(
                        <li key={cert.id}>
                            {cert.certification_name} - {cert.issuing_organization}
                        </li>
                    ))}
                </ul>
                <button onClick={()=>setSelectedEmployee(null)}>
                    Close
                </button>
            </div>
        </div>
    )}
    </div>
</DashboardLayout>
);
};
export default AdminCompetencies;