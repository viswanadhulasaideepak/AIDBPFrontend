import React, { useEffect, useState } from "react";
import toast from "react-hot-toast";
import DashboardLayout from "../../components/layout/DashboardLayout";
import {fetchMyCertifications,addCertification,updateCertification,
  deleteCertification,} from "../../services/api";
import "./EmployeeCertifications.css";
const EmployeeCertifications = () => {
 
  const [certifications, setCertifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingCertification, setEditingCertification] = useState(null);

  const [form, setForm] = useState({
    certification_name: "",
    issuing_organization: "",
    issue_date: "",
    expiry_date: "",
    file: null,
  });

  const loadCertifications = async () => {
    try {
      setLoading(true);
      const data = await fetchMyCertifications();
      setCertifications(data);
    } catch {
      toast.error("Unable to load certifications.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCertifications();
  }, []);

const handleChange = (e) => {
  const { name, value } = e.target;
  setForm({
    ...form,
    [name]: value,
  });

};

const handleFile = (e) => {
  setForm({
    ...form,
    file: e.target.files[0],
  });

};

const openAdd = () => {
  setEditingCertification(null);
  setForm({
    certification_name: "",
    issuing_organization: "",
    issue_date: "",
    expiry_date: "",
    file: null,
  });
  setShowForm(true);
};

const openEdit = (certification) => {
  setEditingCertification(certification);
  setForm({
    certification_name: certification.certification_name,
    issuing_organization: certification.issuing_organization,
    issue_date: certification.issue_date,
    expiry_date: certification.expiry_date || "",
    file: null,
  });
  setShowForm(true);
};

const handleSubmit = async (e) => {
  e.preventDefault();
  if (!form.certification_name.trim()) {
    toast.error("Certification name required");
    return;
  }

  if (!form.issuing_organization.trim()) {
    toast.error("Organization required");
    return;
  }

  if (
    form.expiry_date &&
    form.issue_date &&
    form.expiry_date < form.issue_date
  ) {
    toast.error(
      "Expiry date cannot be earlier than issue date."
    );
    return;
  }

  const data = new FormData();
  data.append(
    "certification_name",
    form.certification_name
  );

  data.append(
    "issuing_organization",
    form.issuing_organization
  );

  data.append(
    "issue_date",
    form.issue_date
  );

  if (form.expiry_date) {
    data.append(
      "expiry_date",
      form.expiry_date
    );
  }

  if (form.file) {
    data.append("file", form.file);
  }

  try {
    if (editingCertification) {
      await updateCertification(
        editingCertification.id,
        data
      );
      toast.success("Certification updated.");
    } else {
      await addCertification(data);
      toast.success("Certification added.");
    }
    setShowForm(false);
    loadCertifications();
  } catch (err) {

    toast.error(
      err?.response?.data?.detail ||
      "Operation failed."
    );
  }
};

const handleDelete = async (id) => {
  if (!window.confirm("Delete certification?"))
    return;
  try {
    await deleteCertification(id);
    toast.success("Deleted.");
    loadCertifications();
  } catch {
    toast.error("Delete failed.");
  }
};

return (
  <DashboardLayout>
    <div className="certification-page">
      <div className="page-header">
        <h2>Professional Certifications</h2>
        <button className="add-btn" onClick={openAdd}>
          + Add Certification
        </button>
      </div>
      {loading ? (
        <div className="loading">
          Loading Certifications...
        </div>

      ) : (

        <table className="certification-table">
          <thead>
            <tr>
              <th>Certification</th>
              <th>Organization</th>
              <th>Issue Date</th>
              <th>Expiry Date</th>
              <th>Status</th>
              <th>Document</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody>
            {certifications.length === 0 ? (
              <tr>
                <td colSpan="7"
                  style={{ textAlign: "center",}}>
                  No Certifications Found.
                </td>
              </tr>

            ) : (

              certifications.map((cert) => {
                const today = new Date();
                const expired =
                  cert.expiry_date &&
                  new Date(cert.expiry_date) < today;
                return (
                  <tr key={cert.id}>
                    <td>
                      {cert.certification_name}
                    </td>

                    <td>
                      {cert.issuing_organization}
                    </td>

                    <td>
                      {cert.issue_date}
                    </td>

                    <td>
                      {cert.expiry_date || "-"}
                    </td>

                    <td>
                      {expired ? (
                        <span className="expired">
                          Expired
                        </span>

                      ) : (

                        <span className="active">
                          Active
                        </span>
                      )}
                    </td>
                    <td>

                      {cert.document_path ? (
                        <a href={`http://localhost:8000/${cert.document_path}`}
                          target="_blank" rel="noreferrer">
                          View
                        </a>

                      ) : (

                        "-"

                      )}
                    </td>
                    <td>
                      <button onClick={() => openEdit(cert)}>
                        Edit
                      </button>

                      <button className="delete-btn"
                        onClick={() => handleDelete(cert.id)}>
                        Delete
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      )}

      {showForm && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>
              {editingCertification ? "Edit Certification" : "Add Certification"}
            </h3>

            <form onSubmit={handleSubmit}>

              <input name="certification_name" placeholder="Certification Name"
                value={form.certification_name} onChange={handleChange}/>

              <input name="issuing_organization" placeholder="Issuing Organization"
                value={form.issuing_organization} onChange={handleChange}/>

              <label>
                Issue Date
              </label>

              <input type="date" name="issue_date"
                value={form.issue_date} onChange={handleChange}/>

              <label>
                Expiry Date
              </label>

              <input type="date" name="expiry_date"
                value={form.expiry_date} onChange={handleChange}/>

              <label>
                Upload Certificate
              </label>

              <input type="file" accept=".pdf,.png,.jpg,.jpeg"
                onChange={handleFile}/>

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
}
export default EmployeeCertifications;