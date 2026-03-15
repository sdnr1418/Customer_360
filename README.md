# Customer 360: Unlocking the Full Picture

**Course:** Data Mining (DS-3005)  
**Instructor:** Mr. Tahir Ejaz  
**Team Members:** Saad Nasir (23L-2625), Ibrahim Moeed (23L-2602), Abdullah Azmat (23L-2611)

---

## 🎯 Project Overview

This project builds a **Customer 360° view** by merging two powerful data mining perspectives:
1. **Association Rule Mining** — "What products are bought together?"
2. **Customer Segmentation** — "Who are our customers based on behavior?"

Using the **Brazilian E-Commerce Public Dataset by Olist** (100K+ orders, 8 tables), we uncover how product associations differ across customer segments to deliver targeted business recommendations.

## ✅ Project Status

- **Phase 1 (Preprocessing & EDA):** ✅ **COMPLETE**
- **Phase 2 (Association Rules):** ⏳ Ibrahim Moeed
- **Phase 3 (Customer Segmentation):** ⏳ Abdullah Azmat
- **Phase 4 (Integration & Insights):** ⏳ Team
- **Phase 5 (Power BI Dashboard):** ⏳ Team

---

## 🛠️ Tech Stack

| Layer | Tools |
|-------|-------|
| **Data Storage** | PostgreSQL (customer_360 database) |
| **Data Processing** | Python 3.9+, Pandas, NumPy |
| **Algorithms** | Apriori, FP-Growth (MLxtend), K-Means Clustering, K-Prototypes |
| **ML/Scaling** | Scikit-learn (StandardScaler, RobustScaler) |
| **Visualization** | Matplotlib, Seaborn, Power BI |
| **Version Control** | Git, GitHub |

---

## 📊 Data Pipeline (Phase 1 Complete)

```
Raw Data (8 CSVs)
    ↓
[preprocessing.py] → Load into PostgreSQL (normalized tables)
    ↓
[cleaning.py] → Remove nulls, duplicates, outliers → master_cleaned table
    ↓
[feature_engineering.py] → Engineer RFM + behavioral features → customer_features table
    ↓
[feature_scaling.py] → Log transform + standardize → clustering-ready datasets
    ↓
[eda_report.py] → Exploratory analysis + visualizations (6 charts + heatmap)
    ↓
PostgreSQL Gold Layer (Ready for Phase 2 & 3)
```

---

## 📁 Key Outputs (Phase 1)

### PostgreSQL Tables

| Table | Purpose | Rows | Columns |
|-------|---------|------|---------|
| `master_cleaned` | Clean transaction data for association rules | 100K+ | 6 (customer_id, order_id, timestamp, product_id, price, category) |
| `customer_features` | Raw engineered features | 40K+ | 7 (RFM + behavioral) |
| `customer_features_kmeans` | K-Means clustering ready (scaled, log-transformed) | 40K+ | 6 (numerical only) |
| `customer_features_kprototypes` | K-Prototypes ready (numerical + categorical) | 40K+ | 9 (mixed-type) |

### CSV Exports (Quick Reference)

Located in `data/` folder:
- `master_cleaned.csv` — For Ibrahim (Association Rules)
- `customer_features_kmeans.csv` — For Abdullah (K-Means)
- `customer_features_kprototypes.csv` — For Abdullah (K-Prototypes)
- `customer_features_full.csv` — Complete feature set (raw + scaled)

### Visualizations

- **eda_report.png** — 6 subplots: categories, trends, RFM distributions, scatter plot
- **correlation_heatmap.png** — Multicollinearity check (flags correlations > 0.85)

---

## 📈 Methodology

### Phase 1: Preprocessing & EDA (✅ Complete)
- Extract 8 raw CSVs, load into PostgreSQL (normalized schema)
- Clean data: handle nulls, duplicates, outliers, invalid prices
- Engineer features: RFM (Recency, Frequency, Monetary) + behavioral metrics
- Scale features: Log transformation + RobustScaler for clustering
- Validate: Multicollinearity check (correlation heatmap)

### Phase 2: Association Rule Mining (⏳ Ibrahim)
- Extract transaction baskets from `master_cleaned` (order → categories)
- Apply **Apriori** and **FP-Growth** algorithms
- Evaluate rules using support, confidence, lift
- Identify product associations and cross-sell opportunities
- Output: Association rules report with business insights

### Phase 3: Customer Segmentation (⏳ Abdullah)
- Use engineered features from `customer_features_kmeans`
- Determine optimal cluster count (Elbow Method, Silhouette Score)
- Apply **K-Means Clustering** (typically 3–5 clusters)
- Profile segments: RFM stats, category preferences, characteristics
- Output: Customer segments with actionable profiles

### Phase 4: Integration (⏳ Team)
- Analyze segment-specific product associations
- Merge Phase 2 + Phase 3 insights: "How do associations differ across segments?"
- Create holistic **Customer 360° profiles**
- Output: Integrated analysis report

### Phase 5: Power BI Dashboard (⏳ Team)
- Connect Power BI to PostgreSQL
- Build interactive visualizations:
  - RFM scatter matrix (Recency vs Monetary, bubble size = Frequency)
  - Geographic maps (customer locations)
  - Category Pareto chart (80/20 revenue rule)
  - Segment profiles with KPIs
- Present to Mr. Tahir Ejaz

---

## 🚀 Quick Start Guide

### 1. Prerequisites

```bash
# Install Python 3.9+ and PostgreSQL locally
# Create customer_360 database in PostgreSQL
# Set up .env file with DB_PASSWORD
```

Example `.env`:
```
DB_PASSWORD=your_postgres_password
```

### 2. Setup Environment

```bash
# Navigate to project
cd DM_project

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 3. Run Phase 1 Pipeline

```bash
# Execute in order:
python preprocessing.py          # Load CSVs → PostgreSQL
python cleaning.py               # Clean data → master_cleaned table
python feature_engineering.py    # Engineer features → customer_features
python feature_scaling.py        # Scale for clustering → clustering-ready tables
python eda_report.py             # Generate visualizations + statistics
```

### 4. Verify Success

After running all scripts:
- ✅ Check PostgreSQL: Tables `master_cleaned`, `customer_features_kmeans` exist
- ✅ Check `data/` folder: CSV exports present
- ✅ Check project root: `eda_report.png` and `correlation_heatmap.png` generated
- ✅ Check console output: No errors, "Feature Engineering Complete" message

---

## 📖 For Team Members

### Ibrahim (Phase 2: Association Rules)

**Start here:** [HANDOVER.md](HANDOVER.md) — "For Ibrahim (Association Rule Mining)"

```python
# Load data for association rules:
import pandas as pd
from preprocessing import engine

master_df = pd.read_sql("SELECT * FROM master_cleaned", engine)
# Group by order_id, extract category lists, apply Apriori/FP-Growth
```

### Abdullah (Phase 3: Customer Segmentation)

**Start here:** [HANDOVER.md](HANDOVER.md) — "For Abdullah (Customer Segmentation)"

```python
# Load clustering-ready data:
import pandas as pd
from preprocessing import engine

clustering_df = pd.read_sql("SELECT * FROM customer_features_kmeans", engine)
# Apply K-Means, determine optimal clusters, profile segments
```

---

## 🔀 Git Workflow

### Current Status
- **Branch:** `feature-preprocessing`
- **Status:** Ready to merge

### Merge to Main
```bash
git checkout main
git pull origin main
git merge feature-preprocessing
git push origin main
```

### For Phase 2 & 3
```bash
# Create new branches for independent work:
git checkout main
git pull origin main

# Ibrahim
git checkout -b feature-association-rules

# Abdullah
git checkout -b feature-segmentation
```

---

## 📚 Project Structure

```
DM_project/
├── .gitignore                          # Ignore data/, venv/, .env
├── .env                                # DB_PASSWORD (not committed)
├── README.md                           # This file
├── HANDOVER.md                         # Phase 2 & 3 guidance
├── requirements.txt                    # Python dependencies
│
├── preprocessing.py                    # Phase 1: Extract & Load (ETL)
├── cleaning.py                         # Phase 1: Transform (data quality)
├── feature_engineering.py              # Phase 1: Engineer RFM + features
├── feature_scaling.py                  # Phase 1: Log transform + scale
├── eda_report.py                       # Phase 1: EDA visualizations
│
├── data/                               # CSV storage (git-ignored)
│   ├── olist_*.csv                    # Raw datasets
│   ├── master_cleaned.csv             # Phase 1 output
│   ├── customer_features_*.csv        # Phase 1 output
│   └── *.png                          # EDA visualizations
│
└── venv/                              # Virtual environment (git-ignored)
```

---

## 📊 Database Schema Quick Reference

### For Association Rules (Ibrahim)
```sql
SELECT order_id, category, COUNT(*) 
FROM master_cleaned 
GROUP BY order_id, category;
```

### For Clustering (Abdullah)
```sql
SELECT * 
FROM customer_features_kmeans 
WHERE log_monetary_scaled > 1.0 
LIMIT 10;
