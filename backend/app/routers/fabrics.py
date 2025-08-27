from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from urllib.parse import urlparse
from ..database import SessionLocal
from .. import models, schemas

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---- helpers ----
def _normalize_urls(urls: List[str]) -> List[str]:
    norm = []
    for u in urls or []:
        try:
            p = urlparse(u).path or u
        except Exception:
            p = u
        norm.append(p)
    out, seen = [], set()
    for u in norm:
        if u in seen:
            continue
        seen.add(u)
        out.append(u)
    return out


# ---- CRUD ----
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

    payload = data.model_dump()
    images_urls = payload.pop("images_urls", None)
    works_urls = payload.pop("works_urls", None)

    # 更新基本欄位
    for k, v in payload.items():
        setattr(obj, k, v)
    db.commit()

    # 有帶清單才處理；沒帶就不動圖片
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


# ---- image/work APIs ----
# 追加（冪等）：存在就略過
@router.post("/{fabric_id}/images")
def add_fabric_images(
    fabric_id: int, urls: List[str] = Body(...), db: Session = Depends(get_db)
):
    obj = db.get(models.Fabric, fabric_id)
    if not obj:
        raise HTTPException(404, "Fabric not found")
    exists = {
        r[0]
        for r in db.query(models.FabricImage.url)
        .filter(models.FabricImage.fabric_id == fabric_id)
        .all()
    }
    ins = 0
    for u in urls or []:
        if u in exists:
            continue
        db.add(models.FabricImage(fabric_id=fabric_id, url=u))
        ins += 1
    db.commit()
    db.refresh(obj)
    return {"ok": True, "inserted": ins, "skipped": len((urls or [])) - ins}


@router.post("/{fabric_id}/works")
def add_fabric_works(
    fabric_id: int, urls: List[str] = Body(...), db: Session = Depends(get_db)
):
    obj = db.get(models.Fabric, fabric_id)
    if not obj:
        raise HTTPException(404, "Fabric not found")
    exists = {
        r[0]
        for r in db.query(models.FabricWork.url)
        .filter(models.FabricWork.fabric_id == fabric_id)
        .all()
    }
    ins = 0
    for u in urls or []:
        if u in exists:
            continue
        db.add(models.FabricWork(fabric_id=fabric_id, url=u))
        ins += 1
    db.commit()
    db.refresh(obj)
    return {"ok": True, "inserted": ins, "skipped": len((urls or [])) - ins}


# 取代（全刪再建）
@router.put("/{fabric_id}/images")
def replace_fabric_images(
    fabric_id: int, urls: List[str] = Body(...), db: Session = Depends(get_db)
):
    obj = db.get(models.Fabric, fabric_id)
    if not obj:
        raise HTTPException(404, "Fabric not found")
    db.query(models.FabricImage).filter(
        models.FabricImage.fabric_id == fabric_id
    ).delete(synchronize_session=False)
    seen = set()
    for u in urls or []:
        if u in seen:
            continue
        seen.add(u)
        db.add(models.FabricImage(fabric_id=fabric_id, url=u))
    db.commit()
    db.refresh(obj)
    return {"ok": True, "count": len(seen)}


@router.put("/{fabric_id}/works")
def replace_fabric_works(
    fabric_id: int, urls: List[str] = Body(...), db: Session = Depends(get_db)
):
    obj = db.get(models.Fabric, fabric_id)
    if not obj:
        raise HTTPException(404, "Fabric not found")
    db.query(models.FabricWork).filter(models.FabricWork.fabric_id == fabric_id).delete(
        synchronize_session=False
    )
    seen = set()
    for u in urls or []:
        if u in seen:
            continue
        seen.add(u)
        db.add(models.FabricWork(fabric_id=fabric_id, url=u))
    db.commit()
    db.refresh(obj)
    return {"ok": True, "count": len(seen)}


# 刪除（支援絕對或相對 URL）
@router.delete("/{fabric_id}/images")
def delete_fabric_images(
    fabric_id: int,
    url: Optional[str] = None,
    urls: Optional[List[str]] = Body(None),
    db: Session = Depends(get_db),
):
    obj = db.get(models.Fabric, fabric_id)
    if not obj:
        raise HTTPException(404, "Fabric not found")
    targets = list(filter(None, (urls or []))) + ([url] if url else [])
    if not targets:
        raise HTTPException(400, "Missing url or urls")
    candidates = list(dict.fromkeys(_normalize_urls(targets) + targets))
    deleted = (
        db.query(models.FabricImage)
        .filter(
            models.FabricImage.fabric_id == fabric_id,
            models.FabricImage.url.in_(candidates),
        )
        .delete(synchronize_session=False)
    )
    db.commit()
    return {"ok": True, "deleted": deleted}


@router.delete("/{fabric_id}/works")
def delete_fabric_works(
    fabric_id: int,
    url: Optional[str] = None,
    urls: Optional[List[str]] = Body(None),
    db: Session = Depends(get_db),
):
    obj = db.get(models.Fabric, fabric_id)
    if not obj:
        raise HTTPException(404, "Fabric not found")
    targets = list(filter(None, (urls or []))) + ([url] if url else [])
    if not targets:
        raise HTTPException(400, "Missing url or urls")
    candidates = list(dict.fromkeys(_normalize_urls(targets) + targets))
    deleted = (
        db.query(models.FabricWork)
        .filter(
            models.FabricWork.fabric_id == fabric_id,
            models.FabricWork.url.in_(candidates),
        )
        .delete(synchronize_session=False)
    )
    db.commit()
    return {"ok": True, "deleted": deleted}
