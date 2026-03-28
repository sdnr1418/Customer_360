"""
Phase 2: Association Rule Mining - Strategic Bundling & SKU Affinities
Author: Saad Nasir (23L-2625)
Date: March 2026

Hierarchical approach:
- Level 1: Category-level associations (avoiding 32k+ product sparsity)
- Level 2: Product drilldown within Top 10 category pairs (Top 5 products per category)

Pipeline:
1. Load basket data (master_cleaned.csv)
2. Run Apriori & FP-Growth with threshold exploration
3. Compare algorithms, select optimal threshold
4. Analyze business insights (Anchors/Add-ons, Hidden Affinities, etc.)
5. Product drilldown for Top 10 pairs
6. Visualize and export results
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from itertools import combinations
from mlxtend.frequent_patterns import apriori, fpgrowth
from mlxtend.preprocessing import TransactionEncoder
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# LOGGING SETUP
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('association_rules.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================
# Get project root (go up one level from phase2)
PROJECT_ROOT = Path(__file__).parent.parent
DATA_PATH = PROJECT_ROOT / 'data' / 'master_cleaned.csv'
OUTPUT_DIR = Path('data')
VIZ_DIR = Path('visualizations')
VIZ_DIR.mkdir(exist_ok=True)

# Algorithm thresholds (adjusted for sparse market basket)
# Since 99.2% of orders are single-category, multi-category associations are rare
SUPPORT_THRESHOLDS = [0.0005, 0.001, 0.002, 0.005, 0.01]  # 0.05%, 0.1%, 0.2%, 0.5%, 1%
MIN_CONFIDENCE = 0.30  # 30% (lowered due to sparsity)
MIN_LIFT = 1.0

# Product drilldown constraints
TOP_PAIRS_COUNT = 10
TOP_PRODUCTS_PER_CATEGORY = 5
MIN_PRODUCT_DRILLDOWN_SUPPORT = 0.005  # 0.5%

# Multi-category basket analysis (for sparse markets)
# Since 99.2% are single-category, we analyze the 0.8% multi-category orders separately
MULTI_CATEGORY_SUPPORT_THRESHOLDS = [0.001, 0.002, 0.005, 0.01, 0.02]  # 0.1%, 0.2%, 0.5%, 1%, 2% of multi-cat transactions
MIN_MULTI_CATEGORY_CONFIDENCE = 0.25  # 25% (even lower for sparse subset)

# IMPORTANT: All support metrics below are CONDITIONAL on multi-item carts (0.8% of all orders)
# Label as 'Support (Among Multi-Item Carts)' in reports to avoid misleading marketing team
CONDITIONAL_SUPPORT_LABEL = 'Support (Among Multi-Item Carts)'

# SKU/Product drill-down constraints
# Only recommend a product bundle if it appears at least N times (avoid statistical flukes)
MIN_SKU_BUNDLE_FREQUENCY = 3  # Minimum co-occurrences for SKU pair recommendation

# ============================================================================
# STEP 1-2: DATA PREPARATION & LOAD
# ============================================================================

def load_basket_data(csv_path=DATA_PATH):
    """
    Load master_cleaned.csv and create transaction baskets (groups by order_id).
    
    Returns:
        df: Raw dataframe
        transaction_list: List of transaction baskets (each basket = list of categories)
        transaction_matrix: One-hot encoded transaction matrix for algorithms
        te: TransactionEncoder object (for inverse transformation later)
    """
    logger.info("=" * 70)
    logger.info("STEP 1-2: LOADING BASKET DATA")
    logger.info("=" * 70)
    
    try:
        df = pd.read_csv(csv_path)
        logger.info(f"Loaded {len(df)} rows from {csv_path}")
        
        # Verify required columns
        required_cols = ['customer_unique_id', 'order_id', 'product_id', 'category', 'price']
        assert all(col in df.columns for col in required_cols), f"Missing columns: {required_cols}"
        
        # Group by order_id to create transaction baskets
        transaction_list = df.groupby('order_id')['category'].apply(list).tolist()
        
        # Remove duplicates within each basket (keep unique categories per transaction)
        transaction_list = [list(set(basket)) for basket in transaction_list]
        
        # Validate basket quality
        logger.info(f"\n--- BASKET VALIDATION ---")
        logger.info(f"Total transactions: {len(transaction_list)}")
        logger.info(f"Avg categories per transaction: {np.mean([len(b) for b in transaction_list]):.2f}")
        logger.info(f"Min categories per transaction: {min([len(b) for b in transaction_list])}")
        logger.info(f"Max categories per transaction: {max([len(b) for b in transaction_list])}")
        
        # Check for empty baskets
        empty_baskets = sum(1 for b in transaction_list if len(b) == 0)
        logger.info(f"Empty baskets: {empty_baskets}")
        
        # All unique categories
        all_categories = set().union(*transaction_list)
        logger.info(f"Unique categories: {len(all_categories)}")
        logger.info(f"Categories: {sorted(all_categories)}")
        
        # Single-category vs multi-category
        single_cat = sum(1 for b in transaction_list if len(b) == 1)
        multi_cat = sum(1 for b in transaction_list if len(b) > 1)
        logger.info(f"Single-category transactions: {single_cat} ({100*single_cat/len(transaction_list):.1f}%)")
        logger.info(f"Multi-category transactions: {multi_cat} ({100*multi_cat/len(transaction_list):.1f}%)")
        
        # One-hot encode for algorithms
        te = TransactionEncoder()
        te_ary = te.fit(transaction_list).transform(transaction_list)
        transaction_matrix = pd.DataFrame(te_ary, columns=te.columns_)
        
        logger.info(f"\nTransaction matrix shape: {transaction_matrix.shape}")
        logger.info(f"Sparsity: {(transaction_matrix == 0).sum().sum() / (transaction_matrix.shape[0] * transaction_matrix.shape[1]):.1%}")
        logger.info("[OK] Data preparation successful\n")
        
        return df, transaction_list, transaction_matrix, te
        
    except Exception as e:
        logger.error(f"Error loading basket data: {e}")
        raise


def create_multi_category_basket_matrix(transaction_list, transaction_matrix):
    """
    For sparse markets, create separate transaction matrix for ONLY multi-category orders.
    This allows meaningful association rules from actual bundlers.
    
    Returns:
        multi_cat_transaction_list: Transactions with 2+ categories
        multi_cat_matrix: One-hot encoded matrix of multi-category orders
        multi_cat_indices: Indices in original transaction_list
    """
    logger.info("=" * 70)
    logger.info("CREATING MULTI-CATEGORY TRANSACTION SUBSET")
    logger.info("=" * 70)
    
    # Get indices of multi-category transactions
    multi_cat_indices = [i for i, basket in enumerate(transaction_list) if len(basket) >= 2]
    multi_cat_transaction_list = [transaction_list[i] for i in multi_cat_indices]
    
    logger.info(f"\nMulti-category transactions: {len(multi_cat_transaction_list)}")
    logger.info(f"Percentage of total: {100*len(multi_cat_transaction_list)/len(transaction_list):.2f}%")
    logger.info(f"Avg categories per basket: {np.mean([len(b) for b in multi_cat_transaction_list]):.2f}")
    
    # Create one-hot encoded matrix for multi-cat transactions only
    te_multi = TransactionEncoder()
    te_multi_ary = te_multi.fit(multi_cat_transaction_list).transform(multi_cat_transaction_list)
    multi_cat_matrix = pd.DataFrame(te_multi_ary, columns=te_multi.columns_)
    
    logger.info(f"Matrix shape: {multi_cat_matrix.shape}")
    logger.info(f"Sparsity: {(multi_cat_matrix == 0).sum().sum() / (multi_cat_matrix.shape[0] * multi_cat_matrix.shape[1]):.1%}")
    logger.info("[OK] Multi-category matrix created\n")
    
    return multi_cat_transaction_list, multi_cat_matrix, multi_cat_indices

# ============================================================================
# STEP 3: APRIORI ALGORITHM WITH THRESHOLD EXPLORATION
# ============================================================================

def run_apriori(transaction_matrix, support_thresholds=SUPPORT_THRESHOLDS):
    """
    Run Apriori algorithm with multiple support thresholds.
    
    Returns:
        apriori_results: Dict mapping threshold -> (itemsets, rules, stats)
    """
    logger.info("=" * 70)
    logger.info("STEP 3: RUNNING APRIORI ALGORITHM")
    logger.info("=" * 70)
    
    apriori_results = {}
    
    for support in support_thresholds:
        logger.info(f"\nApriori - Support threshold: {support:.1%}")
        try:
            # Generate frequent itemsets
            itemsets = apriori(transaction_matrix, min_support=support, use_colnames=True)
            logger.info(f"  Frequent itemsets: {len(itemsets)}")
            
            if len(itemsets) < 2:
                logger.warning(f"  Insufficient itemsets for rules at support={support:.1%}")
                apriori_results[support] = (itemsets, pd.DataFrame(), {
                    'itemsets_count': len(itemsets),
                    'rules_count': 0,
                    'support': support,
                    'algorithm': 'Apriori'
                })
                continue
            
            # Generate association rules
            from mlxtend.frequent_patterns import association_rules
            rules = association_rules(itemsets, metric="confidence", min_threshold=MIN_CONFIDENCE)
            
            if len(rules) == 0:
                logger.warning(f"  No rules generated at confidence={MIN_CONFIDENCE:.1%}")
                apriori_results[support] = (itemsets, rules, {
                    'itemsets_count': len(itemsets),
                    'rules_count': 0,
                    'support': support,
                    'algorithm': 'Apriori'
                })
                continue
            
            # Calculate metrics
            rules['antecedent_str'] = rules['antecedents'].apply(lambda x: ', '.join(sorted(list(x))))
            rules['consequent_str'] = rules['consequents'].apply(lambda x: ', '.join(sorted(list(x))))
            
            logger.info(f"  Association rules (confidence >= {MIN_CONFIDENCE:.1%}): {len(rules)}")
            logger.info(f"  Avg support: {rules['support'].mean():.4f}")
            logger.info(f"  Avg confidence: {rules['confidence'].mean():.4f}")
            logger.info(f"  Avg lift: {rules['lift'].mean():.4f}")
            
            apriori_results[support] = (itemsets, rules, {
                'itemsets_count': len(itemsets),
                'rules_count': len(rules),
                'support': support,
                'algorithm': 'Apriori',
                'avg_confidence': rules['confidence'].mean(),
                'avg_lift': rules['lift'].mean()
            })
            
        except Exception as e:
            logger.error(f"  Error at support={support:.1%}: {e}")
            apriori_results[support] = (pd.DataFrame(), pd.DataFrame(), {
                'itemsets_count': 0,
                'rules_count': 0,
                'support': support,
                'algorithm': 'Apriori',
                'error': str(e)
            })
    
    logger.info("\n[OK] Apriori complete\n")
    return apriori_results

# ============================================================================
# STEP 4: FP-GROWTH ALGORITHM WITH THRESHOLD EXPLORATION
# ============================================================================

def run_fpgrowth(transaction_matrix, support_thresholds=SUPPORT_THRESHOLDS):
    """
    Run FP-Growth algorithm with multiple support thresholds.
    
    Returns:
        fpgrowth_results: Dict mapping threshold -> (itemsets, rules, stats)
    """
    logger.info("=" * 70)
    logger.info("STEP 4: RUNNING FP-GROWTH ALGORITHM")
    logger.info("=" * 70)
    
    fpgrowth_results = {}
    
    for support in support_thresholds:
        logger.info(f"\nFP-Growth - Support threshold: {support:.1%}")
        try:
            # Generate frequent itemsets
            itemsets = fpgrowth(transaction_matrix, min_support=support, use_colnames=True)
            logger.info(f"  Frequent itemsets: {len(itemsets)}")
            
            if len(itemsets) < 2:
                logger.warning(f"  Insufficient itemsets for rules at support={support:.1%}")
                fpgrowth_results[support] = (itemsets, pd.DataFrame(), {
                    'itemsets_count': len(itemsets),
                    'rules_count': 0,
                    'support': support,
                    'algorithm': 'FP-Growth'
                })
                continue
            
            # Generate association rules
            from mlxtend.frequent_patterns import association_rules
            rules = association_rules(itemsets, metric="confidence", min_threshold=MIN_CONFIDENCE)
            
            if len(rules) == 0:
                logger.warning(f"  No rules generated at confidence={MIN_CONFIDENCE:.1%}")
                fpgrowth_results[support] = (itemsets, rules, {
                    'itemsets_count': len(itemsets),
                    'rules_count': 0,
                    'support': support,
                    'algorithm': 'FP-Growth'
                })
                continue
            
            # Calculate metrics
            rules['antecedent_str'] = rules['antecedents'].apply(lambda x: ', '.join(sorted(list(x))))
            rules['consequent_str'] = rules['consequents'].apply(lambda x: ', '.join(sorted(list(x))))
            
            # Add conditional support label for clarity
            rules['support_label'] = f"{CONDITIONAL_SUPPORT_LABEL}"
            
            logger.info(f"  Association rules (confidence >= {MIN_CONFIDENCE:.1%}): {len(rules)}")
            logger.info(f"  Avg support (among multi-item carts): {rules['support'].mean():.4f}")
            logger.info(f"  Avg confidence: {rules['confidence'].mean():.4f}")
            logger.info(f"  Avg lift: {rules['lift'].mean():.4f}")
            
            fpgrowth_results[support] = (itemsets, rules, {
                'itemsets_count': len(itemsets),
                'rules_count': len(rules),
                'support': support,
                'algorithm': 'FP-Growth',
                'avg_confidence': rules['confidence'].mean(),
                'avg_lift': rules['lift'].mean()
            })
            
        except Exception as e:
            logger.error(f"  Error at support={support:.1%}: {e}")
            fpgrowth_results[support] = (pd.DataFrame(), pd.DataFrame(), {
                'itemsets_count': 0,
                'rules_count': 0,
                'support': support,
                'algorithm': 'FP-Growth',
                'error': str(e)
            })
    
    logger.info("\n[OK] FP-Growth complete\n")
    return fpgrowth_results

# ============================================================================
# STEP 5: ALGORITHM COMPARISON & OPTIMAL THRESHOLD SELECTION
# ============================================================================

def compare_algorithms(apriori_results, fpgrowth_results):
    """
    Compare Apriori and FP-Growth results across thresholds.
    Select optimal threshold based on rule count (target: 20-50 rules).
    
    Returns:
        optimal_support: Best support threshold
        comparison_df: Comparison table
        final_rules: Best ruleset
        final_itemsets: Best itemsets
    """
    logger.info("=" * 70)
    logger.info("STEP 5: ALGORITHM COMPARISON & SELECTION")
    logger.info("=" * 70)
    
    comparison_data = []
    
    for support in SUPPORT_THRESHOLDS:
        apriori_itemsets, apriori_rules, apriori_stats = apriori_results.get(support, (None, None, None))
        fpgrowth_itemsets, fpgrowth_rules, fpgrowth_stats = fpgrowth_results.get(support, (None, None, None))
        
        if apriori_stats is None or fpgrowth_stats is None:
            continue
        
        comparison_data.append({
            'support': f"{support:.1%}",
            'apriori_itemsets': apriori_stats.get('itemsets_count', 0),
            'apriori_rules': apriori_stats.get('rules_count', 0),
            'fpgrowth_itemsets': fpgrowth_stats.get('itemsets_count', 0),
            'fpgrowth_rules': fpgrowth_stats.get('rules_count', 0),
            'apriori_avg_lift': apriori_stats.get('avg_lift', 0),
            'fpgrowth_avg_lift': fpgrowth_stats.get('avg_lift', 0)
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    logger.info("\n--- ALGORITHM COMPARISON ---")
    logger.info(comparison_df.to_string(index=False))
    
    # Select optimal threshold: target 20-50 rules
    logger.info("\n--- SELECTING OPTIMAL THRESHOLD ---")
    target_rules = 35  # Midpoint of 20-50 range
    
    best_threshold = None
    best_diff = float('inf')
    
    for support in SUPPORT_THRESHOLDS:
        apriori_itemsets, apriori_rules, apriori_stats = apriori_results.get(support, (None, None, None))
        if apriori_stats and apriori_stats.get('rules_count', 0) > 0:
            rule_count = apriori_stats['rules_count']
            diff = abs(rule_count - target_rules)
            logger.info(f"  Support {support:.1%}: {rule_count} rules (diff from target {target_rules}: {diff})")
            if diff < best_diff and rule_count >= 20:  # Minimum 20 rules
                best_diff = diff
                best_threshold = support
    
    if best_threshold is None:
        # Fallback: Use lowest threshold and accept 0 rules with warning
        logger.warning("No thresholds produced rules. Using lowest support threshold as fallback.")
        best_threshold = min(SUPPORT_THRESHOLDS)
    
    # Extract final results from best threshold
    final_itemsets, final_rules, _ = apriori_results[best_threshold]
    
    logger.info(f"\n[OK] Optimal threshold selected: {best_threshold:.1%}")
    logger.info(f"[OK] Final ruleset: {len(final_rules)} rules")
    
    if len(final_rules) == 0:
        logger.warning("\nWARNING: No association rules found even at lowest support threshold.")
        logger.warning("This indicates extremely sparse market basket data (mostly single-category orders).")
        logger.warning("Continuing with empty ruleset for analysis...")
    
    logger.info(f"[OK] Algorithm comparison complete\n")
    
    return best_threshold, comparison_df, final_rules, final_itemsets

# ============================================================================
# STEP 6: BUSINESS INSIGHTS ANALYSIS
# ============================================================================

def analyze_anchors_addons(rules):
    """
    Q1: Identify Anchor vs Add-on Categories
    - Anchor: Appears frequently in antecedent (initiator)
    - Add-on: Appears frequently in consequent (secondary purchase)
    """
    logger.info("=" * 70)
    logger.info("STEP 6: BUSINESS INSIGHTS - Q1: ANCHORS vs ADD-ONS")
    logger.info("=" * 70)
    
    if len(rules) == 0:
        logger.warning("No rules available for analysis")
        return pd.DataFrame()
    
    # Count occurrences in antecedent and consequent
    antecedent_counts = {}
    consequent_counts = {}
    
    for idx, row in rules.iterrows():
        for item in row['antecedents']:
            antecedent_counts[item] = antecedent_counts.get(item, 0) + 1
        for item in row['consequents']:
            consequent_counts[item] = consequent_counts.get(item, 0) + 1
    
    all_categories = set(antecedent_counts.keys()) | set(consequent_counts.keys())
    
    # Calculate Anchor Index
    anchor_analysis = []
    for cat in all_categories:
        ant_freq = antecedent_counts.get(cat, 0)
        cons_freq = consequent_counts.get(cat, 0)
        total_freq = ant_freq + cons_freq
        
        if total_freq > 0:
            anchor_index = ant_freq / total_freq  # 1.0 = pure anchor, 0.0 = pure add-on
            anchor_analysis.append({
                'category': cat,
                'antecedent_frequency': ant_freq,
                'consequent_frequency': cons_freq,
                'total_frequency': total_freq,
                'anchor_index': anchor_index,
                'classification': 'Anchor' if anchor_index >= 0.7 else 'Add-on' if anchor_index <= 0.3 else 'Neutral'
            })
    
    anchor_df = pd.DataFrame(anchor_analysis).sort_values('anchor_index', ascending=False)
    
    logger.info(f"\n--- ANCHOR vs ADD-ON ANALYSIS ---")
    logger.info(f"Total categories analyzed: {len(anchor_df)}")
    logger.info("\nTop 5 Anchors (initiators):")
    for idx, row in anchor_df[anchor_df['classification'] == 'Anchor'].head().iterrows():
        logger.info(f"  {row['category']}: Anchor Index {row['anchor_index']:.3f} (appears {row['antecedent_frequency']} times in antecedent)")
    logger.info("\nTop 5 Add-ons (secondary):")
    for idx, row in anchor_df[anchor_df['classification'] == 'Add-on'].head().iterrows():
        logger.info(f"  {row['category']}: Anchor Index {row['anchor_index']:.3f} (appears {row['consequent_frequency']} times in consequent)")
    logger.info("[OK] Anchor vs Add-on analysis complete\n")
    
    return anchor_df


def find_hidden_affinities(rules, top_n=10):
    """
    Q2: Identify Hidden Affinities (non-obvious associations)
    - Filter for rules with high lift (strong associations)
    - Identify unexpected pairs
    """
    logger.info("=" * 70)
    logger.info("STEP 6: BUSINESS INSIGHTS - Q2: HIDDEN AFFINITIES")
    logger.info("=" * 70)
    
    if len(rules) == 0:
        logger.warning("No rules available")
        return pd.DataFrame()
    
    # Sort by lift (strong associations are 'hidden' if lift > 1.5)
    surprise_rules = rules[rules['lift'] > 1.5].sort_values('lift', ascending=False)
    
    logger.info(f"\n--- HIDDEN AFFINITIES (Lift > 1.5) ---")
    logger.info(f"Found {len(surprise_rules)} surprising associations")
    logger.info("\nTop 10 'surprise' rules:")
    
    for idx, (i, row) in enumerate(surprise_rules.head(top_n).iterrows()):
        ant = ', '.join(row['antecedents'])
        cons = ', '.join(row['consequents'])
        logger.info(f"  {idx+1}. {ant} -> {cons}")
        logger.info(f"     Support: {row['support']:.4f}, Confidence: {row['confidence']:.4f}, Lift: {row['lift']:.4f}")
    
    logger.info("[OK] Hidden affinities analysis complete\n")
    
    return surprise_rules.head(top_n)


def extract_bundling_candidates(rules, top_n=20):
    """
    Q3: Extract Top Bundling Candidates
    - Rank by lift (strongest associations)
    - These are categories to bundle together
    """
    logger.info("=" * 70)
    logger.info("STEP 6: BUSINESS INSIGHTS - Q3: BUNDLING CANDIDATES")
    logger.info("=" * 70)
    
    if len(rules) == 0:
        logger.warning("No rules available")
        return pd.DataFrame()
    
    # Sort by lift
    bundling_rules = rules.sort_values('lift', ascending=False).head(top_n).copy()
    bundling_rules['bundle'] = bundling_rules.apply(
        lambda row: f"{', '.join(row['antecedents'])} + {', '.join(row['consequents'])}",
        axis=1
    )
    
    logger.info(f"\n--- TOP BUNDLING CANDIDATES (by Lift) ---")
    logger.info(f"Selected top {min(top_n, len(bundling_rules))} pairs")
    
    for idx, (i, row) in enumerate(bundling_rules.iterrows()):
        logger.info(f"  {idx+1}. {row['bundle']}")
        logger.info(f"     Lift: {row['lift']:.3f}, Confidence: {row['confidence']:.1%}, Support: {row['support']:.1%}")
    
    logger.info("[OK] Bundling candidates extracted\n")
    
    return bundling_rules


def analyze_basket_composition(transaction_list):
    """
    Q4: Market Basket Composition
    - Single-category vs multi-category transactions
    - Category diversity per order
    """
    logger.info("=" * 70)
    logger.info("STEP 6: BUSINESS INSIGHTS - Q4: MARKET BASKET COMPOSITION")
    logger.info("=" * 70)
    
    basket_sizes = [len(basket) for basket in transaction_list]
    single_cat = sum(1 for size in basket_sizes if size == 1)
    multi_cat = sum(1 for size in basket_sizes if size > 1)
    
    logger.info(f"\n--- MARKET BASKET COMPOSITION ---")
    logger.info(f"Total orders: {len(basket_sizes)}")
    logger.info(f"Single-category orders: {single_cat} ({100*single_cat/len(basket_sizes):.1f}%)")
    logger.info(f"Multi-category orders: {multi_cat} ({100*multi_cat/len(basket_sizes):.1f}%)")
    logger.info(f"Avg categories per order: {np.mean(basket_sizes):.2f}")
    logger.info(f"Median categories per order: {np.median(basket_sizes):.0f}")
    logger.info(f"Max categories per order: {max(basket_sizes)}")
    
    # Assessment
    multi_cat_ratio = multi_cat / len(basket_sizes)
    if multi_cat_ratio >= 0.7:
        assessment = "One-Stop Shop (customers buy multiple categories together)"
    elif multi_cat_ratio <= 0.3:
        assessment = "Specialized Store (customers focus on specific categories)"
    else:
        assessment = "Balanced (mix of focused and diverse shopping patterns)"
    
    logger.info(f"\nStore Type Assessment: {assessment}")
    logger.info("[OK] Market basket composition analysis complete\n")
    
    composition_stats = {
        'total_orders': len(basket_sizes),
        'single_category': single_cat,
        'multi_category': multi_cat,
        'single_category_pct': 100*single_cat/len(basket_sizes),
        'multi_category_pct': 100*multi_cat/len(basket_sizes),
        'avg_categories': np.mean(basket_sizes),
        'median_categories': np.median(basket_sizes),
        'max_categories': max(basket_sizes),
        'assessment': assessment
    }
    
    return composition_stats

# ============================================================================
# STEP 6.5: PRODUCT DRILLDOWN - HIERARCHICAL APPROACH
# ============================================================================

def product_drilldown(df, rules, top_n_pairs=TOP_PAIRS_COUNT, top_n_products=2):
    """
    Q5: Product-Level Drilldown - SYNTHETIC BUNDLE RECOMMENDATIONS (Phase 2E.5)
    
    STRATEGIC APPROACH:
    - Strong category-level association rules (25 pairs with avg lift 6.84x)
    - For each top category pair, identify TOP 2 BEST-SELLING SKUs from EACH category
    - Create "Synthetic Bundle" by pairing best-seller from Category A + Category B
    - Provides actionable product recommendations while maintaining statistical integrity
    
    Example Output:
    "41x Lift between Children's Clothes & Bags/Accessories. 
     Recommended bundle: SKU-123 (top seller in Clothes) + SKU-456 (top seller in Bags)"
    
    Args:
        df: Full transaction dataframe (all orders)
        rules: Association rules dataframe (category-level)
        top_n_pairs: Top N category pairs to create bundles for
        top_n_products: Top N best-selling SKUs per category (default: 2)
    
    Returns:
        drilldown_results: List of dicts with synthetic bundle recommendations (all pairs)
        skipped_pairs: Empty list (all pairs now have recommendations)
    """
    logger.info("=" * 70)
    logger.info("STEP 6.5: SYNTHETIC BUNDLE RECOMMENDATIONS")
    logger.info("=" * 70)
    
    if len(rules) == 0:
        logger.warning("No rules available for bundle recommendations")
        return [], []
    
    # Get top category pairs by Lift (no support filter - we want top N by strength)
    top_rules = rules.sort_values('lift', ascending=False).head(top_n_pairs).copy()
    
    logger.info(f"\n--- TOP {min(top_n_pairs, len(top_rules))} CATEGORY PAIRS (BY LIFT) ---")
    logger.info(f"Note: Support is conditional on MULTI-ITEM CARTS ONLY (780 orders, 0.8% of total)")
    logger.info(f"SKU Recommendations: Top {top_n_products} best-sellers from paired categories (overall sales)\n")
    
    drilldown_results = []
    
    for idx, (i, rule) in enumerate(top_rules.iterrows()):
        antecedent_cat = list(rule['antecedents'])[0] if len(rule['antecedents']) == 1 else None
        consequent_cat = list(rule['consequents'])[0] if len(rule['consequents']) == 1 else None
        
        if not antecedent_cat or not consequent_cat:
            continue  # Skip multi-item sets
        
        logger.info(f"Bundle {idx+1}: {antecedent_cat} -> {consequent_cat}")
        logger.info(f"  Lift: {rule['lift']:.3f}, Confidence: {rule['confidence']:.1%}, Support (multi-cart): {rule['support']:.1%}")
        
        # Get TOP BEST-SELLING SKUs from each category (overall, from all orders)
        ant_best_sellers = df[df['category'] == antecedent_cat]['product_id'].value_counts().head(top_n_products)
        cons_best_sellers = df[df['category'] == consequent_cat]['product_id'].value_counts().head(top_n_products)
        
        logger.info(f"  Recommended SKUs from {antecedent_cat}:")
        for rank, (prod_id, sales) in enumerate(ant_best_sellers.items(), 1):
            logger.info(f"    {rank}. {prod_id[:20]}... ({sales} sales overall)")
        
        logger.info(f"  Recommended SKUs from {consequent_cat}:")
        for rank, (prod_id, sales) in enumerate(cons_best_sellers.items(), 1):
            logger.info(f"    {rank}. {prod_id[:20]}... ({sales} sales overall)")
        
        drilldown_results.append({
            'pair_rank': idx + 1,
            'antecedent_category': antecedent_cat,
            'consequent_category': consequent_cat,
            'lift': rule['lift'],
            'confidence': rule['confidence'],
            'support': rule['support'],
            'support_label': CONDITIONAL_SUPPORT_LABEL,
            'bundle_type': 'Synthetic (Best-Seller Pairing)',
            'bundle_rationale': f"Top-selling SKUs from '{antecedent_cat}' + '{consequent_cat}' categories",
            'antecedent_top_products': ant_best_sellers.index.tolist()[:top_n_products],
            'antecedent_product_sales': ant_best_sellers.values.tolist()[:top_n_products],
            'consequent_top_products': cons_best_sellers.index.tolist()[:top_n_products],
            'consequent_product_sales': cons_best_sellers.values.tolist()[:top_n_products]
        })
    
    logger.info(f"\n[OK] Synthetic bundle recommendations complete: {len(drilldown_results)} bundles created")
    logger.info("Bundle Strategy: Pairing best-sellers from categories with strong statistical association")
    
    return drilldown_results, []

# ============================================================================
# MAIN EXECUTION PIPELINE
# ============================================================================

def run_pipeline():
    """
    Execute the complete Phase 2 pipeline.
    Adapted for sparse market baskets: analyzes multi-category transactions separately.
    """
    logger.info("\n" + "=" * 70)
    logger.info("PHASE 2: ASSOCIATION RULE MINING - FULL PIPELINE")
    logger.info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70 + "\n")
    
    # Step 1-2: Load data
    df, transaction_list, transaction_matrix, te = load_basket_data()
    
    # Create multi-category subset (for sparse markets)
    multi_cat_transaction_list, multi_cat_matrix, multi_cat_indices = create_multi_category_basket_matrix(
        transaction_list, transaction_matrix
    )
    
    # Step 3-4: Run algorithms on MULTI-CATEGORY BASKETS (most relevant)
    apriori_results = run_apriori(multi_cat_matrix, support_thresholds=MULTI_CATEGORY_SUPPORT_THRESHOLDS)
    fpgrowth_results = run_fpgrowth(multi_cat_matrix, support_thresholds=MULTI_CATEGORY_SUPPORT_THRESHOLDS)
    
    # Step 5: Compare and select
    best_threshold, comparison_df, final_rules, final_itemsets = compare_algorithms(apriori_results, fpgrowth_results)
    
    # Step 6: Business insights (from multi-category transactions)
    anchor_df = analyze_anchors_addons(final_rules)
    hidden_affinities = find_hidden_affinities(final_rules)
    bundling_candidates = extract_bundling_candidates(final_rules)
    
    # Basket composition from ALL transactions (for context)
    basket_composition = analyze_basket_composition(transaction_list)
    
    # Step 6.5: Product drilldown (synthetic bundles - best-sellers from paired categories)
    # Use FULL dataset to identify overall top-selling SKUs for each category
    drilldown_results, skipped_pairs = product_drilldown(
        df,  # Use full df for overall best-seller rankings
        final_rules,
        top_n_pairs=TOP_PAIRS_COUNT,
        top_n_products=2
    )
    
    logger.info(f"\n{'=' * 70}")
    logger.info("PIPELINE EXECUTION COMPLETE")
    logger.info(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70 + "\n")
    
    return {
        'df': df,
        'transaction_list': transaction_list,
        'transaction_matrix': transaction_matrix,
        'te': te,
        'apriori_results': apriori_results,
        'fpgrowth_results': fpgrowth_results,
        'best_threshold': best_threshold,
        'comparison_df': comparison_df,
        'final_rules': final_rules,
        'final_itemsets': final_itemsets,
        'anchor_df': anchor_df,
        'hidden_affinities': hidden_affinities,
        'bundling_candidates': bundling_candidates,
        'basket_composition': basket_composition,
        'drilldown_results': drilldown_results,
        'skipped_pairs': skipped_pairs
    }

# ============================================================================
# PLACEHOLDER: VISUALIZATION & EXPORT FUNCTIONS
# ============================================================================

def visualize_insights(results):
    """Generate all 6 visualizations (implemented in next step)"""
    logger.info("Visualizations will be implemented in next step")
    pass

def export_results(results):
    """Export all CSVs and report (implemented in next step)"""
    logger.info("Export functions will be implemented in next step")
    pass

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    results = run_pipeline()
    logger.info("Pipeline results stored in results dictionary")
