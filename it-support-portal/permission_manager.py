import sqlite3

# Permission level constants
PERMISSION_USER = 0
PERMISSION_ADMIN = 1
PERMISSION_MANAGER = 2

PERMISSION_NAMES = {
    0: "user",
    1: "admin", 
    2: "manager"
}

def set_user_permission(username, permission_level, db_file='tickets.db'):
    """Set permission level for a user"""
    if permission_level not in [0, 1, 2]:
        print("Invalid permission level. Use 0=user, 1=admin, 2=manager")
        return False
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE users SET permission_level = ? WHERE username = ?", 
                      (permission_level, username))
        
        if cursor.rowcount > 0:
            conn.commit()
            print(f"Updated {username} to {PERMISSION_NAMES[permission_level]} (level {permission_level})")
            return True
        else:
            print(f"User {username} not found")
            return False
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        conn.close()

def get_user_permission(username, db_file='tickets.db'):
    """Get permission level for a user"""
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        cursor.execute("SELECT permission_level FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        if result:
            level = result[0]
            print(f"{username}: {PERMISSION_NAMES[level]} (level {level})")
            return level
        else:
            print(f"User {username} not found")
            return None
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        conn.close()

def list_users_by_permission(db_file='tickets.db'):
    """List all users grouped by permission level"""
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        cursor.execute("SELECT username, permission_level FROM users ORDER BY permission_level DESC, username")
        users = cursor.fetchall()
        
        if users:
            current_level = None
            for username, level in users:
                if level != current_level:
                    print(f"\n{PERMISSION_NAMES[level].upper()}S (level {level}):")
                    current_level = level
                print(f"  - {username}")
        else:
            print("No users found")
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("Permission Level Manager")
    print("Available commands:")
    print("1. set_user_permission('username', level)")
    print("2. get_user_permission('username')")
    print("3. list_users_by_permission()")
    print("\nPermission levels: 0=user, 1=admin, 2=manager")