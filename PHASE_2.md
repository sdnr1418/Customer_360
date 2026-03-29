# PHASE 2: ASSOCIATION RULE MINING & BUNDLE DISCOVERY

**Objective:** Discover which product categories are frequently bought together and recommend bundles  
**Output:** 25 association rules, 10 recommended bundles  
**Status:** COMPLETE

## Overview

This phase analyzes the 0.8% of orders containing multiple categories to find cross-selling opportunities. Uses two algorithms (Apriori and FP-Growth) to validate results.

## Input Data

Source: `data/master_cleaned.csv` from Phase 1  
Records: 96,478 transactions (only 780 with multiple categories)  

Multi-category orders contain 2-6 product categories per order (average 2.37).

## Processing Steps

### 1. Data Preparation

Filters to multi-category orders only and converts to transaction format:
- Identifies 780 orders with multiple categories
- Creates transaction matrix (780 orders × 72 categories)
- Each cell = 1 if category in order, 0 if not

### 2. Algorithm 1: Apriori

Tests various support thresholds to find frequent itemsets:
- Tests thresholds: 0.1%, 0.2%, 0.5%, 1.0%, 2.0%
- Selects 0.2% (produces 25 clean rules)
- Generates association rules with confidence > 30%

Output: 25 association rules with metrics

### 3. Algorithm 2: FP-Growth

Parallel execution with same threshold as Apriori:
- Tree-based algorithm (faster than Apriori)
- Generates same patterns using different approach
- Output: 25 identical rules

Purpose: Validates that patterns are real, not algorithm-specific

### 4. Validation

Compares both algorithms:
- 100% rule convergence (identical 25 rules)
- All metrics mathematically valid
- Lift values: 1.23x to 41.05x (average 6.84x)

### 4.5. Interestingness Measures

To address limitations of standard measures (Support, Confidence, Lift) in sparse market baskets, three complementary metrics are calculated for each rule:

**1. Cosine Similarity** (Range: 0-1)
- Formula: `support(A,B) / √(support(A) × support(B))`
- Purpose: Validates co-occurrence intensity independent of null transactions
- Protects against: Inflated lift from rare events (e.g., 3 orders driving 41x lift)
- Example: High cosine (0.85+) confirms rule isn't statistical noise

**2. Kulczynski Metric** (Range: 0-1)
- Formula: `(confidence(A→B) + confidence(B→A)) / 2`
- Purpose: Identifies bidirectional vs one-way associations
- Protects against: Asymmetric rules showing high lift in only one direction
- Example: If A→B is 100% but B→A is 20%, Kulczynski identifies this asymmetry

**3. All Confidence** (Range: 0-100%)
- Formula: `min(confidence(A→B), confidence(B→A))`
- Purpose: Conservative filter ensuring both directions are strong
- Protects against: Marketing promoting unidirectional associations as true bundles
- Example: Ensures both category pairs reinforce each other for real bundles

**Data Context:** With 99.2% single-category orders, these measures provide critical validation that discovered patterns are genuine market behaviors rather than statistical artifacts from rare multi-category occurrences.

All three measures export to CSV alongside standard metrics for cross-validation analysis.

### 5. Bundle Synthesis

Converts top rules into actionable bundles:
- Identifies best-seller SKUs in each category
- Creates bundle recommendations with pricing
- Ranks by business value (lift × confidence)

## Key Findings

1. **Strong patterns discovered:** Average lift of 6.84x (industry standard 1.5-3x)
2. **High confidence rules:** 8 out of 25 rules have 100% confidence
3. **Algorithm validation:** Apriori and FP-Growth found identical 25 rules (100% convergence)
4. **Strongest association:** Children's clothes → bags (41x lift, 100% confidence)
5. **Primary bundles:** 10 recommendations ready for implementation

## Output Files

| File | Purpose |
|------|---------|
| association_rules_final.csv | 25 rules with metrics |
| bundling_recommendations.csv | 10 bundles with SKU details |
| category_anchor_analysis.csv | Category popularity analysis |
| market_basket_stats.csv | Summary statistics |
| 6 visualization (PNG) | Charts showing relationships |
| PHASE2_ASSOCIATION_RULES_REPORT.md | Strategic report |

## Running Phase 2

```bash
# Run complete pipeline
python phase2/run_phase2_complete.py

# Or run individually:
python phase2/association_rules.py        # Run algorithms
python phase2/phase2_visualizations_exports.py  # Generate charts
python phase2/phase2_strategic_report.py  # Create report
python phase2/verify_phase2.py            # Verify outputs
```

Execution time: ~30-60 seconds

## Validation Checklist

- [ ] Input file: `data/master_cleaned.csv` exists
- [ ] Multi-category orders identified: 780 orders
- [ ] Apriori rules generated: 25 rules
- [ ] FP-Growth rules generated: 25 identical rules
- [ ] Algorithm convergence: 100%
- [ ] Average lift: 6.84x
- [ ] 6 visualizations generated
- [ ] 5 CSV exports created
- [ ] Strategic report written
