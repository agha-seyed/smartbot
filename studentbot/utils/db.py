from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    family_name = Column(String)
    age = Column(Integer)
    email = Column(String, unique=True, index=True)
    field_of_study = Column(String)
    country = Column(String)
    registration_date = Column(DateTime, default=datetime.utcnow)

class Consultation(Base):
    __tablename__ = "consultations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    name = Column(String)
    field = Column(String)
    degree = Column(String)
    destination = Column(String)
    language_level = Column(String)
    question = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")

class Gamification(Base):
    __tablename__ = "gamification"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True)
    points = Column(Integer, default=0)
    badges = Column(String, default="")

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_user(user_data):
    db = next(get_db())
    db_user = User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def save_consultation(consultation_data):
    db = next(get_db())
    db_consultation = Consultation(**consultation_data)
    db.add(db_consultation)
    db.commit()
    db.refresh(db_consultation)
    return db_consultation

def get_all_users():
    db = next(get_db())
    return db.query(User).all()
