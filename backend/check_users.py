import sqlite3

conn = sqlite3.connect("employees.db")
cursor = conn.cursor()

# Show all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables:")
for table in cursor.fetchall():
    print(table)

print("\nUsers:")

cursor.execute("SELECT id, username, email, role, company_id FROM users")
for row in cursor.fetchall():
    print(row)

conn.close()