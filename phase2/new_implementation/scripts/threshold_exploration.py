"""
Phase 2: Threshold Exploration for Two ARM Types

Goal:
1) Pick support thresholds that produce usable rule counts.
2) Validate Apriori vs FP-Growth consistency.
3) Keep logic simple enough for TA explanation.
"""

import logging
from pathlib import Path

import numpy as np
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules, fpgrowth
from mlxtend.preprocessing import TransactionEncoder


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_PATH = REPO_ROOT / 'data' / 'master_cleaned.csv'
MIN_CONFIDENCE = 0.30


def add_interestingness_measures(rules: pd.DataFrame, itemsets: pd.DataFrame) -> pd.DataFrame:
    """Add selected interestingness measures used for interpretation."""
    if rules.empty:
        return rules

    itemset_support = dict(zip(itemsets['itemsets'], itemsets['support']))
    support_a = rules['antecedents'].map(itemset_support).fillna(0.0)
    support_b = rules['consequents'].map(itemset_support).fillna(0.0)
    support_ab = rules['support']

    confidence_ab = rules['confidence']
    confidence_ba = np.where(support_b > 0, support_ab / support_b, 0.0)

    denom_cosine = np.sqrt(support_a * support_b)
    rules['cosine'] = np.where(denom_cosine > 0, support_ab / denom_cosine, 0.0)
    rules['kulczynski'] = (confidence_ab + confidence_ba) / 2
    rules['all_confidence'] = np.minimum(confidence_ab, confidence_ba)
    rules['max_confidence'] = np.maximum(confidence_ab, confidence_ba)

    ir_denom = support_a + support_b - support_ab
    rules['imbalance_ratio'] = np.where(ir_denom > 0, np.abs(support_a - support_b) / ir_denom, 0.0)
    return rules


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load data and create per-order transaction breakdown."""
    logger.info("Loading data...")
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Input file not found: {DATA_PATH}. Expected at data/master_cleaned.csv.")

    df = pd.read_csv(DATA_PATH)
    items_per_order = df.groupby('order_id').size()
    categories_per_order = df.groupby('order_id')['category'].nunique()
    products_per_order = df.groupby('order_id')['product_id'].nunique()

    breakdown = pd.DataFrame({
        'order_id': items_per_order.index,
        'num_items': items_per_order.values,
        'num_categories': categories_per_order.values,
        'num_products': products_per_order.values
    })

    total = len(breakdown)
    single = len(breakdown[breakdown['num_categories'] == 1])
    multi = len(breakdown[breakdown['num_categories'] > 1])
    logger.info(f"\nTotal transactions: {total:,d}")
    logger.info(f"  Single-category: {single:,d} ({single/total*100:.2f}%)")
    logger.info(f"  Multi-category: {multi:,d} ({multi/total*100:.2f}%)")
    return df, breakdown


def to_transaction_matrix(df: pd.DataFrame, order_ids: list, basket_col: str) -> pd.DataFrame:
    """Build one-hot encoded basket matrix for selected orders."""
    subset = df[df['order_id'].isin(order_ids)]
    baskets = subset.groupby('order_id')[basket_col].apply(
        lambda x: list(set(x)) if basket_col == 'category' else list(x.unique())
    ).tolist()

    te = TransactionEncoder()
    te_ary = te.fit(baskets).transform(baskets)
    matrix = pd.DataFrame(te_ary, columns=te.columns_)
    return matrix


def prepare_cross_category_matrix(df: pd.DataFrame, breakdown: pd.DataFrame) -> pd.DataFrame:
    """Transactions with 2+ categories; basket item = category."""
    logger.info("\n" + "=" * 70)
    logger.info("CROSS-CATEGORY DATA PREPARATION")
    logger.info("=" * 70)
    order_ids = breakdown[breakdown['num_categories'] > 1]['order_id'].tolist()
    matrix = to_transaction_matrix(df, order_ids, basket_col='category')
    logger.info(f"Baskets: {len(order_ids):,d}")
    logger.info(f"Unique categories: {matrix.shape[1]}")
    logger.info(f"Matrix shape: {matrix.shape}")
    return matrix


def prepare_intra_category_matrix(df: pd.DataFrame, breakdown: pd.DataFrame) -> pd.DataFrame:
    """Transactions with 2+ items and exactly 1 category; basket item = product_id."""
    logger.info("\n" + "=" * 70)
    logger.info("INTRA-CATEGORY DATA PREPARATION")
    logger.info("=" * 70)
    order_ids = breakdown[(breakdown['num_items'] > 1) & (breakdown['num_categories'] == 1)]['order_id'].tolist()
    matrix = to_transaction_matrix(df, order_ids, basket_col='product_id')
    logger.info(f"Baskets: {len(order_ids):,d}")
    logger.info(f"Unique products: {matrix.shape[1]}")
    logger.info(f"Matrix shape: {matrix.shape}")
    return matrix


def rule_set_signature(rules: pd.DataFrame) -> set:
    """Convert rules to comparable (antecedent, consequent) tuples."""
    if rules.empty:
        return set()
    return set(
        rules.apply(
            lambda r: (
                tuple(sorted(list(r['antecedents']))),
                tuple(sorted(list(r['consequents'])))
            ),
            axis=1
        )
    )


def mine_rules_with_algo(matrix: pd.DataFrame, support: float, algorithm: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run Apriori or FP-Growth and return (itemsets, rules)."""
    if algorithm == 'apriori':
        itemsets = apriori(matrix, min_support=support, use_colnames=True)
    else:
        itemsets = fpgrowth(matrix, min_support=support, use_colnames=True)

    if len(itemsets) < 2:
        return itemsets, pd.DataFrame()

    rules = association_rules(itemsets, metric='confidence', min_threshold=MIN_CONFIDENCE)
    rules = add_interestingness_measures(rules, itemsets)
    return itemsets, rules


def explore_thresholds(matrix: pd.DataFrame, arm_type: str, supports: list[float]) -> pd.DataFrame:
    """Evaluate both algorithms at each support threshold."""
    logger.info(f"\nExploring thresholds for {arm_type}...")
    rows = []

    for support in supports:
        try:
            apr_itemsets, apr_rules = mine_rules_with_algo(matrix, support, 'apriori')
            fp_itemsets, fp_rules = mine_rules_with_algo(matrix, support, 'fpgrowth')

            apr_count = len(apr_rules)
            fp_count = len(fp_rules)
            count_convergence = apr_count == fp_count
            exact_rule_match = rule_set_signature(apr_rules) == rule_set_signature(fp_rules)

            rows.append({
                'support': support,
                'support_label': f"{support:.2%}",
                'apriori_itemsets': len(apr_itemsets),
                'apriori_rules': apr_count,
                'apriori_avg_lift': apr_rules['lift'].mean() if apr_count else 0.0,
                'apriori_avg_kulczynski': apr_rules['kulczynski'].mean() if apr_count else 0.0,
                'apriori_avg_cosine': apr_rules['cosine'].mean() if apr_count else 0.0,
                'fpgrowth_itemsets': len(fp_itemsets),
                'fpgrowth_rules': fp_count,
                'fpgrowth_avg_lift': fp_rules['lift'].mean() if fp_count else 0.0,
                'fpgrowth_avg_kulczynski': fp_rules['kulczynski'].mean() if fp_count else 0.0,
                'fpgrowth_avg_cosine': fp_rules['cosine'].mean() if fp_count else 0.0,
                'convergence': 'YES' if count_convergence else 'NO',
                'exact_rule_match': exact_rule_match
            })
        except Exception as exc:
            logger.warning(f"Error at support={support:.2%}: {exc}")
            rows.append({
                'support': support,
                'support_label': f"{support:.2%}",
                'apriori_itemsets': 0,
                'apriori_rules': 0,
                'apriori_avg_lift': 0.0,
                'apriori_avg_kulczynski': 0.0,
                'apriori_avg_cosine': 0.0,
                'fpgrowth_itemsets': 0,
                'fpgrowth_rules': 0,
                'fpgrowth_avg_lift': 0.0,
                'fpgrowth_avg_kulczynski': 0.0,
                'fpgrowth_avg_cosine': 0.0,
                'convergence': 'ERROR',
                'exact_rule_match': False
            })

    return pd.DataFrame(rows)


def select_optimal_support(comparison_df: pd.DataFrame, arm_type: str) -> float:
    """
    Simple threshold logic:
    - Cross-category: choose support closest to 25 rules (minimum 15).
    - Intra-category: choose support closest to 2 rules (minimum 1).
    - Prefer converged/equal results when tie.
    """
    logger.info("\n" + "=" * 70)
    logger.info(f"OPTIMAL THRESHOLD SELECTION - {arm_type}")
    logger.info("=" * 70)

    if arm_type == 'Cross-Category':
        target_rules = 25
        min_rules = 15
    else:
        target_rules = 2
        min_rules = 1

    candidates = comparison_df[comparison_df['apriori_rules'] >= min_rules].copy()
    if candidates.empty:
        candidates = comparison_df[comparison_df['apriori_rules'] > 0].copy()
    if candidates.empty:
        fallback = float(comparison_df.iloc[0]['support'])
        logger.warning(f"No rules found at tested supports. Fallback: {fallback:.2%}")
        return fallback

    candidates['distance_to_target'] = (candidates['apriori_rules'] - target_rules).abs()
    candidates['count_converged'] = candidates['convergence'] == 'YES'
    candidates['set_converged'] = candidates['exact_rule_match'] == True

    candidates = candidates.sort_values(
        by=['distance_to_target', 'set_converged', 'count_converged', 'support'],
        ascending=[True, False, False, True]
    )

    best = candidates.iloc[0]
    logger.info(f"Selected support: {best['support_label']}")
    logger.info(
        "Reason: rules=%s (target=%s), count_convergence=%s, exact_rule_match=%s"
        % (int(best['apriori_rules']), target_rules, best['convergence'], bool(best['exact_rule_match']))
    )
    return float(best['support'])


def log_comparison_table(df: pd.DataFrame, title: str) -> None:
    display = df.copy()
    display['support'] = display['support_label']
    display = display.drop(columns=['support_label'])
    logger.info(f"\n--- {title} ---")
    logger.info(display.to_string(index=False))


def main():
    logger.info("\n" + "=" * 70)
    logger.info("PHASE 2: THRESHOLD EXPLORATION")
    logger.info("=" * 70)

    df, breakdown = load_data()
    cross_supports = [0.0005, 0.001, 0.002, 0.005, 0.01]
    intra_supports = [0.01, 0.02, 0.05, 0.10, 0.15]

    logger.info("\n" + "=" * 70)
    logger.info("TYPE 1: CROSS-CATEGORY ARM")
    logger.info("=" * 70)
    cross_matrix = prepare_cross_category_matrix(df, breakdown)
    cross_comparison = explore_thresholds(cross_matrix, "Cross-Category", cross_supports)
    log_comparison_table(cross_comparison, "CROSS-CATEGORY COMPARISON")
    cross_optimal = select_optimal_support(cross_comparison, "Cross-Category")

    logger.info("\n" + "=" * 70)
    logger.info("TYPE 2: INTRA-CATEGORY ARM")
    logger.info("=" * 70)
    intra_matrix = prepare_intra_category_matrix(df, breakdown)
    intra_comparison = explore_thresholds(intra_matrix, "Intra-Category", intra_supports)
    log_comparison_table(intra_comparison, "INTRA-CATEGORY COMPARISON")
    intra_optimal = select_optimal_support(intra_comparison, "Intra-Category")

    logger.info("\n" + "=" * 70)
    logger.info("THRESHOLD EXPLORATION COMPLETE")
    logger.info("=" * 70)
    logger.info("\n>>> RECOMMENDED THRESHOLDS <<<")
    logger.info(f"  Cross-Category ARM: {cross_optimal:.2%}")
    logger.info(f"  Intra-Category ARM: {intra_optimal:.2%}")
    logger.info("\nUse these thresholds in:")
    logger.info("  - arm_cross_category.py")
    logger.info("  - arm_intra_category.py")
    logger.info("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
