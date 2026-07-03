import React, { useEffect, useState } from "react";
import toast from "react-hot-toast";

import { fetchHolidays, createHoliday, updateHoliday, deleteHoliday} from "../../services/api";
import HolidayCalender from "./HolidayCalender";
import HolidayForm from "../../components/HolidayForm";
import DashboardLayout from "../../components/layout/DashboardLayout";

import "./HolidayManagement.css";

const HolidayManagement = () => {
  const [holidays, setHolidays] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [view, setView] = useState("all");
  const [showForm, setShowForm] = useState(false);
  const [editingHoliday, setEditingHoliday] = useState(null);
  const user = JSON.parse(localStorage.getItem("user"));

  const isAdmin = user?.role?.toLowerCase() === "admin";

  const loadHolidays = async () => {
    try {
      setLoading(true);
      const data = await fetchHolidays();
      console.log("Fetched Holidays:", data);
      setHolidays(
        data.sort(
        (a, b) =>
            new Date(a.holiday_date) -
            new Date(b.holiday_date)
          )
        );
    } catch (err) {
      toast.error( err.response?.data?.detail || "Failed to load holidays.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHolidays();
  }, []);

  const handleAddHoliday = async (holiday) => {
    try {
      await createHoliday(holiday);

      toast.success("Holiday added successfully.");

      setShowForm(false);

      loadHolidays();
    } catch (err) {
      toast.error( err.response?.data?.detail || "Unable to create holiday.");
    }
  };

  const handleUpdateHoliday = async (holiday) => {
    try {
      await updateHoliday(editingHoliday.id, holiday);

      toast.success("Holiday updated successfully.");

      setEditingHoliday(null);

      setShowForm(false);

      loadHolidays();
    } catch (err) {
      toast.error( err.response?.data?.detail || "Unable to update holiday.");
    }
  };

  const handleDeleteHoliday = async (id) => {
    const confirmDelete = window.confirm("Delete this holiday?");
    if (!confirmDelete) return;
    try {
      await deleteHoliday(id);
      toast.success("Holiday deleted.");
      loadHolidays();
    } catch (err) {
      toast.error( err.response?.data?.detail || "Unable to delete holiday.");
    }
  };

  const today = new Date();

  const filteredHolidays = holidays.filter((holiday) => {
    const keyword = search.toLowerCase();
    const holidayDate = new Date(holiday.holiday_date);
    const matchesSearch =
        holiday.name.toLowerCase().includes(keyword) ||
        holiday.description?.toLowerCase().includes(keyword) ||
        holiday.holiday_type?.toLowerCase().includes(keyword);

    if (!matchesSearch) return false;

    if (view === "upcoming")
        return holidayDate >= today;

    if (view === "past")
        return holidayDate < today;

    return true;
});

  const resetForm = () => {
    setEditingHoliday(null);
    setShowForm(false);
};

  return (
    <DashboardLayout>

      <div className="holiday-page">
        <div className="holiday-header">
          <h2>Holiday Management</h2>
          {isAdmin && (
            <button className="add-btn" type="button"
            onClick={() => {
                setEditingHoliday(null);
                setShowForm(true);}}>
              + Add Holiday
            </button>)}
        </div>

        <div className="holiday-filters">
          <button onClick={() => setView("all")}>
           All
          </button>

          <button onClick={() => setView("upcoming")}>
           Upcoming
          </button>

          <button onClick={() => setView("past")}>
           Past
          </button>
        </div>

        <input className="holiday-search" placeholder="Search holidays..."
          value={search} onChange={(e) => setSearch(e.target.value)}/>

        {loading ? (
          <p>Loading...</p>
        ) : (
          <table className="holiday-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Date</th>
                <th>Type</th>
                <th>Description</th>
                <th>Recurring</th>
                {isAdmin && (
                  <th>Actions</th>
                  )}
              </tr>
            </thead>
            <tbody>
              {filteredHolidays.length === 0 ? (
                <tr>
                  <td colSpan={isAdmin ? 6 : 5}>
                    No holidays found.
                  </td>
                </tr>
              ) : (
                filteredHolidays.map((holiday) => (
                  <tr key={holiday.id}>
                    <td>{holiday.name}</td>
                    <td>{new Date(holiday.holiday_date).toLocaleDateString()}</td>
                    <td>{holiday.holiday_type}</td>
                    <td>{holiday.description || "-"}</td>
                    <td>
                      <span className={holiday.recurring ? "recurring-yes" : "recurring-no"}>
                          {holiday.recurring ? "Yes" : "No"}
                      </span>
                    </td>
                    {isAdmin && (
                      <td>
                        <button className="edit-btn"
                          onClick={() => {
                            setEditingHoliday(holiday);
                            setShowForm(true);}}>
                          Edit
                        </button>

                        <button className="delete-btn"
                          onClick={() =>
                            handleDeleteHoliday(
                              holiday.id)}>
                          Delete
                        </button>
                      </td>
                    )}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
        {showForm && (
            <HolidayForm editingHoliday={editingHoliday}
            onCancel={resetForm} onSubmit={(holiday) => {
                if (editingHoliday) {
                    handleUpdateHoliday(holiday);
                } else {
                    handleAddHoliday(holiday);
                }
            }}
            />
            )}
            {!loading && (
            <HolidayCalender holidays={holidays} />
          )}
      </div>
    </DashboardLayout>
  );
};

export default HolidayManagement;