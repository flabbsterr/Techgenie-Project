from fastapi import Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import models
import permissions

templates = Jinja2Templates(directory="templates")

async def manager_dashboard(request: Request, current_user: str, db: Session):
    """Manager dashboard with metrics and analytics"""
    if not permissions.is_manager(current_user, db):
        raise HTTPException(status_code=403, detail="Manager access required")
    
    # Get metrics
    total_tickets = db.query(models.Ticket).count()
    open_tickets = db.query(models.Ticket).filter(models.Ticket.status == "Open").count()
    closed_tickets = db.query(models.Ticket).filter(models.Ticket.status == "Closed").count()
    
    # Priority breakdown
    high_priority = db.query(models.Ticket).filter(models.Ticket.priority == "High").count()
    medium_priority = db.query(models.Ticket).filter(models.Ticket.priority == "Medium").count()
    low_priority = db.query(models.Ticket).filter(models.Ticket.priority == "Low").count()
    
    # User management data
    all_users = db.query(models.User).all()
    admins = [u for u in all_users if u.permission_level == 1]
    managers = [u for u in all_users if u.permission_level == 2]
    regular_users = [u for u in all_users if u.permission_level == 0]
    
    return templates.TemplateResponse("manager_dashboard.html", {
        "request": request,
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "closed_tickets": closed_tickets,
        "high_priority": high_priority,
        "medium_priority": medium_priority,
        "low_priority": low_priority,
        "all_users": all_users,
        "admins": admins,
        "managers": managers,
        "regular_users": regular_users
    })

async def generate_report(request: Request, current_user: str, db: Session):
    """Generate detailed reports"""
    if not permissions.is_manager(current_user, db):
        raise HTTPException(status_code=403, detail="Manager access required")
    
    tickets = db.query(models.Ticket).all()
    
    # Status report
    status_report = {}
    for ticket in tickets:
        status_report[ticket.status] = status_report.get(ticket.status, 0) + 1
    
    # Priority report
    priority_report = {}
    for ticket in tickets:
        priority_report[ticket.priority] = priority_report.get(ticket.priority, 0) + 1
    
    # User activity report
    user_report = {}
    for ticket in tickets:
        user_report[ticket.name] = user_report.get(ticket.name, 0) + 1
    
    return JSONResponse({
        "status_report": status_report,
        "priority_report": priority_report,
        "user_activity": user_report,
        "total_tickets": len(tickets),
        "generated_at": datetime.now().isoformat()
    })

async def view_analytics(request: Request, current_user: str, db: Session):
    """View detailed analytics"""
    if not permissions.is_manager(current_user, db):
        raise HTTPException(status_code=403, detail="Manager access required")
    
    tickets = db.query(models.Ticket).all()
    
    # Calculate analytics
    analytics = {
        "total_tickets": len(tickets),
        "resolution_rate": len([t for t in tickets if t.status == "Closed"]) / len(tickets) * 100 if tickets else 0,
        "high_priority_percentage": len([t for t in tickets if t.priority == "High"]) / len(tickets) * 100 if tickets else 0,
        "status_breakdown": {},
        "priority_breakdown": {}
    }
    
    for ticket in tickets:
        analytics["status_breakdown"][ticket.status] = analytics["status_breakdown"].get(ticket.status, 0) + 1
        analytics["priority_breakdown"][ticket.priority] = analytics["priority_breakdown"].get(ticket.priority, 0) + 1
    
    return templates.TemplateResponse("analytics.html", {
        "request": request,
        "analytics": analytics
    })

async def assign_admin(request: Request, user_id: int, action: str, current_user: str, db: Session):
    """Assign or remove admin privileges"""
    if not permissions.is_manager(current_user, db):
        raise HTTPException(status_code=403, detail="Manager access required")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if action == "promote":
        user.permission_level = 1  # Admin
    elif action == "demote":
        user.permission_level = 0  # Regular user
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    db.commit()
    return RedirectResponse(url="/manager", status_code=302)

async def user_management(request: Request, current_user: str, db: Session):
    """User management interface"""
    if not permissions.is_manager(current_user, db):
        raise HTTPException(status_code=403, detail="Manager access required")
    
    users = db.query(models.User).all()
    return templates.TemplateResponse("user_management.html", {
        "request": request,
        "users": users
    })