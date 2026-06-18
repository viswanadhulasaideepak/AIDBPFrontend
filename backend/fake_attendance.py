import sqlite3

conn = sqlite3.connect("employees.db")
cursor = conn.cursor()

cursor.execute("""
SELECT *
FROM attendance_access_requests
WHERE id = 10;
""")

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()