import React, { useEffect, useState, useContext } from "react";
import { AuthContext } from "../../auth/AuthContext";
import { fetchMyProfile, updateMyProfile, fetchMyProfileCompletion} from "../../services/api";
import toast from "react-hot-toast";
import DashboardLayout from "../../components/layout/DashboardLayout";
import "./Profile.css";

const Profile = () => {
  const { user } = useContext(AuthContext);

  const token = localStorage.getItem("token");

  const [departments, setDepartments] = useState([]);
  const [profileCompletion, setProfileCompletion] = useState(0);
  const [missingFields, setMissingFields] = useState([]);
  const [recommendation, setRecommendation] = useState("");

  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    email: "",
    phone_number: "",
    department_name: "",
    designation: "",
    profile_picture: "",
    address: "",
    joined_date: "",
    employee_code: ""
  });

  // ---------------- LOAD PROFILE ----------------
 useEffect(() => {
  const loadProfile = async () => {
    try {
      const profile = await fetchMyProfile();
      setForm(profile);

      const completion = await fetchMyProfileCompletion();

      setProfileCompletion(completion.completion_percentage);
      setMissingFields(completion.missing_fields || []);
      setRecommendation(completion.recommendation || "");
    } catch (err) {
      toast.error("Failed to load profile");
    }
  };

  loadProfile();
}, []);

  // ---------------- LOAD SUGGESTIONS ----------------
  useEffect(() => {
    const loadSuggestions = async () => {
      try {
        const res = await axios.get(
          "http://localhost:8000/employees/",
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );

        const list = res.data || [];

        const deptList = [
          ...new Set(list.map((e) => e.department_name).filter(Boolean))
        ];

        setDepartments(deptList);
      } catch (err) {
        console.log(err);
      }
    };

    loadSuggestions();
  }, [token]);

  // ---------------- HANDLE CHANGE ----------------
  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value
    });
  };

  // ---------------- SAVE ----------------
  const handleSave = async () => {
  try {
    await updateMyProfile(form);

    toast.success("Profile updated successfully");

    const completion = await fetchMyProfileCompletion();

    setProfileCompletion(completion.completion_percentage);
    setMissingFields(completion.missing_fields || []);
    setRecommendation(completion.recommendation || "");
  } catch (err) {
    toast.error("Update failed");
  }
};
  return (
    <DashboardLayout>
      <div className="profile-page">
        <h2>My Profile</h2>
        <div className="profile-completion-card">
          <h3>Profile Completion: {profileCompletion}%</h3>
       <div className="progress-bar">
    <div className="progress-fill"
      style={{ width: `${profileCompletion}%` }}/>
    </div>
    {missingFields.length > 0 && (
      <>
      <h4>Missing Information</h4>
      
      <ul className="missing-fields">
        {missingFields.map((field) => (
          <li key={field}>{field}</li>
        ))}
      </ul>
      </>
    )}
    <p className="recommendation">
    {recommendation}
    </p>
   </div>
   {["first_name",
     "last_name",
     "email",
     "phone_number",
     "department_name",
     "designation",
     "profile_picture",
     "address",
     "joined_date",
     "employee_code",
    ].map((key) => (
    <div key={key} className="field">
      <label>{key.replaceAll("_", " ")}</label>
      {/* Profile Picture */}
      {key === "profile_picture" ? (
      <>
        <input type="file" accept="image/*"
          onChange={(e) => {
            const file = e.target.files[0];
            if (!file) return;

            const reader = new FileReader();

            reader.onload = () => {
              setForm((prev) => ({
                ...prev,
                profile_picture: reader.result,
              }));
            };
            reader.readAsDataURL(file);
          }}/>

        {form.profile_picture && (
          <img src={form.profile_picture}
            alt="Profile" className="preview-img"/>
        )}
      </>
    ) : key === "department_name" ? (
      <>
        <input list="dept-list" name={key}
          value={form[key] || ""} onChange={handleChange}/>

        <datalist id="dept-list">
          {departments.map((d, i) => (
            <option key={i} value={d} />
          ))}
        </datalist>
      </>
    ) : key === "joined_date" ? (
      <input type="date" name={key}
        value={form[key] || ""} onChange={handleChange}/>
    ) : key === "email" ? (
      <input name={key} value={form[key] || ""}
        readOnly/>
    ) : key === "employee_code" ? (
      <input name={key} value={form[key] || ""}
       readOnly/>
    ) : (
      <input name={key} value={form[key] || ""}
        onChange={handleChange}/>
    )}
  </div>
))}

<button onClick={handleSave} className="save-btn">
  Save Profile
</button>
      </div>
    </DashboardLayout>
  );
};

export default Profile;