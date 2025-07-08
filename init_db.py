import sqlite3
import os

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# ✅ 1. Create posts table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    post TEXT NOT NULL,
    result TEXT NOT NULL
)
''')

# ✅ 2. Try to add feedback column
try:
    cursor.execute("ALTER TABLE posts ADD COLUMN feedback TEXT DEFAULT ''")
    print("✅ Feedback column added.")
except sqlite3.OperationalError as e:
    print("⚠️ Feedback column might already exist:", e)

# ✅ 3. Create users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')
print("✅ Users table ready.")

conn.commit()
conn.close()
