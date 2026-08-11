from fastapi import status
from sqlalchemy import Column, Integer, String
from .database import Base

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