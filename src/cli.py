import argparse
import sys
import os

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrappers.scraper_manager import ScraperManager
from utils.data_processor import generate_price_comparison_report, format_price
import pandas as pd

def search_command(args):
    """Handle the search command"""
    scraper_manager = ScraperManager()
    try:
        print(f"Searching for '{args.query}' across all sites...")
        df = scraper_manager.compare_products(args.query)
        
        if df.empty:
            print("No products found!")
            return
        
        # Display results
        print(f"\nFound {len(df)} products:")
        print("=" * 80)
        
        # Show top 10 cheapest products
        df_sorted = df.sort_values('price').head(10)
        for idx, (_, product) in enumerate(df_sorted.iterrows()):
            print(f"{idx+1}. {product['name'][:50]}...")
            print(f"   Price: {format_price(product['price'])} | Site: {product['site']}")
            print(f"   URL: {product['url']}")
            print()
        
        # Save to file if requested
        if args.output:
            df.to_csv(args.output, index=False)
            print(f"Results saved to {args.output}")
    except Exception as e:
        print(f"Error during search: {e}")
    finally:
        scraper_manager.close()

def compare_command(args):
    """Handle the compare command"""
    scraper_manager = ScraperManager()
    try:
        print(f"Comparing prices for '{args.query}'...")
        df = scraper_manager.compare_products(args.query)
        
        if df.empty:
            print("No products found!")
            return
        
        # Generate report
        report = generate_price_comparison_report(df)
        
        print("\nPrice Comparison Report:")
        print("=" * 40)
        print(f"Total products found: {report['total_products']}")
        print(f"Sites searched: {', '.join(report['sites'])}")
        print(f"Lowest price: {format_price(report['price_stats']['min_price'])}")
        print(f"Highest price: {format_price(report['price_stats']['max_price'])}")
        print(f"Average price: {format_price(report['price_stats']['avg_price'])}")
        
        # Show price by site
        print("\nProducts per site:")
        for site, count in report['products_by_site'].items():
            avg_price = df[df['site'] == site]['price'].mean()
            print(f"  {site}: {count} products (avg: {format_price(avg_price)})")
    except Exception as e:
        print(f"Error during comparison: {e}")
    finally:
        scraper_manager.close()

def interactive_mode():
    """Run in interactive mode"""
    scraper_manager = ScraperManager()
    try:
        print("Electronics Price Tracker - Interactive Mode")
        print("=" * 50)
        print("Enter 'quit' to exit")
        
        while True:
            query = input("\nEnter product to search: ")
            if query.lower() == 'quit':
                break
            
            df = scraper_manager.compare_products(query)
            
            if df.empty:
                print("No products found!")
                continue
            
            # Show best deals
            print(f"\nBest deals for '{query}':")
            print("=" * 40)
            df_sorted = df.sort_values('price').head(5)
            
            for idx, (_, product) in enumerate(df_sorted.iterrows()):
                print(f"{idx+1}. {product['name'][:60]}...")
                print(f"   {format_price(product['price'])} | {product['site']}")
                print()
    except Exception as e:
        print(f"Error in interactive mode: {e}")
    finally:
        scraper_manager.close()

def main():
    parser = argparse.ArgumentParser(description='Electronics Price Tracker')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for products')
    search_parser.add_argument('query', help='Product to search for')
    search_parser.add_argument('-o', '--output', help='Output CSV file')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare prices for a product')
    compare_parser.add_argument('query', help='Product to compare')
    
    args = parser.parse_args()
    
    if args.command == 'search':
        search_command(args)
    elif args.command == 'compare':
        compare_command(args)
    else:
        interactive_mode()

if __name__ == "__main__":
    main()