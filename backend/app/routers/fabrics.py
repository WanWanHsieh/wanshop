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

@router.get("/", response_model=List[schemas.FabricOut])
def list_fabrics(db: Session = Depends(get_db)):
    return db.query(models.Fabric).all()

@router.post("/", response_model=schemas.FabricOut)
def create_fabric(data: schemas.FabricCreate, db: Session = Depends(get_db)):
    obj = models.Fabric(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/{fabric_id}", response_model=schemas.FabricOut)
def get_fabric(fabric_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.Fabric, fabric_id)
    if not obj:
        raise HTTPException(404, "Fabric not found")
    return obj

@router.put("/{fabric_id}", response_model=schemas.FabricOut)
def update_fabric(fabric_id: int, data: schemas.FabricUpdate, db: Session = Depends(get_db)):
    obj = db.get(models.Fabric, fabric_id)
    if not obj:
        raise HTTPException(404, "Fabric not found")
    for k, v in data.model_dump().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{fabric_id}")
def delete_fabric(fabric_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.Fabric, fabric_id)
    if not obj:
        raise HTTPException(404, "Fabric not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}

@router.post("/{fabric_id}/images")
def add_fabric_images(fabric_id: int, urls: List[str], db: Session = Depends(get_db)):
    fabric = db.get(models.Fabric, fabric_id)
    if not fabric:
        raise HTTPException(404, "Fabric not found")
    for u in urls:
        db.add(models.FabricImage(fabric_id=fabric_id, url=u))
    db.commit()
    db.refresh(fabric)
    return {"ok": True, "count": len(urls)}

@router.post("/{fabric_id}/works")
def add_fabric_works(fabric_id: int, urls: List[str], db: Session = Depends(get_db)):
    fabric = db.get(models.Fabric, fabric_id)
    if not fabric:
        raise HTTPException(404, "Fabric not found")
    for u in urls:
        db.add(models.FabricWork(fabric_id=fabric_id, url=u))
    db.commit()
    db.refresh(fabric)
    return {"ok": True, "count": len(urls)}
