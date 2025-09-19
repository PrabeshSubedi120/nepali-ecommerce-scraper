#!/usr/bin/env python3
"""
Main entry point for the Electronics Price Tracker application
"""

import sys
import os

def main():
    # Add src to Python path
    src_path = os.path.join(os.path.dirname(__file__), 'src')
    sys.path.insert(0, src_path)
    
    # Check if user wants to run API or CLI
    if len(sys.argv) > 1 and sys.argv[1] == 'api':
        # Run API server
        import uvicorn
        print("Starting Electronics Price Tracker API...")
        print("Access the API documentation at http://127.0.0.1:8000/docs")
        uvicorn.run("src.api.main:app", host="127.0.0.1", port=8000, reload=True)
    else:
        # Run CLI
        from src.cli import main as cli_main
        cli_main()

if __name__ == "__main__":
    main()