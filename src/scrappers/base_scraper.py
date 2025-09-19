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
        
        # Remove any non-numeric characters except commas, decimals, and digits
        cleaned_text = re.sub(r'[^\d,.]', '', price_text)
        
        try:
            # If we already have a decimal point, use it as-is
            if '.' in cleaned_text:
                standard_format = cleaned_text.replace(',', '')
                price = float(standard_format)
                if 100 <= price <= 500000:  # Reasonable range for electronics
                    return price
            
            # Handle the specific formatting issue where extra digits appear without decimal points
            # This is for cases like "188200" which should be "1882.00"
            elif len(cleaned_text.replace(',', '')) >= 5:
                # Remove commas to work with the digits
                no_comma_text = cleaned_text.replace(',', '')
                
                # For prices with 5+ digits without decimal points, 
                # the last 2 digits represent paise (cents)
                if len(no_comma_text) >= 5:
                    # Check if the original text had commas
                    if ',' in cleaned_text:
                        # Split by comma to understand the structure
                        parts = cleaned_text.split(',')
                        
                        # For cases like "207,0009", the format is:
                        # The comma is a thousands separator, and the last 2 digits are paise
                        # So "207,0009" means 207,000.09
                        # And "168,7006" means 168,700.06
                        
                        if len(parts) >= 2 and len(parts[-1]) > 3:
                            # The last part has more than 3 digits, so the extra are paise
                            last_part = parts[-1]
                            paise_part = last_part[-2:]  # Last 2 digits are paise
                            
                            # Special handling for 4-digit last parts
                            # The format assumes a 5-digit representation where the first 3 digits 
                            # are the ones part and the last 2 are paise
                            # So "7006" represents "07006" conceptually:
                            # - First 3 digits "700" are the ones
                            # - Last 2 digits "06" are the paise
                            if len(last_part) == 4:
                                # Treat as 5-digit format with implicit leading zero
                                # First 3 digits for ones part
                                rupee_digits = last_part[:3]  # First 3 digits
                            else:
                                # Standard case - all digits except last 2
                                rupee_digits = last_part[:-2]
                            
                            # Reconstruct the full rupee amount
                            # parts[:-1] gives us ['207'] for "207,0009"
                            # rupee_digits gives us "000" for "207,0009"
                            # So we join them to get "207000"
                            rupee_part = ''.join(parts[:-1] + [rupee_digits])
                            
                            # Combine with decimal point
                            if rupee_part and paise_part:
                                candidate_price = float(rupee_part + '.' + paise_part)
                                if 100 <= candidate_price <= 500000:
                                    return candidate_price
                        else:
                            # Standard format with comma as thousand separator
                            standard_format = cleaned_text.replace(',', '')
                            price = float(standard_format)
                            if 100 <= price <= 500000:
                                return price
                    else:
                        # No commas, just split the last 2 digits as paise
                        # Extract the last 2 digits as paise
                        paise_part = no_comma_text[-2:]
                        main_part = no_comma_text[:-2]
                        
                        # Combine with decimal point
                        if main_part and paise_part:
                            candidate_price = float(main_part + '.' + paise_part)
                            
                            # Validate the price is in reasonable range
                            if 100 <= candidate_price <= 500000:
                                return candidate_price
                            else:
                                # If not in range, try treating as a regular number
                                price = float(no_comma_text)
                                if 100 <= price <= 500000:
                                    return price
            
            # If we have a simple number without decimal, try it as-is
            standard_format = cleaned_text.replace(',', '')
            if '.' not in standard_format and len(standard_format) >= 3:
                price = float(standard_format)
                if 100 <= price <= 500000:  # Reasonable range for electronics
                    return price
                    
        except ValueError:
            pass
        
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