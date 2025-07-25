# بخش: فایل‌های زیرساختی
# فایل: db.py

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import logger
import os
from datetime import datetime

# Validate DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.error("DATABASE_URL environment variable is not set.")
    raise EnvironmentError("DATABASE_URL environment variable is not set.")

# Replace 'postgres://' with 'postgresql://' for SQLAlchemy compatibility
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create SQLAlchemy engine
try:
    engine = create_engine(DATABASE_URL, echo=False)
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    raise

# Create base class for models
Base = declarative_base()

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True, nullable=False)  # Telegram user ID
    first_name = Column(String, nullable=True)
    family_name = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    email = Column(String, nullable=True)
    field_of_study = Column(String, nullable=True)
    country = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User(user_id={self.user_id}, first_name={self.first_name})>"

def init_db():
    """Initialize the database by creating all tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

def get_db():
    """Provide a database session and ensure it is closed."""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

# Initialize database at startup
init_db()
