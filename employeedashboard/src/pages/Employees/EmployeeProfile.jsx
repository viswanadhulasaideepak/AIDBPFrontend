import React from "react";
import "./EmployeeProfile.css";

const EmployeeProfile = ({ profile }) => {
  if (!profile) {
    return (
      <div className="profile-wrapper">
        <div className="profile-progress">
          <div
            className="profile-progress-fill"
            style={{ width: "0%", backgroundColor: "#ef4444" }}
          />
        </div>

        <div className="profile-percent">0%</div>
        <p className="profile-text">Loading profile...</p>
      </div>
    );
  }

  const score = profile.completion_percentage || 0;

  let color = "#ef4444";
  if (score >= 80) color = "#22c55e";
  else if (score >= 50) color = "#f59e0b";

  return (
    <div className="profile-wrapper">
      <div className="profile-progress">
        <div
          className="profile-progress-fill"
          style={{
            width: `${score}%`,
            backgroundColor: color,
          }}
        />
      </div>

      <div className="profile-percent">{score}%</div>

      {/* Missing fields */}
      {Array.isArray(profile.missing_fields) &&
      profile.missing_fields.length > 0 ? (
        <div className="profile-missing">
          <strong>Missing Fields</strong>
          <ul>
            {profile.missing_fields.map((field, index) => (
              <li key={index}>{field}</li>
            ))}
          </ul>
        </div>
      ) : (
        <p className="profile-complete-text">
          🎉 All profile fields completed
        </p>
      )}
    </div>
  );
};

export default EmployeeProfile;