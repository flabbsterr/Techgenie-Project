import sqlite3

def add_permission_level_column():
    """Add permission_level column to users table in all database files"""
    
    db_files = ['tickets.db', 'tickets_v2.db', 'tickets_v3.db', 'tickets_new.db']
    
    for db_file in db_files:
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Check if column already exists
            cursor.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'permission_level' not in columns:
                # Add permission_level column with default value 0 (user)
                cursor.execute("ALTER TABLE users ADD COLUMN permission_level INTEGER DEFAULT 0")
                print(f"Added permission_level column to {db_file}")
            else:
                print(f"permission_level column already exists in {db_file}")
            
            conn.commit()
            conn.close()
            
        except sqlite3.Error as e:
            print(f"Error updating {db_file}: {e}")
        except FileNotFoundError:
            print(f"Database file {db_file} not found, skipping...")

if __name__ == "__main__":
    add_permission_level_column()