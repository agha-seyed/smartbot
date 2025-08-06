# بخش: زیرساخت
# فایل: db.py

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from studentbot.config import DATABASE_URL
import bcrypt

Base = declarative_base()

from sqlalchemy import Column, Integer, String, create_engine, Float, DateTime, ForeignKey, Boolean
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    first_name = Column(String)
    family_name = Column(String)
    age = Column(Integer)
    email = Column(String)
    field_of_study = Column(String)
    country = Column(String)
    isee = Column(Float)
    points = Column(Integer, default=0)

class Consultation(Base):
    __tablename__ = "consultations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    field = Column(String)
    details = Column(String)
    status = Column(String, default="pending")
    timestamp = Column(DateTime, default=datetime.utcnow)

class MigrationProgress(Base):
    __tablename__ = "migration_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    step = Column(String)
    completed = Column(Boolean, default=False)

class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    def set_password(self, password: str) -> None:
        """
        Hash and set the admin password.
        """
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """
        Check if the provided password matches the stored hash.
        """
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()