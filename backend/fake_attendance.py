import sqlite3

conn = sqlite3.connect("employees.db")
cur = conn.cursor()

cur.execute("""
DELETE FROM attendance
WHERE status IN ('active','inactive','onleave')
""")

conn.commit()
conn.close()

print("Cleaned old attendance records")