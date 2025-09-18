import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

def init_db():
    """Initialize the database and create tables if they don't exist"""
    # Create data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Database setup
    db_path = os.path.join(data_dir, 'products.db')
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    
    return engine

def get_session(engine):
    """Create a database session"""
    Session = sessionmaker(bind=engine)
    return Session()

if __name__ == "__main__":
    engine = init_db()
    print("Database initialized successfully!")
    print(f"Database path: {os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'products.db')}")