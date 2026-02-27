from fastapi import Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import timedelta
import app.core.auth as auth
import app.db.database as database
import app.db.models as models

templates = Jinja2Templates(directory="templates")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = None):
    if not token:
        return None
    return auth.verify_token(token)

async def home(request: Request, current_user: str = None):
    if current_user:
        return RedirectResponse(url="/log", status_code=302)
    return RedirectResponse(url="/login", status_code=302)

async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

async def login_post(request: Request, username: str, password: str, db: Session):
    username = username.replace(" ", "")
    user = db.query(models.User).filter(models.User.username == username).first()
    
    if user and auth.verify_password(password, user.password):
        access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth.create_access_token(
            data={"sub": username}, expires_delta=access_token_expires
        )
        response = RedirectResponse(url="/log", status_code=302)
        response.set_cookie(key="access_token", value=access_token, httponly=True)
        return response
    
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials", "username": username})

async def signup_get(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

async def signup_post(request: Request, username: str, password: str, confirm_password: str, db: Session):
    username = username.strip()
    password = password.strip()
    
    if not username or not password:
        return templates.TemplateResponse("signup.html", {"request": request, "error": "Username and password are required"})
    
    if " " in username:
        return templates.TemplateResponse("signup.html", {"request": request, "error": "Username cannot contain spaces"})
    
    if password != confirm_password:
        return templates.TemplateResponse("signup.html", {"request": request, "error": "Passwords do not match"})
    
    if len(password) < 6 or not any(char.isdigit() for char in password):
        return templates.TemplateResponse("signup.html", {"request": request, "error": "Password must be at least 6 characters with one number"})
    
    if db.query(models.User).filter(models.User.username == username).first():
        return templates.TemplateResponse("signup.html", {"request": request, "error": "Username already exists"})
    
    hashed_password = auth.get_password_hash(password)
    role = "it" if username.lower() == "it" else "staff"
    user = models.User(username=username, password=hashed_password, role=role)
    db.add(user)
    db.commit()
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    response = RedirectResponse(url="/log", status_code=302)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response

async def logout(request: Request):
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie(key="access_token")
    return response

async def log_ticket_get(request: Request, current_user: str):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("log_ticket.html", {"request": request})

async def log_ticket_post(request: Request, name: str, issue: str, current_user: str, db: Session):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    name = name.strip()
    issue = issue.strip()
    
    if name and issue:
        ticket = models.Ticket(name=name, issue=issue, status="Open", priority="Medium")
        db.add(ticket)
        db.commit()
    
    return RedirectResponse(url="/my-tickets", status_code=302)

async def staff_tickets(request: Request, current_user: str, db: Session):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    tickets = db.query(models.Ticket).all()
    return templates.TemplateResponse("staff_tickets.html", {"request": request, "tickets": tickets})

async def it_dashboard_get(request: Request, current_user: str, db: Session):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    tickets = db.query(models.Ticket).all()
    open_count = len([t for t in tickets if t.status == "Open"])
    closed_count = len([t for t in tickets if t.status == "Closed"])
    
    return templates.TemplateResponse("it_dashboard.html", {
        "request": request, 
        "tickets": tickets, 
        "open_count": open_count, 
        "closed_count": closed_count
    })

async def it_dashboard_post(request: Request, ticket_id: int, status: str, priority: str, current_user: str, db: Session):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if ticket:
        ticket.status = status
        ticket.priority = priority
        db.commit()
    
    return RedirectResponse(url="/it", status_code=302)

async def profile(request: Request, current_user: str, db: Session):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    tickets = db.query(models.Ticket).all()
    user_tickets = [t for t in tickets if t.name.lower() == current_user.lower()]
    open_tickets = len([t for t in user_tickets if t.status == "Open"])
    closed_tickets = len([t for t in user_tickets if t.status == "Closed"])
    
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user_tickets": user_tickets,
        "open_tickets": open_tickets,
        "closed_tickets": closed_tickets
    })

async def change_password(request: Request, current_password: str, new_password: str, confirm_password: str, current_user: str, db: Session):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    user = db.query(models.User).filter(models.User.username == current_user).first()
    
    if not user or not auth.verify_password(current_password, user.password):
        return templates.TemplateResponse("profile.html", {"request": request, "error": "Current password is incorrect"})
    
    if new_password != confirm_password:
        return templates.TemplateResponse("profile.html", {"request": request, "error": "New passwords do not match"})
    
    if len(new_password) < 6 or not any(char.isdigit() for char in new_password):
        return templates.TemplateResponse("profile.html", {"request": request, "error": "Password must be at least 6 characters with one number"})
    
    user.password = auth.get_password_hash(new_password)
    db.commit()
    
    return RedirectResponse(url="/profile", status_code=302)

async def delete_account(request: Request, current_user: str, db: Session):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    user = db.query(models.User).filter(models.User.username == current_user).first()
    if user:
        db.delete(user)
        db.commit()
    
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie(key="access_token")
    return response