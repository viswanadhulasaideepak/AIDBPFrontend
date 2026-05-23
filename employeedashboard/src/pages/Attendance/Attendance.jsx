import { useEffect, useState } from "react";

const Attendance = () => {
  const [attendance, setAttendance] = useState([]);

  useEffect(() => {
    fetch("https://jsonplaceholder.typicode.com/posts")
      .then((res) => res.json())
      .then((data) => setAttendance(data.slice(0, 10))); // Fake logs
  }, []);

  return (
    <div>
      <h2>Attendance</h2>
      <ul>
        {attendance.map((log) => (
          <li key={log.id}>{log.title}</li>
        ))}
      </ul>
    </div>
  );
};

export default Attendance;
