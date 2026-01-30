from fastapi import FastAPI, Request, Form, Depends, Cookie
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional
import uvicorn

# Import modules
import database
import models
import auth
import ui
import services
import config
import manager_routes
import permissions

# Create FastAPI app
app = FastAPI(title=config.config.APP_NAME, version=config.config.VERSION)

# Add middleware
@app.middleware("http")
async def add_user_to_request(request: Request, call_next):
    token = request.cookies.get("access_token")
    username = auth.verify_token(token) if token else None
    request.state.user = username
    
    # Add permission level to request state
    if username:
        db = database.SessionLocal()
        try:
            user = db.query(models.User).filter(models.User.username == username).first()
            request.state.user_permission = user.permission_level if user else 0
        finally:
            db.close()
    else:
        request.state.user_permission = 0
    
    response = await call_next(request)
    return response

# Mount static files
app.mount("/static", StaticFiles(directory=config.config.STATIC_DIR), name="static")

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

# Dependency functions
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: Optional[str] = Cookie(None, alias="access_token")):
    if not token:
        return None
    return auth.verify_token(token)

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, current_user: str = Depends(get_current_user)):
    return await ui.home(request, current_user)

@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return await ui.login_get(request)

@app.post("/login")
async def login_post(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    return await ui.login_post(request, username, password, db)

@app.get("/signup", response_class=HTMLResponse)
async def signup_get(request: Request):
    return await ui.signup_get(request)

@app.post("/signup")
async def signup_post(request: Request, username: str = Form(...), password: str = Form(...), confirm_password: str = Form(...), db: Session = Depends(get_db)):
    return await ui.signup_post(request, username, password, confirm_password, db)

@app.get("/logout")
async def logout(request: Request):
    return await ui.logout(request)

@app.get("/log", response_class=HTMLResponse)
async def log_ticket_get(request: Request, current_user: str = Depends(get_current_user)):
    return await ui.log_ticket_get(request, current_user)

@app.post("/log")
async def log_ticket_post(request: Request, name: str = Form(...), issue: str = Form(...), current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    return await ui.log_ticket_post(request, name, issue, current_user, db)

@app.get("/my-tickets", response_class=HTMLResponse)
async def staff_tickets(request: Request, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    return await ui.staff_tickets(request, current_user, db)

@app.get("/it", response_class=HTMLResponse)
async def it_dashboard_get(request: Request, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    return await ui.it_dashboard_get(request, current_user, db)

@app.post("/it")
async def it_dashboard_post(request: Request, ticket_id: int = Form(...), status: str = Form(...), priority: str = Form(...), current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    return await ui.it_dashboard_post(request, ticket_id, status, priority, current_user, db)

@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    return await ui.profile(request, current_user, db)

@app.post("/change-password")
async def change_password(request: Request, current_password: str = Form(...), new_password: str = Form(...), confirm_password: str = Form(...), current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    return await ui.change_password(request, current_password, new_password, confirm_password, current_user, db)

@app.get("/delete-account")
async def delete_account(request: Request, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    return await ui.delete_account(request, current_user, db)

# Manager routes
@app.get("/manager", response_class=HTMLResponse)
async def manager_dashboard(request: Request, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    return await manager_routes.manager_dashboard(request, current_user, db)

@app.get("/manager/analytics", response_class=HTMLResponse)
async def view_analytics(request: Request, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    return await manager_routes.view_analytics(request, current_user, db)

@app.get("/manager/report")
async def generate_report(request: Request, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    return await manager_routes.generate_report(request, current_user, db)

@app.post("/manager/assign-admin")
async def assign_admin(request: Request, user_id: int = Form(...), action: str = Form(...), current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    return await manager_routes.assign_admin(request, user_id, action, current_user, db)

if __name__ == "__main__":
    uvicorn.run("app:app", host=config.config.HOST, port=config.config.PORT, reload=True)