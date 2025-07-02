from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DB_URL
from database.models import Base

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
