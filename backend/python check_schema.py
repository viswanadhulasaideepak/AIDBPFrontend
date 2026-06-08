import sqlite3
conn = sqlite3.connect("employees.db")
cursor = conn.execute("PRAGMA table_info(employees);")
for row in cursor:
    print(row)
