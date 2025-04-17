from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging

# Get logger
logger = logging.getLogger(__name__)

# Get database URL from environment
logger.info("Starting database configuration")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/taxiapp")
logger.info("Database connection configured")

# Create engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import all models here 
from models.user_model import Base

# Create base model for declarative class definitions
def init_db():
    """Initialize database tables"""
    try:
        # Create all tables in the database
        logger.info("Creating database tables")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created")
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        raise

def get_db():
    """Get a database session."""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close() 