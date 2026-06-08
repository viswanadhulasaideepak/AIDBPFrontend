import sqlite3
import os

print("DB path:", os.path.abspath("employees.db"))

conn = sqlite3.connect("employees.db")
cur = conn.cursor()

rows = cur.execute("SELECT * FROM attendance").fetchall()

print("ROWS:", rows)

conn.close()