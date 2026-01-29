from pydantic import BaseModel

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    
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