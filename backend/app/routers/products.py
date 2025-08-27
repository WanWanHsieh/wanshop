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


@router.get("/", response_model=List[schemas.ProductOut])
def list_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()


@router.post("/", response_model=schemas.ProductOut)
def create_product(data: schemas.ProductCreate, db: Session = Depends(get_db)):
    if not db.get(models.Category, data.category_id):
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
def update_product(
    product_id: int, data: schemas.ProductUpdate, db: Session = Depends(get_db)
):
    obj = db.get(models.Product, product_id)
    if not obj:
        raise HTTPException(404, "Product not found")

    payload = data.model_dump()
    images_urls = payload.pop("images_urls", None)

    # 更新基本欄位
    for k, v in payload.items():
        setattr(obj, k, v)
    db.commit()

    # 有帶清單才處理
    if images_urls is not None:
        cur = [
            r[0]
            for r in db.query(models.ProductImage.url)
            .filter(models.ProductImage.product_id == product_id)
            .order_by(models.ProductImage.id.asc())
            .all()
        ]
        if cur != images_urls:
            db.query(models.ProductImage).filter(
                models.ProductImage.product_id == product_id
            ).delete(synchronize_session=False)
            seen = set()
            for u in images_urls or []:
                if u in seen:
                    continue
                seen.add(u)
                db.add(models.ProductImage(product_id=product_id, url=u))
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


# 新增（冪等）
@router.post("/{product_id}/images")
def add_product_images(
    product_id: int, urls: List[str] = Body(...), db: Session = Depends(get_db)
):
    obj = db.get(models.Product, product_id)
    if not obj:
        raise HTTPException(404, "Product not found")
    exists = {
        r[0]
        for r in db.query(models.ProductImage.url)
        .filter(models.ProductImage.product_id == product_id)
        .all()
    }
    ins = 0
    for u in urls or []:
        if u in exists:
            continue
        db.add(models.ProductImage(product_id=product_id, url=u))
        ins += 1
    db.commit()
    db.refresh(obj)
    return {"ok": True, "inserted": ins, "skipped": len((urls or [])) - ins}


# 取代（全刪再建）
@router.put("/{product_id}/images")
def replace_product_images(
    product_id: int, urls: List[str] = Body(...), db: Session = Depends(get_db)
):
    obj = db.get(models.Product, product_id)
    if not obj:
        raise HTTPException(404, "Product not found")
    db.query(models.ProductImage).filter(
        models.ProductImage.product_id == product_id
    ).delete(synchronize_session=False)
    seen = set()
    for u in urls or []:
        if u in seen:
            continue
        seen.add(u)
        db.add(models.ProductImage(product_id=product_id, url=u))
    db.commit()
    db.refresh(obj)
    return {"ok": True, "count": len(seen)}


# 刪除（支援絕對或相對 URL）
@router.delete("/{product_id}/images")
def delete_product_images(
    product_id: int,
    url: Optional[str] = None,
    urls: Optional[List[str]] = Body(None),
    db: Session = Depends(get_db),
):
    obj = db.get(models.Product, product_id)
    if not obj:
        raise HTTPException(404, "Product not found")
    targets = list(filter(None, (urls or []))) + ([url] if url else [])
    if not targets:
        raise HTTPException(400, "Missing url or urls")
    candidates = list(dict.fromkeys(_normalize_urls(targets) + targets))
    deleted = (
        db.query(models.ProductImage)
        .filter(
            models.ProductImage.product_id == product_id,
            models.ProductImage.url.in_(candidates),
        )
        .delete(synchronize_session=False)
    )
    db.commit()
    return {"ok": True, "deleted": deleted}
