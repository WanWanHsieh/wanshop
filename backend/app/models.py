from sqlalchemy import String, Integer, Float, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base
from datetime import datetime

class Fabric(Base):
    __tablename__ = "fabrics"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    origin: Mapped[str] = mapped_column(String(50), default="台灣")
    price: Mapped[float] = mapped_column(Float, default=0)
    size: Mapped[str] = mapped_column(String(100), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    on_clearance: Mapped[bool] = mapped_column(Boolean, default=False)
    clearance_price: Mapped[float] = mapped_column(Float, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    images: Mapped[list["FabricImage"]] = relationship(back_populates="fabric", cascade="all, delete-orphan")
    works: Mapped[list["FabricWork"]] = relationship(back_populates="fabric", cascade="all, delete-orphan")

class FabricImage(Base):
    __tablename__ = "fabric_images"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fabric_id: Mapped[int] = mapped_column(ForeignKey("fabrics.id", ondelete="CASCADE"))
    url: Mapped[str] = mapped_column(String(500))
    fabric: Mapped["Fabric"] = relationship(back_populates="images")

class FabricWork(Base):
    __tablename__ = "fabric_works"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fabric_id: Mapped[int] = mapped_column(ForeignKey("fabrics.id", ondelete="CASCADE"))
    url: Mapped[str] = mapped_column(String(500))
    fabric: Mapped["Fabric"] = relationship(back_populates="works")

class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    products: Mapped[list["Product"]] = relationship(back_populates="category", cascade="all, delete-orphan")

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    price: Mapped[float] = mapped_column(Float, default=0)
    size: Mapped[str] = mapped_column(String(100), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    promo_price: Mapped[float] = mapped_column(Float, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    category: Mapped["Category"] = relationship(back_populates="products")

    images: Mapped[list["ProductImage"]] = relationship(back_populates="product", cascade="all, delete-orphan")

class ProductImage(Base):
    __tablename__ = "product_images"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    url: Mapped[str] = mapped_column(String(500))
    product: Mapped["Product"] = relationship(back_populates="images")

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    order_status: Mapped[str] = mapped_column(String(50), default="尚未處理")
    payment_status: Mapped[str] = mapped_column(String(50), default="貨到付款")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    items: Mapped[list["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    fabric_id: Mapped[int | None] = mapped_column(ForeignKey("fabrics.id"), nullable=True)

    state: Mapped[str] = mapped_column(String(50), default="空白")
    original_price: Mapped[float] = mapped_column(Float, default=0)
    adjustment: Mapped[float] = mapped_column(Float, default=0)  # +50 or -100
    final_price: Mapped[float] = mapped_column(Float, default=0)
    description: Mapped[str] = mapped_column(Text, default="")

    order: Mapped["Order"] = relationship(back_populates="items")
