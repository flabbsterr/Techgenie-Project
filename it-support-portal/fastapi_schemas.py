from pydantic import BaseModel

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str
    permission_level: int = 0

class User(UserBase):
    id: int
    permission_level: int
    
    class Config:
        orm_mode = True

class TicketBase(BaseModel):
    name: str
    issue: str
    status: str
    priority: str

class TicketCreate(TicketBase):
    pass

class Ticket(TicketBase):
    id: int
    
    class Config:
        orm_mode = True