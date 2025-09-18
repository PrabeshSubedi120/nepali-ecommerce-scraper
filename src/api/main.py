import sys
import os

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from typing import List, Dict
from scrappers.scraper_manager import ScraperManager
from database.models import Product
from database.init_db import get_session, init_db
from pydantic import BaseModel
import pandas as pd

app = FastAPI(title="Electronics Price Tracker API")

# Initialize database and scraper manager
engine = init_db()
scraper_manager = ScraperManager()

class ProductSearchRequest(BaseModel):
    query: str
    limit: int = 10

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    currency: str
    site: str
    url: str
    image_url: str = None
    brand: str = None
    category: str = None

@app.get("/")
async def root():
    return {"message": "Electronics Price Tracker API"}

@app.get("/products/search/{query}")
async def search_products(query: str, limit: int = 10):
    """Search for products across all sites"""
    try:
        products = scraper_manager.search_all_sites(query)
        # Save to database
        scraper_manager.save_products_to_db(products)
        
        # Return limited results
        return {"query": query, "products": products[:limit]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products/compare/{query}")
async def compare_products(query: str):
    """Compare prices for a product across sites"""
    try:
        df = scraper_manager.compare_products(query)
        
        if df.empty:
            return {"query": query, "products": [], "message": "No products found"}
        
        # Convert to dict format
        products = df.to_dict('records')
        
        # Generate summary
        summary = {
            "total_products": len(products),
            "sites": df['site'].unique().tolist(),
            "price_range": {
                "min": float(df['price'].min()),
                "max": float(df['price'].max()),
                "average": float(df['price'].mean())
            }
        }
        
        return {
            "query": query,
            "products": products,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))