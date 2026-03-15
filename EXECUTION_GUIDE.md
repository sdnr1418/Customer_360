# Phase 1: Quick Execution Guide

Run the pipeline in this exact order. Each script builds on the previous output.

---

## ⚡ Step-by-Step Execution

### Setup (One-time)

```bash
# Navigate to project
cd c:\Users\sdnr1\OneDrive\Desktop\DM_project

# Activate virtual environment
.\venv\Scripts\activate

# Verify PostgreSQL is running
# Open another terminal: psql -U postgres -d customer_360
```

---

### Run Pipeline

#### 1️⃣ Extract & Load (5-10 min)
```bash
python preprocessing.py
```
✅ **Output:** 
- PostgreSQL tables: `customers`, `orders`, `items`, `products`, `translation`
- CSV: `data/master_df.csv`
- Console: "Preprocessing Complete" + shape confirmation

**Check success:**
```sql
SELECT COUNT(*) FROM orders;
SELECT COUNT(*) FROM customers;
```

---

#### 2️⃣ Clean & Transform (2-5 min)
```bash
python cleaning.py
```
✅ **Output:**
- PostgreSQL table: `master_cleaned` (100K+ rows)
- CSV: `data/master_cleaned.csv`
- Console: Cleaning report (nulls filled, dupes removed, outliers filtered)

**Check success:**
```sql
SELECT COUNT(*) FROM master_cleaned;
SELECT * FROM master_cleaned LIMIT 3;
```

---

#### 3️⃣ Engineer Features (3-7 min)
```bash
python feature_engineering.py
```
✅ **Output:**
- PostgreSQL table: `customer_features` (40K+ rows, 7 features)
- CSV: `data/customer_features.csv`
- Console: "Feature Engineering Complete" + sample rows + statistics

**Check success:**
```sql
SELECT COUNT(*) FROM customer_features;
SELECT * FROM customer_features LIMIT 3;
```

---

#### 4️⃣ Scale & Transform (2-5 min)
```bash
python feature_scaling.py
```
✅ **Output:**
- PostgreSQL tables:
  - `customer_features_kmeans` (K-Means ready)
  - `customer_features_kprototypes` (K-Prototypes ready)
  - `customer_features_full` (complete feature set)
- CSVs: `data/customer_features_*.csv`
- Console: "Feature Scaling Complete" + statistics

**Check success:**
```sql
SELECT COUNT(*) FROM customer_features_kmeans;
DESCRIBE customer_features_kmeans;
```

---

#### 5️⃣ Exploratory Data Analysis (3-5 min)
```bash
python eda_report.py
```
✅ **Output:**
- Images: `eda_report.png`, `correlation_heatmap.png`
- Console: Full EDA summary (dataset overview, RFM stats, correlations, missing values)

**Outputs shown:**
```
EXPLORATORY DATA ANALYSIS SUMMARY
=====================================
--- DATASET OVERVIEW ---
Total Orders: 99,441
Unique Customers: 43,247
Unique Products: 28,372
...

--- RFM STATISTICS ---
recency    frequency    monetary
...

--- CORRELATION ANALYSIS (RFM) ---
                recency  frequency  monetary
recency          1.000      -0.249    -0.234
frequency       -0.249       1.000     0.892
monetary        -0.234       0.892     1.000
```

---

## 🔍 Full Pipeline Execution (All at Once)

If you want to run everything sequentially:

```bash
python preprocessing.py && python cleaning.py && python feature_engineering.py && python feature_scaling.py && python eda_report.py
```

**Total time:** ~20-30 minutes (depending on PostgreSQL performance)

---

## ✅ Verification Checklist

After all scripts complete, verify:

### PostgreSQL Tables
```bash
psql -U postgres -d customer_360
```

```sql
-- Check all required tables exist
\dt

-- Expected tables:
-- customers, orders, items, products, translation
-- master_cleaned
-- customer_features
-- customer_features_kmeans
-- customer_features_kprototypes
-- customer_features_full

-- Quick count checks
SELECT 'master_cleaned' as tbl, COUNT(*) as rows FROM master_cleaned
UNION ALL
SELECT 'customer_features_kmeans', COUNT(*) FROM customer_features_kmeans
UNION ALL
SELECT 'customer_features_kprototypes', COUNT(*) FROM customer_features_kprototypes;
```

### CSV Files
```bash
# Navigate to data folder
cd data\

# Should exist:
ls -la *.csv
# master_df.csv
# master_cleaned.csv
# customer_features.csv
# customer_features_kmeans.csv
# customer_features_kprototypes.csv
# customer_features_full.csv
```

### Visualizations
```bash
# In project root, should see:
ls -la *.png
# eda_report.png
# correlation_heatmap.png
```

---

## 🛑 Troubleshooting

### Error: PostgreSQL connection refused

**Check:**
1. PostgreSQL service is running
2. `.env` file exists with correct `DB_PASSWORD`
3. Database `customer_360` exists

**Fix:**
```bash
# Create database (in PostgreSQL terminal)
CREATE DATABASE customer_360;
```

---

### Error: ModuleNotFoundError (pandas, numpy, etc.)

**Fix:**
```bash
pip install -r requirements.txt
```

---

### Error: CSV files not found

**Check:**
- `data/` folder exists in project root
- CSV files have correct names (e.g., `olist_customers_dataset.csv`)

---

### Scripts run but no PostgreSQL tables created

**Check:**
1. Is PostgreSQL actually running? (`psql -U postgres`)
2. Is `.env` file readable? (Check for typos in `DB_PASSWORD`)
3. Did the script fail silently? (Check error output above)

**Debug:**
```python
# Run this to test connection
from preprocessing import engine
connection = engine.connect()
print("Connection OK")
connection.close()
```

---

## 📞 Need Help?

1. **Check inline code comments** in each Python file
2. **Review [HANDOVER.md](HANDOVER.md)** for phase-specific guidance
3. **See [README.md](README.md)** for overall project structure
4. **Check [PHASE1_COMPLETION.md](PHASE1_COMPLETION.md)** for summary

---

## ✨ When Complete

You'll have:
- ✅ Clean, deduplicated, validated data in PostgreSQL
- ✅ Engineered features ready for clustering
- ✅ EDA visualizations for stakeholder communication
- ✅ Scaled datasets ready for Ibrahim (Phase 2) and Abdullah (Phase 3)
- ✅ CSV exports for quick reference

**Ready to merge to main and hand off to team!**

```bash
git checkout main
git merge feature-preprocessing
git push origin main
```

