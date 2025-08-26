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

def price_of_product(db: Session, product_id: int) -> float:
    product = db.get(models.Product, product_id)
    if not product:
        raise HTTPException(400, "product_id not found")
    return product.promo_price if product.promo_price and product.promo_price > 0 else product.price

@router.get("/", response_model=List[schemas.OrderOut])
def list_orders(db: Session = Depends(get_db)):
    return db.query(models.Order).all()

@router.post("/", response_model=schemas.OrderOut)
def create_order(data: schemas.OrderCreate, db: Session = Depends(get_db)):
    order = models.Order(
        customer_name=data.customer_name,
        description=data.description,
        order_status=data.order_status,
        payment_status=data.payment_status,
    )
    db.add(order)
    db.flush()

    for it in data.items:
        base_price = price_of_product(db, it.product_id)
        final = base_price + (it.adjustment or 0)
        item = models.OrderItem(
            order_id=order.id,
            product_id=it.product_id,
            fabric_id=it.fabric_id,
            state=it.state,
            original_price=base_price,
            adjustment=it.adjustment or 0,
            final_price=final,
            description=it.description,
        )
        db.add(item)
    db.commit()
    db.refresh(order)
    return order

@router.get("/{order_id}", response_model=schemas.OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.Order, order_id)
    if not obj:
        raise HTTPException(404, "Order not found")
    return obj

@router.put("/{order_id}", response_model=schemas.OrderOut)
def update_order(order_id: int, data: schemas.OrderUpdate, db: Session = Depends(get_db)):
    obj = db.get(models.Order, order_id)
    if not obj:
        raise HTTPException(404, "Order not found")
    for k, v in data.model_dump().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.Order, order_id)
    if not obj:
        raise HTTPException(404, "Order not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}
