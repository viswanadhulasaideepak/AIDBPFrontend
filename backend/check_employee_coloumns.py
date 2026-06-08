import sqlite3

conn = sqlite3.connect("employees.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(employees)")
for row in cursor.fetchall():
    print(row)

conn.close()