import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, RobustScaler
from preprocessing import engine

def apply_log_transformation(df):
    """
    Apply log transformation to skewed numerical features.
    Log transform helps normalize highly skewed distributions (e.g., spending).
    """
    print("\n--- Log Transformation ---")
    
    # Log transform for right-skewed features (add 1 to handle zeros)
    df['log_recency'] = np.log1p(df['recency'])
    df['log_frequency'] = np.log1p(df['frequency'])
    df['log_monetary'] = np.log1p(df['monetary'])
    df['log_avg_order_value'] = np.log1p(df['avg_order_value'])
    df['log_value_per_order'] = np.log1p(df['value_per_order'])
    
    print("✓ Log-transformed features created (log_recency, log_frequency, log_monetary, etc.)")
    return df

def scale_features(df, method='standard'):
    """
    Standardize numerical features for clustering.
    StandardScaler: Mean 0, SD 1 (works well if no outliers)
    RobustScaler: Median 0, uses IQR (robust to outliers)
    """
    print(f"\n--- Feature Scaling ({method.upper()}) ---")
    
    # Select features to scale
    features_to_scale = [
        'log_recency', 'log_frequency', 'log_monetary', 
        'log_avg_order_value', 'log_value_per_order', 'category_diversity'
    ]
    
    if method == 'standard':
        scaler = StandardScaler()
    elif method == 'robust':
        scaler = RobustScaler()
    else:
        raise ValueError("method must be 'standard' or 'robust'")
    
    # Fit and transform
    scaled_data = scaler.fit_transform(df[features_to_scale])
    
    # Create new dataframe with scaled features
    scaled_df = df.copy()
    for i, col in enumerate(features_to_scale):
        scaled_df[f'{col}_scaled'] = scaled_data[:, i]
    
    print(f"✓ {len(features_to_scale)} features scaled using {method} scaler")
    print(f"  Scaled features: {', '.join([f'{col}_scaled' for col in features_to_scale])}")
    
    return scaled_df, scaler

def prepare_clustering_dataset(df):
    """
    Full pipeline: Log transform + Scale + Create clustering-ready dataset.
    Output: Both numerical (for K-Means) and mixed-type (for K-Prototypes).
    """
    print("\n" + "="*70)
    print("PREPARING DATA FOR CLUSTERING (Phase 3)")
    print("="*70)
    
    # Step 1: Log Transform
    df = apply_log_transformation(df)
    
    # Step 2: Scale using Robust Scaler (better for potential outliers)
    df_scaled, scaler = scale_features(df, method='robust')
    
    # Step 3: Create two datasets for different clustering approaches
    
    # Dataset A: Pure numerical (for K-Means)
    kmeans_features = [
        'log_recency_scaled', 'log_frequency_scaled', 'log_monetary_scaled',
        'log_avg_order_value_scaled', 'log_value_per_order_scaled', 'category_diversity_scaled'
    ]
    clustering_numerical = df_scaled[kmeans_features].copy()
    
    # Dataset B: Mixed-type (for K-Prototypes, if needed)
    kprototypes_features = kmeans_features + ['preferred_category', 'recency_quartile', 'monetary_quartile']
    clustering_mixed = df_scaled[kprototypes_features].copy()
    
    print("\n✓ Clustering datasets prepared:")
    print(f"  - K-Means ready: {clustering_numerical.shape} (numerical only)")
    print(f"  - K-Prototypes ready: {clustering_mixed.shape} (numerical + categorical)")
    
    return clustering_numerical, clustering_mixed, df_scaled

def save_clustering_data(numerical_df, mixed_df, full_df):
    """
    Save all three datasets to PostgreSQL for Phase 3.
    """
    print("\n--- Saving Clustering Datasets to PostgreSQL ---")
    
    # Save numerical (K-Means ready)
    numerical_df.to_sql('customer_features_kmeans', engine, if_exists='replace', index=True)
    numerical_df.to_csv('data/customer_features_kmeans.csv', index=True)
    print("✓ Saved K-Means ready features → 'customer_features_kmeans' table")
    
    # Save mixed-type (K-Prototypes ready)
    mixed_df.to_sql('customer_features_kprototypes', engine, if_exists='replace', index=True)
    mixed_df.to_csv('data/customer_features_kprototypes.csv', index=True)
    print("✓ Saved K-Prototypes ready features → 'customer_features_kprototypes' table")
    
    # Save full dataset (with both raw + scaled + log-transformed)
    full_df.to_sql('customer_features_full', engine, if_exists='replace', index=True)
    full_df.to_csv('data/customer_features_full.csv', index=True)
    print("✓ Saved full feature set → 'customer_features_full' table")

if __name__ == "__main__":
    # 1. Load customer features from Phase 1
    print("Loading customer features...")
    customer_features = pd.read_sql("SELECT * FROM customer_features", engine, index_col='customer_unique_id')
    
    # 2. Prepare clustering data
    numerical_clf, mixed_clf, full_features = prepare_clustering_dataset(customer_features)
    
    # 3. Save for Phase 3
    save_clustering_data(numerical_clf, mixed_clf, full_features)
    
    # 4. Display summary
    print("\n" + "="*70)
    print("FEATURE SCALING COMPLETE")
    print("="*70)
    print("\nFirst 5 rows (K-Means features):")
    print(numerical_clf.head())
    print(f"\nShape: {numerical_clf.shape}")
    print(f"\nFeature statistics (K-Means):")
    print(numerical_clf.describe())
    print("\n✓ Ready for Phase 3: Customer Segmentation (K-Means / K-Prototypes)")
