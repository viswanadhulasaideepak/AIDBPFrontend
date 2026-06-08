import sqlite3
from datetime import datetime

conn = sqlite3.connect("employees.db")
cur = conn.cursor()

cur.execute("""
INSERT INTO attendance (employee_id, date, status, company_id)
VALUES (?, ?, ?, ?)
""", (1, datetime.now().strftime("%Y-%m-%d"), "Present", 1))

conn.commit()
conn.close()

print("Attendance added")