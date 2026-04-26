import pandas as pd
import numpy as np
import logging
from pathlib import Path
from mlxtend.frequent_patterns import fpgrowth, association_rules
from mlxtend.preprocessing import TransactionEncoder
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================
REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / 'data'
ORDERS_PATH = DATA_DIR / 'master_cleaned.csv'
SEGMENTS_PATH = DATA_DIR / 'customer_segments_k3.csv'
OUTPUT_DIR = REPO_ROOT / 'phase4' / 'outputs'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SUPPORT_THRESHOLD = 0.002  # 0.2%
MIN_CONFIDENCE = 0.30

# ============================================================================
# LOGGING SETUP
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(OUTPUT_DIR / 'phase4_arm.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_and_merge_data():
    logger.info("Loading orders data...")
    orders_df = pd.read_csv(ORDERS_PATH)
    logger.info("Loading segments data...")
    segments_df = pd.read_csv(SEGMENTS_PATH)
    
    # In customer_segments_k3.csv the column is segment_k3
    if 'segment_k3' not in segments_df.columns and 'Cluster' in segments_df.columns:
        segments_df.rename(columns={'Cluster': 'segment_k3'}, inplace=True)
        
    logger.info("Merging orders with segments...")
    # Merge to get segment for each order
    merged_df = pd.merge(orders_df, segments_df[['customer_unique_id', 'segment_k3']], on='customer_unique_id', how='inner')
    logger.info(f"Total merged items: {len(merged_df)}")
    return merged_df

def run_fpgrowth_for_segment(df, segment_id):
    logger.info(f"\n{'='*40}")
    logger.info(f"RUNNING FP-GROWTH FOR SEGMENT {segment_id}")
    logger.info(f"{'='*40}")
    
    # Count categories per order
    categories_per_order = df.groupby('order_id')['category'].nunique()
    
    # Filter to multi-category orders (2+ categories)
    multi_cat_orders = categories_per_order[categories_per_order > 1].index.tolist()
    multi_cat_df = df[df['order_id'].isin(multi_cat_orders)]
    
    logger.info(f"Total multi-category orders in Segment {segment_id}: {len(multi_cat_orders):,d}")
    
    if len(multi_cat_orders) == 0:
        logger.warning("No multi-category orders found for this segment.")
        return pd.DataFrame()
        
    # Create baskets: each order = list of unique categories
    baskets = multi_cat_df.groupby('order_id')['category'].apply(lambda x: list(set(x))).tolist()
    
    # One-hot encode
    te = TransactionEncoder()
    te_ary = te.fit(baskets).transform(baskets)
    matrix = pd.DataFrame(te_ary, columns=te.columns_)
    
    # Run FP-Growth
    # Dynamically set support to require at least 3 occurrences in this specific segment
    # This ensures statistical soundness regardless of segment size (188 vs 416 orders)
    dynamic_min_support = 3 / len(multi_cat_orders)
    logger.info(f"Dynamic min_support for Segment {segment_id}: {dynamic_min_support:.4f} (requires >= 3 orders)")
    
    itemsets = fpgrowth(matrix, min_support=dynamic_min_support, use_colnames=True)
    if len(itemsets) < 2:
        logger.warning("Insufficient itemsets for rules.")
        return pd.DataFrame()
        
    rules = association_rules(itemsets, metric="confidence", min_threshold=MIN_CONFIDENCE)
    logger.info(f"Rules found: {len(rules)}")
    if len(rules) > 0:
        # Format rules
        rules['antecedents'] = rules['antecedents'].apply(lambda x: ', '.join(sorted(list(x))))
        rules['consequents'] = rules['consequents'].apply(lambda x: ', '.join(sorted(list(x))))
        rules = rules.sort_values('lift', ascending=False)
        
        # Save rules
        output_path = OUTPUT_DIR / f'segment_{segment_id}_rules.csv'
        rules.to_csv(output_path, index=False)
        logger.info(f"Saved segment {segment_id} rules to {output_path}")
        
    return rules

def main():
    merged_df = load_and_merge_data()
    
    segments = merged_df['segment_k3'].unique()
    segments.sort()
    
    all_rules = {}
    for seg in segments:
        segment_df = merged_df[merged_df['segment_k3'] == seg]
        rules = run_fpgrowth_for_segment(segment_df, seg)
        all_rules[seg] = rules

if __name__ == "__main__":
    main()
