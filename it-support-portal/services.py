from sqlalchemy.orm import Session
import models
import auth

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
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str):
        user = UserService.get_user_by_username(db, username)
        if user and auth.verify_password(password, user.password):
            return user
        return None
    
    @staticmethod
    def update_password(db: Session, username: str, new_password: str):
        user = UserService.get_user_by_username(db, username)
        if user:
            user.password = auth.get_password_hash(new_password)
            db.commit()
            return True
        return False
    
    @staticmethod
    def delete_user(db: Session, username: str):
        user = UserService.get_user_by_username(db, username)
        if user:
            db.delete(user)
            db.commit()
            return True
        return False

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
    
    @staticmethod
    def get_tickets_by_user(db: Session, username: str):
        return db.query(models.Ticket).filter(models.Ticket.name.ilike(f"%{username}%")).all()
    
    @staticmethod
    def update_ticket(db: Session, ticket_id: int, status: str = None, priority: str = None):
        ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
        if ticket:
            if status:
                ticket.status = status
            if priority:
                ticket.priority = priority
            db.commit()
            return ticket
        return None
    
    @staticmethod
    def get_ticket_stats(db: Session):
        tickets = TicketService.get_all_tickets(db)
        return {
            "total": len(tickets),
            "open": len([t for t in tickets if t.status == "Open"]),
            "in_progress": len([t for t in tickets if t.status == "In Progress"]),
            "closed": len([t for t in tickets if t.status == "Closed"])
        }