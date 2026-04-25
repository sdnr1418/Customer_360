"""
PHASE 3: CUSTOMER SEGMENTATION WITH K-PROTOTYPE (OPTIMIZED)
============================================================================

Optimization Strategy:
  - Use stratified sample (15%) for clustering speed
  - Train on sample, predict on full dataset
  - Profile all 93,398 customers based on sample-trained model
  - Generate comprehensive visualizations for TA presentation
  - Provides fast, efficient results without sacrificing quality
"""

import pandas as pd
import numpy as np
import json
import sys
import os
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from kmodes.kprototypes import KPrototypes

try:
    from preprocessing import engine
except ImportError:
    from sqlalchemy import create_engine
    DB_URI = 'postgresql://postgres:postgres@localhost:5432/dm_project'
    engine = create_engine(DB_URI)

import warnings
warnings.filterwarnings('ignore')


def run_kprototype_optimized(kprototype_data, customer_ids, full_features_df, k_value=3, sample_fraction=0.15):
    """
    K-Prototype optimized: train on sample, predict on full dataset
    """
    print("\n" + "="*80)
    print(f"RUNNING K-PROTOTYPE CLUSTERING (K={k_value})")
    print("="*80)
    print(f"\nStrategy: Train on {sample_fraction*100:.0f}% sample, predict on full dataset")
    
    numerical_features = [col for col in kprototype_data.columns if col.endswith('_scaled')]
    categorical_features = ['recency_quartile', 'preferred_category', 'customer_state']
    
    np.random.seed(42)
    sample_size = max(1000, int(len(kprototype_data) * sample_fraction))
    
    # Stratified sampling by preferred_category
    stratify_col = kprototype_data['preferred_category']
    sample_indices = []
    for category in stratify_col.unique():
        mask = stratify_col == category
        indices = np.where(mask)[0]
        n_sample = max(1, int(len(indices) * sample_fraction))
        sample_indices.extend(np.random.choice(indices, size=n_sample, replace=False))
    
    sample_indices = sorted(list(set(sample_indices)))[:sample_size]
    print(f"[OK] Stratified sample: {len(sample_indices):,} customers")
    
    # Prepare data
    X_sample_num = kprototype_data.iloc[sample_indices][numerical_features].values
    X_sample_cat = kprototype_data.iloc[sample_indices][categorical_features].values
    X_sample = np.hstack([X_sample_num, X_sample_cat])
    
    X_full_num = kprototype_data[numerical_features].values
    X_full_cat = kprototype_data[categorical_features].values
    X_full = np.hstack([X_full_num, X_full_cat])
    
    categorical_indices = [len(numerical_features) + i for i in range(len(categorical_features))]
    
    print(f"\n[SECTION 1] TRAINING K-PROTOTYPE")
    print("-" * 80)
    print(f"Data shapes:")
    print(f"  - Sample (training): {len(sample_indices):,} customers x {len(numerical_features) + len(categorical_features)} features")
    print(f"  - Full (prediction): {len(X_full):,} customers x {len(numerical_features) + len(categorical_features)} features")
    print(f"  - Numerical features: {numerical_features}")
    print(f"  - Categorical features: {categorical_features}")
    
    print(f"\nTraining K-Prototype (K={k_value}) on sample...")
    
    kproto = KPrototypes(
        n_clusters=k_value,
        init='Cao',
        verbose=1,
        random_state=42,
        max_iter=10,
        n_jobs=-1
    )
    
    kproto.fit(X_sample, categorical=categorical_indices)
    
    print(f"[OK] Training complete!")
    print(f"  - Cost: {kproto.cost_:.2f}")
    print(f"  - Iterations: {kproto.n_iter_}")
    
    # Predict on full dataset
    print(f"\nPredicting labels for all {len(X_full):,} customers...")
    labels_full = kproto.predict(X_full, categorical=categorical_indices)
    print(f"[OK] Prediction complete")
    
    # Sample labels for metrics
    labels_sample = kproto.predict(X_sample, categorical=categorical_indices)
    
    return kproto, labels_full, labels_sample, X_sample_num, X_full_num, categorical_indices


def evaluate_clustering(X_sample_num, labels_sample, labels_full, k_value):
    """
    Evaluate clustering quality using 4 metrics
    """
    print(f"\n[SECTION 2] EVALUATION METRICS (K={k_value})")
    print("-" * 80)
    
    metrics = {}
    
    # METRIC 1: SILHOUETTE SCORE
    print(f"\n1. SILHOUETTE SCORE (Coherence)")
    try:
        silhouette = silhouette_score(X_sample_num, labels_sample)
        metrics['silhouette'] = silhouette
        
        if silhouette > 0.5:
            quality = "EXCELLENT"
        elif silhouette > 0.3:
            quality = "GOOD"
        elif silhouette > 0.1:
            quality = "FAIR"
        else:
            quality = "POOR"
        
        print(f"   Result: {silhouette:.4f} [{quality}]")
    except Exception as e:
        print(f"   Error: {e}")
        metrics['silhouette'] = None
    
    # METRIC 2: DAVIES-BOULDIN INDEX
    print(f"\n2. DAVIES-BOULDIN INDEX (Separation)")
    try:
        db_index = davies_bouldin_score(X_sample_num, labels_sample)
        metrics['davies_bouldin'] = db_index
        
        if db_index < 0.7:
            quality = "EXCELLENT"
        elif db_index < 1.0:
            quality = "GOOD"
        elif db_index < 1.5:
            quality = "FAIR"
        else:
            quality = "POOR"
        
        print(f"   Result: {db_index:.4f} [{quality}]")
    except Exception as e:
        print(f"   Error: {e}")
        metrics['davies_bouldin'] = None
    
    # METRIC 3: CALINSKI-HARABASZ INDEX
    print(f"\n3. CALINSKI-HARABASZ INDEX (F-statistic)")
    try:
        ch_index = calinski_harabasz_score(X_sample_num, labels_sample)
        metrics['calinski_harabasz'] = ch_index
        print(f"   Result: {ch_index:.2f}")
    except Exception as e:
        print(f"   Error: {e}")
        metrics['calinski_harabasz'] = None
    
    # METRIC 4: CLUSTER SIZE DISTRIBUTION (BALANCE)
    print(f"\n4. CLUSTER SIZE DISTRIBUTION (Balance)")
    unique, counts = np.unique(labels_full, return_counts=True)
    
    print(f"   Clusters: {len(unique)}")
    for cluster_id, count in zip(unique, counts):
        pct = (count / len(labels_full)) * 100
        bar = "[" + "=" * int(pct / 5) + "]"
        print(f"     Segment {cluster_id}: {count:7,} customers ({pct:5.1f}%) {bar}")
    
    pct_values = (counts / len(labels_full)) * 100
    imbalance = max(pct_values) / (min(pct_values) + 1e-9)
    
    if imbalance < 2:
        balance_quality = "EXCELLENT"
    elif imbalance < 3:
        balance_quality = "GOOD"
    elif imbalance < 5:
        balance_quality = "FAIR"
    else:
        balance_quality = "POOR (imbalanced)"
    
    print(f"   Balance ratio (max/min): {imbalance:.2f} [{balance_quality}]")
    metrics['balance'] = imbalance
    metrics['cluster_sizes'] = dict(zip(unique, counts))
    
    return metrics


def profile_segments(df_with_features, labels, k_value):
    """Profile each segment and return summary table"""
    print(f"\n[SECTION 3] SEGMENT PROFILES (K={k_value})")
    print("-" * 80)
    
    df_segment = df_with_features.copy()
    df_segment['segment'] = labels
    
    segment_profiles = []
    
    for seg in range(k_value):
        segment_df = df_segment[df_segment['segment'] == seg]
        n_customers = len(segment_df)
        pct = (n_customers / len(df_segment)) * 100
        
        profile = {
            'segment': seg,
            'size': n_customers,
            'pct': pct,
            'avg_spending': segment_df['monetary'].mean(),
            'median_spending': segment_df['monetary'].median(),
            'pct_high_value': segment_df['is_high_value'].mean() * 100,
            'avg_orders': segment_df['num_orders'].mean(),
            'pct_repeat': segment_df['is_repeat_customer'].mean() * 100,
            'pct_sp': segment_df['is_sp'].mean() * 100,
            'top_category': segment_df['preferred_category'].mode().values[0] if len(segment_df) > 0 else 'N/A',
            'avg_recency': segment_df['recency'].mean()
        }
        
        segment_profiles.append(profile)
        
        print(f"\nSegment {seg} ({n_customers:,} customers, {pct:.1f}%)")
        print(f"  Spending: ${profile['avg_spending']:.2f} avg | ${profile['median_spending']:.2f} median | {profile['pct_high_value']:.1f}% high-value")
        print(f"  Behavior: {profile['avg_orders']:.2f} orders avg | {profile['pct_repeat']:.1f}% repeat")
        print(f"  Geography: {profile['pct_sp']:.1f}% São Paulo")
        print(f"  Preferences: {profile['top_category']} (top) | {profile['avg_recency']:.0f} days recency")
    
    return pd.DataFrame(segment_profiles)


def save_results(customer_ids, labels, k_value, metrics, segment_profiles):
    """Save clustering results and metrics"""
    print(f"\n[SECTION 4] SAVING RESULTS")
    print("-" * 80)
    
    # CSV: Segment assignments
    assignments_df = pd.DataFrame({
        'customer_unique_id': customer_ids,
        f'segment_k{k_value}': labels
    })
    
    assignments_df.to_csv(f'data/customer_segments_k{k_value}.csv', index=False)
    print(f"[OK] Saved: data/customer_segments_k{k_value}.csv")
    
    # PostgreSQL
    try:
        assignments_df.to_sql(f'customer_segments_k{k_value}', engine, if_exists='replace', index=False)
        print(f"[OK] Saved to PostgreSQL: customer_segments_k{k_value}")
    except Exception as e:
        print(f"[!] PostgreSQL save failed: {e}")
    
    # JSON: Metrics
    metrics_path = f'data/clustering_metrics_k{k_value}.json'
    with open(metrics_path, 'w') as f:
        metrics_copy = metrics.copy()
        cluster_sizes = {str(k): int(v) for k, v in metrics_copy.pop('cluster_sizes').items()}
        json.dump({
            'k_value': k_value,
            'metrics': {k: float(v) if v is not None else None for k, v in metrics_copy.items()},
            'cluster_sizes': cluster_sizes,
            'total_customers': len(assignments_df)
        }, f, indent=2)
    print(f"[OK] Saved: {metrics_path}")
    
    # CSV: Segment profiles summary
    profiles_csv = f'data/segment_profiles_k{k_value}.csv'
    segment_profiles.to_csv(profiles_csv, index=False)
    print(f"[OK] Saved: {profiles_csv}")





def main():
    """Main Phase 3 execution"""
    print("="*80)
    print("PHASE 3: CUSTOMER SEGMENTATION WITH K-PROTOTYPE")
    print("="*80)
    
    k_value = 3
    
    # Load datasets
    print("\n[STEP 1] LOADING DATASETS")
    print("-" * 80)
    try:
        kprototype_df = pd.read_sql("SELECT * FROM customer_features_kprototype", engine)
        full_features_df = pd.read_sql("SELECT * FROM customer_features", engine)
        print(f"[OK] K-Prototype dataset: {kprototype_df.shape}")
        print(f"[OK] Full features dataset: {full_features_df.shape}")
        customer_ids = full_features_df['customer_unique_id'].values
    except Exception as e:
        print(f"PostgreSQL error, loading from CSV...")
        try:
            kprototype_df = pd.read_csv('data/customer_features_kprototype.csv')
            full_features_df = pd.read_csv('data/customer_features.csv')
            customer_ids = full_features_df['customer_unique_id'].values
        except Exception as e2:
            print(f"[ERROR] Could not load data: {e2}")
            return
    
    # K-Prototype clustering
    kproto, labels_full, labels_sample, X_sample_num, X_full_num, categorical_indices = run_kprototype_optimized(
        kprototype_df, customer_ids, full_features_df, k_value=k_value, sample_fraction=0.15
    )
    
    # Evaluate
    metrics = evaluate_clustering(X_sample_num, labels_sample, labels_full, k_value)
    
    # Profile segments
    segment_profiles = profile_segments(full_features_df, labels_full, k_value)
    
    # Save results
    save_results(customer_ids, labels_full, k_value, metrics, segment_profiles)
    
    # Print summary table
    print(f"\n" + "="*80)
    print("SEGMENT SUMMARY TABLE")
    print("="*80)
    print(segment_profiles.to_string(index=False))
    
    print(f"\n" + "="*80)
    print("PHASE 3 COMPLETE")
    print("="*80)
    print(f"""
[OK] {len(customer_ids):,} customers segmented into {k_value} clusters

RESULTS SAVED:
  - Segment assignments: data/customer_segments_k{k_value}.csv
  - Metrics: data/clustering_metrics_k{k_value}.json
  - Profile summary: data/segment_profiles_k{k_value}.csv
  
TO CREATE VISUALIZATIONS:
  Run: python phase3/create_phase3_visualizations.py
  
  This generates 4 publication-quality PNG files:
  - Segment distribution: phase3/visualizations/segment_distribution_k3.png
  - Profile comparison: phase3/visualizations/segment_profiles_k3.png
  - Evaluation metrics: phase3/visualizations/evaluation_metrics_k3.png
  - Spending distribution: phase3/visualizations/spending_distribution_k3.png
  
NEXT STEPS:
  Phase 4: Segment-specific association mining (repeat Phase 2 per segment)
  - Mine rules for Segment 0
  - Mine rules for Segment 1
  - Mine rules for Segment 2
  - Compare rules across segments
""")


if __name__ == '__main__':
    main()
