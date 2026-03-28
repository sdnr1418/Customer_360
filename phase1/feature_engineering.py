import pandas as pd
import numpy as np
from datetime import datetime
from preprocessing import engine

def engineer_rfm_features(df):
    """
    Construct RFM (Recency, Frequency, Monetary) metrics per customer.
    These are crucial for Phase 3 (Customer Segmentation).
    """
    print("\n--- Engineering RFM Features ---")
    
    # Convert timestamp to datetime
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    
    # Reference date: max date in dataset + 1 day (to ensure all customers have positive recency)
    reference_date = df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
    
    # Group by customer
    rfm_data = df.groupby('customer_unique_id').agg({
        'order_id': 'nunique',  # Frequency: number of orders
        'order_purchase_timestamp': lambda x: (reference_date - x.max()).days,  # Recency: days since last purchase
        'price': 'sum'  # Monetary: total spending
    }).rename(columns={
        'order_id': 'frequency',
        'order_purchase_timestamp': 'recency',
        'price': 'monetary'
    })
    
    print(f"RFM computed for {len(rfm_data)} unique customers")
    return rfm_data

def engineer_customer_profile_features(df):
    """
    Augment RFM with behavioral and geographic features.
    Useful for mixed-type clustering (K-Prototypes) with continuous + categorical.
    """
    print("\n--- Engineering Customer Profile Features ---")
    
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    
    # Start with RFM
    customer_features = engineer_rfm_features(df)
    
    # 1. Average order value (AOV)
    aov = df.groupby('customer_unique_id')['price'].mean().rename('avg_order_value')
    customer_features = customer_features.join(aov)
    
    # 2. Number of unique product categories purchased
    category_diversity = df.groupby('customer_unique_id')['category'].nunique().rename('category_diversity')
    customer_features = customer_features.join(category_diversity)
    
    # 3. Most frequent category purchased (for categorical clustering)
    most_bought_category = df.groupby('customer_unique_id')['category'].agg(lambda x: x.value_counts().index[0]).rename('preferred_category')
    customer_features = customer_features.join(most_bought_category)
    
    # 4. State (geographic feature)
    # Note: You may need to join with the customers table if state info is separate
    # For now, we'll assume state is available via a merge with customers
    
    # 5. Recency quartile (easier to interpret than raw recency)
    customer_features['recency_quartile'] = pd.qcut(customer_features['recency'], q=4, labels=['recent', 'moderate', 'older', 'inactive'], duplicates='drop')
    
    # 6. Monetary quartile (Low, Medium, High, Very High spenders)
    customer_features['monetary_quartile'] = pd.qcut(customer_features['monetary'], q=4, labels=['low', 'medium', 'high', 'very_high'], duplicates='drop')
    
    # 7. Value-to-frequency ratio (spending per order)
    customer_features['value_per_order'] = customer_features['monetary'] / customer_features['frequency']
    
    print(f"Customer profile features engineered: {customer_features.shape[1]} features")
    return customer_features

def save_engineered_features(df):
    """
    Persist engineered features to a new Postgres table for Phase 3.
    """
    print("\nSaving engineered features to PostgreSQL...")
    df.to_sql('customer_features', engine, if_exists='replace', index=True)
    
    # Also save locally for quick reference
    df.to_csv('data/customer_features.csv', index=True)
    print("Saved features to data/customer_features.csv")

if __name__ == "__main__":
    # 1. Pull cleaned data from Postgres
    print("Loading cleaned data...")
    cleaned_df = pd.read_sql("SELECT * FROM master_cleaned", engine)
    
    # 2. Engineer features
    customer_features = engineer_customer_profile_features(cleaned_df)
    
    # 3. Save
    save_engineered_features(customer_features)
    
    # 4. Display summary
    print("\n--- Feature Engineering Complete ---")
    print(customer_features.head())
    print("\nFeature Summary:")
    print(customer_features.describe())