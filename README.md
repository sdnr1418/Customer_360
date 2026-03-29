# Data Mining Project: Olist Product Bundling Analysis

**Status:** Phase 1 & 2 Complete  
**Last Updated:** March 29, 2026

## Project Overview

This project analyzes product purchasing patterns in the Olist Brazilian marketplace to identify cross-selling opportunities. We analyzed 96,478 transactions across 72 product categories and discovered 25 association rules with up to 41x lift, resulting in 10 recommended product bundles.

**Main Finding:** While 99.2% of orders contain single categories, the remaining 0.8% reveal strong cross-category purchasing patterns. The strongest association (children's clothing → bags) shows 41x higher probability than random chance.

## Project Structure

```
DM_project/
├── PHASE_1.md              Phase 1 data preparation guide
├── PHASE_2.md              Phase 2 analysis guide
├── README.md               This file
│
├── phase1/                 Phase 1 scripts
│   ├── preprocessing.py
│   ├── cleaning.py
│   ├── feature_engineering.py
│   └── eda_report.py
│
├── phase2/                 Phase 2 scripts
│   ├── association_rules.py
│   ├── phase2_visualizations_exports.py
│   ├── phase2_strategic_report.py
│   └── run_phase2_complete.py
│
├── phase2_outputs/         Final deliverables
│   ├── association_rules_final.csv
│   ├── bundling_recommendations.csv
│   ├── visualizations/     6 charts (PNG)
│   └── exports/            5 CSV files
│
└── data/                   Raw and processed data files
```

## What We Did

### Phase 1: Data Cleaning
- Consolidated 8 raw CSV files (100K+ records)
- Removed invalid records (14.3% filtered out)
- Generated 96,478 clean transactions
- Created feature sets for analysis
- Output: master_cleaned.csv + 4 feature files

### Phase 2: Association Rule Mining
- Applied Apriori algorithm: 25 rules at 0.2% support threshold
- Applied FP-Growth algorithm: 25 identical rules (validation)
- Identified 10 actionable bundles with strong associations
- Generated visualizations and comprehensive report
- Output: association rules, bundle recommendations, 6 charts
## Key Results

| Metric | Value |
|--------|-------|
| Records Processed | 96,478 |
| Product Categories | 72 |
| Multi-category Orders | 780 (0.8%) |
| Association Rules Found | 25 |
| Algorithm Agreement | 100% (Apriori = FP-Growth) |
| Strongest Association | 41.05x lift (children's → bags) |
| Average Lift | 6.84x |
| High Confidence Rules (100%) | 8 out of 25 |
| Recommended Bundles | 10 |

## Top Bundles (First 3)

1. **Children's Clothing → Bags** - 41x lift, 100% confidence
2. **Books → Marketplace** - 26x lift, 40% confidence  
3. **Audio → Watches & Gifts** - 19.5x lift, 100% confidence

*See phase2_outputs/bundling_recommendations.csv for all 10*

## How to Run

```bash
# Activate environment
source venv/Scripts/Activate.ps1

# Run all validations
python RUN_PROJECT_COMPLETE.py
```

## Key Files

- **Phase 1 Guide:** [PHASE_1.md](PHASE_1.md)
- **Phase 2 Guide:** [PHASE_2.md](PHASE_2.md)  
- **Bundle CSV:** phase2_outputs/bundling_recommendations.csv
- **Rules CSV:** phase2_outputs/association_rules_final.csv
- **Report:** phase2_outputs/PHASE2_ASSOCIATION_RULES_REPORT.md
- **Charts:** phase2_outputs/visualizations/

## Technologies Used

- Python 3.12
- pandas, numpy (data processing)
- scikit-learn, mlxtend (algorithms)
- Apriori & FP-Growth algorithms
- matplotlib, seaborn (visualization)

**For questions or navigation help, see [PRESENTATION_INDEX.md](PRESENTATION_INDEX.md)**
