# PHASE 1: DATA PREPARATION & EXPLORATORY ANALYSIS

**Objective:** Clean raw Olist data and prepare features for analysis  
**Output:** 96,478 cleaned transactions with engineered features  
**Status:** COMPLETE

## Overview

This phase consolidates 8 raw CSV files into a single cleaned dataset and generates features for clustering analysis in Phase 2.

## Input Data

Raw files from the Olist Brazilian e-commerce dataset:
- olist_customers_dataset.csv (119,094 rows)
- olist_orders_dataset.csv (99,441 rows)
- olist_order_items_dataset.csv (112,650 rows)
- olist_products_dataset.csv (32,951 rows)
- olist_sellers_dataset.csv (3,095 rows)
- olist_order_reviews_dataset.csv (98,992 rows)
- olist_geolocation_dataset.csv (1,000,163 rows)
- product_category_name_translation.csv (71 rows)

## Processing Steps

### 1. Data Consolidation (preprocessing.py)

Merges all 8 datasets into a single transaction table:
- Joins orders with customers, order items, products, and reviews
- Maps product category names to English
- Creates denormalized transaction format (one row per item in order)
- Output: `master_df.csv` (112,650 rows)

### 2. Data Cleaning (cleaning.py)

Removes invalid records and handles missing values:
- Removes duplicate transactions
- Removes rows with null values in key columns
- Converts data types (prices to float, dates to datetime)
- Detects and flags outliers (extreme prices, unusually large orders)
- Output: `master_cleaned.csv` (96,478 rows)

Data retained: 85.7% (16,172 invalid records removed)

### 3. Feature Engineering (feature_engineering.py)

Creates derived features from raw transaction data:
- **Transaction-level:** order_id, product_category, price, order_value, review_score, payment_type, customer_state
- **Order-level:** items_per_order, unique_categories_per_order, total_order_value
- **Category-level:** category_popularity, avg_price, sales_volume, avg_review_score
- Output: `customer_features_full.csv` (96,478 rows with 50+ features)

### 4. Exploratory Data Analysis (eda_report.py)

Basic statistics and visualizations:
- Overall dataset: 96,478 transactions, 72 product categories
- Date range: 2016-2018 (2+ years)
- Average order value: $121.23
- 99.2% of orders are single-category (focused shopping)
- Top 3 states: São Paulo (33.6%), Rio de Janeiro (18.9%), Minas Gerais (12.5%)
- Generates visualizations for distributions and trends

### 5. Feature Scaling (feature_scaling.py)

Prepares features for clustering algorithms:

**KMeans Format** (`customer_features_kmeans.csv`)
- Numeric features only (32 features)
- StandardScaler normalization: (x - mean) / std_dev

**KPrototypes Format** (`customer_features_kprototypes.csv`)
- Mixed numeric + categorical (45 features)  
- Numeric features scaled, categorical features encoded
- Useful for algorithms that handle both data types

## Output Files

| File | Size | Rows | Purpose |
|------|------|------|---------|
| master_df.csv | ~16 MB | 112,650 | Raw consolidated data |
| master_cleaned.csv | ~13 MB | 96,478 | Cleaned transactions |
| customer_features_full.csv | ~23.7 MB | 96,478 | Full feature set |
| customer_features_kmeans.csv | ~10.8 MB | 96,478 | Numeric features for KMeans |
| customer_features_kprototypes.csv | ~13.3 MB | 96,478 | Mixed features for KPrototypes |

## Data Quality

| Metric | Before | After |
|--------|--------|-------|
| Total Records | 112,650 | 96,478 |
| Null Values | Present | 0 |
| Duplicates | 412 | 0 |
| Data Quality Grade | C | A |

All key columns are complete and validated.

## Key Findings

1. **Single-category dominance:** 99.2% of orders contain products from only one category
2. **Geographic concentration:** 65% of orders from 3 states (São Paulo, Rio de Janeiro, Minas Gerais)
3. **Seasonal variation:** 30% higher demand in November-December
4. **Price variation:** Large range ($0.50 to $13,500) with most items under $500
5. **High satisfaction:** Average review score 4.2/5

## Validation

Run `phase1/validate_phase1.py` to verify:
- All output files exist
- Data has 96,478 records
- No null values
- Expected columns present
