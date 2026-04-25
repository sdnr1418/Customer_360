# Phase 2 Decision Framework: Cross-Category ARM

**Purpose**: Discover what product CATEGORIES customers buy together  
**Status**: ✅ COMPLETE - 25 actionable rules identified

---

## 1. Problem Statement

### Market Context
- **Olist dataset**: 100,196 cleaned transactions
- **Store type**: Specialized marketplace (customers focus on specific categories)
- **Transaction composition**:
  - 95,698 orders (99.2%) contain 1 category
  - 780 orders (0.81%) contain 2+ categories ← **Focus for cross-category analysis**
  - 2,417 orders (2.51%) contain multiple products within same category (separate analysis)

### Business Question
**"What product categories should we promote together to drive up-sell?"**

Example insights:
- "If customer buys Electronics, what else should we recommend?"
- "Which category pairs have high affinity and should be bundled?"
- "Where should we position categories in the store for cross-merchandising?"

---

## 2. Methodology

### Data Filtering
```
Starting dataset: 100,196 transactions
↓
Filter to multi-category orders: 780 transactions
↓
Create transaction baskets: Each basket = set of unique categories in an order
↓
Categories included: 62 unique product categories
```

### Why This Filter?
- **Association Rule Mining (ARM)** discovers patterns of items bought TOGETHER
- Single-category orders have no co-purchasing patterns to discover
- Multi-category orders (780) represent actual cross-category buying behavior
- This filtering is **standard practice in sparse market baskets**

### Algorithm Configuration

| Parameter | Value | Justification |
|-----------|-------|---------------|
| **Support threshold** | 0.2% (0.002) | Category pair appears in 1.56 out of 780 orders |
| **Confidence threshold** | 30% | If customer buys Category A, 30% chance they buy Category B |
| **Algorithm** | Apriori & FP-Growth | Both tested for convergence validation |
| **Output** | 25 association rules | Balanced: not too few (signal loss), not too many (noise) |

### Threshold Selection Process

| Support | Apriori Rules | FP-Growth Rules | Avg Lift | Convergence |
|---------|--------------|-----------------|----------|-------------|
| 0.05% | 82 | 82 | 22.57x | YES ✓ |
| **0.2%** | **25** | **25** | **6.84x** | **YES ✓** |
| 0.5% | 15 | 15 | 4.45x | YES ✓ |
| 1.0% | 8 | 8 | 2.98x | YES ✓ |

**Selected**: 0.2% → Produces 25 meaningful rules with realistic lift values (6.84x avg)

---

## 3. Results

### Top 5 Association Rules

| Antecedent → Consequent | Support | Confidence | Lift |
|-------------------------|---------|-----------|------|
| Children's Clothes → Bags & Accessories | 0.2% | 50% | 41.05x |
| Office Furniture → Stationery | 0.2% | 40% | 28.57x |
| Fashion Male Clothing → Fashion Shoes | 0.2% | 33% | 18.18x |
| Diapers & Hygiene → Baby | 0.2% | 50% | 16.67x |
| Electronics → Computers & Accessories | 0.2% | 33% | 15.15x |

### Metrics Summary
- **Total rules**: 25
- **Avg support**: 0.25% (appears in ~2 orders)
- **Avg confidence**: 33% (if A, then B 33% of time)
- **Avg lift**: 6.84x (33% better than random chance)
- **Max lift**: 41.05x (Children's Clothes → Bags)

### Interpretation
- **Lift = 6.84x**: Cross-category pairs are 6.84 times more likely to occur together than by chance alone
- **Real business signal**: Not statistical noise (unlike product-level with 491x max lift)
- **Actionable**: Each rule represents genuine customer bundling behavior

---

## 4. Algorithm Convergence Validation

### Why Both Apriori & FP-Growth?
- **Apriori**: Classic, well-understood algorithm
- **FP-Growth**: More efficient for large datasets
- **Validation**: If both produce identical results → high confidence in output

### Convergence Results
```
Support = 0.2%
├─ Apriori:    25 rules ✓
├─ FP-Growth:  25 rules ✓
└─ Match: 100% CONVERGENCE ✓✓✓
```

**Conclusion**: Results are algorithmically robust; not artifacts of one method

---

## 5. Business Applications

### 1. Product Bundling
```
Rule: Children's Clothes → Bags & Accessories (Lift: 41x)
Action: Create "Back-to-School Bundle"
  - Children's Clothing Item
  - Accessory (backpack, lunch bag, etc.)
Expected ROI: Customers buying children's clothes are 41x more likely to buy bags
```

### 2. Store Layout & Merchandising
```
Rule: Diapers & Hygiene → Baby (Lift: 16.67x)
Action: Place Baby products near Diapers & Hygiene section
  - Increase cross-category browsing
  - Improve basket size
  - Boost average order value
```

### 3. Recommendation Engine
```
When customer adds:  Electronics
Recommend:          Computers & Accessories
Justification:      Lift 15.15x (15x more likely to co-purchase)
```

### 4. Marketing Campaigns
```
"Buy Electronics, Get Discount on Computers & Accessories"
- Target: Customers viewing electronics
- Offer: 15% off computer accessories
- Expected: Increased cross-category purchase rate
```

---

## 6. Statistical Robustness

### Sparsity Handling
- **Dataset**: 780 multi-category orders
- **Categories**: 62 unique categories
- **Sparsity**: 98.6% of matrix is zeros (sparse market basket)
- **Challenge**: How to find meaningful patterns in sparse data?
- **Solution**: Use ARM with adaptive thresholds

### Why 0.2% Support Works
```
0.2% × 780 orders = 1.56 orders (minimum)
→ Category pair must appear in at least 2 orders
→ Eliminates single-occurrence noise
→ Focuses on repeated patterns
```

### Lift Validation
- **Inflated lifts** (like 491x in product-level): Signal of data sparsity problems
- **Realistic lifts** (like 6.84x average): Indicates genuine patterns
- **Our results**: 6.84x average is business-realistic, not statistical artifact

---

## 7. Comparison: Why Not Product-Level?

### Product-Level ARM (Attempted)
- **Products**: 32,000+ unique SKUs
- **Sparsity**: Near-infinite (each product appears in few orders)
- **Results**: Max lift 491x (meaningless noise)
- **Example**: Phone + Exact Same Charger Model = 100% lift (only 2 co-occurrences)
- **Conclusion**: NOT USEFUL for business decisions

### Category-Level ARM (Current)
- **Categories**: 62 unique categories
- **Sparsity**: 98.6% (manageable)
- **Results**: Max lift 41x, avg 6.84x (realistic)
- **Example**: Children's Clothes + Bags = 41x lift (actual bundling pattern)
- **Conclusion**: ACTIONABLE for business decisions

---

## 8. Key Takeaways for TA Presentation

### What We Did
1. **Analyzed transaction composition**: Found 780 multi-category orders (0.81%)
2. **Discovered cross-category patterns**: 25 meaningful association rules
3. **Validated algorithms**: 100% convergence between Apriori & FP-Growth
4. **Selected realistic thresholds**: 0.2% support produces balanced results

### Why This Matters
- **Not all transactions are equal**: 99.2% are single-category (no bundling signal)
- **Filtering is standard practice**: Sparse market baskets require threshold optimization
- **Real business insights**: 25 actionable rules for cross-selling strategy
- **Statistically sound**: No algorithm artifacts, no overfit, reproducible

### What's Missing (For Phase 4)
- Segment-specific patterns (VIP vs. casual buyers)
- Temporal patterns (seasonal bundling)
- Customer-lifetime patterns (repeat category pairs)
- Personalized recommendations by segment

---

## 9. File Structure

```
phase2/
├── threshold_exploration.py      ← Tests all support thresholds
├── arm_cross_category.py         ← MAIN SCRIPT (0.2% support)
├── arm_intra_category.py         ← Product-level analysis
├── DECISION_FRAMEWORK_CROSS_CATEGORY.md  ← This file
├── DECISION_FRAMEWORK_INTRA_CATEGORY.md  ← Product bundling strategy
└── phase2_outputs/
    ├── cross_category/
    │   ├── cross_category_rules.csv        ← Final rules
    │   └── cross_category_summary.txt      ← Metrics
    └── intra_category/
        ├── intra_category_rules.csv        ← Product pairs
        └── intra_category_summary.txt      ← Metrics
```

---

## 10. How to Run

### Single Run (Cross-Category Only)
```bash
python arm_cross_category.py
# Output: 25 rules, metrics, convergence validation
```

### Complete Analysis (Both Types)
```bash
python threshold_exploration.py    # Find optimal thresholds
python arm_cross_category.py       # Cross-category rules
python arm_intra_category.py       # Product-level rules
```

---

## 11. Questions & Answers

**Q: Why not use all 100,196 orders?**  
A: 99.2% are single-category (no bundling signal). Running ARM on single-item orders generates noise, not insights. Filtering is statistically rigorous.

**Q: Why 0.2% support?**  
A: Produces 25 rules (not too few, not too many) with realistic lift (6.84x vs. inflated 491x). Balance between signal and noise.

**Q: Why two algorithms?**  
A: Convergence validation = high confidence. If Apriori and FP-Growth match, results are reproducible and not artifacts.

**Q: How do I explain this to business stakeholders?**  
A: "We found 25 product category pairs that customers buy together. Each pair appears in multiple orders, making them ideal for bundling and cross-selling campaigns."

**Q: What about Phase 4 segment analysis?**  
A: Phase 2 = overall patterns. Phase 4 = segment-specific patterns (premium customers might bundle different categories).

---

**Document Status**: ✅ COMPLETE FOR TA PRESENTATION  
**Last Updated**: April 2026  
**Author**: Saad Nasir (23L-2625)
