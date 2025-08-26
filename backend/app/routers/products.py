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

@router.get("/", response_model=List[schemas.ProductOut])
def list_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()

@router.post("/", response_model=schemas.ProductOut)
def create_product(data: schemas.ProductCreate, db: Session = Depends(get_db)):
    cat = db.get(models.Category, data.category_id)
    if not cat:
        raise HTTPException(400, "category_id not found")
    obj = models.Product(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.Product, product_id)
    if not obj:
        raise HTTPException(404, "Product not found")
    return obj

@router.put("/{product_id}", response_model=schemas.ProductOut)
def update_product(product_id: int, data: schemas.ProductUpdate, db: Session = Depends(get_db)):
    obj = db.get(models.Product, product_id)
    if not obj:
        raise HTTPException(404, "Product not found")
    for k, v in data.model_dump().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.Product, product_id)
    if not obj:
        raise HTTPException(404, "Product not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}

@router.post("/{product_id}/images")
def add_product_images(product_id: int, urls: List[str], db: Session = Depends(get_db)):
    obj = db.get(models.Product, product_id)
    if not obj:
        raise HTTPException(404, "Product not found")
    for u in urls:
        db.add(models.ProductImage(product_id=product_id, url=u))
    db.commit()
    db.refresh(obj)
    return {"ok": True}
