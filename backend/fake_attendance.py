import sqlite3

conn = sqlite3.connect("employees.db")
cursor = conn.cursor()

print("\nEMPLOYEES TABLE")
cursor.execute("""
SELECT id,name,email,company_id
FROM employees
ORDER BY id
""")

for row in cursor.fetchall():
    print(row)

conn.close()