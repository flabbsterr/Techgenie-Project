from sqlalchemy.orm import Session
from ..database import models
from ..auth import auth

class UserService:
    @staticmethod
    def create_user(db: Session, username: str, password: str):
        hashed_password = auth.get_password_hash(password)
        user = models.User(username=username, password=hashed_password)
        db.add(user)
        db.commit()
        return user
    
    @staticmethod
    def get_user_by_username(db: Session, username: str):
        return db.query(models.User).filter(models.User.username == username).first()

class TicketService:
    @staticmethod
    def create_ticket(db: Session, name: str, issue: str, status: str = "Open", priority: str = "Medium"):
        ticket = models.Ticket(name=name, issue=issue, status=status, priority=priority)
        db.add(ticket)
        db.commit()
        return ticket
    
    @staticmethod
    def get_all_tickets(db: Session):
        return db.query(models.Ticket).all()