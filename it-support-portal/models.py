from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    permission_level = Column(Integer, default=0)  # 0=user, 1=admin, 2=manager

class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    issue = Column(String)
    status = Column(String)
    priority = Column(String)