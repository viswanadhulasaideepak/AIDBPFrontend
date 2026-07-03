import React from "react";
import DashboardLayout from "../../components/layout/DashboardLayout"
import "./HolidayCalender.css";

const HolidayCalender = ({ holidays = [] }) => {
  const today = new Date();

  // Current month
  const year = today.getFullYear();
  const month = today.getMonth();

  const firstDay = new Date(year, month, 1).getDay();
  const totalDays = new Date(year, month + 1, 0).getDate();

  const holidayMap = {};

  holidays.forEach((holiday) => {

    console.log("Holiday:", holiday);

    const [y, m, d] = holiday.holiday_date.split("T")[0].split("-");

    const date = new Date(Number(y),Number(m) - 1,Number(d));

    console.log(holiday.name, holiday.holiday_date,date.toString(),
    "Month =", date.getMonth(),"Day =", date.getDate()
  );

    // Recurring holiday
    if (holiday.recurring) {
      if (date.getMonth() === month) {
        holidayMap[date.getDate()] = holiday;
      }
    }
    // Normal holiday
    else {
      if (
        date.getFullYear() === year &&
        date.getMonth() === month
      ) {
        holidayMap[date.getDate()] = holiday;
      }
    }
  });

  const cells = [];

  // Empty cells before month starts
  for (let i = 0; i < firstDay; i++) {
    cells.push(
      <div
        key={`empty-${i}`}
        className="calendar-cell empty"
      />
    );
  }

  // Month days
  for (let day = 1; day <= totalDays; day++) {
    const holiday = holidayMap[day];

    const isToday =
      day === today.getDate() &&
      month === today.getMonth() &&
      year === today.getFullYear();

    cells.push(
      <div
        key={day}
        className={`calendar-cell ${
          holiday ? "holiday" : ""
        } ${isToday ? "today" : ""}`}
      >
        <div className="calendar-date">
          {day}
        </div>

        {holiday && (
          <>
            <div className="holiday-name">
              {holiday.name}
            </div>

            <div className="holiday-type">
              {holiday.holiday_type}
            </div>

            {holiday.recurring && (
              <div className="holiday-recurring">
                🔁 Recurring
              </div>
            )}

            {holiday.description && (
              <div className="holiday-description">
                {holiday.description}
              </div>
            )}
          </>
        )}
      </div>
    );
  }

  return (
  
    <div className="holiday-calendar">
      <h3>
        {today.toLocaleString("default", {
          month: "long",
        })}{" "}
        {year}
      </h3>

      <div className="calendar-header">
        <div>Sun</div>
        <div>Mon</div>
        <div>Tue</div>
        <div>Wed</div>
        <div>Thu</div>
        <div>Fri</div>
        <div>Sat</div>
      </div>

      <div className="calendar-grid">
        {cells}
      </div>
    </div>
  );
};

export default HolidayCalender;