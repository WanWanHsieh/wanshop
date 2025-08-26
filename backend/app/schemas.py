from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# ------------ Fabric ------------
class FabricImage(BaseModel):
    id: int
    url: str
    class Config:
        from_attributes = True

class FabricWork(BaseModel):
    id: int
    url: str
    class Config:
        from_attributes = True

class FabricBase(BaseModel):
    name: str
    origin: str = "台灣"
    price: float = 0
    size: str = ""
    description: str = ""
    on_clearance: bool = False
    clearance_price: float = 0

class FabricCreate(FabricBase):
    pass

class FabricUpdate(FabricBase):
    pass

class FabricOut(FabricBase):
    id: int
    created_at: datetime
    images: List[FabricImage] = []
    works: List[FabricWork] = []
    class Config:
        from_attributes = True

# ------------ Category ------------
class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# ------------ Product ------------
class ProductImage(BaseModel):
    id: int
    url: str
    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    name: str
    category_id: int
    price: float = 0
    size: str = ""
    description: str = ""
    promo_price: float = 0

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class ProductOut(ProductBase):
    id: int
    created_at: datetime
    images: List[ProductImage] = []
    class Config:
        from_attributes = True

# ------------ Orders ------------
class OrderItemBase(BaseModel):
    product_id: int
    fabric_id: Optional[int] = None
    state: str = "空白"
    adjustment: float = 0
    description: str = ""

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemUpdate(OrderItemBase):
    pass

class OrderItemOut(OrderItemBase):
    id: int
    original_price: float
    final_price: float
    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    customer_name: str
    description: str = ""
    order_status: str = "尚未處理"
    payment_status: str = "貨到付款"

class OrderCreate(OrderBase):
    items: List[OrderItemCreate] = []

class OrderUpdate(OrderBase):
    pass

class OrderOut(BaseModel):
    id: int
    customer_name: str
    description: str
    order_status: str
    payment_status: str
    created_at: datetime
    items: List[OrderItemOut] = []
    class Config:
        from_attributes = True
