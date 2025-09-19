import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrappers.scraper_manager import ScraperManager
from src.utils.data_processor import format_price

# Set page config
st.set_page_config(
    page_title="Nepal Electronics Price Tracker",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Main background and text colors */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Header styling */
    .header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    /* Card styling */
    .product-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    
    /* Price styling */
    .price-tag {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 1.2rem;
        display: inline-block;
    }
    
    /* Site badge styling */
    .site-badge {
        background-color: #e9ecef;
        color: #495057;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
    }
    
    /* Progress bar styling */
    .stProgress > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Metric styling */
    [data-testid="metric-container"] {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="header">
    <h1>📱 Nepal Electronics Price Tracker</h1>
    <p>Compare prices of electronics across Nepalese e-commerce platforms</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'search_results' not in st.session_state:
    st.session_state.search_results = None
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

# Sidebar
with st.sidebar:
    st.header("🔍 Search")
    search_query = st.text_input("Enter product name:", value=st.session_state.search_query)
    
    if st.button("🔍 Search Products", use_container_width=True):
        if search_query:
            st.session_state.search_query = search_query
            with st.spinner("Searching for products... This may take a moment."):
                try:
                    scraper_manager = ScraperManager()
                    df = scraper_manager.compare_products(search_query)
                    st.session_state.search_results = df
                    scraper_manager.close()
                except Exception as e:
                    st.error(f"Error occurred while searching: {str(e)}")
        else:
            st.warning("Please enter a product name to search.")
    
    st.markdown("---")
    st.header("ℹ️ About")
    st.markdown("""
    This tool helps you compare prices of electronics across 
    various Nepalese e-commerce platforms, starting with Daraz Nepal.
    
    **Features:**
    - Real-time price comparison
    - Accurate price parsing for Nepalese Rupees
    - Clean and intuitive interface
    """)
    
    st.markdown("---")
    st.markdown("Made with ❤️ by Prabesh Subedi")

# Main content
if st.session_state.search_results is not None and not st.session_state.search_results.empty:
    df = st.session_state.search_results
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Products", len(df))
    
    with col2:
        st.metric("Lowest Price", format_price(df['price'].min()))
    
    with col3:
        st.metric("Highest Price", format_price(df['price'].max()))
    
    with col4:
        avg_price = df['price'].mean()
        st.metric("Average Price", format_price(avg_price))
    
    # Display products
    st.markdown("### 📊 Price Comparison Results")
    
    # Sort options
    sort_option = st.selectbox(
        "Sort by:",
        ["Price (Low to High)", "Price (High to Low)", "Name (A-Z)"],
        key="sort_option"
    )
    
    # Sort the dataframe
    if sort_option == "Price (Low to High)":
        df_sorted = df.sort_values('price')
    elif sort_option == "Price (High to Low)":
        df_sorted = df.sort_values('price', ascending=False)
    else:
        df_sorted = df.sort_values('name')
    
    # Display products in a grid
    for idx, row in df_sorted.iterrows():
        with st.container():
            st.markdown(f"""
            <div class="product-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <h3 style="margin: 0 0 0.5rem 0;">{row['name']}</h3>
                        <div class="price-tag">{format_price(row['price'])}</div>
                        <div style="margin: 1rem 0;">
                            <span class="site-badge">{row['site']}</span>
                        </div>
                    </div>
                    <div>
                        <a href="{row['url']}" target="_blank" style="text-decoration: none;">
                            <button style="background: #28a745; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; cursor: pointer;">
                                View on Site
                            </button>
                        </a>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Export option
    st.markdown("---")
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("💾 Export to CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"price_comparison_{search_query.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
else:
    # Welcome message
    st.markdown("""
    ### 🎯 How to Use This Tool
    
    1. **Enter a product name** in the search box (e.g., "iPhone 15", "Samsung Galaxy", "Laptop")
    2. **Click "Search Products"** to compare prices across platforms
    3. **View results** sorted by price or name
    4. **Click "View on Site"** to go directly to the product page
    
    ### 📱 Supported Platforms
    
    - **Daraz Nepal** - Currently the primary platform
    
    ### 💡 Tips
    
    - Use specific product names for better results
    - Try searching for "iPhone", "Samsung", "Laptop", etc.
    - Results are updated in real-time from the e-commerce sites
    """)
    
    # Example searches
    st.markdown("### 🔍 Popular Searches")
    example_col1, example_col2, example_col3 = st.columns(3)
    
    with example_col1:
        if st.button("iPhone 15", use_container_width=True):
            st.session_state.search_query = "iPhone 15"
            st.experimental_rerun()
    
    with example_col2:
        if st.button("Samsung Galaxy", use_container_width=True):
            st.session_state.search_query = "Samsung Galaxy"
            st.experimental_rerun()
    
    with example_col3:
        if st.button("Gaming Laptop", use_container_width=True):
            st.session_state.search_query = "Gaming Laptop"
            st.experimental_rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6c757d;">
    <p>Prices are fetched in real-time from e-commerce platforms. Results may vary based on availability.</p>
    <p>Nepal Electronics Price Tracker &copy; 2025</p>
</div>
""", unsafe_allow_html=True)