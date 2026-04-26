"""
Phase 2: Intra-Category Association Rule Mining
Discovers what PRODUCTS go together within the SAME CATEGORY

Type: Product Complementarity (within-category bundling)
Dataset: 2,417 multi-item, single-category transactions
Threshold: 1.0% support (finalized from threshold_exploration.py)
Note: Product-level sparsity is high; rules represent strong product affinities

Business Context:
  - Phone + charger (electronics)
  - Bed + pillows (furniture)
  - Shirt + pants (fashion)
  These are natural product pairs customers buy together
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from mlxtend.frequent_patterns import apriori, fpgrowth, association_rules
from mlxtend.preprocessing import TransactionEncoder
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================
REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_PATH = REPO_ROOT / 'data' / 'master_cleaned.csv'
OUTPUT_BASE_DIR = Path(__file__).resolve().parents[1] / 'outputs'
OUTPUT_DIR = OUTPUT_BASE_DIR / 'intra_category'
EXPORT_DIR = OUTPUT_DIR / 'exports'
VIZ_DIR = OUTPUT_DIR / 'visualizations'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
EXPORT_DIR.mkdir(parents=True, exist_ok=True)
VIZ_DIR.mkdir(parents=True, exist_ok=True)

# FINALIZED THRESHOLD (from threshold_exploration.py)
SUPPORT_THRESHOLD = 0.01  # 1.0% (must appear in 1%+ of intra-category orders)
MIN_CONFIDENCE = 0.30

# ============================================================================
# LOGGING SETUP
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(OUTPUT_DIR / 'intra_category_arm.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def add_interestingness_measures(rules, itemsets):
    """Add null-invariant and balance-oriented interestingness measures."""
    if len(rules) == 0:
        return rules

    itemset_support = dict(zip(itemsets['itemsets'], itemsets['support']))

    support_a = rules['antecedents'].map(itemset_support).fillna(0.0)
    support_b = rules['consequents'].map(itemset_support).fillna(0.0)
    support_ab = rules['support']

    confidence_ab = rules['confidence']
    confidence_ba = np.where(support_b > 0, support_ab / support_b, 0.0)

    denominator_cosine = np.sqrt(support_a * support_b)
    rules['cosine'] = np.where(denominator_cosine > 0, support_ab / denominator_cosine, 0.0)
    rules['kulczynski'] = (confidence_ab + confidence_ba) / 2
    rules['all_confidence'] = np.minimum(confidence_ab, confidence_ba)
    rules['max_confidence'] = np.maximum(confidence_ab, confidence_ba)

    ir_denominator = support_a + support_b - support_ab
    rules['imbalance_ratio'] = np.where(
        ir_denominator > 0,
        np.abs(support_a - support_b) / ir_denominator,
        0.0
    )

    return rules

# ============================================================================
# LOAD AND PREPARE DATA
# ============================================================================
def load_and_prepare_data():
    """Load data and create intra-category transaction baskets"""
    logger.info("="*70)
    logger.info("INTRA-CATEGORY ARM: DATA PREPARATION")
    logger.info("="*70)
    
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Input file not found: {DATA_PATH}. Expected at data/master_cleaned.csv."
        )
    df = pd.read_csv(DATA_PATH)
    
    # Count items and categories per order
    items_per_order = df.groupby('order_id').size()
    categories_per_order = df.groupby('order_id')['category'].nunique()
    
    # Filter to multi-item, single-category orders
    multi_item_single_cat = (items_per_order > 1) & (categories_per_order == 1)
    valid_orders = multi_item_single_cat[multi_item_single_cat].index.tolist()
    
    multi_item_df = df[df['order_id'].isin(valid_orders)]
    
    logger.info(f"\nOrders with 2+ items, 1 category: {len(valid_orders):,d}")
    logger.info(f"Total items in these orders: {len(multi_item_df):,d}")
    logger.info(f"Avg items per order: {len(multi_item_df)/len(valid_orders):.2f}")
    logger.info(f"Unique products involved: {multi_item_df['product_id'].nunique():,d}")
    
    # Create baskets: each order = list of unique products
    baskets = multi_item_df.groupby('order_id')['product_id'].apply(lambda x: list(x.unique())).tolist()
    
    logger.info(f"\nBaskets created: {len(baskets):,d}")
    logger.info(f"Avg unique products per basket: {np.mean([len(b) for b in baskets]):.2f}")
    
    # One-hot encode
    te = TransactionEncoder()
    te_ary = te.fit(baskets).transform(baskets)
    matrix = pd.DataFrame(te_ary, columns=te.columns_)
    
    logger.info(f"Matrix shape: {matrix.shape} ({len(te.columns_)} unique products)")
    logger.info(f"Sparsity: {(matrix == 0).sum().sum() / (matrix.shape[0] * matrix.shape[1]):.1%}")
    logger.info(f"\nNote: High sparsity is expected with {len(te.columns_):,d} products")
    logger.info("[OK] Data preparation complete\n")
    
    return matrix, df, valid_orders

# ============================================================================
# APRIORI ALGORITHM
# ============================================================================
def run_apriori(matrix):
    """Run Apriori with finalized support threshold"""
    logger.info("="*70)
    logger.info("APRIORI ALGORITHM")
    logger.info("="*70)
    logger.info(f"\nSupport threshold: {SUPPORT_THRESHOLD:.1%}")
    
    # Generate frequent itemsets
    itemsets = apriori(matrix, min_support=SUPPORT_THRESHOLD, use_colnames=True)
    logger.info(f"Frequent itemsets: {len(itemsets)}")
    
    if len(itemsets) < 2:
        logger.warning("Insufficient itemsets for rules")
        return pd.DataFrame(), itemsets
    
    # Generate association rules
    rules = association_rules(itemsets, metric="confidence", min_threshold=MIN_CONFIDENCE)
    logger.info(f"Association rules (confidence >= {MIN_CONFIDENCE:.0%}): {len(rules)}")
    
    if len(rules) > 0:
        rules = add_interestingness_measures(rules, itemsets)
        logger.info(f"  Avg support: {rules['support'].mean():.4f}")
        logger.info(f"  Avg confidence: {rules['confidence'].mean():.2%}")
        logger.info(f"  Avg lift: {rules['lift'].mean():.2f}")
        logger.info(f"  Max lift: {rules['lift'].max():.2f}")
        logger.info(f"  Avg cosine: {rules['cosine'].mean():.4f}")
        logger.info(f"  Avg kulczynski: {rules['kulczynski'].mean():.4f}")
        logger.info(f"  Avg all_confidence: {rules['all_confidence'].mean():.4f}")
        logger.info(f"  Avg max_confidence: {rules['max_confidence'].mean():.4f}")
        logger.info(f"  Avg imbalance_ratio: {rules['imbalance_ratio'].mean():.4f}")
        logger.info(f"\n  These products co-occur frequently enough to be:")
        logger.info(f"  - Recommended together")
        logger.info(f"  - Pre-bundled")
        logger.info(f"  - Cross-merchandised in store")
    
    logger.info("[OK] Apriori complete\n")
    return rules, itemsets

# ============================================================================
# FP-GROWTH ALGORITHM
# ============================================================================
def run_fpgrowth(matrix):
    """Run FP-Growth with finalized support threshold"""
    logger.info("="*70)
    logger.info("FP-GROWTH ALGORITHM")
    logger.info("="*70)
    logger.info(f"\nSupport threshold: {SUPPORT_THRESHOLD:.1%}")
    
    # Generate frequent itemsets
    itemsets = fpgrowth(matrix, min_support=SUPPORT_THRESHOLD, use_colnames=True)
    logger.info(f"Frequent itemsets: {len(itemsets)}")
    
    if len(itemsets) < 2:
        logger.warning("Insufficient itemsets for rules")
        return pd.DataFrame(), itemsets
    
    # Generate association rules
    rules = association_rules(itemsets, metric="confidence", min_threshold=MIN_CONFIDENCE)
    logger.info(f"Association rules (confidence >= {MIN_CONFIDENCE:.0%}): {len(rules)}")
    
    if len(rules) > 0:
        rules = add_interestingness_measures(rules, itemsets)
        logger.info(f"  Avg support: {rules['support'].mean():.4f}")
        logger.info(f"  Avg confidence: {rules['confidence'].mean():.2%}")
        logger.info(f"  Avg lift: {rules['lift'].mean():.2f}")
        logger.info(f"  Max lift: {rules['lift'].max():.2f}")
        logger.info(f"  Avg cosine: {rules['cosine'].mean():.4f}")
        logger.info(f"  Avg kulczynski: {rules['kulczynski'].mean():.4f}")
        logger.info(f"  Avg all_confidence: {rules['all_confidence'].mean():.4f}")
        logger.info(f"  Avg max_confidence: {rules['max_confidence'].mean():.4f}")
        logger.info(f"  Avg imbalance_ratio: {rules['imbalance_ratio'].mean():.4f}")
    
    logger.info("[OK] FP-Growth complete\n")
    return rules, itemsets

# ============================================================================
# ALGORITHM CONVERGENCE VALIDATION
# ============================================================================
def validate_convergence(apriori_rules, fpgrowth_rules):
    """Validate that both algorithms produce the same rules"""
    logger.info("="*70)
    logger.info("ALGORITHM CONVERGENCE VALIDATION")
    logger.info("="*70)
    
    apriori_count = len(apriori_rules)
    fpgrowth_count = len(fpgrowth_rules)
    
    logger.info(f"\nApriori rules: {apriori_count}")
    logger.info(f"FP-Growth rules: {fpgrowth_count}")
    
    if apriori_count == fpgrowth_count:
        logger.info("[OK] 100% CONVERGENCE: Both algorithms produced identical rule counts")
        convergence_status = "PASS"
    else:
        logger.warning(f"[WARNING] Algorithms diverged by {abs(apriori_count - fpgrowth_count)} rules")
        convergence_status = "WARN"
    
    logger.info(f"\nConvergence status: {convergence_status}\n")
    return convergence_status


def save_visualizations(output_rules):
    """Save professional visualizations for intra-category rules."""
    if len(output_rules) == 0:
        logger.warning("No rules available for visualizations")
        return

    sns.set_theme(style="whitegrid", context="talk")

    # 1) Top rules by lift
    top_rules = output_rules.head(15).copy()
    top_rules['rule'] = top_rules['antecedents'] + ' -> ' + top_rules['consequents']

    plt.figure(figsize=(14, 9))
    sns.barplot(
        data=top_rules.iloc[::-1],
        x='lift',
        y='rule',
        hue='lift',
        palette='viridis',
        legend=False
    )
    plt.xlabel('Lift')
    plt.ylabel('Association Rule')
    plt.title('Top Intra-Category Product Rules by Lift', pad=20)
    plt.tight_layout()
    plt.savefig(VIZ_DIR / '01_top_rules_by_lift.png', dpi=300)
    plt.close()

    # 2) Support vs confidence with interestingness overlays
    plt.figure(figsize=(10, 7))
    scatter = plt.scatter(
        output_rules['support'],
        output_rules['confidence'],
        c=output_rules['kulczynski'],
        s=(output_rules['max_confidence'] * 450) + 40,
        cmap='plasma',
        alpha=0.85,
        edgecolors='black',
        linewidths=0.4
    )
    plt.colorbar(scatter, label='Kulczynski')
    plt.xlabel('Support')
    plt.ylabel('Confidence')
    plt.title('Support vs Confidence (size = MaxConfidence, color = Kulczynski)')
    plt.tight_layout()
    plt.savefig(VIZ_DIR / '02_support_confidence_kulczynski.png', dpi=300)
    plt.close()

    # 3) Interestingness profile heatmap
    top_heat = output_rules.head(12).copy()
    # Truncate rule names for better display
    top_heat['rule'] = (top_heat['antecedents'] + ' -> ' + top_heat['consequents']).apply(lambda x: x[:45] + '...' if len(x) > 45 else x)
    metric_cols = ['support', 'confidence', 'lift', 'cosine', 'kulczynski', 'all_confidence', 'max_confidence', 'imbalance_ratio']
    heat_df = top_heat.set_index('rule')[metric_cols]
    plt.figure(figsize=(15, 10))
    # Normalize each column for color mapping only
    col_min = heat_df.min()
    col_max = heat_df.max()
    heat_df_norm = (heat_df - col_min) / (col_max - col_min)
    heat_df_norm = heat_df_norm.fillna(0.5)  # Handle columns with same values

    sns.heatmap(heat_df_norm, cmap='YlGnBu', annot=heat_df, fmt='.3f', annot_kws={"size": 9}, cbar_kws={'label': 'Relative Strength'})
    plt.title('Interestingness Metrics for Intra-Category Rules', pad=20)
    plt.xlabel('Metrics')
    plt.ylabel('Rules')
    plt.tight_layout()
    plt.savefig(VIZ_DIR / '03_interestingness_heatmap.png', dpi=300)
    plt.close()

    logger.info(f"Visualizations saved to: {VIZ_DIR}")

# ============================================================================
# OUTPUT RESULTS
# ============================================================================
def save_results(rules, convergence_status, df, valid_orders):
    """Save rules and metrics to CSV with product context"""
    logger.info("="*70)
    logger.info("SAVING RESULTS")
    logger.info("="*70)
    
    if len(rules) == 0:
        logger.warning("No rules found at this support threshold")
        logger.info("Note: This is expected given high product sparsity (3,677 products)")
        return
    
    # Format rules for export
    output_rules = rules[[
        'antecedents', 'consequents', 'support', 'confidence', 'lift',
        'cosine', 'kulczynski', 'all_confidence', 'max_confidence', 'imbalance_ratio'
    ]].copy()
    output_rules['antecedents'] = output_rules['antecedents'].apply(lambda x: ', '.join(sorted(list(x))))
    output_rules['consequents'] = output_rules['consequents'].apply(lambda x: ', '.join(sorted(list(x))))
    
    # Sort by lift
    output_rules = output_rules.sort_values('lift', ascending=False)
    
    # Save primary output
    output_path = OUTPUT_DIR / 'intra_category_rules.csv'
    output_rules.to_csv(output_path, index=False)
    logger.info(f"\nRules saved to: {output_path}")

    # Save non-duplicate analytical exports
    output_rules.sort_values(['kulczynski', 'lift'], ascending=[False, False]).head(20).to_csv(
        EXPORT_DIR / 'intra_category_top20_kulczynski.csv', index=False
    )
    output_rules.sort_values(['imbalance_ratio', 'kulczynski'], ascending=[True, False]).head(20).to_csv(
        EXPORT_DIR / 'intra_category_top20_balanced_rules.csv', index=False
    )
    metric_snapshot = pd.DataFrame([{
        'rules_count': len(output_rules),
        'avg_support': output_rules['support'].mean(),
        'avg_confidence': output_rules['confidence'].mean(),
        'avg_lift': output_rules['lift'].mean(),
        'avg_cosine': output_rules['cosine'].mean(),
        'avg_kulczynski': output_rules['kulczynski'].mean(),
        'avg_all_confidence': output_rules['all_confidence'].mean(),
        'avg_max_confidence': output_rules['max_confidence'].mean(),
        'avg_imbalance_ratio': output_rules['imbalance_ratio'].mean()
    }])
    metric_snapshot.to_csv(EXPORT_DIR / 'intra_category_metrics_snapshot.csv', index=False)
    logger.info(f"Exports saved to: {EXPORT_DIR}")
    
    # Summary
    summary_path = OUTPUT_DIR / 'intra_category_summary.txt'
    with open(summary_path, 'w') as f:
        f.write("INTRA-CATEGORY ASSOCIATION RULES SUMMARY\n")
        f.write("="*70 + "\n\n")
        f.write(f"Dataset: 2,417 multi-item, single-category orders\n")
        f.write(f"Products analyzed: 3,677 unique SKUs\n")
        f.write(f"Support threshold: {SUPPORT_THRESHOLD:.1%} (1%+ of intra-category orders)\n")
        f.write(f"Confidence threshold: {MIN_CONFIDENCE:.0%}\n\n")
        f.write(f"Total rules: {len(rules)}\n")
        if len(rules) > 0:
            f.write(f"Avg lift: {rules['lift'].mean():.2f}\n")
            f.write(f"Max lift: {rules['lift'].max():.2f}\n")
            f.write(f"Avg cosine: {rules['cosine'].mean():.4f}\n")
            f.write(f"Avg kulczynski: {rules['kulczynski'].mean():.4f}\n")
            f.write(f"Avg all_confidence: {rules['all_confidence'].mean():.4f}\n")
            f.write(f"Avg max_confidence: {rules['max_confidence'].mean():.4f}\n")
            f.write(f"Avg imbalance_ratio: {rules['imbalance_ratio'].mean():.4f}\n")
        f.write(f"Convergence: {convergence_status}\n\n")
        f.write("Business Application:\n")
        f.write("  - Product bundling recommendations\n")
        f.write("  - Cross-merchandising strategy\n")
        f.write("  - Inventory positioning\n")
    
    logger.info(f"Summary saved to: {summary_path}")
    save_visualizations(output_rules)
    logger.info("[OK] Results saved\n")

# ============================================================================
# MAIN
# ============================================================================
def main():
    logger.info("\n" + "="*70)
    logger.info("PHASE 2: INTRA-CATEGORY ASSOCIATION RULE MINING")
    logger.info("="*70 + "\n")
    
    # Load and prepare data
    matrix, df, valid_orders = load_and_prepare_data()
    
    # Run both algorithms
    apriori_rules, _ = run_apriori(matrix)
    fpgrowth_rules, _ = run_fpgrowth(matrix)
    
    # Validate convergence
    convergence_status = validate_convergence(apriori_rules, fpgrowth_rules)
    
    # Use Apriori results as final output
    final_rules = apriori_rules
    
    # Save results
    save_results(final_rules, convergence_status, df, valid_orders)
    
    logger.info("="*70)
    logger.info("INTRA-CATEGORY ARM COMPLETE")
    logger.info("="*70 + "\n")

if __name__ == "__main__":
    main()
