from fastapi import APIRouter, Depends
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

@router.get("/fabrics/clearance", response_model=List[schemas.FabricOut])
def clearance_fabrics(db: Session = Depends(get_db)):
    return db.query(models.Fabric).filter(models.Fabric.on_clearance == True).all()  # noqa: E712

@router.get("/fabrics", response_model=List[schemas.FabricOut])
def list_fabrics(db: Session = Depends(get_db)):
    return db.query(models.Fabric).all()

@router.get("/categories", response_model=List[schemas.CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()

@router.get("/products/by_category/{category_id}", response_model=List[schemas.ProductOut])
def products_by_category(category_id: int, db: Session = Depends(get_db)):
    return db.query(models.Product).filter(models.Product.category_id == category_id).all()
