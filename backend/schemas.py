from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from datetime import date

# Schema per i dati in entrata (Signup e Login)
class UserCreate(BaseModel):
    email: EmailStr # Valida in automatico che sia una mail vera
    password: str

# Schema per i dati in uscita (Non contiene la password!)
class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime

    # Necessario per leggere direttamente dagli oggetti SQLAlchemy
    class Config:
        from_attributes = True 

# Schema per il token
class Token(BaseModel):
    access_token: str
    token_type: str

class TagBase(BaseModel):
    name: str
    color: Optional[str] = None # Es. "#FF5733" per i colori in formato HEX

class TagCreate(TagBase):
    pass

class TagUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None

class TagResponse(TagBase):
    id: int

    class Config:
        from_attributes = True

# Dati inviati dall'utente per creare un pensiero
class EntryCreate(BaseModel):
    title: Optional[str] = None
    content: str
    mood_score: Optional[int] = None
    entry_date: date
    tag_ids: Optional[List[int]] = []

# Dati restituiti dal backend
class EntryResponse(BaseModel):
    id: int
    title: Optional[str]
    content: str
    mood_score: Optional[int]
    entry_date: date
    created_at: datetime
    tags: List[TagResponse] = [] 
    
    class Config:
        from_attributes = True

class EntryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    entry_date: Optional[date] = None
    mood_score: Optional[int] = None
    tag_ids: Optional[List[int]] = None

class PasswordChange(BaseModel):
    old_password: str
    new_password: str