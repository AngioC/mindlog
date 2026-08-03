from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import models, schemas, security
from database import get_db
# 1. AGGIUNGI QUESTO IMPORT PER PROTEGGERE LA ROTTA
from dependencies import get_current_user 

router = APIRouter(tags=["Auth"])

@router.post("/signup", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email già registrata")
    
    hashed_pwd = security.get_password_hash(user.password)
    new_user = models.User(email=user.email, password_hash=hashed_pwd)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    if not db_user or not security.verify_password(form_data.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Email o password errati")
    
    access_token = security.create_access_token(data={"sub": str(db_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.put("/change-password")
def change_password(
    password_data: schemas.PasswordChange,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # 1. Verifica che la vecchia password sia corretta
    if not security.verify_password(password_data.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="La password attuale è errata.")
    
    # 2. Genera l'hash della nuova password
    current_user.password_hash = security.get_password_hash(password_data.new_password)
    
    # 3. Salva nel database
    db.commit()
    
    return {"detail": "Password aggiornata con successo"}

@router.get("/me", response_model=schemas.UserResponse)
def get_current_user_profile(current_user: models.User = Depends(get_current_user)):
    """Restituisce i dati dell'utente attualmente loggato"""
    return current_user