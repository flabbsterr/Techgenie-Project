import sqlite3

conn = sqlite3.connect("tickets.db")
conn.execute("""
    CREATE TABLE tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        issue TEXT NOT NULL,
        status TEXT NOT NULL,
        priority TEXT NOT NULL
    )
""")
conn.commit()
conn.close()
