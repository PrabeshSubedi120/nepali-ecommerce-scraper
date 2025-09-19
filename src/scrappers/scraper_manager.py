import time
import pandas as pd
import sys
import os

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict
from scrappers.daraz_scraper import DarazScraper
from database.models import Product
from database.init_db import get_session, init_db

class ScraperManager:
    def __init__(self):
        self._scrapers = {}
        self._scraper_classes = {
            'Daraz': DarazScraper
        }
        self.engine = init_db()
    
    @property
    def scrapers(self):
        """Lazy initialization of scrapers"""
        if not self._scrapers:
            for name, scraper_class in self._scraper_classes.items():
                self._scrapers[name] = scraper_class()
        return self._scrapers
    
    def search_all_sites(self, query: str) -> List[Dict]:
        """Search for products across all sites"""
        all_products = []
        
        for site_name, scraper in self.scrapers.items():
            print(f"Searching {site_name} for '{query}'...")
            try:
                products = scraper.search_products(query)
                all_products.extend(products)
                print(f"Found {len(products)} products on {site_name}")
                # Be respectful to servers by adding a delay
                time.sleep(2)
            except Exception as e:
                print(f"Error searching {site_name}: {str(e)}")
                continue
        
        return all_products
    
    def save_products_to_db(self, products: List[Dict]):
        """Save products to database"""
        session = get_session(self.engine)
        
        try:
            for product_data in products:
                # Check if product already exists
                existing = session.query(Product).filter_by(
                    name=product_data['name'],
                    site=product_data['site'],
                    price=product_data['price']
                ).first()
                
                if not existing:
                    product = Product(**product_data)
                    session.add(product)
            
            session.commit()
            print(f"Saved {len(products)} products to database")
        except Exception as e:
            session.rollback()
            print(f"Error saving products to database: {str(e)}")
        finally:
            session.close()
    
    def compare_products(self, query: str) -> pd.DataFrame:
        """Search for products and return a comparison DataFrame"""
        products = self.search_all_sites(query)
        
        if not products:
            print("No products found!")
            return pd.DataFrame()
        
        # Save to database
        self.save_products_to_db(products)
        
        # Create DataFrame for comparison
        df = pd.DataFrame(products)
        
        # Sort by price
        df = df.sort_values('price')
        
        return df
    
    def get_product_details_from_all_sites(self, product_urls: List[str]) -> List[Dict]:
        """Get detailed information for specific products"""
        details = []
        
        # Group URLs by site
        urls_by_site = {}
        for url in product_urls:
            for site_name, scraper in self.scrapers.items():
                if site_name.lower() in url.lower():
                    if site_name not in urls_by_site:
                        urls_by_site[site_name] = []
                    urls_by_site[site_name].append(url)
                    break
        
        # Get details from each site
        for site_name, urls in urls_by_site.items():
            scraper = self.scrapers[site_name]
            for url in urls:
                try:
                    detail = scraper.get_product_details(url)
                    if detail:
                        details.append(detail)
                    time.sleep(1)  # Be respectful
                except Exception as e:
                    print(f"Error getting details from {site_name}: {str(e)}")
                    continue
        
        return details
    
    def close(self):
        """Close all scraper resources"""
        for scraper in self.scrapers.values():
            try:
                scraper.close()
            except Exception:
                pass