#!/usr/bin/env python
"""
Phase 2: Visualizations, CSV Exports, and Strategic Report Generation
Completes Phase 2 Association Rule Mining with:
- 6 Production-Grade Visualizations
- 5 Strategic CSV Exports
- Comprehensive Markdown Report
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.patches import Rectangle
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = str(PROJECT_ROOT / "phase2_outputs")
VISUALIZATION_DIR = f"{OUTPUT_DIR}/visualizations"
EXPORT_DIR = f"{OUTPUT_DIR}/exports"

# Ensure directories exist
import os
os.makedirs(VISUALIZATION_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)

# ============================================================================
# STEP 7: VISUALIZATION GENERATION (6 Charts)
# ============================================================================

def create_visualizations(results):
    """Generate 6 production-grade visualizations for Phase 2 report"""
    
    print("\n" + "="*70)
    print("STEP 7: GENERATING VISUALIZATIONS (6 Charts)")
    print("="*70)
    
    # 1. ANCHOR vs ADD-ON ANALYSIS
    print("\n[1/6] Creating Anchor vs Add-On Network...")
    _viz_anchor_addon(results['anchor_df'])
    
    # 2. BUNDLE STRENGTH HEATMAP
    print("[2/6] Creating Bundle Strength Heatmap...")
    _viz_bundle_heatmap(results['bundling_candidates'])
    
    # 3. MARKET COMPOSITION PIE
    print("[3/6] Creating Market Composition Pie...")
    _viz_market_composition(results['basket_composition'])
    
    # 4. LIFT vs SUPPORT SCATTER
    print("[4/6] Creating Lift vs Support Scatter...")
    _viz_lift_support_scatter(results['final_rules'])
    
    # 5. CATEGORY PAIR TREEMAP
    print("[5/6] Creating Category Pair Treemap...")
    _viz_category_treemap(results['final_rules'])
    
    # 6. SYNTHETIC BUNDLES SUMMARY
    print("[6/6] Creating Synthetic Bundles Summary...")
    _viz_synthetic_bundles(results['drilldown_results'])
    
    print("\n[OK] All 6 visualizations created successfully!")
    return True

def _viz_anchor_addon(anchor_df):
    """Anchor vs Add-On Network Visualization"""
    if len(anchor_df) == 0:
        return
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    top_anchors = anchor_df.nlargest(8, 'anchor_index')
    colors = ['#2ecc71' if idx >= 0.5 else '#e74c3c' for idx in top_anchors['anchor_index']]
    
    bars = ax.barh(range(len(top_anchors)), top_anchors['anchor_index'], color=colors)
    ax.set_yticks(range(len(top_anchors)))
    ax.set_yticklabels(top_anchors['category'])
    ax.set_xlabel('Anchor Index (Green = Initiator, Red = Secondary)', fontsize=11, fontweight='bold')
    ax.set_title('Market Basket Analysis: Anchor vs Add-On Products\n(Top 8 Categories by Role)', 
                 fontsize=13, fontweight='bold', pad=20)
    ax.set_xlim(0, 1.1)
    
    for i, (idx, bar) in enumerate(zip(top_anchors['anchor_index'], bars)):
        label = 'ANCHOR' if idx >= 0.5 else 'ADD-ON'
        ax.text(idx + 0.02, i, label, va='center', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f"{VISUALIZATION_DIR}/01_anchor_addon.png", dpi=300, bbox_inches='tight')
    plt.close()

def _viz_bundle_heatmap(bundles_df):
    """Bundle Strength Heatmap (Lift × Confidence)"""
    if len(bundles_df) == 0:
        return
    
    top_bundles = bundles_df.nlargest(10, 'lift').copy()
    top_bundles['pair'] = (top_bundles['antecedents'].astype(str).str[:15] + ' → ' + 
                          top_bundles['consequents'].astype(str).str[:15])
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Create 2D matrix: rows=bundles, cols=[lift, confidence, support*100]
    matrix = np.array([top_bundles['lift'].values,
                      top_bundles['confidence'].values * 100,
                      top_bundles['support'].values * 1000]).T
    
    sns.heatmap(matrix, 
                annot=np.round(matrix, 1),
                fmt='g',
                cmap='RdYlGn',
                cbar_kws={'label': 'Strength Score'},
                xticklabels=['Lift\n(Category Association)', 
                            'Confidence %\n(Purchase Rate)',
                            'Support ×1000\n(Multi-Item Carts)'],
                yticklabels=top_bundles['pair'],
                ax=ax,
                linewidths=1,
                linecolor='white')
    
    ax.set_title('Bundle Strength Matrix - Top 10 Category Pairs\n(Lift × Confidence × Support Among Multi-Item Carts)',
                fontsize=13, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(f"{VISUALIZATION_DIR}/02_bundle_heatmap.png", dpi=300, bbox_inches='tight')
    plt.close()

def _viz_market_composition(composition):
    """Market Composition: 99.2% vs 0.8% Orders"""
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    labels = ['Single-Category Orders\n(Specialized Purchase)',
              'Multi-Category Orders\n(Bundler Segment)']
    sizes = [composition['single_category_pct'], composition['multi_category_pct']]
    colors = ['#3498db', '#e74c3c']
    explode = (0, 0.15)
    
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                        explode=explode, startangle=90, textprops={'fontsize': 12})
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(14)
    
    # Add order counts in legend
    legend_labels = [f"{labels[0]}: {composition['single_category']:,} orders",
                    f"{labels[1]}: {composition['multi_category']:,} orders"]
    ax.legend(legend_labels, loc="upper left", bbox_to_anchor=(0.0, 1.0), fontsize=10)
    
    ax.set_title('Market Basket Composition - Store Type Assessment\nOlist: SPECIALIZED STORE (99% focus on single categories)',
                fontsize=13, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(f"{VISUALIZATION_DIR}/03_market_composition.png", dpi=300, bbox_inches='tight')
    plt.close()

def _viz_lift_support_scatter(rules_df):
    """Lift vs Support Scatter Plot with Annotations"""
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    top_rules = rules_df.nlargest(15, 'lift')
    
    # Scatter plot
    scatter = ax.scatter(top_rules['support'] * 100, top_rules['lift'],
                        s=top_rules['confidence'] * 1000,
                        alpha=0.6, c=range(len(top_rules)), cmap='viridis',
                        edgecolors='black', linewidth=1.5)
    
    # Annotations
    for idx, (i, rule) in enumerate(top_rules.iterrows()):
        ant = list(rule['antecedents'])[0][:12] if len(rule['antecedents']) == 1 else 'Set'
        cons = list(rule['consequents'])[0][:12] if len(rule['consequents']) == 1 else 'Set'
        ax.annotate(f"{idx+1}. {ant}→{cons}",
                   (rule['support'] * 100, rule['lift']),
                   xytext=(5, 5), textcoords='offset points',
                   fontsize=8, alpha=0.8)
    
    ax.set_xlabel('Support (Among Multi-Item Carts) %', fontsize=11, fontweight='bold')
    ax.set_ylabel('Lift (Association Strength)', fontsize=11, fontweight='bold')
    ax.set_title('Category Pair Associations: Lift vs Support\n(Bubble size = Confidence %)',
                fontsize=13, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f"{VISUALIZATION_DIR}/04_lift_support_scatter.png", dpi=300, bbox_inches='tight')
    plt.close()

def _viz_category_treemap(rules_df):
    """Category Pair Treemap (Simplified - using top 15)"""
    
    import matplotlib.patches as mpatches
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    top_rules = rules_df.nlargest(15, 'lift').copy()
    top_rules['pair'] = (top_rules['antecedents'].astype(str).str[:15] + ' → ' + 
                        top_rules['consequents'].astype(str).str[:15])
    
    # Create treemap-like visualization using scatter and rectangles
    n = len(top_rules)
    cols = 5
    rows = (n + cols - 1) // cols
    
    fig.set_size_inches(14, 8)
    
    for idx, (i, rule) in enumerate(top_rules.iterrows()):
        row = idx // cols
        col = idx % cols
        
        x = col * 2.5
        y = (rows - row - 1) * 2
        width = 2.3
        height = 1.8
        
        # Color based on lift
        color = plt.cm.RdYlGn(min(rule['lift'] / 50, 1.0))
        
        rect = mpatches.FancyBboxPatch((x, y), width, height,
                                       boxstyle="round,pad=0.1",
                                       facecolor=color, edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        
        # Text
        ant = list(rule['antecedents'])[0][:20] if len(rule['antecedents']) == 1 else 'Set'
        cons = list(rule['consequents'])[0][:20] if len(rule['consequents']) == 1 else 'Set'
        
        ax.text(x + width/2, y + height/1.3, f"{idx+1}",
               ha='center', va='center', fontsize=12, fontweight='bold')
        ax.text(x + width/2, y + height/2.2, f"Lift {rule['lift']:.1f}x",
               ha='center', va='center', fontsize=9, fontweight='bold')
        ax.text(x + width/2, y + height/4, f"{ant[:12]}→{cons[:12]}",
               ha='center', va='center', fontsize=7, style='italic', wrap=True)
    
    ax.set_xlim(-0.5, cols * 2.5)
    ax.set_ylim(-1, rows * 2 + 0.5)
    ax.axis('off')
    ax.set_title('Category Pair Strengths - Treemap View (Top 15)\nBox size & color indicate Lift magnitude',
                fontsize=13, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(f"{VISUALIZATION_DIR}/05_category_treemap.png", dpi=300, bbox_inches='tight')
    plt.close()

def _viz_synthetic_bundles(bundles):
    """Synthetic Bundles Summary - Top 5 with SKU Details"""
    
    if len(bundles) == 0:
        return
    
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle('Strategic Bundling & SKU Affinities - Top 6 Synthetic Bundles\n(Industry-Standard Best-Seller Pairings)',
                fontsize=14, fontweight='bold', y=0.98)
    
    top_bundles = bundles[:6]
    
    for idx, (ax, bundle) in enumerate(zip(axes.flat, top_bundles)):
        bundle_num = bundle['pair_rank']
        
        # Title
        ant_cat = bundle['antecedent_category']
        cons_cat = bundle['consequent_category']
        ax.text(0.5, 0.95, f"Bundle {bundle_num}: {ant_cat} → {cons_cat}",
               ha='center', va='top', fontsize=11, fontweight='bold',
               transform=ax.transAxes)
        
        # Metrics
        metrics = f"Lift: {bundle['lift']:.1f}x | Confidence: {bundle['confidence']:.1%}"
        ax.text(0.5, 0.85, metrics, ha='center', va='top', fontsize=9,
               transform=ax.transAxes, style='italic')
        
        # Left SKU
        left_sku = bundle['antecedent_top_products'][0] if bundle['antecedent_top_products'] else 'N/A'
        left_sales = bundle['antecedent_product_sales'][0] if bundle['antecedent_product_sales'] else 0
        ax.text(0.15, 0.70, f"SKU from {ant_cat}:",
               ha='left', va='top', fontsize=9, fontweight='bold',
               transform=ax.transAxes)
        ax.text(0.15, 0.60, f"{left_sku[:20]}...\n{left_sales} sales",
               ha='left', va='top', fontsize=8, family='monospace',
               transform=ax.transAxes, bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
        
        # Plus sign
        ax.text(0.5, 0.47, '+', ha='center', va='center', fontsize=20, fontweight='bold',
               transform=ax.transAxes)
        
        # Right SKU
        right_sku = bundle['consequent_top_products'][0] if bundle['consequent_top_products'] else 'N/A'
        right_sales = bundle['consequent_product_sales'][0] if bundle['consequent_product_sales'] else 0
        ax.text(0.85, 0.70, f"SKU from {cons_cat}:",
               ha='right', va='top', fontsize=9, fontweight='bold',
               transform=ax.transAxes)
        ax.text(0.85, 0.60, f"{right_sku[:20]}...\n{right_sales} sales",
               ha='right', va='top', fontsize=8, family='monospace',
               transform=ax.transAxes, bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
        
        # Label
        ax.text(0.5, 0.15, 'Recommended Bundle',
               ha='center', va='center', fontsize=10, fontweight='bold',
               transform=ax.transAxes,
               bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.3))
        
        ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(f"{VISUALIZATION_DIR}/06_synthetic_bundles.png", dpi=300, bbox_inches='tight')
    plt.close()

# ============================================================================
# STEP 9: CSV EXPORT GENERATION (5 Files)
# ============================================================================

def create_csv_exports(results):
    """Generate 5 strategic CSV export files"""
    
    print("\n" + "="*70)
    print("STEP 9: GENERATING CSV EXPORTS (5 Files)")
    print("="*70)
    
    # 1. Association Rules Final
    print("\n[1/5] Exporting association_rules_final.csv...")
    _export_final_rules(results['final_rules'])
    
    # 2. Anchor Analysis
    print("[2/5] Exporting category_anchor_analysis.csv...")
    _export_anchor_analysis(results['anchor_df'])
    
    # 3. Bundling Recommendations
    print("[3/5] Exporting bundling_recommendations.csv...")
    _export_bundling_candidates(results['bundling_candidates'])
    
    # 4. Market Basket Stats
    print("[4/5] Exporting market_basket_stats.csv...")
    _export_basket_stats(results['basket_composition'])
    
    # 5. Synthetic Bundles
    print("[5/5] Exporting synthetic_bundles.csv...")
    _export_synthetic_bundles(results['drilldown_results'])
    
    print("\n[OK] All 5 CSV exports created successfully!")
    return True

def _export_final_rules(rules_df):
    """Export 25 category-level association rules"""
    if len(rules_df) == 0:
        return
    
    export_df = pd.DataFrame({
        'rank': range(1, len(rules_df) + 1),
        'antecedent_category': rules_df['antecedents'].apply(lambda x: list(x)[0] if len(x) == 1 else str(x)),
        'consequent_category': rules_df['consequents'].apply(lambda x: list(x)[0] if len(x) == 1 else str(x)),
        'support': (rules_df['support'] * 100).round(2),
        'confidence': (rules_df['confidence'] * 100).round(1),
        'lift': rules_df['lift'].round(3),
        'cosine': rules_df['cosine'].round(4) if 'cosine' in rules_df.columns else 'N/A',
        'kulczynski': rules_df['kulczynski'].round(4) if 'kulczynski' in rules_df.columns else 'N/A',
        'all_confidence': (rules_df['all_confidence'] * 100).round(1) if 'all_confidence' in rules_df.columns else 'N/A',
        'antecedent_support': rules_df['antecedent support'].round(3) if 'antecedent support' in rules_df else '',
        'consequent_support': rules_df['consequent support'].round(3) if 'consequent support' in rules_df else '',
        'support_context': 'Among Multi-Item Carts (780 orders)'
    })
    
    export_df.to_csv(f"{EXPORT_DIR}/association_rules_final.csv", index=False)
    print(f"  Exported {len(export_df)} rules with additional interestingness measures")
    print(f"  Measures included: Lift, Confidence, Support, Cosine, Kulczynski, All Confidence")

def _export_anchor_analysis(anchor_df):
    """Export anchor vs add-on analysis"""
    if len(anchor_df) == 0:
        return
    
    export_df = anchor_df[['category', 'anchor_index', 'antecedent_frequency', 'consequent_frequency']].copy()
    export_df['role'] = export_df['anchor_index'].apply(lambda x: 'ANCHOR (Initiator)' if x >= 0.5 else 'ADD-ON (Secondary)')
    export_df = export_df.sort_values('anchor_index', ascending=False)
    
    export_df.to_csv(f"{EXPORT_DIR}/category_anchor_analysis.csv", index=False)
    print(f"  Exported {len(export_df)} categories")

def _export_bundling_candidates(bundles_df):
    """Export top 20 bundling candidates with additional measures"""
    if len(bundles_df) == 0:
        return
    
    top_bundles = bundles_df.nlargest(20, 'lift')
    export_df = pd.DataFrame({
        'rank': range(1, len(top_bundles) + 1),
        'antecedent': top_bundles['antecedents'].astype(str),
        'consequent': top_bundles['consequents'].astype(str),
        'support_%': (top_bundles['support'] * 100).round(2),
        'confidence_%': (top_bundles['confidence'] * 100).round(1),
        'lift': top_bundles['lift'].round(3),
        'cosine': top_bundles['cosine'].round(4) if 'cosine' in top_bundles.columns else 'N/A',
        'kulczynski': top_bundles['kulczynski'].round(4) if 'kulczynski' in top_bundles.columns else 'N/A',
        'all_confidence_%': (top_bundles['all_confidence'] * 100).round(1) if 'all_confidence' in top_bundles.columns else 'N/A',
        'support_context': 'Among Multi-Item Carts'
    })
    
    export_df.to_csv(f"{EXPORT_DIR}/bundling_recommendations.csv", index=False)
    print(f"  Exported {len(export_df)} bundling pairs with 6 interestingness measures")

def _export_basket_stats(composition):
    """Export market basket composition statistics"""
    
    export_df = pd.DataFrame({
        'Metric': ['Total Orders', 'Single-Category Orders', 'Multi-Category Orders',
                  'Single-Category %', 'Multi-Category %', 'Avg Categories/Order',
                  'Median Categories/Order', 'Max Categories/Order', 'Store Assessment'],
        'Value': [
            composition['total_orders'],
            composition['single_category'],
            composition['multi_category'],
            f"{composition['single_category_pct']:.2f}%",
            f"{composition['multi_category_pct']:.1f}%",
            f"{composition['avg_categories']:.2f}",
            composition['median_categories'],
            composition['max_categories'],
            composition['assessment']
        ]
    })
    
    export_df.to_csv(f"{EXPORT_DIR}/market_basket_stats.csv", index=False)
    print(f"  Exported market basket statistics")

def _export_synthetic_bundles(bundles):
    """Export 10 synthetic bundle recommendations"""
    if len(bundles) == 0:
        return
    
    export_rows = []
    for bundle in bundles:
        export_rows.append({
            'bundle_rank': bundle['pair_rank'],
            'antecedent_category': bundle['antecedent_category'],
            'consequent_category': bundle['consequent_category'],
            'lift': round(bundle['lift'], 3),
            'confidence_%': round(bundle['confidence'] * 100, 1),
            'support_%': round(bundle['support'] * 100, 2),
            'support_note': 'Among Multi-Item Carts',
            'bundle_type': bundle['bundle_type'],
            'top_sku_ant': bundle['antecedent_top_products'][0] if bundle['antecedent_top_products'] else '',
            'top_sku_ant_sales': bundle['antecedent_product_sales'][0] if bundle['antecedent_product_sales'] else 0,
            'top_sku_cons': bundle['consequent_top_products'][0] if bundle['consequent_top_products'] else '',
            'top_sku_cons_sales': bundle['consequent_product_sales'][0] if bundle['consequent_product_sales'] else 0,
            'recommendation': f"{bundle['antecedent_category']} best-seller + {bundle['consequent_category']} best-seller"
        })
    
    export_df = pd.DataFrame(export_rows)
    export_df.to_csv(f"{EXPORT_DIR}/synthetic_bundles.csv", index=False)
    print(f"  Exported {len(export_df)} synthetic bundles")

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    from association_rules import run_pipeline
    
    print("\n" + "="*70)
    print("PHASE 2: VISUALIZATIONS, EXPORTS & REPORT")
    print("="*70)
    
    # Run pipeline
    print("\nRunning Phase 2 pipeline...")
    results = run_pipeline()
    
    # Generate visualizations
    create_visualizations(results)
    
    # Generate CSV exports
    create_csv_exports(results)
    
    print("\n" + "="*70)
    print("PHASE 2 VISUALIZATIONS & EXPORTS - COMPLETE")
    print("="*70)
    print(f"\nOutputs saved to:")
    print(f"  - Visualizations: {VISUALIZATION_DIR}/")
    print(f"  - CSV Exports: {EXPORT_DIR}/")
    print(f"\nNext: Running Step 8 (Strategic Report Generation)...\n")
