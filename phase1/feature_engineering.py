import pandas as pd
import numpy as np
import json
from datetime import datetime
from preprocessing import engine

def get_top_categories(df, top_n=15):
    """
    Get the top N categories by frequency.
    Returns list of top categories; all others will be binned as 'others'.
    Note: Increased from 10 to 15 to retain more category information for Phase 2 analysis
    """
    top_cats = df['category'].value_counts().head(top_n).index.tolist()
    return top_cats

def engineer_customer_features(df):
    """
    Engineer customer segmentation features from cleaned transaction data.
    
    Approach: Instead of traditional RFM (ineffective with 97% one-time buyers),
    focus on PURCHASE BEHAVIOR features that discriminate:
    - Monetary value (spending power)
    - Purchase behavior (repeat vs one-time, order frequency)
    - Category preferences (what they buy)
    - Geographic location (regional clustering - full state + SP flag)
    - Recency (purchase timing patterns)
    
    P0 Priority Fixes (for Phase 4 Integration):
    - Keep customer_unique_id as explicit column (traceability)
    - Keep full customer_state (regional segmentation in Phase 3)
    - Keep num_orders as feature (frequency variance, not binary)
    
    P1 Priority Fixes (for Phase 3 quality):
    - Increase top_n categories from 10→15 (Phase 2 association mining)
    - Add recency_quartile (purchase timing patterns)
    """
    print("\n--- Engineering Customer Features (Purchase Behavior Focus) ---")
    
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    
    # Get top 15 categories for binning (increased from 10 for Phase 2)
    top_categories = get_top_categories(df, top_n=15)
    print(f"Top categories retained: {len(top_categories)} (increased from 10 for Phase 2 analysis)")
    
    # Calculate reference date for recency (same as original RFM approach)
    reference_date = df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
    
    # Calculate monetary thresholds from data
    monetary_95th = df.groupby('customer_unique_id')['price'].sum().quantile(0.95)
    print(f"High-value threshold (95th percentile): ${monetary_95th:.2f}")
    
    # Save threshold for reproducibility (P1 fix)
    threshold_metadata = {
        'timestamp': datetime.now().isoformat(),
        'high_value_threshold_95th': float(monetary_95th),
        'top_n_categories': len(top_categories),
        'reference_date': reference_date.isoformat() # max date in dataset
    }
    with open('data/feature_engineering_metadata.json', 'w') as f:
        json.dump(threshold_metadata, f, indent=2)
    print(f"✓ Saved feature engineering metadata to data/feature_engineering_metadata.json")
    
    # Aggregate by customer - include recency calculation
    customer_agg = df.groupby('customer_unique_id').agg({
        'order_id': 'nunique',                                          # Number of orders
        'price': ['sum', 'mean', 'count'],                              # Spending metrics
        'category': lambda x: x.value_counts().index[0],                # Most frequent category
        'order_purchase_timestamp': lambda x: (reference_date - x.max()).days,  # Recency: days since last purchase
    })
    
    # Flatten column names
    customer_agg.columns = ['num_orders', 'monetary', 'avg_item_price', 'total_items_bought', 'preferred_category', 'recency']
    
    # Get customer state (from customers table via SQL)
    customer_state_query = "SELECT DISTINCT customer_unique_id, customer_state FROM customers"
    customer_state = pd.read_sql(customer_state_query, engine)
    customer_agg = customer_agg.join(customer_state.set_index('customer_unique_id')['customer_state'])
    
    # Preserve customer_unique_id as explicit column for Phase 4 traceability (P0 fix)
    customer_agg['customer_unique_id'] = customer_agg.index
    
    # ===== FEATURE ENGINEERING =====
    
    # 1. NUM_ORDERS (continuous) — P0 FIX
    # Why: Frequency variance (not binary); captures bulk buyers vs one-timers
    # Phase 3: Better segmentation (frequency not just repeat flag)
    # Phase 4: Order pattern traceability
    customer_agg['num_orders'] = customer_agg['num_orders']
    
    # 2. MONETARY (continuous)
    # Why: Spending power directly discriminates high-value vs budget customers
    customer_agg['monetary'] = customer_agg['monetary']
    
    # 3. AVG_ORDER_VALUE (continuous)
    # Why: Average transaction size; complements monetary (interpretable even if correlated)
    customer_agg['avg_order_value'] = customer_agg['monetary'] / customer_agg['num_orders']
    
    # 4. TOTAL_ITEMS_BOUGHT (continuous)
    # Why: Purchase volume; discriminates bulk buyers from cherry-pickers
    customer_agg['total_items_bought'] = customer_agg['total_items_bought']
    
    # 5. AVG_ITEM_PRICE (continuous)
    # Why: Price sensitivity indicator; high avg_item_price suggests premium buyer
    customer_agg['avg_item_price'] = customer_agg['avg_item_price']
    
    # 6. RECENCY (continuous) — P1 FIX
    # Why: Purchase timing patterns; captures "active" vs "dormant" customers
    # Phase 3: Temporal clustering can identify engaged vs inactive segments
    customer_agg['recency'] = customer_agg['recency']
    
    # 7. RECENCY_QUARTILE (categorical) — P1 FIX
    # Why: Bin recency into interpretable tiers for clustering
    # Phase 3: Mixed-type clustering (K-Prototypes) can leverage categorical tier
    customer_agg['recency_quartile'] = pd.qcut(
        customer_agg['recency'], 
        q=4, 
        labels=['very_recent', 'recent', 'older', 'inactive'],
        duplicates='drop'
    )
    
    # 8. IS_REPEAT_CUSTOMER (binary: 0/1)
    # Why: Only 3.1% are repeat buyers; strong behavioral signal for loyalty potential
    customer_agg['is_repeat_customer'] = (customer_agg['num_orders'] > 1).astype(int)
    
    # 9. IS_HIGH_VALUE (binary: 0/1)
    # Why: Top 5% spenders (high-value segment) warrant separate treatment; outliers matter
    customer_agg['is_high_value'] = (customer_agg['monetary'] >= monetary_95th).astype(int)
    
    # 10. PREFERRED_CATEGORY (categorical)
    # Why: What customer buys reveals lifestyle/needs; bin top 15 (increased from 10), rest='others'
    # Phase 2: Top 15 retains more categories for association analysis
    customer_agg['preferred_category'] = customer_agg['preferred_category'].apply(
        lambda x: x if x in top_categories else 'others'
    )
    
    # 11. CUSTOMER_STATE (categorical) — P0 FIX
    # Why: Keep full geographic detail (not just SP binary)
    # Phase 3: Regional clustering can identify South vs Northeast vs Center patterns
    # Phase 4: Segment-specific geographic insights
    customer_agg['customer_state'] = customer_agg['customer_state']
    
    # 12. IS_SP (binary: 0/1)
    # Why: Geographic clustering; São Paulo dominates (40.8%), strong regional patterns
    customer_agg['is_sp'] = (customer_agg['customer_state'] == 'SP').astype(int)
    
    # ===== CLEANUP =====
    
    # Keep all engineered features (P0+P1 fixes included)
    final_features = ['customer_unique_id', 'num_orders', 'monetary', 'avg_order_value', 
                      'total_items_bought', 'avg_item_price', 'recency', 'recency_quartile',
                      'is_repeat_customer', 'is_high_value', 'preferred_category', 
                      'customer_state', 'is_sp']
    
    customer_agg = customer_agg[final_features]
    
    print(f"\n✓ Features engineered for {len(customer_agg)} unique customers")
    print(f"✓ Feature set: {customer_agg.shape[1]} features (P0+P1 fixes applied)")
    print(f"✓ Continuous features: num_orders, monetary, avg_order_value, total_items_bought, avg_item_price, recency")
    print(f"✓ Categorical features: recency_quartile, preferred_category (top 15), customer_state")
    print(f"✓ Binary flags: is_repeat_customer, is_high_value, is_sp")
    print(f"✓ High-value customers (top 5%): {customer_agg['is_high_value'].sum():,}")
    print(f"✓ Repeat customers: {customer_agg['is_repeat_customer'].sum():,}")
    print(f"✓ São Paulo customers: {customer_agg['is_sp'].sum():,}")
    
    return customer_agg

def save_engineered_features(df):
    """
    Persist engineered features to PostgreSQL and CSV for Phase 3/4.
    Ensures customer_unique_id is preserved as index for traceability (P0 fix).
    """
    print("\n--- Saving Engineered Features ---")
    
    # Set customer_unique_id as index for CSV/database (P0 traceability)
    df_indexed = df.set_index('customer_unique_id')
    
    df_indexed.to_sql('customer_features', engine, if_exists='replace', index=True)
    df_indexed.to_csv('data/customer_features.csv', index=True)
    print("✓ Saved to PostgreSQL table 'customer_features' (with customer_unique_id index)")
    print("✓ Saved to data/customer_features.csv (with customer_unique_id index)")
    print("✓ Metadata saved to data/feature_engineering_metadata.json")

if __name__ == "__main__":
    # 1. Load cleaned data
    print("Loading cleaned data from PostgreSQL...")
    cleaned_df = pd.read_sql("SELECT * FROM master_cleaned", engine)
    print(f"   → Loaded {len(cleaned_df):,} transaction records")
    
    # 2. Engineer features
    customer_features = engineer_customer_features(cleaned_df)
    
    # 3. Save
    save_engineered_features(customer_features)
    
    # 4. Display summary
    print("\n--- Feature Engineering Complete ---")
    print("\nFirst 10 customers (with all features):")
    print(customer_features.head(10))
    print("\n--- Continuous Features Summary ---")
    continuous_cols = ['num_orders', 'monetary', 'avg_order_value', 'total_items_bought', 'avg_item_price', 'recency']
    print(customer_features[continuous_cols].describe())
    print("\n--- Categorical Features Distribution ---")
    print(f"\nRecency Quartiles:")
    print(customer_features['recency_quartile'].value_counts().sort_index())
    print(f"\nPreferred Category Distribution (Top 15 + others):")
    print(customer_features['preferred_category'].value_counts())
    print(f"\nCustomer State Distribution:")
    print(customer_features['customer_state'].value_counts())
    print(f"\nBinary Flags Summary:")
    print(f"  is_repeat_customer: {customer_features['is_repeat_customer'].sum():,} ({customer_features['is_repeat_customer'].mean()*100:.1f}%)")
    print(f"  is_high_value: {customer_features['is_high_value'].sum():,} ({customer_features['is_high_value'].mean()*100:.1f}%)")
    print(f"  is_sp: {customer_features['is_sp'].sum():,} ({customer_features['is_sp'].mean()*100:.1f}%)")