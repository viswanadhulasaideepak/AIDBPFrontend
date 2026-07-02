import React, { useEffect, useState } from "react";
import DashboardLayout from "../../components/layout/DashboardLayout";
import { fetchCompanyProfileCompletion } from "../../services/api";
import toast from "react-hot-toast";
import "./Company.css";

const Company = () => {
  const [members, setMembers] = useState([]);
  const [adminCount, setAdminCount] = useState(0);
  const [userCount, setUserCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCompanyData();
  }, []);

  const loadCompanyData = async () => {
    try {
      const data = await fetchCompanyProfileCompletion();
      console.log(data);

      setMembers(data.members || []);
      setAdminCount(data.admin_count || 0);
      setUserCount(data.user_count || 0);
    } catch (error) {
      console.error(error);
      toast.error("Failed to load company data");
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="company-page">
        <h2>Company Overview</h2>

        {/* Summary Cards */}
        <div className="company-summary">

          <div className="summary-card">
            <h3>Total Members</h3>
            <p>{members.length}</p>
          </div>

          <div className="summary-card">
            <h3>Admins</h3>
            <p>{adminCount}</p>
          </div>

          <div className="summary-card">
            <h3>Users</h3>
            <p>{userCount}</p>
          </div>

        </div>

        {/* Members Table */}
        <div className="company-table-container">

          <h3>Company Members</h3>

          {loading ? (
            <p>Loading...</p>
          ) : members.length === 0 ? (
            <p>No members found.</p>
          ) : (
            <table className="company-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Role</th>
                  <th>Department</th>
                  <th>Designation</th>
                  <th>Completion</th>
                  <th>Missing Fields</th>
                </tr>
              </thead>

              <tbody>
                {members.map((member) => (
                  <tr key={member.employee_id}>
                    <td>{member.employee_name}</td>

                    <td>{member.role}</td>

                    <td>
                      {member.department || "-"}
                    </td>

                    <td>
                      {member.designation || "-"}
                    </td>

                    <td>
                      <div className="progress-wrapper">
                        <div className="progress-bar">
                          <div
                            className="progress-fill"
                            style={{
                              width: `${member.completion_percentage}%`
                            }}
                          />
                        </div>

                        <span>
                          {member.completion_percentage}%
                        </span>
                      </div>
                    </td>

                    <td>
                      {member.missing_fields?.length > 0
                        ? member.missing_fields.join(", ")
                        : "Completed"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Company;