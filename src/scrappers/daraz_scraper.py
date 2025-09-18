import time
from typing import List, Dict
from .base_scraper import BaseScraper
import re

class DarazScraper(BaseScraper):
    def __init__(self):
        # Use Selenium for Daraz as it's heavily JavaScript-based
        super().__init__(use_selenium=True)
        self.base_url = "https://www.daraz.com.np"
        self.search_url = "https://www.daraz.com.np/catalog/?q="
        # Remove artificial price limits to allow high-end devices
        # Only keep basic validation to filter out clearly invalid prices
        self.min_price = 100  # Minimum reasonable price for any product
        self.max_price = 5000000  # 50 lakhs, high enough for premium devices
    
    def search_products(self, query: str) -> List[Dict]:
        """Search for products on Daraz"""
        search_url = self.search_url + query.replace(' ', '+')
        soup = self.get_page(search_url)
        
        if not soup:
            return []
        
        products = []
        
        # Look for product items using multiple selectors
        selectors = [
            '[data-qa-locator="product-item"]',
            '.product-card',
            '.c-product-card',
            '.product-item',
            '[data-tracking="product-card"]',
            '.sku-item'
        ]
        
        product_items = []
        for selector in selectors:
            items = soup.select(selector)
            if items:
                product_items.extend(items)
        
        print(f"Daraz: Found {len(product_items)} product items with selectors")
        
        # If we still don't have items, try a more general approach
        if not product_items:
            # Look for any divs with price-like text
            all_divs = soup.find_all('div')
            for div in all_divs:
                text = div.get_text()
                if 'Rs.' in text and len(text) > 10:  # Likely a product container
                    product_items.append(div)
        
        for item in product_items[:15]:  # Limit to first 15 results
            try:
                # Extract name
                name_selectors = [
                    '.title', 
                    '.name', 
                    'h4', 
                    '.product-title',
                    '[title]'
                ]
                
                name = ''
                for selector in name_selectors:
                    name = self._safe_extract(item, selector)
                    if name and len(name) > 3:
                        break
                
                # If still no name, try getting it from title attribute
                if not name:
                    name = item.get('title', '') if item.name == 'a' else ''
                
                # Extract price with better precision
                price = 0.0
                
                # Look for price with specific selectors first
                price_selectors = [
                    '.price', 
                    '.product-price', 
                    '.c-product-card__price',
                    '[data-price]',
                    '.origin-price'
                ]
                
                price_text = ''
                for selector in price_selectors:
                    price_text = self._safe_extract(item, selector)
                    if price_text and ('Rs' in price_text or 'NPR' in price_text):
                        price = self._parse_price(price_text)
                        if price > 0:
                            # Debug: Show what we extracted
                            print(f"DEBUG: Extracted price '{price_text}' -> {price:,.2f}")
                            break
                
                # If no price found with selectors, look in the text content
                if price == 0:
                    item_text = item.get_text()
                    # Look for price patterns
                    price_patterns = [
                        r'Rs\.\s*[\d,]+\.?\d*',
                        r'Rs\s*[\d,]+\.?\d*',
                        r'NPR\s*[\d,]+\.?\d*'
                    ]
                    
                    for pattern in price_patterns:
                        matches = re.findall(pattern, item_text)
                        if matches:
                            # Try each match until we get a valid price
                            for match in matches:
                                price = self._parse_price(match)
                                if price > 0:
                                    # Debug: Show what we extracted
                                    print(f"DEBUG: Pattern match '{match}' -> {price:,.2f}")
                                    break
                            if price > 0:
                                break
                
                # Extract URL
                url_selectors = ['.title', '.name', 'a']
                product_url = ''
                for selector in url_selectors:
                    product_url = self._safe_extract(item, selector, 'href')
                    if product_url:
                        break
                
                # If no URL found, look for any link
                if not product_url:
                    links = item.find_all('a', href=True)
                    if links:
                        product_url = links[0].get('href', '')
                
                if product_url and not product_url.startswith('http'):
                    product_url = 'https:' + product_url if product_url.startswith('//') else self.base_url + product_url
                
                # Validate price is within reasonable range (removed strict limits)
                if name and price >= self.min_price and price <= self.max_price:
                    products.append({
                        'name': name[:150],  # Limit length
                        'price': price,
                        'currency': 'NPR',
                        'site': 'Daraz',
                        'url': product_url,
                        'image_url': '',
                        'brand': '',
                        'category': '',
                        'description': ''
                    })
                elif name and price > 0:
                    print(f"Skipping product '{name[:50]}...' with price Rs. {price:,.2f} (outside reasonable range {self.min_price}-{self.max_price})")
            except Exception as e:
                print(f"Error parsing Daraz product: {str(e)}")
                continue
        
        # Remove duplicates based on name
        seen_names = set()
        unique_products = []
        for product in products:
            if product['name'] not in seen_names:
                seen_names.add(product['name'])
                unique_products.append(product)
        
        print(f"Daraz: Found {len(unique_products)} unique products")
        return unique_products[:15]  # Increase limit to 15 products
    
    def get_product_details(self, url: str) -> Dict:
        """Get detailed information about a specific product on Daraz"""
        soup = self.get_page(url)
        
        if not soup:
            return {}
        
        # Extract basic information
        title = soup.title.string if soup.title else ''
        name = title.replace(' | Daraz Nepal', '').replace(' - Buy Online at Best Price', '') if title else 'Unknown Product'
        
        # Try to find price
        price = 0
        price_elements = soup.find_all(string=lambda text: text and ('Rs.' in text or 'NPR' in text))
        for element in price_elements:
            parsed_price = self._parse_price(element)
            if parsed_price >= self.min_price and parsed_price <= self.max_price:
                price = parsed_price
                break
        
        # If still no price, look for common price selectors
        if price == 0:
            price_selectors = [
                '.pdp-price',
                '.product-price', 
                '.price',
                '[data-price]'
            ]
            
            for selector in price_selectors:
                price_text = self._safe_extract(soup, selector)
                if price_text:
                    parsed_price = self._parse_price(price_text)
                    if parsed_price >= self.min_price and parsed_price <= self.max_price:
                        price = parsed_price
                        break
        
        product = {
            'name': name[:150] if name else 'Unknown Product',
            'price': price,
            'currency': 'NPR',
            'site': 'Daraz',
            'url': url,
            'image_url': '',
            'brand': '',
            'category': '',
            'description': ''
        }
        
        return product
    
    def close(self):
        """Close Selenium driver"""
        super().close()