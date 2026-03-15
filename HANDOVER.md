# Customer 360 — Phase 1 Complete | Handover to Phase 2 & 3

## Overview

Phase 1 (Data Preprocessing) is complete. The PostgreSQL warehouse is ready with cleaned data and engineered features. This document guides Ibrahim (Phase 2: Association Rules) and Abdullah (Phase 3: Segmentation) on their next steps.

---

## ✅ Phase 1 Completion Summary

| Task | Status | Output |
|------|--------|--------|
| Extract raw CSVs → PostgreSQL | ✓ Complete | `orders`, `customers`, `items`, `products`, `translation` tables |
| Transform via SQL JOINs | ✓ Complete | `master_cleaned` table (100K+ rows, 6 columns) |
| Data Cleaning (duplicates, nulls, outliers) | ✓ Complete | Removed invalid prices, filled missing categories |
| Feature Engineering (RFM + behavioral) | ✓ Complete | `customer_features` table (7 features per customer) |
| EDA + Multicollinearity Check | ✓ Complete | `eda_report.png`, `correlation_heatmap.png` |
| Feature Scaling (Log transform + Standardization) | ✓ Complete | `customer_features_kmeans`, `customer_features_kprototypes` tables |

---

## 📊 Database Schema (Ready to Use)

### For Ibrahim (Association Rule Mining)

**Table:** `master_cleaned`

```sql
SELECT * FROM master_cleaned LIMIT 5;
```

| Column | Type | Description |
|--------|------|-------------|
| `customer_unique_id` | VARCHAR | Customer identifier |
| `order_id` | VARCHAR | Order identifier |
| `order_purchase_timestamp` | TIMESTAMP | When order was placed |
| `product_id` | VARCHAR | Product identifier |
| `price` | FLOAT | Item price |
| `category` | VARCHAR | Product category (English) |

**Your Task:**
1. Group by `order_id` to create transaction baskets
2. Extract `category` lists per transaction
3. Apply **Apriori** / **FP-Growth** algorithms
4. Find rules like: `{Electronics} → {Accessories}`

**Expected Output:** Association rules with support, confidence, lift metrics.

---

### For Abdullah (Customer Segmentation)

**Table:** `customer_features_kmeans` (Ready for K-Means)

```sql
SELECT * FROM customer_features_kmeans LIMIT 5;
```

| Column | Type | Description |
|--------|------|-------------|
| `log_recency_scaled` | FLOAT | Days since last purchase (log + scaled) |
| `log_frequency_scaled` | FLOAT | Purchase count (log + scaled) |
| `log_monetary_scaled` | FLOAT | Total spending (log + scaled) |
| `log_avg_order_value_scaled` | FLOAT | Avg $ per order (log + scaled) |
| `log_value_per_order_scaled` | FLOAT | Spending per order (log + scaled) |
| `category_diversity_scaled` | FLOAT | # unique categories (scaled) |

**Alternative Table:** `customer_features_kprototypes` (For K-Prototypes with categorical features)

```sql
SELECT * FROM customer_features_kprototypes LIMIT 5;
```

Includes additional columns:
- `preferred_category` (categorical) — Top category per customer
- `recency_quartile` (categorical) — recent/moderate/older/inactive
- `monetary_quartile` (categorical) — low/medium/high/very_high

**Your Task:**
1. Load `customer_features_kmeans` into Python
2. Determine optimal cluster count (Elbow Method, Silhouette Score)
3. Run **K-Means Clustering** (typically 3–5 clusters)
4. Profile segments (e.g., "Champions", "At Risk", "New Customers")
5. Generate actionable business recommendations

**Expected Output:** Customer segments with business profiles and strategic recommendations.

---

## 🔧 How to Use the Data Locally

### 1. Pull Data from PostgreSQL

```python
import pandas as pd
from preprocessing import engine

# For Association Rules (Ibrahim)
master_df = pd.read_sql("SELECT * FROM master_cleaned", engine)

# For Clustering (Abdullah)
clustering_df = pd.read_sql("SELECT * FROM customer_features_kmeans", engine)
```

### 2. Alternative: Use Local CSV Files

All tables are auto-exported to CSVs in the `data/` folder:

```
data/
├── master_cleaned.csv              (for Ibrahim)
├── customer_features_kmeans.csv    (for Abdullah — K-Means ready)
├── customer_features_kprototypes.csv (for Abdullah — K-Prototypes ready)
└── customer_features_full.csv      (all features, both raw + scaled)
```

---

## 📈 Visual References

The following visualizations are already generated (check the project root):

1. **eda_report.png** — 6 charts showing RFM distributions and trends
2. **correlation_heatmap.png** — Multicollinearity check (if $r > 0.85$, consider PCA)

---

## 🚀 Python Scripts Execution Order

If you wish to **rebuild the pipeline from scratch:**

```bash
# Terminal (with venv activated)
python preprocessing.py          # ETL: Load CSVs → PostgreSQL
python cleaning.py               # Transform: Master table
python feature_engineering.py    # Engineer RFM + behavioral features
python feature_scaling.py        # Log transform + scaling for clustering
python eda_report.py             # Generate visualizations + multicollinearity check
```

---

## 📋 Dependencies

All required packages are in `requirements.txt`. To install for your environment:

```bash
pip install -r requirements.txt
```

Key libraries:
- `pandas`, `numpy` — Data manipulation
- `sqlalchemy`, `psycopg2-binary` — PostgreSQL connection
- `scikit-learn` — Scaling, clustering algorithms
- `seaborn`, `matplotlib` — Visualization

---

## 🔀 Git Workflow (Team Sync)

Once Phase 1 is approved:

```bash
# 1. Merge feature branch → main
git checkout main
git pull origin main
git merge feature-preprocessing
git push origin main

# 2. Create feature branches for Phase 2 & 3
git checkout main
git pull origin main

# Ibrahim (Phase 2)
git checkout -b feature-association-rules

# Abdullah (Phase 3)
git checkout -b feature-segmentation
```

Always pull before branching to stay in sync!

---

## 📞 Questions?

- **Database Connection Issues?** Check `.env` file for `DB_PASSWORD`
- **Missing Imports?** Run `pip install -r requirements.txt`
- **Data Looks Wrong?** Verify `cleaning.py` logic and re-run `python cleaning.py`

---

## ✨ Next Steps

| Person | Phase | Task | Deadline |
|--------|-------|------|----------|
| Saad | 1 | ✓ Complete | Done |
| Ibrahim | 2 | Association Rules (Apriori/FP-Growth) | TBD |
| Abdullah | 3 | Customer Segmentation (K-Means) | TBD |
| Team | 4 | Integration + Power BI Dashboard | TBD |

---

**Generated:** 2026-03-15  
**Status:** Ready for Phase 2 & 3  
**Database:** PostgreSQL (customer_360)
