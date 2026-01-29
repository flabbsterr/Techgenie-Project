import sqlite3

def view_db():
    conn = sqlite3.connect('tickets.db')
    cursor = conn.cursor()
    
    print("=== USERS TABLE ===")
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    print("ID | Username | Password Hash")
    print("-" * 50)
    for user in users:
        print(f"{user[0]} | {user[1]} | {user[2][:20]}...")
    
    print("\n=== TICKETS TABLE ===")
    cursor.execute("SELECT * FROM tickets")
    tickets = cursor.fetchall()
    print("ID | Name | Issue | Status | Priority")
    print("-" * 60)
    for ticket in tickets:
        print(f"{ticket[0]} | {ticket[1]} | {ticket[2][:20]}... | {ticket[3]} | {ticket[4]}")
    
    conn.close()

if __name__ == "__main__":
    view_db()