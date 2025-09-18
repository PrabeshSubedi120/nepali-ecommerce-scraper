# Usage Guide

## Prerequisites

Make sure you have the required dependencies installed:

```bash
pip install -r requirements.txt
```

For Selenium to work properly, you also need:

1. Chrome browser installed
2. ChromeDriver matching your Chrome version

## Running the Application

### Interactive Mode

```bash
python run.py
```

This will start the interactive CLI where you can enter product names to search for.

### Command Line Search

```bash
python run.py search "smartphone"
```

This will search for "smartphone" on Daraz Nepal and display results.

### Save Results to CSV

```bash
python run.py search "laptop" --output laptop_prices.csv
```

This will search for "laptop" and save the results to a CSV file.

### Using the Original Main Script

```bash
python src/main_scraper.py
```

This also starts the interactive mode.

```bash
python src/main_scraper.py "headphones"
```

This searches for "headphones" and saves results to a CSV file.

## Supported Search Terms

Try these common product categories:

- "smartphone"
- "laptop"
- "headphones"
- "camera"
- "tablet"
- "smartwatch"

## API Mode

To run the API server:

```bash
python run.py api
```

Then access the API documentation at http://127.0.0.1:8000/docs

API endpoints:

- `GET /products/search/{query}` - Search for products
- `GET /products/compare/{query}` - Compare product prices

## Troubleshooting

1. **No products found**: Try different search terms or check your internet connection
2. **Selenium errors**: Make sure Chrome and ChromeDriver are properly installed
3. **Slow performance**: This is intentional to be respectful to websites

## Adding New Sites

To add support for new e-commerce sites:

1. Create a new scraper in `src/scrappers/` following the pattern of existing scrapers
2. Add the scraper to the `scrapers` dictionary in `src/scrappers/scraper_manager.py`
3. Test the new scraper

## Data Storage

Product data is stored in a SQLite database located at `data/products.db`.
You can view this data using any SQLite browser or command-line tool.