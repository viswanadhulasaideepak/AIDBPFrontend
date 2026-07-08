import React, { useEffect, useState } from "react";
import toast from "react-hot-toast";
import DashboardLayout from "../../components/layout/DashboardLayout";
import {fetchMySkills,addSkill,updateSkill,deleteSkill,} from "../../services/api";
import "./EmployeeSkills.css";

const emptySkill = {
  skill_name: "",
  proficiency: "Beginner",
  years_experience: 0,
  is_primary: false,
};

const EmployeeSkills = () => {
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingSkill, setEditingSkill] = useState(null);
  const [form, setForm] = useState(emptySkill);

  const loadSkills = async () => {
    try {
      setLoading(true);
      const data = await fetchMySkills();
      setSkills(data);
    } catch (err) {
      toast.error("Unable to load skills.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSkills();
  }, []);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm({
      ...form,
      [name]:
        type === "checkbox"
          ? checked
          : type === "number"
          ? Number(value)
          : value,
    });
  };

  const openAdd = () => {
    setEditingSkill(null);
    setForm(emptySkill);
    setShowForm(true);
  };

  const openEdit = (skill) => {
    setEditingSkill(skill);
    setForm({
      skill_name: skill.skill_name,
      proficiency: skill.proficiency,
      years_experience: skill.years_experience,
      is_primary: skill.is_primary,
    });

    setShowForm(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.skill_name.trim()) {
      toast.error("Skill name required");
      return;
    }
    if (form.years_experience < 0) {
      toast.error("Invalid experience");
      return;
    }
    try {
      if (editingSkill) {
        await updateSkill(editingSkill.id,form);
        toast.success("Skill updated.");
      } else {
        await addSkill(form);
        toast.success("Skill added.");
      }
      setShowForm(false);
      loadSkills();
    } catch (err) {

      toast.error(
        err?.response?.data?.detail ||
        "Operation failed."
      );
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete skill?"))
      return;
    try {
      await deleteSkill(id);
      toast.success("Skill deleted.");
      loadSkills();
    } catch {
      toast.error("Delete failed.");
    }
  };

  return (
    <DashboardLayout>
      <div className="skills-page">
        <div className="page-header">
          <h2>Skills & Certifications</h2>
          <button className="add-btn" onClick={openAdd}>
            + Add Skill
          </button>
        </div>
        {loading ? (
          <div className="loading">
            Loading...
          </div>

        ) : (

          <table className="skills-table">
            <thead>
              <tr>
                <th>Skill</th>
                <th>Level</th>
                <th>Experience</th>
                <th>Primary</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {skills.length === 0 ? (
                <tr>
                  <td colSpan="5" style={{ textAlign: "center",}}>
                    No skills added.
                  </td>

                </tr>

              ) : (

                skills.map((skill) => (
                  <tr key={skill.id}>
                    <td>{skill.skill_name}</td>
                    <td>{skill.proficiency}</td>
                    <td>
                      {skill.years_experience} Years
                    </td>
                    <td>
                      {skill.is_primary ? (
                        <span className="primary-badge">
                          Primary
                        </span>
                      ) : (
                        "-"
                      )}
                    </td>
                    <td>
                      <button onClick={() => openEdit(skill)}>
                        Edit
                      </button>

                      <button className="delete-btn" onClick={() => handleDelete(skill.id)}>
                        Delete
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
        {showForm && (
          <div className="modal-overlay">
            <div className="modal">
              <h3>
                {editingSkill ? "Edit Skill" : "Add Skill"}
              </h3>
              <form onSubmit={handleSubmit}>
                <input name="skill_name" placeholder="Skill"
                  value={form.skill_name} onChange={handleChange}/>

                <select name="proficiency" value={form.proficiency}
                  onChange={handleChange}>

                  <option>Beginner</option>
                  <option>Intermediate</option>
                  <option>Advanced</option>
                  <option>Expert</option>

                </select>

                <input type="number" name="years_experience"
                  value={form.years_experience} onChange={handleChange}/>

                <label>

                  <input type="checkbox" name="is_primary"
                    checked={form.is_primary} onChange={handleChange}/>
                  Primary Skill

                </label>

                <div className="modal-buttons">
                  <button type="submit">
                    Save
                  </button>

                  <button type="button" onClick={() =>
                      setShowForm(false)}>
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};
export default EmployeeSkills;