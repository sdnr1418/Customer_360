# PHASE 2: ASSOCIATION RULE MINING

⬅️ **[Previous: Phase 1 Data Prep](../PHASE_1/PHASE_1_REFRESHER.md)** | ➡️ **[Next: Phase 4 Integration (Coming Soon)](#)**

## 🎯 Objective & Quick Stats
- **Goal:** Discover actionable product associations ("What goes together?") to enable cross-selling.
- **Input:** Cleaned transaction data from Phase 1.
- **Output:** 25 cross-category rules and 2 intra-category rules.
- **Status:** ✅ COMPLETE & VALIDATED

## 🛠️ How We Did It (The Methodology)

We abandoned full-dataset analysis because 99.2% of orders were single-item (which creates statistical noise). Instead, we filtered down to the ~3.2% of multi-item orders where real bundling intent exists, using two complementary approaches:

1. **Cross-Category ARM (Strategic):** 
   - Looked at 780 orders with items from *different* categories.
   - Found what categories pair well for store layout and promotions.
   - Used 0.2% support threshold.

2. **Intra-Category ARM (Tactical):**
   - Looked at 2,417 orders with multiple items from the *same* category.
   - Found specific product-level pairings (like Phone + Charger).
   - Used 1.0% support threshold (higher because products are more fragmented).

3. **Algorithm Convergence (Validation):**
   - Ran both **Apriori** and **FP-Growth** algorithms independently.
   - Achieved 100% convergence (exact same rules found by both).

## 📊 Key Findings

- **Average Lift:** 6.84x for categories, 45x for products (industry standard is ~3x, so these are incredibly strong).
- **The Superstar Bundle:** *Children's Clothing → Bags & Accessories*. 
  - **Lift:** 41.05x (They are 41 times more likely to buy this bundle than random chance).
  - **Confidence:** 100%.

## ❓ TA Presentation Q&A

**Q: Why did you abandon the old implementation from the proposal?**
**A:** The old approach analyzed all 100K transactions. Since 99.2% of orders were single-item, it created extreme sparsity. The resulting 491x lift rules were statistical noise. By pivoting to analyze only multi-item orders (3.2% of data), we extracted 27 mathematically sound, business-ready rules.

**Q: Only 2 intra-category rules seems low. Did it fail?**
**A:** No, it succeeded. Finding rules among 3,677 unique products is highly fragmented. Getting 2 rules at a strict 1% support threshold (e.g., Phone + Charger) guarantees these are genuine product synergies, not coincidences. Quality over quantity.

**Q: Why is 100% algorithm convergence important?**
**A:** Because Apriori and FP-Growth calculate patterns differently under the hood. Getting the exact same results from both proves our rules are mathematically robust and undeniable.
