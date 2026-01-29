import sqlite3
from typing import Optional

def validate_username(username: str) -> tuple[bool, Optional[str]]:
    """Validate username format"""
    if not username or not username.strip():
        return False, "Username is required"
    
    username = username.strip()
    
    if " " in username:
        return False, "Username cannot contain spaces"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    return True, None

def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """Validate password strength"""
    if not password:
        return False, "Password is required"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one number"
    
    return True, None

def validate_ticket_data(name: str, issue: str) -> tuple[bool, Optional[str]]:
    """Validate ticket creation data"""
    if not name or not name.strip():
        return False, "Name is required"
    
    if not issue or not issue.strip():
        return False, "Issue description is required"
    
    if len(issue.strip()) < 10:
        return False, "Issue description must be at least 10 characters"
    
    return True, None

def view_database():
    """View database contents for debugging"""
    try:
        conn = sqlite3.connect('tickets.db')
        cursor = conn.cursor()
        
        print("=== USERS TABLE ===")
        cursor.execute("SELECT id, username FROM users")
        users = cursor.fetchall()
        for user in users:
            print(f"ID: {user[0]}, Username: {user[1]}")
        
        print("\n=== TICKETS TABLE ===")
        cursor.execute("SELECT id, name, issue, status, priority FROM tickets")
        tickets = cursor.fetchall()
        for ticket in tickets:
            print(f"ID: {ticket[0]}, Name: {ticket[1]}, Issue: {ticket[2][:30]}..., Status: {ticket[3]}, Priority: {ticket[4]}")
        
        conn.close()
    except Exception as e:
        print(f"Error viewing database: {e}")

def clean_input(text: str) -> str:
    """Clean and sanitize user input"""
    if not text:
        return ""
    return text.strip()

def format_ticket_id(ticket_id: int) -> str:
    """Format ticket ID for display"""
    return f"#{ticket_id:04d}"