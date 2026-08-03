from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import get_db
from dependencies import get_current_user

router = APIRouter(prefix="/habits", tags=["Habits"])

@router.post("/", response_model=schemas.HabitResponse, status_code=status.HTTP_201_CREATED)
def create_habit(habit: schemas.HabitCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    new_habit = models.Habit(**habit.model_dump(), user_id=current_user.id)
    db.add(new_habit)
    db.commit()
    db.refresh(new_habit)
    return new_habit

@router.get("/", response_model=List[schemas.HabitResponse])
def get_habits(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Habit).filter(models.Habit.user_id == current_user.id).all()

@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_habit(habit_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    habit = db.query(models.Habit).filter(models.Habit.id == habit_id, models.Habit.user_id == current_user.id).first()
    if not habit: raise HTTPException(status_code=404, detail="Abitudine non trovata")
    db.delete(habit)
    db.commit()
    return None

@router.put("/{habit_id}", response_model=schemas.HabitResponse)
def update_habit(
    habit_id: int, 
    habit_update: schemas.HabitUpdate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    habit = db.query(models.Habit).filter(
        models.Habit.id == habit_id, 
        models.Habit.user_id == current_user.id
    ).first()
    
    if not habit:
        raise HTTPException(status_code=404, detail="Abitudine non trovata")
    
    update_data = habit_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(habit, key, value)
        
    db.commit()
    db.refresh(habit)
    return habit