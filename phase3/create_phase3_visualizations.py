"""
PHASE 3: VISUALIZATION GENERATOR (Standalone)
============================================================================

Generate publication-quality visualizations from Phase 3 clustering results.
Run this script independently to recreate visualizations without re-clustering.

"""

import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

from pathlib import Path

warnings.filterwarnings('ignore')

# Set plotting style for publication quality
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Setup output directory
VIZ_DIR = Path(__file__).resolve().parent / 'visualizations'
VIZ_DIR.mkdir(parents=True, exist_ok=True)


def load_clustering_results(k_value=3):
    """Load pre-computed clustering results"""
    print("\n" + "="*80)
    print(f"PHASE 3: VISUALIZATION GENERATOR (K={k_value})")
    print("="*80)
    
    # Load customer features
    print("\n[STEP 1] LOADING DATA")
    print("-" * 80)
    
    try:
        full_features_df = pd.read_csv('data/customer_features_full.csv')
        print(f"[OK] Loaded full features: {full_features_df.shape}")
    except FileNotFoundError:
        print("[ERROR] Missing data/customer_features_full.csv")
        return None
    
    try:
        segment_assignments = pd.read_csv(f'data/customer_segments_k{k_value}.csv')
        print(f"[OK] Loaded segment assignments: {segment_assignments.shape}")
    except FileNotFoundError:
        print(f"[ERROR] Missing data/customer_segments_k{k_value}.csv")
        return None
    
    try:
        with open(f'data/clustering_metrics_k{k_value}.json', 'r') as f:
            metrics_data = json.load(f)
        metrics = metrics_data['metrics']
        metrics['cluster_sizes'] = metrics_data['cluster_sizes']
        print(f"[OK] Loaded metrics: K={k_value}")
    except FileNotFoundError:
        print(f"[ERROR] Missing data/clustering_metrics_k{k_value}.json")
        return None
    
    try:
        segment_profiles = pd.read_csv(f'data/segment_profiles_k{k_value}.csv')
        print(f"[OK] Loaded segment profiles: {segment_profiles.shape}")
    except FileNotFoundError:
        print(f"[ERROR] Missing data/segment_profiles_k{k_value}.csv")
        return None
    
    # Merge data
    labels = segment_assignments[f'segment_k{k_value}'].values
    
    return {
        'features': full_features_df,
        'labels': labels,
        'metrics': metrics,
        'profiles': segment_profiles,
        'k_value': k_value
    }


def create_visualizations(data):
    """Create comprehensive visualizations for TA presentation"""
    print(f"\n[STEP 2] CREATING VISUALIZATIONS")
    print("-" * 80)
    
    # Merge features with labels by customer_unique_id
    features_df = data['features'].copy()
    segment_assignments = pd.DataFrame({
        'customer_unique_id': range(len(data['labels'])),
        'segment': data['labels']
    })
    
    # Reset features index to align with segment labels
    if 'customer_unique_id' in features_df.columns:
        features_df = features_df.reset_index(drop=True)
    
    # Create aligned dataframe
    df_vis = features_df.copy()
    df_vis['segment'] = data['labels'][:len(df_vis)]
    
    labels = data['labels']
    k_value = data['k_value']
    metrics = data['metrics']
    segment_profiles = data['profiles'].copy()
    
    segment_names = {0: "Low-Value", 1: "High-Value", 2: "Recent-Active"}
    segment_profiles['segment_name'] = segment_profiles['segment'].map(segment_names)
    
    colors = sns.color_palette("husl", k_value)
    
    # ========================================================================
    # VISUALIZATION 1: Segment Distribution (Pie Chart + Bar Chart)
    # ========================================================================
    print("Creating: Segment Size Distribution...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    sizes = {int(k): int(v) for k, v in metrics['cluster_sizes'].items()}
    
    labels_pie = [f"{segment_names.get(i, f'Segment {i}')}\n{sizes[i]:,} customers\n({sizes[i]/sum(sizes.values())*100:.1f}%)" 
                  for i in range(k_value)]
    ax1.pie(sizes.values(), labels=labels_pie, autopct='%1.1f%%', colors=colors, startangle=90)
    ax1.set_title(f'Segment Distribution (K={k_value})', fontsize=12, fontweight='bold')
    
    # Bar chart of sizes
    ax2.bar(range(k_value), list(sizes.values()), color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    ax2.set_xlabel('Segment ID', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Number of Customers', fontsize=11, fontweight='bold')
    ax2.set_title(f'Segment Sizes (K={k_value})', fontsize=12, fontweight='bold')
    ax2.set_xticks(range(k_value))
    for i, v in enumerate(sizes.values()):
        ax2.text(i, v + 1000, f'{v:,}', ha='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(VIZ_DIR / 'segment_distribution_k3.png', dpi=300, bbox_inches='tight')
    print(f"[OK] Saved: {VIZ_DIR / 'segment_distribution_k3.png'}")
    plt.close()
    
    # ========================================================================
    # VISUALIZATION 2: Segment Profiles Comparison (6-Panel Dashboard)
    # ========================================================================
    print("Creating: Segment Profiles Comparison...")
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle(f'Segment Characteristics Comparison (K={k_value})', fontsize=14, fontweight='bold')
    
    # Panel 1: Spending
    axes[0, 0].bar(segment_profiles['segment_name'], segment_profiles['avg_spending'], 
                   color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    axes[0, 0].set_ylabel('Average Spending ($)', fontweight='bold')
    axes[0, 0].set_title('Average Spending per Segment')
    axes[0, 0].set_xlabel('Segment')
    
    # Panel 2: High-value percentage
    axes[0, 1].bar(segment_profiles['segment_name'], segment_profiles['pct_high_value'], 
                   color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    axes[0, 1].set_ylabel('Percentage (%)', fontweight='bold')
    axes[0, 1].set_title('High-Value Customers (%)')
    axes[0, 1].set_xlabel('Segment')
    
    # Panel 3: Average orders
    axes[0, 2].bar(segment_profiles['segment_name'], segment_profiles['avg_orders'], 
                   color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    axes[0, 2].set_ylabel('Average Orders', fontweight='bold')
    axes[0, 2].set_title('Average Orders per Segment')
    axes[0, 2].set_xlabel('Segment')
    
    # Panel 4: Repeat customer percentage
    axes[1, 0].bar(segment_profiles['segment_name'], segment_profiles['pct_repeat'], 
                   color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    axes[1, 0].set_ylabel('Percentage (%)', fontweight='bold')
    axes[1, 0].set_title('Repeat Customers (%)')
    axes[1, 0].set_xlabel('Segment')
    
    # Panel 5: São Paulo percentage
    axes[1, 1].bar(segment_profiles['segment_name'], segment_profiles['pct_sp'], 
                   color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    axes[1, 1].set_ylabel('Percentage (%)', fontweight='bold')
    axes[1, 1].set_title('São Paulo Customers (%)')
    axes[1, 1].set_xlabel('Segment')
    
    # Panel 6: Recency
    axes[1, 2].bar(segment_profiles['segment_name'], segment_profiles['avg_recency'], 
                   color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    axes[1, 2].set_ylabel('Average Recency (days)', fontweight='bold')
    axes[1, 2].set_title('Average Recency per Segment')
    axes[1, 2].set_xlabel('Segment')
    
    plt.tight_layout()
    plt.savefig(VIZ_DIR / 'segment_profiles_k3.png', dpi=300, bbox_inches='tight')
    print(f"[OK] Saved: {VIZ_DIR / 'segment_profiles_k3.png'}")
    plt.close()
    
    # ========================================================================
    # VISUALIZATION 3: Evaluation Metrics Dashboard (4-Panel)
    # ========================================================================
    print("Creating: Evaluation Metrics Dashboard...")
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f'Clustering Evaluation Metrics (K={k_value})', fontsize=14, fontweight='bold')
    
    # Silhouette
    sil_color = '#2E86AB' if metrics['silhouette'] and metrics['silhouette'] > 0.3 else '#FF6B6B'
    axes[0, 0].barh(['Silhouette'], [metrics['silhouette']], color=sil_color, alpha=0.8, 
                    edgecolor='black', linewidth=2)
    axes[0, 0].set_xlim([0, 1])
    axes[0, 0].axvline(x=0.3, color='green', linestyle='--', linewidth=2, alpha=0.7, label='Good (>0.3)')
    axes[0, 0].axvline(x=0.5, color='blue', linestyle='--', linewidth=2, alpha=0.7, label='Excellent (>0.5)')
    axes[0, 0].set_title('Silhouette Score (Coherence) [Higher Better]', fontweight='bold')
    axes[0, 0].text(metrics['silhouette'] + 0.02, 0, f"{metrics['silhouette']:.4f}", 
                    va='center', fontweight='bold')
    axes[0, 0].legend(loc='lower right', fontsize=9)
    
    # Davies-Bouldin
    db_color = '#2E86AB' if metrics['davies_bouldin'] and metrics['davies_bouldin'] < 1.0 else '#FF6B6B'
    axes[0, 1].barh(['Davies-Bouldin'], [metrics['davies_bouldin']], color=db_color, alpha=0.8, 
                    edgecolor='black', linewidth=2)
    axes[0, 1].set_xlim([0, 2])
    axes[0, 1].axvline(x=0.7, color='blue', linestyle='--', linewidth=2, alpha=0.7, label='Excellent (<0.7)')
    axes[0, 1].axvline(x=1.0, color='green', linestyle='--', linewidth=2, alpha=0.7, label='Good (<1.0)')
    axes[0, 1].set_title('Davies-Bouldin Index (Separation) [Lower Better]', fontweight='bold')
    axes[0, 1].text(metrics['davies_bouldin'] + 0.05, 0, f"{metrics['davies_bouldin']:.4f}", 
                    va='center', fontweight='bold')
    axes[0, 1].legend(loc='lower right', fontsize=9)
    
    # Calinski-Harabasz
    axes[1, 0].barh(['Calinski-Harabasz'], [metrics['calinski_harabasz']], color='#A23B72', 
                    alpha=0.8, edgecolor='black', linewidth=2)
    axes[1, 0].set_title('Calinski-Harabasz Index (F-statistic) [Higher Better]', fontweight='bold')
    axes[1, 0].text(metrics['calinski_harabasz'] + 100, 0, f"{metrics['calinski_harabasz']:.1f}", 
                    va='center', fontweight='bold')
    
    # Balance
    balance_color = '#2E86AB' if metrics['balance'] < 3 else '#FF6B6B'
    axes[1, 1].barh(['Balance Ratio'], [metrics['balance']], color=balance_color, alpha=0.8, 
                    edgecolor='black', linewidth=2)
    axes[1, 1].axvline(x=2, color='blue', linestyle='--', linewidth=2, alpha=0.7, label='Excellent (<2)')
    axes[1, 1].axvline(x=3, color='green', linestyle='--', linewidth=2, alpha=0.7, label='Good (<3)')
    axes[1, 1].set_title('Balance Ratio (Max/Min Size) [Lower Better]', fontweight='bold')
    axes[1, 1].text(metrics['balance'] + 0.05, 0, f"{metrics['balance']:.2f}", 
                    va='center', fontweight='bold')
    axes[1, 1].legend(loc='lower right', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(VIZ_DIR / 'evaluation_metrics_k3.png', dpi=300, bbox_inches='tight')
    print(f"[OK] Saved: {VIZ_DIR / 'evaluation_metrics_k3.png'}")
    plt.close()
    
    # ========================================================================
    # VISUALIZATION 4: Spending Distribution (Box + Violin Plot)
    # ========================================================================
    print("Creating: Spending Distribution by Segment...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Box plot
    segment_spending = [df_vis[df_vis['segment'] == i]['monetary'].values for i in range(k_value)]
    bp = ax1.boxplot(segment_spending, labels=[segment_names.get(i, f'Segment {i}') for i in range(k_value)],
                      patch_artist=True, widths=0.6)
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    ax1.set_ylabel('Spending ($)', fontsize=11, fontweight='bold')
    ax1.set_title('Spending Distribution by Segment (Box Plot)', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Violin plot
    data_for_violin = []
    segment_labels_violin = []
    for seg in range(k_value):
        data_for_violin.extend(df_vis[df_vis['segment'] == seg]['monetary'].values)
        segment_labels_violin.extend([segment_names.get(seg, f'Segment {seg}')] * len(df_vis[df_vis['segment'] == seg]))
    
    violin_df = pd.DataFrame({'Spending': data_for_violin, 'Segment': segment_labels_violin})
    sns.violinplot(data=violin_df, x='Segment', y='Spending', ax=ax2, palette=colors)
    ax2.set_ylabel('Spending ($)', fontsize=11, fontweight='bold')
    ax2.set_title('Spending Distribution by Segment (Violin Plot)', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(VIZ_DIR / 'spending_distribution_k3.png', dpi=300, bbox_inches='tight')
    print(f"[OK] Saved: {VIZ_DIR / 'spending_distribution_k3.png'}")
    plt.close()
    
    print("\n[OK] All visualizations created successfully!")
    
    # Print summary
    print(f"\n[SECTION 3] SUMMARY")
    print("-" * 80)
    print(f"Visualizations created: 4 PNG files (300 dpi)")
    print(f"  1. segment_distribution_k3.png - Segment sizes overview")
    print(f"  2. segment_profiles_k3.png - 6-panel segment characteristics")
    print(f"  3. evaluation_metrics_k3.png - 4-metric clustering quality dashboard")
    print(f"  4. spending_distribution_k3.png - Spending patterns by segment")
    print("\n" + "="*80)


if __name__ == "__main__":
    data = load_clustering_results(k_value=3)
    if data is not None:
        create_visualizations(data)
        print("\n[COMPLETE] Visualization generation finished!")
    else:
        print("\n[ERROR] Failed to load clustering results. Please run phase3_clustering.py first.")
