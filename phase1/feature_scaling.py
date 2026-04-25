import pandas as pd
import numpy as np
import json
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from sklearn.cluster import KMeans
from preprocessing import engine

def apply_log_transformation(df):
    """Apply log1p transformation to handle right-skewed distributions."""
    print("\n--- Log Transformation (Step 1: Handle Skewness) ---")
    
    # Identify continuous features to transform
    continuous_features = ['num_orders', 'monetary', 'avg_order_value', 
                          'total_items_bought', 'avg_item_price', 'recency']
    
    # Log transform: log1p(x) = log(1+x) handles zeros gracefully
    for col in continuous_features:
        df[f'log_{col}'] = np.log1p(df[col])
    
    print(f"[OK] Log-transformed {len(continuous_features)} continuous features")
    print(f"  Features: {', '.join(continuous_features)}")
    return df

def scale_features_robust(df):
    """Scale features using RobustScaler (median-based, outlier-resistant)."""
    print("\n--- Feature Scaling (Step 2: Normalize Scales) ---")
    
    # Select log-transformed features to scale
    log_features = [col for col in df.columns if col.startswith('log_')]
    
    # RobustScaler: median=0, IQR=1 (ignores outliers beyond Q1/Q3)
    scaler = RobustScaler()
    scaled_data = scaler.fit_transform(df[log_features])
    
    # Save scaled features back to dataframe
    for i, col in enumerate(log_features):
        df[f'{col}_scaled'] = scaled_data[:, i]
    
    print(f"[OK] RobustScaler applied to {len(log_features)} log-transformed features")
    print(f"\n  Data ranges: Monetary ${df['monetary'].min():.2f}->${df['monetary'].max():.2f}, Recency {df['recency'].min()}->{df['recency'].max()} days")
    
    return df, scaler, log_features

def prepare_kmeans_dataset(df):
    """Prepare numerical-only dataset for K-Means (baseline comparison)."""
    print("\n--- Dataset A: K-Means Ready (Numerical Only) ---")
    
    kmeans_features = [col for col in df.columns if col.endswith('_scaled')]
    clustering_kmeans = df[kmeans_features].copy()
    
    print(f"[OK] K-Means dataset: {clustering_kmeans.shape}")
    print(f"  Features: {len(kmeans_features)} (all continuous, log+scaled)")
    print(f"  Limitation: Ignores categorical (recency_quartile, preferred_category, customer_state)")
    print(f"  Use for: Baseline comparison only")
    
    return clustering_kmeans

def prepare_kprototype_dataset(df):
    """Prepare mixed-type dataset for K-Prototype (primary approach)."""
    print("\n--- Dataset B: K-Prototype Ready (Mixed-Type) [PRIMARY] ---")
    
    # Numerical features (scaled, log-transformed)
    numerical_features = [col for col in df.columns if col.endswith('_scaled')]
    
    # Categorical features (keep original)
    categorical_features = ['recency_quartile', 'preferred_category', 'customer_state']
    
    kprototype_features = numerical_features + categorical_features
    clustering_kprototype = df[kprototype_features].copy()
    
    print(f"[OK] K-Prototype dataset: {clustering_kprototype.shape}")
    print(f"  Numerical features: {len(numerical_features)} (log-transformed + scaled)")
    print(f"  Categorical features: {len(categorical_features)}")
    print(f"  Advantage: Captures both spending patterns AND customer preferences")
    print(f"  Note: Requires kmodes.KPrototypes (not sklearn)")
    
    return clustering_kprototype

def prepare_gower_dataset(df):
    """Prepare mixed-type dataset for K-Medoids with Gower distance (robust alternative)."""
    print("\n--- Dataset C: K-Medoids + Gower Distance (Mixed-Type, Robust) [SECONDARY] ---")
    
    # For K-Medoids, use ORIGINAL (not scaled) features + categorical
    # Gower distance will handle mixed-type scaling internally
    
    gower_features = ['num_orders', 'monetary', 'avg_order_value', 'total_items_bought',
                     'avg_item_price', 'recency',  # Continuous (original scale)
                     'recency_quartile', 'preferred_category', 'customer_state']  # Categorical
    
    clustering_gower = df[gower_features].copy()
    
    print(f"[OK] K-Medoids dataset: {clustering_gower.shape}")
    print(f"  Numerical features: 6 (ORIGINAL scale, not log-transformed)")
    print(f"  Categorical features: 3")
    print(f"  Distance metric: Gower (handles mixed-type naturally)")
    print(f"  Advantage: Centroid is actual customer (interpretable)")
    print(f"  Disadvantage: O(n²) computationally expensive")
    
    return clustering_gower

def test_kmeans_elbow_curve(data_kmeans):
    """Elbow method: find K where inertia gains diminish."""
    print("\n" + "="*80)
    print("TEST 1: K-MEANS ELBOW METHOD")
    print("="*80)
    print("-" * 80)
    
    inertias = []
    k_range = list(range(2, 11))
    
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(data_kmeans)
        inertias.append(kmeans.inertia_)
        print(f"K={k:2d}  | Inertia: {kmeans.inertia_:12.2f}")
    

    
    return k_range, inertias

def test_silhouette_score(data_kmeans, k_values=[2,3,4,5,6,7,8], sample_size=10000):
    """Silhouette score: measure cluster coherence (sample-based for efficiency)."""
    print("\n" + "="*80)
    print("TEST 2: SILHOUETTE SCORE (SAMPLED)")
    print("="*80)
    print(f"NOTE: Using sample n={sample_size:,} for efficiency")
    print("-" * 80)
    
    # Stratified sample for efficiency
    np.random.seed(42)
    sample_indices = np.random.choice(len(data_kmeans), size=min(sample_size, len(data_kmeans)), replace=False)
    data_sample = data_kmeans.iloc[sample_indices]
    
    silhouette_scores = []
    
    for k in k_values:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(data_sample)
        score = silhouette_score(data_sample, labels)
        silhouette_scores.append(score)
        
        quality = "EXCELLENT" if score > 0.5 else "GOOD" if score > 0.3 else "POOR"
        print(f"K={k}  | Silhouette Score: {score:.4f}  [{quality}]")
    
    best_k = k_values[np.argmax(silhouette_scores)]
    print(f"\n[BEST] Best K by Silhouette: {best_k} (score: {max(silhouette_scores):.4f})")
    
    return k_values, silhouette_scores, best_k

def test_davies_bouldin_index(data_kmeans, k_values=[2,3,4,5,6,7,8], sample_size=10000):
    """Davies-Bouldin index: measure cluster separation (sample-based, lower is better)."""
    print("\n" + "="*80)
    print("TEST 3: DAVIES-BOULDIN INDEX (SAMPLED, Lower is Better)")
    print("="*80)
    print(f"NOTE: Using sample n={sample_size:,} for efficiency")
    print("-" * 80)
    
    # Stratified sample for efficiency
    np.random.seed(42)
    sample_indices = np.random.choice(len(data_kmeans), size=min(sample_size, len(data_kmeans)), replace=False)
    data_sample = data_kmeans.iloc[sample_indices]
    
    db_scores = []
    
    for k in k_values:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(data_sample)
        score = davies_bouldin_score(data_sample, labels)
        db_scores.append(score)
        
        quality = "EXCELLENT" if score < 0.5 else "GOOD" if score < 1.0 else "POOR"
        print(f"K={k}  | Davies-Bouldin: {score:.4f}  [{quality}]")
    
    best_k = k_values[np.argmin(db_scores)]
    print(f"\n[BEST] Best K by Davies-Bouldin: {best_k} (score: {min(db_scores):.4f})")
    
    return k_values, db_scores, best_k

def test_calinski_harabasz_index(data_kmeans, k_values=[2,3,4,5,6,7,8], sample_size=10000):
    """Calinski-Harabasz index: F-statistic-like metric (sample-based, higher is better)."""
    print("\n" + "="*80)
    print("TEST 4: CALINSKI-HARABASZ INDEX (SAMPLED, Higher is Better)")
    print("="*80)
    print(f"NOTE: Using sample n={sample_size:,} for efficiency")
    print("-" * 80)
    
    # Stratified sample for efficiency
    np.random.seed(42)
    sample_indices = np.random.choice(len(data_kmeans), size=min(sample_size, len(data_kmeans)), replace=False)
    data_sample = data_kmeans.iloc[sample_indices]
    
    ch_scores = []
    
    for k in k_values:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(data_sample)
        score = calinski_harabasz_score(data_sample, labels)
        ch_scores.append(score)
        
        print(f"K={k}  | Calinski-Harabasz: {score:.4f}")
    
    best_k = k_values[np.argmax(ch_scores)]
    print(f"\n[BEST] Best K by Calinski-Harabasz: {best_k} (score: {max(ch_scores):.4f})")
    
    return k_values, ch_scores, best_k

def save_scaling_summary(scaler, log_features, k_test_results):
    """
    Save scaling summary and test results for reproducibility.
    """
    print("\n--- Saving Feature Scaling Summary ---")
    
    summary = {
        'scaling_method': 'RobustScaler (median=0, IQR=1)',
        'why_robust': 'Data has extreme outliers in monetary (right-skewed)',
        'log_transformed_features': log_features,
        'categorical_features': ['recency_quartile', 'preferred_category', 'customer_state'],
        'binary_features': ['is_repeat_customer', 'is_high_value', 'is_sp'],
        'test_results': k_test_results
    }
    
    with open('data/feature_scaling_summary.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print("[OK] Saved scaling summary to data/feature_scaling_summary.json")

def main():
    print("="*80)
    print("PHASE 1 -> PHASE 3 BRIDGE: FEATURE SCALING + ALGORITHM SELECTION")
    print("="*80)
    
    # 1. Load engineered features
    print("\n1. Loading engineered features from Phase 1...")
    df = pd.read_sql("SELECT * FROM customer_features", engine)
    print(f"   [OK] Loaded {len(df):,} customers with {df.shape[1]} features")
    
    # 2. Log transform
    df = apply_log_transformation(df)
    
    # 3. Scale features
    df_scaled, scaler, log_features = scale_features_robust(df)
    
    # 4. Prepare datasets
    print("\n--- Preparing Datasets ---")
    data_kmeans = prepare_kmeans_dataset(df_scaled)
    data_kprototype = prepare_kprototype_dataset(df_scaled)
    data_gower = prepare_gower_dataset(df_scaled)
    
    # 5. Save datasets to CSV and PostgreSQL
    print("\n--- Saving Datasets ---")
    data_kmeans.to_csv('data/customer_features_kmeans.csv', index=True)
    data_kmeans.to_sql('customer_features_kmeans', engine, if_exists='replace', index=True)
    print("[OK] K-Means dataset saved")
    
    data_kprototype.to_csv('data/customer_features_kprototype.csv', index=True)
    data_kprototype.to_sql('customer_features_kprototype', engine, if_exists='replace', index=True)
    print("[OK] K-Prototype dataset saved")
    
    data_gower.to_csv('data/customer_features_gower.csv', index=True)
    data_gower.to_sql('customer_features_gower', engine, if_exists='replace', index=True)
    print("[OK] K-Medoids (Gower) dataset saved")
    
    # 6. RUN EVALUATION TESTS
    print("\n" + "="*80)
    print("RUNNING EVALUATION TESTS FOR TA PRESENTATION")
    print("="*80)
    
    k_test_results = {}
    
    # Test 1: Elbow curve
    k_range, inertias = test_kmeans_elbow_curve(data_kmeans)
    k_test_results['elbow_inertias'] = {k: float(inertia) for k, inertia in zip(k_range, inertias)}
    
    # Test 2: Silhouette score
    k_values, silhouette_scores, best_k_silhouette = test_silhouette_score(data_kmeans)
    k_test_results['silhouette_scores'] = {k: float(score) for k, score in zip(k_values, silhouette_scores)}
    k_test_results['best_k_silhouette'] = int(best_k_silhouette)
    
    # Test 3: Davies-Bouldin index
    k_values, db_scores, best_k_db = test_davies_bouldin_index(data_kmeans)
    k_test_results['davies_bouldin_scores'] = {k: float(score) for k, score in zip(k_values, db_scores)}
    k_test_results['best_k_davies_bouldin'] = int(best_k_db)
    
    # Test 4: Calinski-Harabasz index
    k_values, ch_scores, best_k_ch = test_calinski_harabasz_index(data_kmeans)
    k_test_results['calinski_harabasz_scores'] = {k: float(score) for k, score in zip(k_values, ch_scores)}
    k_test_results['best_k_calinski_harabasz'] = int(best_k_ch)
    
    # 7. Save results
    save_scaling_summary(scaler, log_features, k_test_results)
    
    # 8. Summary
    print("\n" + "="*80)
    print("FEATURE SCALING COMPLETE - READY FOR PHASE 3")
    print("="*80)
    print(f"\nDatasets: K-Means {data_kmeans.shape} | K-Prototype {data_kprototype.shape} | K-Medoids {data_gower.shape}")
    print(f"Recommendations: Silhouette K={best_k_silhouette} | DB Index K={best_k_db} | CH Index K={best_k_ch}")
    print(f"Best K range: {{3, 4, 5, 6}} (test with K-PROTOTYPE)")
    print("="*80)

if __name__ == "__main__":
    main()

