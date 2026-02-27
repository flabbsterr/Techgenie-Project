from fastapi import FastAPI, Request, Form, Depends, Cookie
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional
import uvicorn

try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    RATE_LIMIT_ENABLED = True
except ImportError:
    RATE_LIMIT_ENABLED = False

import app.db.database as database
import app.db.models as models
import app.core.auth as auth
import app.api.ui as ui
import app.core.services as services
import app.core.config as config

app = FastAPI(title=config.config.APP_NAME, version=config.config.VERSION)

if RATE_LIMIT_ENABLED:
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.middleware("http")
async def add_user_to_request(request: Request, call_next):
    token = request.cookies.get("access_token")
    username = auth.verify_token(token) if token else None
    request.state.user = username
    request.state.user_permission = 0
    
    if username:
        db = database.SessionLocal()
        try:
            user = db.query(models.User).filter(models.User.username == username).first()
            if user:
                if user.role == "it":
                    request.state.user_permission = 2
                elif user.role == "manager":
                    request.state.user_permission = 1
        finally:
            db.close()
    
    response = await call_next(request)
    return response

app.mount("/static", StaticFiles(directory=config.config.STATIC_DIR), name="static")
models.Base.metadata.create_all(bind=database.engine)

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

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, current_user: str = Depends(get_current_user)):
    return await ui.home(request, current_user)

@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return await ui.login_get(request)

if RATE_LIMIT_ENABLED:
    @app.post("/login")
    @limiter.limit("5/minute")
    async def login_post(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
        return await ui.login_post(request, username, password, db)
else:
    @app.post("/login")
    async def login_post(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
        return await ui.login_post(request, username, password, db)

@app.get("/signup", response_class=HTMLResponse)
async def signup_get(request: Request):
    return await ui.signup_get(request)

if RATE_LIMIT_ENABLED:
    @app.post("/signup")
    @limiter.limit("3/minute")
    async def signup_post(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...), confirm_password: str = Form(...), db: Session = Depends(get_db)):
        return await ui.signup_post(request, username, email, password, confirm_password, db)
else:
    @app.post("/signup")
    async def signup_post(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...), confirm_password: str = Form(...), db: Session = Depends(get_db)):
        return await ui.signup_post(request, username, email, password, confirm_password, db)

@app.get("/logout")
async def logout(request: Request):
    return await ui.logout(request)

@app.get("/log", response_class=HTMLResponse)
async def log_ticket_get(request: Request, current_user: str = Depends(get_current_user)):
    return await ui.log_ticket_get(request, current_user)

@app.post("/log")
async def log_ticket_post(request: Request, name: str = Form(...), department: str = Form(...), category: str = Form(...), issue: str = Form(...), current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    return await ui.log_ticket_post(request, name, None, department, category, issue, current_user, db)

@app.get("/my-tickets", response_class=HTMLResponse)
async def staff_tickets(request: Request, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    return await ui.staff_tickets(request, current_user, db)

@app.post("/my-tickets/edit")
async def edit_ticket(request: Request, ticket_id: int = Form(...), name: str = Form(...), department: str = Form(...), category: str = Form(...), issue: str = Form(...), current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    return await ui.edit_ticket(request, ticket_id, name, department, category, issue, current_user, db)

@app.get("/my-tickets/delete/{ticket_id}")
async def delete_ticket(request: Request, ticket_id: int, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    return await ui.delete_ticket(request, ticket_id, current_user, db)

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

@app.get("/manager", response_class=HTMLResponse)
async def manager_dashboard(request: Request, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    return await ui.manager_dashboard(request, current_user, db)

@app.get("/manager/download-report")
async def download_manager_report(request: Request, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    return await ui.download_manager_report(request, current_user, db)

if __name__ == "__main__":
    uvicorn.run("main:app", host=config.config.HOST, port=config.config.PORT, reload=config.config.DEBUG)
