#!/usr/bin/env python3
"""
Run the Electronics Price Tracker Web App
"""

import subprocess
import sys
import os

def main():
    """Run the Streamlit web application"""
    try:
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Path to the web app
        web_app_path = os.path.join(script_dir, 'src', 'web_app.py')
        
        # Run the Streamlit app
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', web_app_path
        ], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"Error running the web app: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nWeb app stopped.")
        sys.exit(0)

if __name__ == "__main__":
    main()