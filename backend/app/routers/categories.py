from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import SessionLocal
from .. import models, schemas

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[schemas.CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()

@router.post("/", response_model=schemas.CategoryOut)
def create_category(data: schemas.CategoryCreate, db: Session = Depends(get_db)):
    exists = db.query(models.Category).filter(models.Category.name == data.name).first()
    if exists:
        raise HTTPException(400, "Category exists")
    obj = models.Category(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.put("/{category_id}", response_model=schemas.CategoryOut)
def update_category(category_id: int, data: schemas.CategoryUpdate, db: Session = Depends(get_db)):
    obj = db.get(models.Category, category_id)
    if not obj:
        raise HTTPException(404, "Category not found")
    obj.name = data.name
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.Category, category_id)
    if not obj:
        raise HTTPException(404, "Category not found")
    if obj.products:
        raise HTTPException(400, "Category has products")
    db.delete(obj)
    db.commit()
    return {"ok": True}
