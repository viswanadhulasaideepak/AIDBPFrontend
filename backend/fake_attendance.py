import sqlite3
conn = sqlite3.connect("employees.db")
cur = conn.cursor()
cur.execute("SELECT id, employee_id, date, check_in, check_out FROM attendance")
print(cur.fetchall())
conn.close()
exit()