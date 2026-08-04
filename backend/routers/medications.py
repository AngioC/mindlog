from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
from typing import List
import models, schemas
from database import get_db
from dependencies import get_current_user

router = APIRouter(prefix="/medications", tags=["Medications"])

# 1. CREA UN FARMACO
@router.post("/", response_model=schemas.MedicationResponse, status_code=status.HTTP_201_CREATED)
def create_medication(med: schemas.MedicationCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    new_med = models.Medication(**med.model_dump(), user_id=current_user.id)
    db.add(new_med)
    db.commit()
    db.refresh(new_med)
    return new_med

# 2. LEGGI TUTTI I FARMACI (Per Settings)
@router.get("/", response_model=List[schemas.MedicationResponse])
def get_medications(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Medication).filter(models.Medication.user_id == current_user.id).all()

# 3. ELIMINA FARMACO
@router.delete("/{med_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medication(med_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    med = db.query(models.Medication).filter(models.Medication.id == med_id, models.Medication.user_id == current_user.id).first()
    if not med: raise HTTPException(status_code=404, detail="Farmaco non trovato")
    db.delete(med)
    db.commit()
    return None

# 4. GET FARMACI CON LOG DI OGGI (Per la Dashboard)
@router.get("/today", response_model=List[schemas.MedicationTodayResponse])
def get_todays_medications(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    today_date = date.today()
    medications = db.query(models.Medication).filter(models.Medication.user_id == current_user.id).all()
    
    result = []
    for med in medications:
        # Cerchiamo se esiste già un log per oggi
        log = db.query(models.MedicationLog).filter(
            models.MedicationLog.medication_id == med.id,
            models.MedicationLog.date == today_date,
            models.MedicationLog.user_id == current_user.id
        ).first()
        
        taken = log.taken_count if log else 0
        result.append({
            "medication": med,
            "taken_count": taken
        })
        
    return result

# 5. AGGIORNA LE SPUNTE DI OGGI
@router.post("/{med_id}/log", response_model=schemas.MedicationLogResponse)
def update_medication_log(med_id: int, log_data: schemas.MedicationLogUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Controlla se il farmaco esiste ed è dell'utente
    med = db.query(models.Medication).filter(models.Medication.id == med_id, models.Medication.user_id == current_user.id).first()
    if not med: raise HTTPException(status_code=404, detail="Farmaco non trovato")

    today_date = date.today()
    
    # Cerca il log di oggi
    log = db.query(models.MedicationLog).filter(
        models.MedicationLog.medication_id == med_id,
        models.MedicationLog.date == today_date,
        models.MedicationLog.user_id == current_user.id
    ).first()

    # Se non esiste lo crea, altrimenti lo aggiorna
    if not log:
        log = models.MedicationLog(
            user_id=current_user.id,
            medication_id=med_id,
            date=today_date,
            taken_count=log_data.taken_count
        )
        db.add(log)
    else:
        log.taken_count = log_data.taken_count

    db.commit()
    db.refresh(log)
    return log