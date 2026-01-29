from fastapi import FastAPI, Request, Form, Depends, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from typing import Optional

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./tickets_v3.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    permission_level = Column(Integer, default=0)

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    username = Column(String)
    issue = Column(String)
    status = Column(String)
    priority = Column(String)

Base.metadata.create_all(bind=engine)

# Auth setup
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except:
        return None

# FastAPI app
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.middleware("http")
async def add_user_to_request(request: Request, call_next):
    token = request.cookies.get("access_token")
    username = verify_token(token) if token else None
    request.state.user = username
    
    if username:
        db = SessionLocal()
        user = db.query(User).filter(User.username == username).first()
        request.state.user_permission = user.permission_level if user else 0
        db.close()
    else:
        request.state.user_permission = 0
    
    response = await call_next(request)
    return response

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: Optional[str] = Cookie(None, alias="access_token")):
    if not token:
        return None
    return verify_token(token)

# Initialize database
def init_db():
    db = SessionLocal()
    if not db.query(User).filter(User.username == "staff").first():
        staff_user = User(username="staff", password=get_password_hash("password123"), permission_level=0)
        db.add(staff_user)
    if not db.query(User).filter(User.username == "it").first():
        it_user = User(username="it", password=get_password_hash("itadmin123"), permission_level=1)
        db.add(it_user)
    if not db.query(Ticket).first():
        tickets = [
            Ticket(name="John Doe", username="staff", issue="Computer won't start", status="Open", priority="High"),
            Ticket(name="Jane Smith", username="it", issue="Email not working", status="In Progress", priority="Medium"),
            Ticket(name="Bob Johnson", username="staff", issue="Printer offline", status="Closed", priority="Low")
        ]
        for ticket in tickets:
            db.add(ticket)
    db.commit()
    db.close()

init_db()

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(current_user: str = Depends(get_current_user)):
    if current_user:
        return RedirectResponse(url="/log", status_code=302)
    return RedirectResponse(url="/login", status_code=302)

@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_post(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    username = username.replace(" ", "")
    user = db.query(User).filter(User.username == username).first()
    
    if user and verify_password(password, user.password):
        access_token = create_access_token(data={"sub": username})
        response = RedirectResponse(url="/log", status_code=302)
        response.set_cookie(key="access_token", value=access_token, httponly=True)
        return response
    
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials", "username": username})

@app.get("/signup", response_class=HTMLResponse)
async def signup_get(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup")
async def signup_post(request: Request, username: str = Form(...), password: str = Form(...), confirm_password: str = Form(...), db: Session = Depends(get_db)):
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
    
    if db.query(User).filter(User.username == username).first():
        return templates.TemplateResponse("signup.html", {"request": request, "error": "Username already exists"})
    
    hashed_password = get_password_hash(password)
    user = User(username=username, password=hashed_password, permission_level=0)
    db.add(user)
    db.commit()
    
    access_token = create_access_token(data={"sub": username})
    response = RedirectResponse(url="/log", status_code=302)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie(key="access_token")
    return response

@app.get("/log", response_class=HTMLResponse)
async def log_ticket_get(request: Request, current_user: str = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("log_ticket.html", {"request": request})

@app.post("/log")
async def log_ticket_post(request: Request, name: str = Form(...), issue: str = Form(...), current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    if not name.strip() or not issue.strip():
        return templates.TemplateResponse("log_ticket.html", {"request": request, "error": "Name and issue are required"})
    
    if len(issue.strip()) < 25 or len(issue.strip()) > 250:
        return templates.TemplateResponse("log_ticket.html", {"request": request, "error": "Issue description must be between 25 and 250 characters", "name": name, "issue": issue})
    
    ticket = Ticket(name=name.strip(), username=current_user, issue=issue.strip(), status="Open", priority="Medium")
    db.add(ticket)
    db.commit()
    
    return RedirectResponse(url="/my-tickets", status_code=302)

@app.get("/my-tickets", response_class=HTMLResponse)
async def staff_tickets(request: Request, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    tickets = db.query(Ticket).all()
    user_tickets = [t for t in tickets if t.username == current_user]
    open_tickets_list = [t for t in user_tickets if t.status != "Closed"]
    closed_tickets_list = [t for t in user_tickets if t.status == "Closed"]
    sorted_tickets = open_tickets_list + closed_tickets_list
    return templates.TemplateResponse("staff_tickets.html", {"request": request, "tickets": sorted_tickets})

@app.get("/it", response_class=HTMLResponse)
async def it_dashboard_get(request: Request, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    user = db.query(User).filter(User.username == current_user).first()
    if not user or user.permission_level < 1:
        return RedirectResponse(url="/log", status_code=302)
    
    tickets = db.query(Ticket).all()
    open_tickets = [t for t in tickets if t.status != "Closed"]
    closed_tickets = [t for t in tickets if t.status == "Closed"]
    all_tickets = open_tickets + closed_tickets
    open_count = len([t for t in tickets if t.status == "Open"])
    closed_count = len([t for t in tickets if t.status == "Closed"])
    
    return templates.TemplateResponse("it_dashboard.html", {
        "request": request, 
        "tickets": all_tickets, 
        "open_count": open_count, 
        "closed_count": closed_count
    })

@app.post("/it")
async def it_dashboard_post(request: Request, ticket_id: int = Form(...), status: str = Form(...), priority: str = Form(...), current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    user = db.query(User).filter(User.username == current_user).first()
    if not user or user.permission_level < 1:
        return RedirectResponse(url="/log", status_code=302)
    
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket:
        ticket.status = status
        ticket.priority = priority
        db.commit()
    
    return RedirectResponse(url="/it", status_code=302)

@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    tickets = db.query(Ticket).all()
    user_tickets = [t for t in tickets if t.username == current_user]
    open_tickets_list = [t for t in user_tickets if t.status != "Closed"]
    closed_tickets_list = [t for t in user_tickets if t.status == "Closed"]
    sorted_tickets = open_tickets_list + closed_tickets_list
    open_tickets = len([t for t in user_tickets if t.status == "Open"])
    closed_tickets = len([t for t in user_tickets if t.status == "Closed"])
    
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user_tickets": sorted_tickets,
        "open_tickets": open_tickets,
        "closed_tickets": closed_tickets
    })

@app.post("/admin/set-permission")
async def set_permission(username: str = Form(...), permission_level: int = Form(...), current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    admin_user = db.query(User).filter(User.username == current_user).first()
    if not admin_user or admin_user.permission_level < 1:
        return RedirectResponse(url="/log", status_code=302)
    
    user = db.query(User).filter(User.username == username).first()
    if user:
        user.permission_level = permission_level
        db.commit()
    
    return RedirectResponse(url="/it", status_code=302)

@app.post("/delete-ticket")
async def delete_ticket(ticket_id: int = Form(...), current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket and ticket.username == current_user:
        db.delete(ticket)
        db.commit()
    
    return RedirectResponse(url="/my-tickets", status_code=302)

@app.post("/edit-ticket")
async def edit_ticket(ticket_id: int = Form(...), name: str = Form(...), issue: str = Form(...), current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    if len(issue.strip()) < 25 or len(issue.strip()) > 250:
        return RedirectResponse(url="/my-tickets", status_code=302)
    
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket and ticket.username == current_user:
        ticket.name = name.strip()
        ticket.issue = issue.strip()
        db.commit()
    
    return RedirectResponse(url="/my-tickets", status_code=302)

@app.post("/delete-account")
async def delete_account(password: str = Form(...), current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    user = db.query(User).filter(User.username == current_user).first()
    if user and verify_password(password, user.password):
        db.delete(user)
        db.commit()
        response = RedirectResponse(url="/login", status_code=302)
        response.delete_cookie(key="access_token")
        return response
    
    return RedirectResponse(url="/profile", status_code=302)

if __name__ == "__main__":
    import uvicorn
    print("\nTo change user permissions:")
    print("1. Use DB Browser for SQLite to edit tickets_new.db")
    print("2. Or POST to /admin/set-permission with username and permission_level (0 or 1)")
    print("\nDefault accounts: staff (level 0), it (level 1)\n")
    uvicorn.run(app, host="0.0.0.0", port=8001)