from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import models, schemas
from database import get_db
from dependencies import get_current_user

router = APIRouter(
    prefix="/tags",
    tags=["Tags"]
)

# 1. CREATE
@router.post("/", response_model=schemas.TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(tag: schemas.TagCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Controlliamo che l'utente non abbia già un tag con questo stesso nome
    existing_tag = db.query(models.Tag).filter(models.Tag.name == tag.name, models.Tag.user_id == current_user.id).first()
    if existing_tag:
        raise HTTPException(status_code=400, detail="Hai già un tag con questo nome")

    new_tag = models.Tag(**tag.model_dump(), user_id=current_user.id)
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    return new_tag

# 2. READ ALL
@router.get("/", response_model=List[schemas.TagResponse])
def read_tags(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    tags = db.query(models.Tag).filter(models.Tag.user_id == current_user.id).all()
    return tags

# 3. READ ONE
@router.get("/{tag_id}", response_model=schemas.TagResponse)
def read_single_tag(tag_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id, models.Tag.user_id == current_user.id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag non trovato")
    return tag

# 4. UPDATE
@router.put("/{tag_id}", response_model=schemas.TagResponse)
def update_tag(tag_id: int, tag_update: schemas.TagUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_tag = db.query(models.Tag).filter(models.Tag.id == tag_id, models.Tag.user_id == current_user.id).first()
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag non trovato")
    
    update_data = tag_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_tag, key, value)
        
    db.commit()
    db.refresh(db_tag)
    return db_tag

# 5. DELETE
@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_tag = db.query(models.Tag).filter(models.Tag.id == tag_id, models.Tag.user_id == current_user.id).first()
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag non trovato")
        
    db.delete(db_tag)
    db.commit()
    return None