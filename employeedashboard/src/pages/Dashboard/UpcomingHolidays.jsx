import React, { useEffect, useState } from "react";
import { fetchHolidays } from "../../services/api";

const UpcomingHolidays = () => {
  const [holidays, setHolidays] = useState([]);

  useEffect(() => {
    loadUpcoming();
  }, []);

  const loadUpcoming = async () => {
    try {
      const data = await fetchHolidays();
      const today = new Date();

      const upcoming = data.map((holiday) => {
        const holidayDate = new Date(holiday.holiday_date);
        
        if (holiday.recurring) {
          holidayDate.setFullYear(today.getFullYear());

        if (holidayDate < today) {
          holidayDate.setFullYear(today.getFullYear() + 1);
        }
      }

    return {
      ...holiday,
      nextDate: holidayDate,
    };
  })
  .filter((holiday) => holiday.nextDate >= today)
  .sort((a, b) => a.nextDate - b.nextDate)
  .slice(0, 5);

      setHolidays(upcoming);
    } catch (err) {
      console.log(err);
    }
  };

  return (
    <div className="dashboard-card">
      <h3>Upcoming Holidays</h3>
      {holidays.length === 0 ? (
        <p>No upcoming holidays.</p>
      ) : (
        <ul className="upcoming-list">
          {holidays.map((holiday) => (
            <li key={holiday.id}>
              <strong>{holiday.name}</strong>
              <br />

              {new Date(holiday.nextDate).toLocaleDateString()}
              <br />
              <small>{holiday.holiday_type}</small>

              <br />

              {holiday.description && (
                <>
                <br />
                <small>{holiday.description}</small>
                </>
              )}
            </li>
          ))}

        </ul>
      )}

    </div>
  );
};

export default UpcomingHolidays;