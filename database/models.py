from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)  
    name = Column(String(50), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)
    interests = Column(String(255), nullable=True)
    city = Column(String(50), nullable=True)
    is_premium = Column(Boolean, default=False)
    vip_until = Column(DateTime, nullable=True)
    telegram_username = Column(String(50), nullable=True)
    notify_likes = Column(Boolean, default=True)
    notify_matches = Column(Boolean, default=True)
    is_hidden = Column(Boolean, default=False)
