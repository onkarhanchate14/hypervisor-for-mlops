from sqlalchemy import create_engine, text
from app.core.config import settings
from app.db.base import Base

def reset_database():
    """Drop all tables and recreate them"""
    engine = create_engine(settings.DATABASE_URL)
    
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("Database reset completed successfully!")

if __name__ == "__main__":
    reset_database() 