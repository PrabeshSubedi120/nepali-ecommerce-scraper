import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
from typing import List, Dict
from urllib.parse import urljoin
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import re

class BaseScraper:
    def __init__(self, use_selenium=False):
        self.use_selenium = use_selenium
        if use_selenium:
            self.driver = self._init_selenium()
        else:
            self.session = requests.Session()
            self.ua = UserAgent()
            self.session.headers.update({
                'User-Agent': self.ua.random
            })
        # Add some delays to be respectful to servers
        self.delay_range = (2, 5)
    
    def _init_selenium(self):
        """Initialize Selenium WebDriver"""
        try:
            options = Options()
            options.add_argument('--headless')  # Run in background
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument(f'--user-agent={UserAgent().random}')
            # Suppress logging
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            options.add_experimental_option('useAutomationExtension', False)
            
            driver = webdriver.Chrome(options=options)
            return driver
        except Exception as e:
            print(f"Failed to initialize Selenium: {e}")
            return None
    
    def get_page(self, url: str) -> BeautifulSoup:
        """Fetch and parse a web page"""
        if self.use_selenium and self.driver:
            return self._get_page_selenium(url)
        else:
            return self._get_page_requests(url)
    
    def _get_page_requests(self, url: str) -> BeautifulSoup:
        """Fetch and parse a web page using requests"""
        try:
            # Add random delay to be respectful
            time.sleep(random.uniform(*self.delay_range))
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return None
    
    def _get_page_selenium(self, url: str) -> BeautifulSoup:
        """Fetch and parse a web page using Selenium"""
        try:
            if not self.driver:
                return None
                
            self.driver.get(url)
            # Wait for page to load
            time.sleep(random.uniform(*self.delay_range))
            
            # Wait for basic elements to load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except TimeoutException:
                pass  # Continue even if wait times out
            
            page_source = self.driver.page_source
            return BeautifulSoup(page_source, 'html.parser')
        except Exception as e:
            print(f"Selenium error fetching {url}: {str(e)}")
            return None
    
    def _parse_price(self, price_text: str) -> float:
        """Extract numeric price from text (handles Nepalese price formatting)"""
        if not price_text:
            return 0.0
        
        # Remove currency symbols and extra whitespace
        price_text = price_text.replace('Rs.', '').replace('Rs', '').replace('NPR', '').strip()
        
        # Handle price ranges (take the lower price)
        if '-' in price_text:
            price_text = price_text.split('-')[0].strip()
        
        # Handle the specific formatting issue where extra digits appear after valid price digits
        # For example: "15,9997" should be "15,999" (remove extra "7" at the end)
        # Or "207,00011" should be "207,000" (remove extra "11" at the end)
        if ',' in price_text:
            # Split by comma
            parts = price_text.split(',')
            
            # If we have more than one part, check if the last part might be extra digits
            if len(parts) > 1:
                last_part = parts[-1]
                # If the last part has more than 3 digits, it's likely extra digits
                # In Nepalese format, the part after comma should be 2-3 digits for thousands
                if len(last_part) > 3:
                    # Check if removing the last few digits would make sense
                    # For example, if we have "9997", the extra "7" should be removed
                    # If we have "00011", the extra "11" should be removed
                    
                    # Simple approach: remove the last 1-2 digits if they look like extras
                    if len(last_part) == 4:
                        # "9997" -> "999"
                        parts[-1] = last_part[:-1]
                    elif len(last_part) == 5:
                        # "00011" -> "000"
                        parts[-1] = last_part[:-2]
                    elif len(last_part) == 6:
                        # "999137" -> "999"
                        parts[-1] = last_part[:-3]
            
            # Reconstruct the price text
            price_text = ','.join(parts)
        # If there's no comma but the number is very long, it might also have extra digits
        elif len(price_text) > 6:
            # For very long numbers without commas, try to detect extra digits
            # This is a heuristic - if the last few digits seem like extras, remove them
            if len(price_text) >= 7 and len(price_text) <= 8:
                # For 7-8 digit numbers, check if last 1-2 digits might be extras
                # e.g., "1234567" might be "123456"
                price_text = price_text[:-1]  # Remove last digit as a test
        
        # For Nepalese prices, commas are typically thousand separators
        # Remove all commas
        price_text = price_text.replace(',', '')
        
        try:
            return float(price_text)
        except ValueError:
            return 0.0
    
    def _safe_extract(self, soup, selector: str, attribute: str = None) -> str:
        """Safely extract text or attribute from BeautifulSoup element"""
        try:
            element = soup.select_one(selector)
            if element:
                if attribute:
                    return element.get(attribute, '').strip()
                else:
                    return element.get_text().strip()
            return ''
        except Exception:
            return ''
    
    def close(self):
        """Close any open resources"""
        if self.use_selenium and self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass