import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from preprocessing import engine  # Import the same engine

def compute_rfm(df):
    """Helper to compute RFM metrics for analysis"""
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    reference_date = df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
    
    rfm = df.groupby('customer_unique_id').agg({
        'order_id': 'nunique',
        'order_purchase_timestamp': lambda x: (reference_date - x.max()).days,
        'price': 'sum'
    }).rename(columns={
        'order_id': 'frequency',
        'order_purchase_timestamp': 'recency',
        'price': 'monetary'
    })
    return rfm

def run_eda():
    # 1. Pull the cleaned data
    df = pd.read_sql("SELECT * FROM master_cleaned", engine)
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    
    # Compute RFM for segmentation-focused analysis
    rfm = compute_rfm(df)

    # Set the visual style
    sns.set_theme(style="whitegrid")
    
    # Create a larger figure with 6 subplots
    fig = plt.figure(figsize=(16, 18))

    # --- Plot 1: Top 10 Product Categories ---
    plt.subplot(3, 2, 1)
    top_categories = df['category'].value_counts().head(10)
    sns.barplot(x=top_categories.values, y=top_categories.index, palette='viridis')
    plt.title('Top 10 Product Categories by Volume', fontsize=12, fontweight='bold')
    plt.xlabel('Number of Orders')

    # --- Plot 2: Monthly Sales Trend ---
    plt.subplot(3, 2, 2)
    df['month_year'] = df['order_purchase_timestamp'].dt.to_period('M').astype(str)
    monthly_sales = df.groupby('month_year')['price'].sum().reset_index()
    sns.lineplot(data=monthly_sales, x='month_year', y='price', marker='o', color='teal', linewidth=2)
    plt.xticks(rotation=45)
    plt.title('Total Monthly Revenue Over Time', fontsize=12, fontweight='bold')
    plt.ylabel('Revenue ($)')

    # --- Plot 3: Recency Distribution (Days since last purchase) ---
    plt.subplot(3, 2, 3)
    sns.histplot(rfm['recency'], bins=50, kde=True, color='orange')
    plt.title('Customer Recency Distribution (Days Since Last Purchase)', fontsize=12, fontweight='bold')
    plt.xlabel('Recency (days)')

    # --- Plot 4: Monetary Distribution (Customer Lifetime Value) ---
    plt.subplot(3, 2, 4)
    sns.histplot(rfm['monetary'], bins=50, kde=True, color='purple')
    plt.xscale('log')
    plt.title('Customer Monetary Distribution (Log Scale)', fontsize=12, fontweight='bold')
    plt.xlabel('Total Spend ($)')

    # --- Plot 5: Frequency Distribution (Purchase Behavior) ---
    plt.subplot(3, 2, 5)
    sns.histplot(rfm['frequency'], bins=30, kde=True, color='green')
    plt.title('Customer Purchase Frequency Distribution', fontsize=12, fontweight='bold')
    plt.xlabel('Number of Orders')
    plt.ylabel('Number of Customers')

    # --- Plot 6: Recency vs Monetary Scatter (Segmentation Preview) ---
    plt.subplot(3, 2, 6)
    # Sample if dataset is large to avoid overplotting
    sample_size = min(5000, len(rfm))
    rfm_sample = rfm.sample(n=sample_size, random_state=42)
    scatter = plt.scatter(rfm_sample['recency'], rfm_sample['monetary'], 
                         c=rfm_sample['frequency'], cmap='coolwarm', alpha=0.6, s=50)
    plt.colorbar(scatter, label='Frequency')
    plt.title('Recency vs Monetary (colored by Frequency)', fontsize=12, fontweight='bold')
    plt.xlabel('Recency (days)')
    plt.ylabel('Monetary ($)')
    plt.yscale('log')

    plt.tight_layout()
    plt.savefig('eda_report.png', dpi=150, bbox_inches='tight')
    print("EDA Report saved as eda_report.png!")
    plt.show()

def run_detailed_eda():
    """Extended EDA with more statistical insights"""
    df = pd.read_sql("SELECT * FROM master_cleaned", engine)
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    
    rfm = compute_rfm(df)
    
    print("\n" + "="*60)
    print("EXPLORATORY DATA ANALYSIS SUMMARY")
    print("="*60)
    
    print("\n--- DATASET OVERVIEW ---")
    print(f"Total Orders: {len(df):,}")
    print(f"Unique Customers: {df['customer_unique_id'].nunique():,}")
    print(f"Unique Products: {df['product_id'].nunique():,}")
    print(f"Date Range: {df['order_purchase_timestamp'].min().date()} to {df['order_purchase_timestamp'].max().date()}")
    
    print("\n--- RFM STATISTICS ---")
    print(rfm[['recency', 'frequency', 'monetary']].describe())
    
    print("\n--- CATEGORICAL INSIGHTS ---")
    print(f"Top 5 Categories:")
    print(df['category'].value_counts().head())
    
    print(f"\nMissing Values:")
    print(df.isnull().sum())
    
    print("\n--- CORRELATION ANALYSIS (RFM) ---")
    print(rfm[['recency', 'frequency', 'monetary']].corr())
    
    print("\n" + "="*60)

def check_multicollinearity():
    """
    Check for multicollinearity in numerical features.
    If correlation > 0.85, features may overshadow each other in clustering.
    """
    print("\n" + "="*60)
    print("MULTICOLLINEARITY CHECK")
    print("="*60)
    
    df = pd.read_sql("SELECT * FROM master_cleaned", engine)
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    
    rfm = compute_rfm(df)
    
    # Add average order value
    aov = df.groupby('customer_unique_id')['price'].mean()
    rfm['avg_order_value'] = aov
    
    # Calculate correlation matrix
    corr_matrix = rfm[['recency', 'frequency', 'monetary', 'avg_order_value']].corr()
    
    print("\nCorrelation Matrix:")
    print(corr_matrix)
    
    # Visualize
    plt.figure(figsize=(8, 6))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", square=True, cbar_kws={"shrink": 0.8})
    plt.title('Feature Correlation Heatmap (Multicollinearity Check)', fontweight='bold')
    plt.tight_layout()
    plt.savefig('correlation_heatmap.png', dpi=150, bbox_inches='tight')
    print("\nCorrelation heatmap saved as correlation_heatmap.png")
    
    # Flag high correlations
    print("\n⚠️  High Correlations (> 0.85):")
    flagged = False
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            if abs(corr_matrix.iloc[i, j]) > 0.85:
                print(f"   {corr_matrix.columns[i]} <-> {corr_matrix.columns[j]}: {corr_matrix.iloc[i, j]:.3f}")
                flagged = True
    if not flagged:
        print("   ✓ No high correlations detected. Features are suitable for clustering.")

if __name__ == "__main__":
    # Generate visualizations
    run_eda()
    
    # Print detailed statistical summary
    run_detailed_eda()
    
    # Check for multicollinearity
    check_multicollinearity()