# Phase 2: Association Rule Mining - Strategic Insights & SKU Affinities

**Generated:** March 29, 2026 at 04:00:30

**Study Period:** Olist Marketplace (100,196 transactions, 96,478 unique orders)

---

## Executive Summary

### Key Finding: Olist is a **SPECIALIZED STORE**

- **99.2%** of orders contain a single product category
- **0.8%** (780 orders) are multi-category "bundler" transactions
- Customers shop by category focus, not as one-stop shoppers
- **Implication:** Strategic bundling is a HIGH-IMPACT growth opportunity

### Market Basket Composition
- Total Orders: 96,478
- Single-Category Orders: 95,698 (99.2%)
- Multi-Category Orders: 780 (0.8%)
- Average Categories/Order: 1.01

---

## Section 1: Anchor vs Add-On Analysis
### Q1: Which categories initiate purchases vs complement them?

**Methodology:** Calculated Anchor Index = (Antecedent Count) / (Antecedent Count + Consequent Count)
- **Anchor Index 1.0** = Pure initiator categories (always trigger purchases)
- **Anchor Index 0.0** = Pure add-on categories (always secondary)

### Top 5 ANCHOR Categories (Purchase Initiators)
1. **kitchen_dining_laundry_garden_furniture** - Anchor Index: 1.00
2. **costruction_tools_garden** - Anchor Index: 1.00
3. **pet_shop** - Anchor Index: 1.00
4. **luggage_accessories** - Anchor Index: 1.00
5. **art** - Anchor Index: 1.00

### Top 5 ADD-ON Categories (Complementary)
1. **housewares** - Anchor Index: 0.00
2. **others** - Anchor Index: 0.00
3. **baby** - Anchor Index: 0.00
4. **health_beauty** - Anchor Index: 0.00
5. **sports_leisure** - Anchor Index: 0.00

**Business Implication:** Feature anchor categories prominently; position add-ons for upsell

---

## Section 2: Hidden Affinities & Surprise Associations
### Q2: Which unexpected category pairs have strong associations?

**Methodology:** Identified rules with Lift > 1.5 (associations 50%+ stronger than random)

### Top 5 Surprise Associations (Highest Lift)
1. **fashion_childrens_clothes -> fashion_bags_accessories**
   - Lift: 41.05x | Confidence: 100.0% | Support (multi-cart): 0.3%
2. **books_general_interest -> market_place**
   - Lift: 26.00x | Confidence: 40.0% | Support (multi-cart): 0.3%
3. **audio -> watches_gifts**
   - Lift: 19.50x | Confidence: 100.0% | Support (multi-cart): 0.8%
4. **fashion_shoes -> baby**
   - Lift: 8.39x | Confidence: 100.0% | Support (multi-cart): 0.3%
5. **luggage_accessories -> stationery**
   - Lift: 7.88x | Confidence: 33.3% | Support (multi-cart): 0.6%

**Business Implication:** Use surprise associations for cross-category promotions and discovery

---

## Section 3: Top Bundling Opportunities by Lift
### Q3: Should we recommend category pairs as bundles?

**Analysis:** Ranked all category pairs by their **Lift** (association strength relative to random purchase)

### Top 10 Bundling Pairs (Lift-Ranked)

**1. fashion_childrens_clothes + fashion_bags_accessories**
  - Lift: **41.05x** | Confidence: 100.0% | Support (multi-cart): 0.3%
**2. books_general_interest + market_place**
  - Lift: **26.00x** | Confidence: 40.0% | Support (multi-cart): 0.3%
**3. audio + watches_gifts**
  - Lift: **19.50x** | Confidence: 100.0% | Support (multi-cart): 0.8%
**4. fashion_shoes + baby**
  - Lift: **8.39x** | Confidence: 100.0% | Support (multi-cart): 0.3%
**5. luggage_accessories + stationery**
  - Lift: **7.88x** | Confidence: 33.3% | Support (multi-cart): 0.6%
**6. tablets_printing_image + cool_stuff**
  - Lift: **7.76x** | Confidence: 66.7% | Support (multi-cart): 0.3%
**7. fashion_bags_accessories + others**
  - Lift: **6.06x** | Confidence: 47.4% | Support (multi-cart): 1.2%
**8. food_drink + sports_leisure**
  - Lift: **5.42x** | Confidence: 50.0% | Support (multi-cart): 0.3%
**9. pet_shop + others**
  - Lift: **5.11x** | Confidence: 40.0% | Support (multi-cart): 0.8%
**10. perfumery + health_beauty**
  - Lift: **4.48x** | Confidence: 40.7% | Support (multi-cart): 1.4%

**Business Implication:** Highest-lift pairs are prime candidates for website bundles, email campaigns, and recommendations

---

## Section 4: Market Type Assessment
### Q4: What market basket structure does Olist have?

**Finding:** SPECIALIZED STORE

- 99.2% of customers focus on specific categories per order
- Only 0.8% purchase multi-category items (the "bundlers")
- Not a one-stop-shop; customers visit for targeted category purchases

**Strategic Context:** This specialized behavior makes the 0.8% bundlers even more valuable.
By showing the right cross-category offers to focused shoppers, we can unlock bundling growth.

---

## Section 5: Strategic Bundling & SKU Affinities (Flagship)
### Actionable Product-Level Recommendations

**Approach:** For each top category pair, identify the best-selling SKU from each category.
This "synthetic bundling" strategy balances:
- Statistical rigor (category associations are mathematically validated)
- Business practicality (recommending proven best-sellers)
- Risk mitigation (avoiding statistical flukes from small sample)

### 10 Recommended Synthetic Bundles

**Bundle #1: fashion_childrens_clothes -> fashion_bags_accessories** (Lift: 41.1x)
> SKU from fashion_childrens_clothes: `57bdf3098169cccdb62221bd3e089c` (3 sales overall)
> SKU from fashion_bags_accessories: `d017a2151d543a9885604dc62a3d9d` (137 sales overall)
> Recommended as: Cross-category bundle | Confidence: 100.0%

**Bundle #2: books_general_interest -> market_place** (Lift: 26.0x)
> SKU from books_general_interest: `f35927953ed82e19d06ad3aac2f063` (54 sales overall)
> SKU from market_place: `8d1cfc0463b545928bfb4e589e017b` (23 sales overall)
> Recommended as: Cross-category bundle | Confidence: 40.0%

**Bundle #3: audio -> watches_gifts** (Lift: 19.5x)
> SKU from audio: `db5efde3ad0cc579b130d71c4b2db5` (48 sales overall)
> SKU from watches_gifts: `53b36df67ebb7c41585e8d54d6772e` (304 sales overall)
> Recommended as: Cross-category bundle | Confidence: 100.0%

**Bundle #4: fashion_shoes -> baby** (Lift: 8.4x)
> SKU from fashion_shoes: `a2c75a23c2f838881dd4275c0cec51` (9 sales overall)
> SKU from baby: `cac9e5692471a0700418aa3400b9b2` (87 sales overall)
> Recommended as: Cross-category bundle | Confidence: 100.0%

**Bundle #5: luggage_accessories -> stationery** (Lift: 7.9x)
> SKU from luggage_accessories: `f71973c922ccaab05514a36a8bc741` (60 sales overall)
> SKU from stationery: `fb55982be901439613a95940feefd9` (82 sales overall)
> Recommended as: Cross-category bundle | Confidence: 33.3%

**Bundle #6: tablets_printing_image -> cool_stuff** (Lift: 7.8x)
> SKU from tablets_printing_image: `6bbe55cf8f85c87b6eebb775a53402` (32 sales overall)
> SKU from cool_stuff: `c6dd917a0be2a704582055949915ab` (120 sales overall)
> Recommended as: Cross-category bundle | Confidence: 66.7%

**Bundle #7: fashion_bags_accessories -> others** (Lift: 6.1x)
> SKU from fashion_bags_accessories: `d017a2151d543a9885604dc62a3d9d` (137 sales overall)
> SKU from others: `5a848e4ab52fd5445cdc07aab1c40e` (187 sales overall)
> Recommended as: Cross-category bundle | Confidence: 47.4%

**Bundle #8: food_drink -> sports_leisure** (Lift: 5.4x)
> SKU from food_drink: `84f5c4f480ad6c9998d6a6860f1a2e` (23 sales overall)
> SKU from sports_leisure: `c6336fa91fbd87c359e44f5dca5a90` (80 sales overall)
> Recommended as: Cross-category bundle | Confidence: 50.0%

**Bundle #9: pet_shop -> others** (Lift: 5.1x)
> SKU from pet_shop: `a4aa7c1427c31344e5f7cc3d839fe5` (41 sales overall)
> SKU from others: `5a848e4ab52fd5445cdc07aab1c40e` (187 sales overall)
> Recommended as: Cross-category bundle | Confidence: 40.0%

**Bundle #10: perfumery -> health_beauty** (Lift: 4.5x)
> SKU from perfumery: `2028bf1b01cafb2d2b1901fca40832` (128 sales overall)
> SKU from health_beauty: `154e7e31ebfa092203795c972e5804` (262 sales overall)
> Recommended as: Cross-category bundle | Confidence: 40.7%

#### Implementation Roadmap
1. **Quick Wins:** Launch top 3 bundles as "Frequently Bought Together" recommendations
2. **Email Campaign:** Feature Bundle #1 (41x lift) to high-value customers
3. **A/B Testing:** Compare bundle conversion rates vs control group
4. **Optimization:** Adjust SKU selection based on real bundle purchase data

---

## Methodology & Data Notes

### Algorithms Used
- **Apriori:** Frequent itemset mining with support threshold optimization
- **FP-Growth:** Fast pattern mining for validation of Apriori results
- **Both converged on 0.2% support threshold** (optimal for 780 multi-category orders)

### Support Metric Clarification
**Important:** All support percentages are **CONDITIONAL on multi-item carts** (780 orders, 0.8% of total)

Example: A rule with 1.4% support means:
- 1.4% of the 780 multi-category orders (11 orders)
- NOT 1.4% of all 96,478 orders
- This clarification prevents marketing misinterpretation

### Key Statistics
- Total Association Rules: 25
- Average Rule Lift: 6.84x
- Average Confidence: 52.9%
- Max Lift Observed: 41.05x
- Categories Involved: 33 out of 72 total

---

## Appendix: Artifacts Generated

### Visualizations (6 charts)
1. `01_anchor_addon.png` - Anchor Index breakdown (initiators vs add-ons)
2. `02_bundle_heatmap.png` - Bundle Strength Matrix (Lift × Confidence × Support)
3. `03_market_composition.png` - Pie chart (99.2% vs 0.8%)
4. `04_lift_support_scatter.png` - Category pair 2D space
5. `05_category_treemap.png` - Treemap view of top 15 pairs
6. `06_synthetic_bundles.png` - Top 6 bundles with SKU details

### Data Exports (5 CSV files)
1. `association_rules_final.csv` - 25 rules with metrics
2. `category_anchor_analysis.csv` - Anchor index by category
3. `bundling_recommendations.csv` - Top 20 bundling pairs
4. `market_basket_stats.csv` - Composition statistics
5. `synthetic_bundles.csv` - 10 bundles with SKU details

## Next Steps

1. **Marketing Review:** Present Section 5 (Synthetic Bundles) to marketing team
2. **Product Implementation:** Code "Frequently Bought Together" widgets
3. **A/B Testing:** Compare bundle recommendations vs control (7-14 days)
4. **Optimization Loop:** Refine SKU selection based on real conversion data
5. **Phase 2B (Optional):** Analyze lifetime customer baskets for returning customer patterns
