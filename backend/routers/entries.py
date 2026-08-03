from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import extract
from typing import List, Optional

# Dobbiamo importare i nostri moduli (usiamo .. se siamo in una sottocartella, oppure il nome del modulo se PYTHONPATH è configurato)
# Per semplicità in locale, assumendo di eseguire da 'backend':
import models, schemas
from database import get_db
from dependencies import get_current_user

# Creiamo il router. Tutti gli endpoint inizieranno in automatico con /entries
router = APIRouter(
    prefix="/entries",
    tags=["Entries"]
)

# 1. CREATE (Crea)
@router.post("/", response_model=schemas.EntryResponse, status_code=status.HTTP_201_CREATED)
def create_entry(entry: schemas.EntryCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Rimuoviamo tag_ids e habit_ids per creare il record base
    entry_data = entry.model_dump(exclude={"tag_ids", "habit_ids"})
    new_entry = models.Entry(**entry_data, user_id=current_user.id)
    
    if entry.tag_ids:
        tags = db.query(models.Tag).filter(models.Tag.id.in_(entry.tag_ids), models.Tag.user_id == current_user.id).all()
        if len(tags) != len(set(entry.tag_ids)):
            raise HTTPException(status_code=400, detail="Uno o più tag non sono validi")
        new_entry.tags = tags

    if entry.habit_ids:
        habits = db.query(models.Habit).filter(models.Habit.id.in_(entry.habit_ids), models.Habit.user_id == current_user.id).all()
        if len(habits) != len(set(entry.habit_ids)):
            raise HTTPException(status_code=400, detail="Una o più abitudini non sono valide")
        new_entry.habits = habits

    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry

# 2. READ ALL (Leggi lista filtrata)
@router.get("/", response_model=List[schemas.EntryResponse])
def read_entries(year: Optional[int] = None, month: Optional[int] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    query = db.query(models.Entry).filter(models.Entry.user_id == current_user.id)
    if year: query = query.filter(extract('year', models.Entry.entry_date) == year)
    if month: query = query.filter(extract('month', models.Entry.entry_date) == month)
    return query.order_by(models.Entry.entry_date.desc()).offset(skip).limit(limit).all()

# 3. READ ONE (Leggi un singolo pensiero specifico)
@router.get("/{entry_id}", response_model=schemas.EntryResponse)
def read_single_entry(entry_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    entry = db.query(models.Entry).filter(models.Entry.id == entry_id, models.Entry.user_id == current_user.id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Pensiero non trovato")
    return entry

# 4. UPDATE (Modifica)
@router.put("/{entry_id}", response_model=schemas.EntryResponse)
def update_entry(entry_id: int, entry_update: schemas.EntryUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_entry = db.query(models.Entry).filter(models.Entry.id == entry_id, models.Entry.user_id == current_user.id).first()
    if not db_entry: raise HTTPException(status_code=404, detail="Pensiero non trovato")
    
    update_data = entry_update.model_dump(exclude_unset=True)
    
    if "tag_ids" in update_data:
        tag_ids = update_data.pop("tag_ids")
        if tag_ids is not None:
            tags = db.query(models.Tag).filter(models.Tag.id.in_(tag_ids), models.Tag.user_id == current_user.id).all()
            db_entry.tags = tags
        else: db_entry.tags = []

    if "habit_ids" in update_data:
        habit_ids = update_data.pop("habit_ids")
        if habit_ids is not None:
            habits = db.query(models.Habit).filter(models.Habit.id.in_(habit_ids), models.Habit.user_id == current_user.id).all()
            db_entry.habits = habits
        else: db_entry.habits = []

    for key, value in update_data.items():
        setattr(db_entry, key, value)
        
    db.commit()
    db.refresh(db_entry)
    return db_entry

# 5. DELETE (Elimina)
@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(entry_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_entry = db.query(models.Entry).filter(models.Entry.id == entry_id, models.Entry.user_id == current_user.id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Pensiero non trovato")
        
    db.delete(db_entry)
    db.commit()
    return None # In un 204 No Content non si restituisce nulla