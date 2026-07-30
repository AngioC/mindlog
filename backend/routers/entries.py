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
    new_entry = models.Entry(**entry.model_dump(), user_id=current_user.id)
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
    if not db_entry:
        raise HTTPException(status_code=404, detail="Pensiero non trovato")
    
    # Aggiorna solo i campi inviati (exclude_unset=True evita di sovrascrivere con None i campi non forniti)
    update_data = entry_update.model_dump(exclude_unset=True)
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