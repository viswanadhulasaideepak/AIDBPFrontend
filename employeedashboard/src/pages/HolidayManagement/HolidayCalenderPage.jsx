import React, { useEffect, useState } from "react";
import DashboardLayout from "../../components/layout/DashboardLayout";
import HolidayCalender from "./HolidayCalender";
import { fetchHolidays } from "../../services/api";
import toast from "react-hot-toast";

const HolidayCalenderPage = () => {
  const [holidays, setHolidays] = useState([]);
  const [loading, setLoading] =useState(true);

  useEffect(() => {
    loadHolidays();
  }, []);

  const loadHolidays = async () => {
    try {
      const data = await fetchHolidays();
      setHolidays(data);
    } catch (err) {
      toast.error("Failed to load holidays");
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <HolidayCalender holidays={holidays} />
      )}
    </DashboardLayout>
  );
};

export default HolidayCalenderPage;