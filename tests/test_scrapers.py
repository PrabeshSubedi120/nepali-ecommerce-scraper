import sys
import os
import unittest
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scrappers.base_scraper import BaseScraper
from scrappers.daraz_scraper import DarazScraper
from scrappers.sastodeal_scraper import SastoDealScraper
from scrappers.hamrobazar_scraper import HamroBazarScraper

class TestBaseScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = BaseScraper()
    
    def test_parse_price(self):
        # Test normal price
        self.assertEqual(self.scraper._parse_price("Rs. 1000"), 1000.0)
        self.assertEqual(self.scraper._parse_price("Rs.1,000"), 1000.0)
        self.assertEqual(self.scraper._parse_price("1000"), 1000.0)
        
        # Test price range (should take lower value)
        self.assertEqual(self.scraper._parse_price("Rs. 1000 - 2000"), 1000.0)
        
        # Test invalid price
        self.assertEqual(self.scraper._parse_price("N/A"), 0.0)
        self.assertEqual(self.scraper._parse_price(""), 0.0)

class TestDarazScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = DarazScraper()
    
    def test_init(self):
        self.assertEqual(self.scraper.base_url, "https://www.daraz.com.np")
        self.assertEqual(self.scraper.search_url, "https://www.daraz.com.np/catalog/?q=")

class TestSastoDealScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = SastoDealScraper()
    
    def test_init(self):
        self.assertEqual(self.scraper.base_url, "https://www.sastodeal.com")
        self.assertEqual(self.scraper.search_url, "https://www.sastodeal.com/catalogsearch/result/?q=")

class TestHamroBazarScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = HamroBazarScraper()
    
    def test_init(self):
        self.assertEqual(self.scraper.base_url, "https://hamrobazar.com")
        self.assertEqual(self.scraper.search_url, "https://hamrobazar.com/search?search=")

if __name__ == '__main__':
    unittest.main()