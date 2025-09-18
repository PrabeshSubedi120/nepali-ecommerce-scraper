# Electronics Price Tracker

A web scraping tool to compare electronics prices across multiple Nepalese e-commerce sites.

## Features

- Scrapes product information from Daraz Nepal
- Compares prices for the same or similar products
- Provides both CLI and API interfaces
- Exports comparison results to CSV
- Uses Selenium for better handling of JavaScript-heavy sites

## Supported Sites

1. Daraz Nepal (https://www.daraz.com.np) - **Working**

## Prerequisites

1. Python 3.7+
2. Chrome browser (for Selenium)
3. ChromeDriver (matching your Chrome version)

## Installation

1. Clone the repository:

   ```
   git clone <repository-url>
   cd electronics_price_tracker
   ```

2. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Install ChromeDriver:
   - Download from https://chromedriver.chromium.org/
   - Add to your system PATH

## Usage

### Interactive Mode

```
python run.py
```

### Command Line Search

```
python run.py search "iPhone 15"
```

### Compare Prices

```
python run.py compare "Samsung Galaxy S24"
```

### API Mode

```
python run.py api
```

Access the API documentation at http://127.0.0.1:8000/docs

See [USAGE.md](USAGE.md) for detailed usage instructions.

## Project Structure

```
electronics_price_tracker/
├── src/
│   ├── scrappers/
│   │   ├── base_scraper.py
│   │   └── daraz_scraper.py
│   ├── database/
│   │   ├── models.py
│   │   └── init_db.py
│   ├── utils/
│   │   └── data_processor.py
│   ├── api/
│   │   └── main.py
│   ├── cli.py
│   └── main_scraper.py
├── tests/
├── requirements.txt
├── README.md
└── USAGE.md
```

## Troubleshooting

1. **No products found**: Try different search terms or check your internet connection
2. **Selenium errors**: Make sure Chrome and ChromeDriver are properly installed
3. **Slow performance**: This is intentional to be respectful to websites

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

This project is licensed under the MIT License.