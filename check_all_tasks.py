import sqlite3

conn = sqlite3.connect('maccs/coordination.db')
cursor = conn.cursor()

cursor.execute("SELECT task_id, title, status, priority FROM tasks ORDER BY posted_at")
rows = cursor.fetchall()

print(f'\nTotal tasks: {len(rows)}\n')
for row in rows:
    print(f'{row[0]}: {row[1]}')
    print(f'  Status: {row[2]}, Priority: {row[3]}\n')

conn.close()
