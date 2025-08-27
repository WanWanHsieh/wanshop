
from fastapi import APIRouter, Depends, HTTPException, Body
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
def update_fabric(
    fabric_id: int, data: schemas.FabricUpdate, db: Session = Depends(get_db)
):
    obj = db.get(models.Fabric, fabric_id)
    if not obj:
        raise HTTPException(404, "Fabric not found")

    # 取出 payload，另外拉出可選的圖片清單欄位
    payload = data.model_dump()
    images_urls = payload.pop("images_urls", None)
    works_urls = payload.pop("works_urls", None)

    # 更新基本欄位
    for k, v in payload.items():
        setattr(obj, k, v)
    db.commit()

    # 只有當前端有帶入對應清單時才處理圖；完全不帶表示不動圖片
    if images_urls is not None:
        cur = [
            r[0]
            for r in db.query(models.FabricImage.url)
            .filter(models.FabricImage.fabric_id == fabric_id)
            .order_by(models.FabricImage.id.asc())
            .all()
        ]
        if cur != images_urls:
            db.query(models.FabricImage).filter(
                models.FabricImage.fabric_id == fabric_id
            ).delete(synchronize_session=False)
            seen = set()
            for u in images_urls or []:
                if u in seen:
                    continue
                seen.add(u)
                db.add(models.FabricImage(fabric_id=fabric_id, url=u))
            db.commit()

    if works_urls is not None:
        cur = [
            r[0]
            for r in db.query(models.FabricWork.url)
            .filter(models.FabricWork.fabric_id == fabric_id)
            .order_by(models.FabricWork.id.asc())
            .all()
        ]
        if cur != works_urls:
            db.query(models.FabricWork).filter(
                models.FabricWork.fabric_id == fabric_id
            ).delete(synchronize_session=False)
            seen = set()
            for u in works_urls or []:
                if u in seen:
                    continue
                seen.add(u)
                db.add(models.FabricWork(fabric_id=fabric_id, url=u))
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
def add_fabric_images(
    fabric_id: int, urls: List[str] = Body(...), db: Session = Depends(get_db)
):
    fabric = db.get(models.Fabric, fabric_id)
    if not fabric:
        raise HTTPException(404, "Fabric not found")
    # Idempotent: insert only urls not already present
    exists = {
        r[0]
        for r in db.query(models.FabricImage.url)
        .filter(models.FabricImage.fabric_id == fabric_id)
        .all()
    }
    inserted = 0
    for u in urls or []:
        if u in exists:
            continue
        db.add(models.FabricImage(fabric_id=fabric_id, url=u))
        inserted += 1
    db.commit()
    db.refresh(fabric)
    return {"ok": True, "inserted": inserted, "skipped": len((urls or [])) - inserted}


@router.post("/{fabric_id}/works")
def add_fabric_works(
    fabric_id: int, urls: List[str] = Body(...), db: Session = Depends(get_db)
):
    fabric = db.get(models.Fabric, fabric_id)
    if not fabric:
        raise HTTPException(404, "Fabric not found")
    exists = {
        r[0]
        for r in db.query(models.FabricWork.url)
        .filter(models.FabricWork.fabric_id == fabric_id)
        .all()
    }
    inserted = 0
    for u in urls or []:
        if u in exists:
            continue
        db.add(models.FabricWork(fabric_id=fabric_id, url=u))
        inserted += 1
    db.commit()
    db.refresh(fabric)
    return {"ok": True, "inserted": inserted, "skipped": len((urls or [])) - inserted}


# === replace APIs ===
@router.put("/{fabric_id}/images")
def replace_fabric_images(
    fabric_id: int, urls: List[str] = Body(...), db: Session = Depends(get_db)
):
    fabric = db.get(models.Fabric, fabric_id)
    if not fabric:
        raise HTTPException(404, "Fabric not found")
    db.query(models.FabricImage).filter(
        models.FabricImage.fabric_id == fabric_id
    ).delete(synchronize_session=False)
    # de-duplicate while keeping order
    seen = set()
    for u in urls or []:
        if u in seen:
            continue
        seen.add(u)
        db.add(models.FabricImage(fabric_id=fabric_id, url=u))
    db.commit()
    db.refresh(fabric)
    return {"ok": True, "count": len(seen)}


@router.put("/{fabric_id}/works")
def replace_fabric_works(
    fabric_id: int, urls: List[str] = Body(...), db: Session = Depends(get_db)
):
    fabric = db.get(models.Fabric, fabric_id)
    if not fabric:
        raise HTTPException(404, "Fabric not found")
    db.query(models.FabricWork).filter(
        models.FabricWork.fabric_id == fabric_id
    ).delete(synchronize_session=False)
    seen = set()
    for u in urls or []:
        if u in seen:
            continue
        seen.add(u)
        db.add(models.FabricWork(fabric_id=fabric_id, url=u))
    db.commit()
    db.refresh(fabric)
    return {"ok": True, "count": len(seen)}
