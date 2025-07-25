# بخش: زیرساخت
# فایل: db.py

from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
import logging

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True)
    first_name = Column(String)
    family_name = Column(String)
    age = Column(Integer)
    email = Column(String)
    field_of_study = Column(String)
    country = Column(String)
    isee = Column(Float, nullable=True)
    points = Column(Integer, default=0)  # New field for gamification points

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

logging.info("Database initialized successfully")