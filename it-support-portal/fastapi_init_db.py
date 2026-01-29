from sqlalchemy.orm import Session
import fastapi_models as models
import fastapi_database as database
import fastapi_auth as auth

models.Base.metadata.create_all(bind=database.engine)

def init_db():
    db = database.SessionLocal()
    
    # Create default users with hashed passwords
    if not db.query(models.User).filter(models.User.username == "staff").first():
        staff_user = models.User(username="staff", password=auth.get_password_hash("password123"))
        db.add(staff_user)
    
    if not db.query(models.User).filter(models.User.username == "it").first():
        it_user = models.User(username="it", password=auth.get_password_hash("itadmin123"))
        db.add(it_user)
    
    # Create sample tickets
    if not db.query(models.Ticket).first():
        tickets = [
            models.Ticket(name="John Doe", issue="Computer won't start", status="Open", priority="High"),
            models.Ticket(name="Jane Smith", issue="Email not working", status="In Progress", priority="Medium"),
            models.Ticket(name="Bob Johnson", issue="Printer offline", status="Closed", priority="Low")
        ]
        for ticket in tickets:
            db.add(ticket)
    
    db.commit()
    db.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()