from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import List
import models, schemas
from database import get_db
from dependencies import get_current_user

router = APIRouter(prefix="/medications", tags=["Medications"])

@router.post("/", response_model=schemas.MedicationResponse, status_code=status.HTTP_201_CREATED)
def create_medication(med: schemas.MedicationCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    new_med = models.Medication(**med.model_dump(), user_id=current_user.id)
    db.add(new_med)
    db.commit()
    db.refresh(new_med)
    return new_med

@router.get("/", response_model=List[schemas.MedicationResponse])
def get_medications(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Medication).filter(models.Medication.user_id == current_user.id).all()

@router.delete("/{med_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medication(med_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    med = db.query(models.Medication).filter(models.Medication.id == med_id, models.Medication.user_id == current_user.id).first()
    if not med: raise HTTPException(status_code=404, detail="Farmaco non trovato")
    db.delete(med)
    db.commit()
    return None

# --- NUOVO: RICERCA PER DATA SPECIFICA ---
@router.get("/by-date", response_model=List[schemas.MedicationTodayResponse])
def get_medications_by_date(target_date: date, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    medications = db.query(models.Medication).filter(models.Medication.user_id == current_user.id).all()
    
    result = []
    for med in medications:
        log = db.query(models.MedicationLog).filter(
            models.MedicationLog.medication_id == med.id,
            models.MedicationLog.date == target_date,
            models.MedicationLog.user_id == current_user.id
        ).first()
        
        taken = log.taken_count if log else 0
        result.append({
            "medication": med,
            "taken_count": taken
        })
        
    return result

# --- MODIFICATO: ACCETTA LA DATA NELLO SCHEMA ---
@router.post("/{med_id}/log", response_model=schemas.MedicationLogResponse)
def update_medication_log(med_id: int, log_data: schemas.MedicationLogUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    med = db.query(models.Medication).filter(models.Medication.id == med_id, models.Medication.user_id == current_user.id).first()
    if not med: raise HTTPException(status_code=404, detail="Farmaco non trovato")

    # Usa la data inviata, altrimenti usa quella di oggi di default
    log_date = log_data.target_date or date.today()
    
    log = db.query(models.MedicationLog).filter(
        models.MedicationLog.medication_id == med_id,
        models.MedicationLog.date == log_date,
        models.MedicationLog.user_id == current_user.id
    ).first()

    if not log:
        log = models.MedicationLog(
            user_id=current_user.id,
            medication_id=med_id,
            date=log_date,
            taken_count=log_data.taken_count
        )
        db.add(log)
    else:
        log.taken_count = log_data.taken_count

    db.commit()
    db.refresh(log)
    return log

@router.get("/history")
def get_medications_history(start_date: date, end_date: date, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # 1. Calcoliamo quante dosi totali l'utente deve prendere ogni giorno
    meds = db.query(models.Medication).filter(models.Medication.user_id == current_user.id).all()
    total_daily_doses = sum(med.daily_doses for med in meds)

    if total_daily_doses == 0:
        return [] # Nessun farmaco configurato

    # 2. Recuperiamo tutti i log nel periodo richiesto
    logs = db.query(models.MedicationLog).filter(
        models.MedicationLog.user_id == current_user.id,
        models.MedicationLog.date >= start_date,
        models.MedicationLog.date <= end_date
    ).all()

    # Raggruppiamo le prese per data
    taken_by_date = {}
    for log in logs:
        date_str = log.date.isoformat()
        if date_str not in taken_by_date:
            taken_by_date[date_str] = 0
        taken_by_date[date_str] += log.taken_count

    # 3. Creiamo l'array finale riempiendo anche i giorni vuoti con 0%
    result = []
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.isoformat()
        taken = taken_by_date.get(date_str, 0)
        
        percentage = round((taken / total_daily_doses) * 100)
        percentage = min(percentage, 100) # Evitiamo percentuali oltre il 100% in caso di errori
        
        result.append({
            "date": date_str,
            "percentage": percentage
        })
        current_date += timedelta(days=1)
        
    return result