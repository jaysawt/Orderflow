from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    outlet_name = Column(String, index=True, nullable=False)
    location = Column(String, nullable=False)
    status = Column(Integer, nullable=False, default=1, server_default='1')

class Beverage(Base):
    __tablename__ = "beverages"

    id = Column(Integer, primary_key=True, index=True)
    product_brand = Column(String, index=True, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    order_name = Column(String, unique=True, index=True, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    status = Column(Integer, nullable=False, default=0, server_default='0')  # 0="pending" | 1="delivered"
    grand_total = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    client = relationship("Client")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    beverage_id = Column(Integer, ForeignKey("beverages.id"), nullable=False)
    mrp = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    cases = Column(Integer, nullable=False)
    discount = Column(Numeric(10, 2), default=0)
    total_price = Column(Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")
    beverage = relationship("Beverage")
