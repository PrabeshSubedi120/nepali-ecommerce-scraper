#!/usr/bin/env python3
"""
Electronics Price Tracker
This script compares prices of electronics products across multiple Nepalese e-commerce sites.
"""

import sys
import argparse
import pandas as pd
import os

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrappers.scraper_manager import ScraperManager

def main():
    parser = argparse.ArgumentParser(description='Electronics Price Tracker')
    parser.add_argument('product', nargs='?', help='Product to search for')
    parser.add_argument('--compare', action='store_true', help='Compare prices across sites')
    
    args = parser.parse_args()
    
    # Initialize scraper manager
    scraper_manager = ScraperManager()
    
    try:
        if args.product:
            print(f"Searching for: {args.product}")
            df = scraper_manager.compare_products(args.product)
            
            if not df.empty:
                print("\nPrice Comparison:")
                print("=" * 80)
                print(df[['name', 'price', 'site']].to_string(index=False))
                
                # Save to CSV
                filename = f"{args.product.replace(' ', '_')}_comparison.csv"
                df.to_csv(filename, index=False)
                print(f"\nResults saved to {filename}")
            else:
                print("No products found!")
        else:
            # Interactive mode
            print("Electronics Price Tracker")
            print("=" * 30)
            while True:
                product = input("\nEnter product name to search (or 'quit' to exit): ")
                if product.lower() == 'quit':
                    break
                
                df = scraper_manager.compare_products(product)
                
                if not df.empty:
                    print("\nPrice Comparison (sorted by price):")
                    print("=" * 80)
                    print(df[['name', 'price', 'site']].head(10).to_string(index=False))
                    
                    # Save to CSV
                    filename = f"{product.replace(' ', '_')}_comparison.csv"
                    df.to_csv(filename, index=False)
                    print(f"\nResults saved to {filename}")
                else:
                    print("No products found!")
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        scraper_manager.close()

if __name__ == "__main__":
    main()