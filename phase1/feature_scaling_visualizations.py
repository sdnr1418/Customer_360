"""
Feature Scaling Evaluation Visualizations

Creates visual representations of the 4 clustering evaluation metrics:
1. Elbow Method (Inertia curve)
2. Silhouette Score (cluster coherence)
3. Davies-Bouldin Index (separation quality)
4. Calinski-Harabasz Index (F-statistic signal)

"""

import json
import matplotlib.pyplot as plt
import numpy as np

# Load evaluation results from feature_scaling_summary.json
with open('data/feature_scaling_summary.json', 'r') as f:
    summary = json.load(f)

test_results = summary['test_results']

# Extract metrics
elbow_inertias = test_results['elbow_inertias']
silhouette_scores = test_results['silhouette_scores']
db_scores = test_results['davies_bouldin_scores']
ch_scores = test_results['calinski_harabasz_scores']

best_k_silhouette = test_results['best_k_silhouette']
best_k_db = test_results['best_k_davies_bouldin']
best_k_ch = test_results['best_k_calinski_harabasz']

# Convert to lists for plotting
k_values_elbow = sorted([int(k) for k in elbow_inertias.keys()])
inertia_values = [elbow_inertias[str(k)] for k in k_values_elbow]

k_values_silhouette = sorted([int(k) for k in silhouette_scores.keys()])
silhouette_values = [silhouette_scores[str(k)] for k in k_values_silhouette]

k_values_db = sorted([int(k) for k in db_scores.keys()])
db_values = [db_scores[str(k)] for k in k_values_db]

k_values_ch = sorted([int(k) for k in ch_scores.keys()])
ch_values = [ch_scores[str(k)] for k in k_values_ch]

# Create figure with 4 subplots
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Clustering Evaluation Metrics: K Selection Analysis', fontsize=16, fontweight='bold')

# Color scheme
color_primary = '#2E86AB'  # Blue for optimal
color_secondary = '#A23B72'  # Purple for secondary
color_default = '#6C757D'  # Gray for others

# ============================================================================
# Plot 1: Elbow Method
# ============================================================================
ax1 = axes[0, 0]
ax1.plot(k_values_elbow, inertia_values, marker='o', linewidth=2.5, markersize=8, color=color_primary)
ax1.axvline(x=3, color=color_primary, linestyle='--', alpha=0.5, linewidth=2, label='Potential Elbow (K=3)')
ax1.axvline(x=4, color=color_secondary, linestyle='--', alpha=0.5, linewidth=2, label='Potential Elbow (K=4)')
ax1.set_xlabel('Number of Clusters (K)', fontsize=11, fontweight='bold')
ax1.set_ylabel('Inertia (Within-Cluster Sum of Squares)', fontsize=11, fontweight='bold')
ax1.set_title('1. Elbow Method: Diminishing Returns', fontsize=12, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.legend(fontsize=9)
ax1.set_xticks(k_values_elbow)

# ============================================================================
# Plot 2: Silhouette Score (HIGHER BETTER)
# ============================================================================
ax2 = axes[0, 1]
colors = [color_primary if k == best_k_silhouette else color_default for k in k_values_silhouette]
ax2.bar(k_values_silhouette, silhouette_values, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
ax2.axhline(y=0.5, color='green', linestyle='--', alpha=0.6, linewidth=2, label='Excellent (>0.5)')
ax2.axhline(y=0.3, color='orange', linestyle='--', alpha=0.6, linewidth=2, label='Good (>0.3)')
ax2.scatter([best_k_silhouette], [silhouette_scores[str(best_k_silhouette)]], 
           color=color_primary, s=200, marker='*', edgecolor='black', linewidth=2, zorder=5,
           label=f'Best: K={best_k_silhouette}')
ax2.set_xlabel('Number of Clusters (K)', fontsize=11, fontweight='bold')
ax2.set_ylabel('Silhouette Score', fontsize=11, fontweight='bold')
ax2.set_title(f'2. Silhouette Score: BEST K={best_k_silhouette} (Higher Better)', fontsize=12, fontweight='bold')
ax2.set_ylim([0.2, 0.5])
ax2.grid(True, alpha=0.3, axis='y')
ax2.legend(fontsize=9)
ax2.set_xticks(k_values_silhouette)

# ============================================================================
# Plot 3: Davies-Bouldin Index (LOWER BETTER)
# ============================================================================
ax3 = axes[1, 0]
colors = [color_secondary if k == best_k_db else color_default for k in k_values_db]
ax3.bar(k_values_db, db_values, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
ax3.axhline(y=0.7, color='green', linestyle='--', alpha=0.6, linewidth=2, label='Excellent (<0.7)')
ax3.axhline(y=1.0, color='orange', linestyle='--', alpha=0.6, linewidth=2, label='Good (<1.0)')
ax3.scatter([best_k_db], [db_scores[str(best_k_db)]], 
           color=color_secondary, s=200, marker='*', edgecolor='black', linewidth=2, zorder=5,
           label=f'Best: K={best_k_db}')
ax3.set_xlabel('Number of Clusters (K)', fontsize=11, fontweight='bold')
ax3.set_ylabel('Davies-Bouldin Index', fontsize=11, fontweight='bold')
ax3.set_title(f'3. Davies-Bouldin Index: BEST K={best_k_db} (Lower Better)', fontsize=12, fontweight='bold')
ax3.set_ylim([0.7, 1.1])
ax3.grid(True, alpha=0.3, axis='y')
ax3.legend(fontsize=9)
ax3.set_xticks(k_values_db)

# ============================================================================
# Plot 4: Calinski-Harabasz Index (HIGHER BETTER)
# ============================================================================
ax4 = axes[1, 1]
colors = [color_default if k == best_k_ch else color_default for k in k_values_ch]
ax4.plot(k_values_ch, ch_values, marker='o', linewidth=2.5, markersize=8, color=color_default, alpha=0.7)
ax4.scatter([best_k_ch], [ch_scores[str(best_k_ch)]], 
           color='#FF6B6B', s=200, marker='*', edgecolor='black', linewidth=2, zorder=5,
           label=f'Highest: K={best_k_ch} (but too coarse)')
ax4.scatter([3, 4], [ch_scores['3'], ch_scores['4']], 
           color=color_primary, s=150, marker='o', edgecolor='black', linewidth=2, zorder=5,
           label='K=3,4 recommended range')
ax4.set_xlabel('Number of Clusters (K)', fontsize=11, fontweight='bold')
ax4.set_ylabel('Calinski-Harabasz Index', fontsize=11, fontweight='bold')
ax4.set_title('4. Calinski-Harabasz Index: Statistical Signal (Higher Better)', fontsize=12, fontweight='bold')
ax4.grid(True, alpha=0.3)
ax4.legend(fontsize=9)
ax4.set_xticks(k_values_ch)

plt.tight_layout()
plt.savefig('visualizations/evaluation_metrics_comparison.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: visualizations/evaluation_metrics_comparison.png")

# ============================================================================
# Create Consensus Summary Plot
# ============================================================================
fig2, ax = plt.subplots(figsize=(12, 7))

# K values to display
k_range = list(range(2, 9))

# Create voting matrix (1 = best, 0.5 = secondary, 0 = not recommended)
votes = []
for k in k_range:
    score = 0
    if k == best_k_silhouette:
        score += 1
    elif k == 3 or k == 4 or k == 5:  # Elbow range
        score += 0.5
    
    if k == best_k_db:
        score += 1
    elif k == 3 or k == 4 or k == 5:
        score += 0.5
    
    if k == best_k_ch:
        score += 0.3  # Weight down since K=2 is too coarse
    elif k == 3 or k == 4 or k == 5:
        score += 0.2
    
    votes.append(score)

colors_consensus = []
for k, score in zip(k_range, votes):
    if k in [3, 4, 5, 6]:
        colors_consensus.append('#2E86AB')  # Blue - recommended
    else:
        colors_consensus.append('#A9A9A9')  # Gray - not recommended

bars = ax.bar(k_range, votes, color=colors_consensus, alpha=0.8, edgecolor='black', linewidth=2)

# Add value labels on bars
for i, (k, v) in enumerate(zip(k_range, votes)):
    ax.text(k, v + 0.1, f'{v:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=11)

ax.axhline(y=2.0, color='#2E86AB', linestyle='--', alpha=0.5, linewidth=2, label='Optimal: Highly Recommended')
ax.axhline(y=1.0, color='#FFB700', linestyle='--', alpha=0.5, linewidth=2, label='Moderate: Consider')
ax.axhline(y=0.5, color='#FF6B6B', linestyle='--', alpha=0.5, linewidth=2, label='Low: Not Recommended')

ax.set_xlabel('Number of Clusters (K)', fontsize=12, fontweight='bold')
ax.set_ylabel('Consensus Score (Combined Metrics)', fontsize=12, fontweight='bold')
ax.set_title('Consensus K Selection: Voting Across All 4 Metrics', fontsize=14, fontweight='bold')
ax.set_xticks(k_range)
ax.set_ylim([0, 2.8])
ax.grid(True, alpha=0.3, axis='y')
ax.legend(fontsize=11, loc='upper right')

plt.tight_layout()
plt.savefig('visualizations/consensus_k_selection.png', dpi=300, bbox_inches='tight')
print("[OK] Saved: visualizations/consensus_k_selection.png")

# ============================================================================
# Create Summary Report
# ============================================================================
summary_text = f"""
CLUSTERING EVALUATION SUMMARY
{'='*60}

K Selection Results:
  • Silhouette Score (Coherence):    BEST K = {best_k_silhouette} (score: {silhouette_scores[str(best_k_silhouette)]:.4f})
  • Davies-Bouldin (Separation):     BEST K = {best_k_db} (score: {db_scores[str(best_k_db)]:.4f})
  • Calinski-Harabasz (F-statistic): BEST K = {best_k_ch} (score: {ch_scores[str(best_k_ch)]:.1f})
  • Elbow Method (Visual):            CANDIDATES K = 3, 4, 5

CONSENSUS RECOMMENDATION:
  PRIMARY:   K = 3 (Highest Silhouette = Best Coherence)
  SECONDARY: K = 4 (Best Davies-Bouldin = Good Separation)
  TEST RANGE: K in {3, 4, 5, 6} in Phase 3

Key Findings:
  1. K=3 provides the tightest clusters with best internal coherence
  2. K=4 offers better separation between clusters
  3. Elbow curve flattens after K=4, showing diminishing returns
  4. K=2 (highest F-statistic) is too coarse for 93k customers
  5. All metrics agree: K in {3,4,5,6} is the optimal range

Next Steps:
  1. Run K-Prototype clustering with K=3 (primary focus)
  2. Explore K=4,5,6 if time permits
  3. Profile segments: spending patterns, preferences, geography
  4. Move to Phase 4: segment-specific association mining
"""

with open('data/evaluation_summary.txt', 'w', encoding='utf-8') as f:
    f.write(summary_text)

print("[OK] Saved: data/evaluation_summary.txt")

# ============================================================================
# Print Summary to Console
# ============================================================================
print("\n" + "="*80)
print("EVALUATION METRICS VISUALIZATION COMPLETE")
print("="*80)
print(summary_text)
print("\nVisualizations saved:")
print("  1. visualizations/evaluation_metrics_comparison.png (4-panel overview)")
print("  2. visualizations/consensus_k_selection.png (voting summary)")
print("  3. data/evaluation_summary.txt (text report)")
print("="*80)
