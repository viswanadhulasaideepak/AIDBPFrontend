import { useEffect, useState } from "react";

const initialState = {
  name: "",
  holiday_date: "",
  description: "",
  holiday_type: "Public Holiday",
  recurring: false,
};

export default function HolidayForm({
  onSubmit,
  editingHoliday,
  onCancel,
}) {
  const [form, setForm] = useState(initialState);

  useEffect(() => {
    if (editingHoliday) {
      setForm({
        name: editingHoliday.name || "",
        holiday_date: editingHoliday.holiday_date
        ? editingHoliday.holiday_date.substring(0, 10)
        : "",
        description: editingHoliday.description || "",
        holiday_type: editingHoliday.holiday_type || "Public Holiday",
        recurring: editingHoliday.recurring || false,
      });
    } else {
      setForm(initialState);
    }
  }, [editingHoliday]);

  const handleChange = (e) => {
  const { name, value, type, checked } = e.target;
  setForm({
    ...form,
    [name]: type === "checkbox" ? checked : value,
  });
};

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.name.trim()) {
      alert("Holiday Name is required.");
      return;
    }

    if (!form.holiday_date) {
      alert("Holiday Date is required.");
      return;
      }
    onSubmit({
      ...form,
      name: form.name.trim(),
      description: form.description.trim(),
      holiday_type: form.holiday_type,
      recurring: form.recurring,
    });
    setForm(initialState);
  };

  return (
    <form className="holiday-form" onSubmit={handleSubmit}>
      <input type="text" name="name" placeholder="Holiday Name"
        value={form.name} onChange={handleChange} required/>

      <input type="date" name="holiday_date" value={form.holiday_date}
        onChange={handleChange} required/>

      <select name="holiday_type" value={form.holiday_type} onChange={handleChange}>
        <option value="Public Holiday">
          Public Holiday
        </option>

        <option value="Company Holiday">
          Company Holiday
        </option>

        <option value="Optional Holiday">
          Optional Holiday
        </option>
      </select>  

      <input type="text" name="description" placeholder="Description"
        value={form.description} onChange={handleChange}/>

        <label className="checkbox-label">
          <input type="checkbox" name="recurring"
           checked={form.recurring} onChange={handleChange}/>
              Recurring Every Year
        </label>

      <button type="submit">
        {editingHoliday ? "Update Holiday" : "Add Holiday"}
      </button>

      {editingHoliday && (
        <button type="button" onClick={() => {
            setForm(initialState);
            onCancel();
            }}>
                Cancel
        </button>
      )}
    </form>
  );
}