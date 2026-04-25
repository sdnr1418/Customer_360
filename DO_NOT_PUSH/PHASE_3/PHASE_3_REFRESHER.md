# PHASE 3: CUSTOMER SEGMENTATION

⬅️ **[Previous: Phase 1 Features](../PHASE_1/PHASE_1_REFRESHER.md)** | ➡️ **[Next: Phase 4 Integration (Coming Soon)](#)**

## 🎯 Objective & Quick Stats
- **Goal:** Group 93,398 customers into distinct, actionable segments based on behavior and geography.
- **Input:** 9 engineered features (6 numerical, 3 categorical) from Phase 1.
- **Output:** 3 distinct customer segments.
- **Status:** ✅ COMPLETE & VALIDATED

## 🛠️ How We Did It (The Methodology)

1. **Algorithm Selection (K-Prototypes):** 
   - Standard K-Means only handles numbers (losing geographic/category info). K-Prototypes handles *mixed data types* (Euclidean distance for numbers, Hamming distance for categories).
2. **Scalability Solution (Sample-Train-Predict):**
   - Running K-Prototypes on 93K rows takes 30+ minutes. 
   - We took a **15% stratified sample** to train the centroids in 3 minutes, then predicted labels for all 93K customers in 30 seconds.
3. **Evaluating 'K' (Consensus):**
   - Tested K=2 through K=6 using 4 intrinsic metrics.
   - **Silhouette Score** (coherence) pointed to K=3.
   - **Davies-Bouldin** (separation) pointed to K=4.
   - **Elbow Method** pointed to K=3 to 5.
   - **Consensus:** K=3 provided the tightest, most business-actionable clusters.

## 📊 Key Findings: The 3 Segments

| Segment | Size | Avg Spend | Recency | Repeat % | Label / Business Action |
|---------|------|-----------|---------|----------|-------------------------|
| **0** | 41% | $52.89 | 278 days | 2.2% | 💤 **Low-value, Churned:** Need aggressive reactivation. |
| **1** | 41% | $226.57 | 272 days | 3.7% | 💰 **High-value, Inactive:** Win-back campaign targets. |
| **2** | 18% | $102.90 | 70 days | 3.5% | 🔥 **Recent & Active:** Prime targets for Phase 2 cross-selling. |

## ❓ TA Presentation Q&A

**Q: Why K-Prototype and not K-Means?**
**A:** K-Means forces us to drop categorical data. K-Prototype lets us cluster using both numerical spending habits AND categorical preferences (like State and Favorite Category) simultaneously. 

**Q: Doesn't training on a 15% sample ruin accuracy?**
**A:** No, because it was a *stratified* sample. If 5% of our full dataset are high-value buyers, our 15% sample maintains exactly that 5% ratio. This ensures our cluster centroids are perfectly representative while giving us a 10x speedup in computation.

**Q: What if your evaluation metrics disagree (e.g., Davies-Bouldin says K=4, Silhouette says K=3)?**
**A:** We use consensus and robustness. Silhouette is the most comprehensive metric (weighing both coherence and separation), so we lead with K=3. We acknowledge K=4 was strong for separation, showing we didn't just guess blindly.

**Q: How does this connect to Phase 2?**
**A:** Phase 2 tells us *what products bundle together*. Phase 3 tells us *who the customers are*. Phase 4 will merge them to ask: "Does Segment 1 buy different bundles than Segment 2?"
