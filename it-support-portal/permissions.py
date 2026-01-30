from sqlalchemy.orm import Session
import models

def get_user_permission_level(username: str, db: Session) -> int:
    """Get user's permission level"""
    user = db.query(models.User).filter(models.User.username == username).first()
    return user.permission_level if user else 0

def is_manager(username: str, db: Session) -> bool:
    """Check if user is manager (level 2)"""
    return get_user_permission_level(username, db) == 2

def is_admin(username: str, db: Session) -> bool:
    """Check if user is admin (level 1) or higher"""
    return get_user_permission_level(username, db) >= 1

def require_manager(username: str, db: Session):
    """Raise exception if user is not manager"""
    if not is_manager(username, db):
        raise PermissionError("Manager access required")

def require_admin(username: str, db: Session):
    """Raise exception if user is not admin"""
    if not is_admin(username, db):
        raise PermissionError("Admin access required")