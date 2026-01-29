from src.database import database, models
from src.auth import auth
from src.config import config

def init_database():
    models.Base.metadata.create_all(bind=database.engine)
    
    db = database.SessionLocal()
    
    try:
        for user_data in config.DEFAULT_USERS:
            if not db.query(models.User).filter(models.User.username == user_data["username"]).first():
                hashed_password = auth.get_password_hash(user_data["password"])
                user = models.User(username=user_data["username"], password=hashed_password)
                db.add(user)
        
        if not db.query(models.Ticket).first():
            for ticket_data in config.SAMPLE_TICKETS:
                ticket = models.Ticket(**ticket_data)
                db.add(ticket)
        
        db.commit()
        print("Database initialized successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()