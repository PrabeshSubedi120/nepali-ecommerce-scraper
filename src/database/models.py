from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(500), nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String(10), default='NPR')  # Nepalese Rupee
    site = Column(String(100), nullable=False)  # e.g., 'Daraz', 'SastoDeal'
    url = Column(Text, nullable=False)
    image_url = Column(Text)
    description = Column(Text)
    brand = Column(String(100))
    category = Column(String(100))  # e.g., 'Mobile', 'Laptop'
    scraped_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Product(name='{self.name}', price={self.price}, site='{self.site}')>"