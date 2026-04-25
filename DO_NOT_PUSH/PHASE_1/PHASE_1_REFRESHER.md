# PHASE 1: DATA PREPARATION & EDA

⬅️ *Start of Pipeline* | ➡️ **[Next: Phase 2 Association Rules](../PHASE_2/PHASE_2_REFRESHER.md)** | ➡️ **[Next: Phase 3 Clustering](../PHASE_3/PHASE_3_REFRESHER.md)**

## 🎯 Objective & Quick Stats
- **Goal:** Clean raw Olist datasets and engineer features for downstream clustering and association mining.
- **Input:** 8 raw CSV files (110,197 transactions).
- **Output:** `master_cleaned.csv` (100,196 clean rows) + `customer_features.csv` (93,398 unique customers).
- **Status:** ✅ COMPLETE & VALIDATED

## 🛠️ How We Did It (The Pipeline)

1. **Consolidation:** Merged 8 relational tables into a single transaction table.
2. **Cleaning:** Dropped nulls, removed duplicates, and removed invalid prices. Data retention was excellent (90.9%).
3. **Feature Engineering:** Built 12 features per customer based on RFM (Recency, Frequency, Monetary) + Geography + Category Preferences.
4. **Preprocessing for Phase 3:** Applied `log1p` transformation (to handle extreme skewness) and `RobustScaler` (median-based, to ignore massive outliers like $7,388 spenders).
5. **Format Exports:** Prepared separate datasets for K-Means (numeric only) and K-Prototypes (mixed-type data).

## 📊 Key Findings (From EDA)

- **One-Time Buyers Rule:** 96.96% of customers bought only once. (This is why standard RFM struggles, and why we use clustering!)
- **High-Value Spenders:** The top 5% spend over $389.
- **Geographic Concentration:** 41.92% of all customers come from SÃ£o Paulo.
- **Distribution Shape:** Spending is highly right-skewed (Pareto principle: many small spenders, few massive spenders).

## ❓ TA Presentation Q&A

**Q: Why keep highly correlated features (e.g., Monetary & Avg_Order_Value)?**
**A:** Linear models hate multicollinearity, but K-Prototype is non-linear and handles it better. Dropping them loses business interpretability, and our evaluation metrics proved keeping them didn't hurt cluster quality.

**Q: Why use RobustScaler instead of StandardScaler?**
**A:** StandardScaler uses the mean, which is dragged up by massive outliers (like one person spending $7,388). RobustScaler uses the median and IQR, meaning it scales the 99% of normal customers properly without letting the outlier ruin the scale.

**Q: Why the log transformation?**
**A:** Our Q-Q plots proved the data is highly right-skewed. Log compression turns exponential spreads into a linear scale, so monetary value doesn't completely overpower all other features in the clustering algorithm.
