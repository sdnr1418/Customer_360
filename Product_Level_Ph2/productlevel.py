"""
Phase 2: Product-Level Association Rule Mining
Adapted for sparse Olist baskets

This version:
1. Loads master_cleaned.csv
2. Filters rare products to reduce sparsity
3. Keeps only multi-item orders
4. Optionally keeps top-N most frequent products
5. Creates product-level baskets
6. Runs Apriori and FP-Growth
7. Compares results and selects best threshold
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from mlxtend.frequent_patterns import apriori, fpgrowth, association_rules
from mlxtend.preprocessing import TransactionEncoder
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

# ============================================================================
# LOGGING SETUP
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("product_level_rules.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================
PROJECT_ROOT = Path(__file__).parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "master_cleaned.csv"

# Sparsity handling
MIN_PRODUCT_FREQUENCY = 10      # keep only products purchased at least 10 times
TOP_N_PRODUCTS = 1000           # keep top 1000 most frequent products; set to None to disable
USE_TOP_N_FILTER = True         # True = apply top-N filter
USE_MULTI_ITEM_ONLY = True      # True = keep only orders with 2+ products

# Thresholds for product-level mining
SUPPORT_THRESHOLDS = [0.0001, 0.0002, 0.0005, 0.001]
MIN_CONFIDENCE = 0.20
MIN_LIFT = 1.0

# ============================================================================
# STEP 1: LOAD DATA
# ============================================================================

def load_product_data(csv_path=DATA_PATH):
    logger.info("=" * 70)
    logger.info("STEP 1: LOADING PRODUCT-LEVEL DATA")
    logger.info("=" * 70)

    df = pd.read_csv(csv_path)
    logger.info(f"Loaded {len(df)} rows from {csv_path}")

    required_cols = ["customer_unique_id", "order_id", "product_id", "price"]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    logger.info(f"Unique orders: {df['order_id'].nunique()}")
    logger.info(f"Unique products: {df['product_id'].nunique()}")
    logger.info(f"Unique customers: {df['customer_unique_id'].nunique()}")

    return df

# ============================================================================
# STEP 2: HANDLE SPARSITY
# ============================================================================

def reduce_sparsity(df):
    logger.info("=" * 70)
    logger.info("STEP 2: REDUCING SPARSITY")
    logger.info("=" * 70)

    original_rows = len(df)
    original_orders = df["order_id"].nunique()
    original_products = df["product_id"].nunique()

    logger.info(f"Original rows: {original_rows}")
    logger.info(f"Original orders: {original_orders}")
    logger.info(f"Original products: {original_products}")

    # 1. Remove rare products
    product_counts = df["product_id"].value_counts()
    frequent_products = product_counts[product_counts >= MIN_PRODUCT_FREQUENCY].index
    df = df[df["product_id"].isin(frequent_products)].copy()

    logger.info(f"After min frequency >= {MIN_PRODUCT_FREQUENCY}:")
    logger.info(f"  Rows: {len(df)}")
    logger.info(f"  Products: {df['product_id'].nunique()}")

    # 2. Keep only top N products if enabled
    if USE_TOP_N_FILTER and TOP_N_PRODUCTS is not None:
        top_products = df["product_id"].value_counts().head(TOP_N_PRODUCTS).index
        df = df[df["product_id"].isin(top_products)].copy()
        logger.info(f"After top {TOP_N_PRODUCTS} products filter:")
        logger.info(f"  Rows: {len(df)}")
        logger.info(f"  Products: {df['product_id'].nunique()}")

    # 3. Keep only multi-item orders if enabled
    if USE_MULTI_ITEM_ONLY:
        order_sizes = df.groupby("order_id")["product_id"].nunique()
        multi_item_orders = order_sizes[order_sizes >= 2].index
        df = df[df["order_id"].isin(multi_item_orders)].copy()

        logger.info("After keeping only multi-item orders:")
        logger.info(f"  Rows: {len(df)}")
        logger.info(f"  Orders: {df['order_id'].nunique()}")
        logger.info(f"  Products: {df['product_id'].nunique()}")

    # Recheck after filtering
    logger.info("\nFinal filtered dataset summary:")
    logger.info(f"Rows: {len(df)}")
    logger.info(f"Orders: {df['order_id'].nunique()}")
    logger.info(f"Products: {df['product_id'].nunique()}")

    if len(df) == 0:
        raise ValueError("Filtering removed all data. Loosen thresholds.")

    return df

# ============================================================================
# STEP 3: CREATE PRODUCT BASKETS
# ============================================================================

def create_product_baskets(df):
    logger.info("=" * 70)
    logger.info("STEP 3: CREATING PRODUCT BASKETS")
    logger.info("=" * 70)

    # group products by order
    transaction_list = df.groupby("order_id")["product_id"].apply(list).tolist()

    # remove duplicates within each basket
    transaction_list = [list(set(basket)) for basket in transaction_list]

    logger.info(f"Total baskets: {len(transaction_list)}")
    logger.info(f"Average products per basket: {np.mean([len(b) for b in transaction_list]):.2f}")
    logger.info(f"Min basket size: {min(len(b) for b in transaction_list)}")
    logger.info(f"Max basket size: {max(len(b) for b in transaction_list)}")

    # one-hot encoding
    te = TransactionEncoder()
    te_array = te.fit(transaction_list).transform(transaction_list)
    transaction_matrix = pd.DataFrame(te_array, columns=te.columns_)

    sparsity = (transaction_matrix == 0).sum().sum() / (transaction_matrix.shape[0] * transaction_matrix.shape[1])
    logger.info(f"Transaction matrix shape: {transaction_matrix.shape}")
    logger.info(f"Sparsity: {sparsity:.2%}")

    return transaction_list, transaction_matrix

# ============================================================================
# STEP 4: APRIORI
# ============================================================================

def run_apriori(transaction_matrix, support_thresholds=SUPPORT_THRESHOLDS):
    logger.info("=" * 70)
    logger.info("STEP 4: RUNNING APRIORI")
    logger.info("=" * 70)

    results = {}

    for support in support_thresholds:
        logger.info(f"\nApriori - support threshold: {support:.4f}")

        try:
            itemsets = apriori(transaction_matrix, min_support=support, use_colnames=True)
            logger.info(f"Frequent itemsets: {len(itemsets)}")

            if len(itemsets) < 2:
                results[support] = (itemsets, pd.DataFrame(), {
                    "algorithm": "Apriori",
                    "support": support,
                    "itemsets_count": len(itemsets),
                    "rules_count": 0
                })
                continue

            rules = association_rules(itemsets, metric="confidence", min_threshold=MIN_CONFIDENCE)

            if len(rules) == 0:
                results[support] = (itemsets, rules, {
                    "algorithm": "Apriori",
                    "support": support,
                    "itemsets_count": len(itemsets),
                    "rules_count": 0
                })
                continue

            rules = rules[rules["lift"] >= MIN_LIFT].copy()

            if len(rules) > 0:
                rules["antecedent_str"] = rules["antecedents"].apply(lambda x: ", ".join(sorted(list(x))))
                rules["consequent_str"] = rules["consequents"].apply(lambda x: ", ".join(sorted(list(x))))
                logger.info(f"Rules: {len(rules)}")
                logger.info(f"Avg support: {rules['support'].mean():.4f}")
                logger.info(f"Avg confidence: {rules['confidence'].mean():.4f}")
                logger.info(f"Avg lift: {rules['lift'].mean():.4f}")

            results[support] = (itemsets, rules, {
                "algorithm": "Apriori",
                "support": support,
                "itemsets_count": len(itemsets),
                "rules_count": len(rules),
                "avg_confidence": rules["confidence"].mean() if len(rules) else 0,
                "avg_lift": rules["lift"].mean() if len(rules) else 0
            })

        except Exception as e:
            logger.error(f"Error at support {support}: {e}")
            results[support] = (pd.DataFrame(), pd.DataFrame(), {
                "algorithm": "Apriori",
                "support": support,
                "itemsets_count": 0,
                "rules_count": 0,
                "error": str(e)
            })

    return results

# ============================================================================
# STEP 5: FP-GROWTH
# ============================================================================

def run_fpgrowth(transaction_matrix, support_thresholds=SUPPORT_THRESHOLDS):
    logger.info("=" * 70)
    logger.info("STEP 5: RUNNING FP-GROWTH")
    logger.info("=" * 70)

    results = {}

    for support in support_thresholds:
        logger.info(f"\nFP-Growth - support threshold: {support:.4f}")

        try:
            itemsets = fpgrowth(transaction_matrix, min_support=support, use_colnames=True)
            logger.info(f"Frequent itemsets: {len(itemsets)}")

            if len(itemsets) < 2:
                results[support] = (itemsets, pd.DataFrame(), {
                    "algorithm": "FP-Growth",
                    "support": support,
                    "itemsets_count": len(itemsets),
                    "rules_count": 0
                })
                continue

            rules = association_rules(itemsets, metric="confidence", min_threshold=MIN_CONFIDENCE)

            if len(rules) == 0:
                results[support] = (itemsets, rules, {
                    "algorithm": "FP-Growth",
                    "support": support,
                    "itemsets_count": len(itemsets),
                    "rules_count": 0
                })
                continue

            rules = rules[rules["lift"] >= MIN_LIFT].copy()

            if len(rules) > 0:
                rules["antecedent_str"] = rules["antecedents"].apply(lambda x: ", ".join(sorted(list(x))))
                rules["consequent_str"] = rules["consequents"].apply(lambda x: ", ".join(sorted(list(x))))
                logger.info(f"Rules: {len(rules)}")
                logger.info(f"Avg support: {rules['support'].mean():.4f}")
                logger.info(f"Avg confidence: {rules['confidence'].mean():.4f}")
                logger.info(f"Avg lift: {rules['lift'].mean():.4f}")

            results[support] = (itemsets, rules, {
                "algorithm": "FP-Growth",
                "support": support,
                "itemsets_count": len(itemsets),
                "rules_count": len(rules),
                "avg_confidence": rules["confidence"].mean() if len(rules) else 0,
                "avg_lift": rules["lift"].mean() if len(rules) else 0
            })

        except Exception as e:
            logger.error(f"Error at support {support}: {e}")
            results[support] = (pd.DataFrame(), pd.DataFrame(), {
                "algorithm": "FP-Growth",
                "support": support,
                "itemsets_count": 0,
                "rules_count": 0,
                "error": str(e)
            })

    return results

# ============================================================================
# STEP 6: COMPARE RESULTS
# ============================================================================

def compare_algorithms(apriori_results, fpgrowth_results):
    logger.info("=" * 70)
    logger.info("STEP 6: COMPARING APRIORI VS FP-GROWTH")
    logger.info("=" * 70)

    comparison_rows = []

    for support in SUPPORT_THRESHOLDS:
        a_itemsets, a_rules, a_stats = apriori_results.get(support, (None, None, None))
        f_itemsets, f_rules, f_stats = fpgrowth_results.get(support, (None, None, None))

        if a_stats is None or f_stats is None:
            continue

        comparison_rows.append({
            "support": support,
            "apriori_itemsets": a_stats.get("itemsets_count", 0),
            "apriori_rules": a_stats.get("rules_count", 0),
            "apriori_avg_lift": a_stats.get("avg_lift", 0),
            "fpgrowth_itemsets": f_stats.get("itemsets_count", 0),
            "fpgrowth_rules": f_stats.get("rules_count", 0),
            "fpgrowth_avg_lift": f_stats.get("avg_lift", 0)
        })

    comparison_df = pd.DataFrame(comparison_rows)
    logger.info("\nComparison table:")
    logger.info(comparison_df.to_string(index=False))

    # pick Apriori threshold with best nonzero rules
    best_threshold = None
    best_count = -1

    for support in SUPPORT_THRESHOLDS:
        stats = apriori_results[support][2]
        count = stats.get("rules_count", 0)
        if count > best_count:
            best_count = count
            best_threshold = support

    best_itemsets = apriori_results[best_threshold][0]
    best_rules = apriori_results[best_threshold][1]

    logger.info(f"\nSelected Apriori threshold: {best_threshold}")
    logger.info(f"Selected Apriori rules count: {len(best_rules)}")

    return best_threshold, comparison_df, best_itemsets, best_rules

# ============================================================================
# STEP 7: SAVE OUTPUTS
# ============================================================================

def save_outputs(comparison_df, best_itemsets, best_rules):
    logger.info("=" * 70)
    logger.info("STEP 7: SAVING OUTPUTS")
    logger.info("=" * 70)

    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)

    comparison_df.to_csv(output_dir / "product_level_algorithm_comparison.csv", index=False)
    best_itemsets.to_csv(output_dir / "product_level_apriori_itemsets.csv", index=False)
    best_rules.to_csv(output_dir / "product_level_apriori_rules.csv", index=False)

    logger.info("Saved:")
    logger.info("  data/product_level_algorithm_comparison.csv")
    logger.info("  data/product_level_apriori_itemsets.csv")
    logger.info("  data/product_level_apriori_rules.csv")

# ============================================================================
# MAIN PIPELINE
# ============================================================================

def run_pipeline():
    logger.info("\n" + "=" * 70)
    logger.info("PRODUCT-LEVEL ASSOCIATION RULE MINING PIPELINE")
    logger.info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70 + "\n")

    df = load_product_data()
    df_filtered = reduce_sparsity(df)
    transaction_list, transaction_matrix = create_product_baskets(df_filtered)

    apriori_results = run_apriori(transaction_matrix)
    fpgrowth_results = run_fpgrowth(transaction_matrix)

    best_threshold, comparison_df, best_itemsets, best_rules = compare_algorithms(
        apriori_results, fpgrowth_results
    )

    save_outputs(comparison_df, best_itemsets, best_rules)

    logger.info("\n" + "=" * 70)
    logger.info("PIPELINE COMPLETE")
    logger.info("=" * 70)

    return {
        "filtered_df": df_filtered,
        "transaction_list": transaction_list,
        "transaction_matrix": transaction_matrix,
        "apriori_results": apriori_results,
        "fpgrowth_results": fpgrowth_results,
        "best_threshold": best_threshold,
        "comparison_df": comparison_df,
        "best_itemsets": best_itemsets,
        "best_rules": best_rules
    }

if __name__ == "__main__":
    results = run_pipeline()