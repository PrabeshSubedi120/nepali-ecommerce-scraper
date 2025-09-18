import pandas as pd
from typing import List, Dict

def normalize_product_names(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize product names to improve matching"""
    df_copy = df.copy()
    
    # Convert to lowercase
    df_copy['name_normalized'] = df_copy['name'].str.lower()
    
    # Remove common words that don't affect product identity
    common_words = ['new', 'latest', 'official', 'original', 'brand', 'nepal', 'nepali']
    for word in common_words:
        df_copy['name_normalized'] = df_copy['name_normalized'].str.replace(word, '', case=False)
    
    # Remove extra spaces
    df_copy['name_normalized'] = df_copy['name_normalized'].str.strip()
    
    return df_copy

def find_similar_products(df: pd.DataFrame, threshold: float = 0.8) -> List[Dict]:
    """
    Find similar products across different sites based on name similarity
    This is a simplified version - in practice, you might want to use more sophisticated
    string matching algorithms or ML-based similarity detection
    """
    # This is a placeholder implementation
    # In a real implementation, you would use techniques like:
    # - Fuzzy string matching (difflib, fuzzywuzzy)
    # - Text embedding similarity
    # - Clustering algorithms
    
    similar_products = []
    
    # For now, we'll just group by simplified name
    df_normalized = normalize_product_names(df)
    
    # Group by normalized name
    grouped = df_normalized.groupby('name_normalized')
    
    for name, group in grouped:
        if len(group) > 1:  # Found similar products
            similar_products.append({
                'product_name': name,
                'count': len(group),
                'sites': group['site'].tolist(),
                'prices': group['price'].tolist()
            })
    
    return similar_products

def generate_price_comparison_report(df: pd.DataFrame) -> Dict:
    """Generate a summary report of price comparisons"""
    if df.empty:
        return {}
    
    report = {
        'total_products': len(df),
        'sites': df['site'].unique().tolist(),
        'price_stats': {
            'min_price': df['price'].min(),
            'max_price': df['price'].max(),
            'avg_price': df['price'].mean(),
            'median_price': df['price'].median()
        },
        'products_by_site': df['site'].value_counts().to_dict()
    }
    
    return report

def format_price(price: float) -> str:
    """Format price for display"""
    return f"Rs. {price:,.2f}"