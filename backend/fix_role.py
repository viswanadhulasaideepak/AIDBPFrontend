import sqlite3

conn = sqlite3.connect("employees.db")
cursor = conn.cursor()

columns = [
    ("performed_by", "VARCHAR"),
    ("ip_address", "VARCHAR"),
    ("browser", "VARCHAR"),
    ("is_new_device", "BOOLEAN DEFAULT 0"),
    ("is_new_ip", "BOOLEAN DEFAULT 0"),
    ("details", "TEXT")
]

for name, datatype in columns:
    try:
        cursor.execute(f"ALTER TABLE audit_logs ADD COLUMN {name} {datatype}")
        print(f"Added: {name}")
    except Exception as e:
        print(f"Skipped {name}: {e}")

conn.commit()
conn.close()

print("Finished")