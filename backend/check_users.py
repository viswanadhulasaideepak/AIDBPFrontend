import sqlite3

conn = sqlite3.connect("employees.db")
cursor = conn.cursor()

columns = [
    ("first_name", "TEXT"),
    ("last_name", "TEXT"),
    ("phone_number", "TEXT"),
    ("designation", "TEXT"),
    ("profile_picture", "TEXT"),
    ("address", "TEXT"),
]

for col, col_type in columns:
    try:
        cursor.execute(f"ALTER TABLE employees ADD COLUMN {col} {col_type}")
        print(f"Added column: {col}")
    except Exception as e:
        print(f"Skipping {col}: {e}")

conn.commit()
conn.close()

print("Migration completed safely")