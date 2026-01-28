import sqlite3

conn = sqlite3.connect("tickets.db")
conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
""")
conn.execute("""
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        issue TEXT NOT NULL,
        status TEXT NOT NULL,
        priority TEXT NOT NULL
    )
""")
conn.commit()
conn.close()

print("Database initialized successfully!")
