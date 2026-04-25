# Customer 360 — Quick Reference Sheet

> **Project:** Data Mining on Olist Brazilian E-Commerce (2016–2018)
> **Status:** Phase 1 ✅ | Phase 2 ✅ | Phase 3 ✅ | Phase 4 🔜

---

## The One-Line Pitch

> *"We analyzed 100,000 transactions to answer two questions: what products go together, and who are our customers? Together, they give us a Customer 360 view — enabling segment-specific cross-selling."*

---

## Key Numbers to Know

| Metric | Value |
|--------|-------|
| Raw orders processed | 100,196 |
| Customers profiled | 93,398 |
| Product categories | 72 |
| Multi-category orders | 780 (0.8%) |
| Association rules found | 25 |
| Algorithm agreement | 100% (Apriori = FP-Growth) |
| Top bundle lift | **41.05x** |
| Average lift | **6.84x** |
| Industry benchmark | 1.5–3x |
| Customer segments (K) | **3** |
| Silhouette score | 0.38 (Good) |
| Davies-Bouldin index | 0.97 (Good) |

---

## Phase 2 — Top 5 Association Rules

| # | If customer buys... | They also buy... | Lift | Confidence |
|---|---------------------|-----------------|------|-----------|
| 1 | Children's Clothes | Bags & Accessories | **41.05x** | 100% |
| 2 | General Books | Marketplace items | 26.00x | 40% |
| 3 | Audio Equipment | Watches & Gifts | 19.50x | 100% |
| 4 | Fashion Shoes | Baby products | 8.39x | 100% |
| 5 | Luggage & Accessories | Stationery | 7.88x | 33% |

**What is lift?** A lift of 41 means customers who bought children's clothes are 41× more likely to buy bags than a random customer — far above the 1.5–3x industry benchmark.

---

## Phase 3 — Customer Segments

| Segment | Size | Avg Spend | Recency | Repeat % | Label |
|---------|------|-----------|---------|----------|-------|
| **0** | 38,353 (41%) | $52.89 | 278 days | 2.2% | 💤 Low-value, Churned |
| **1** | 38,143 (41%) | $226.57 | 272 days | 3.7% | 💰 High-value, Inactive |
| **2** | 16,902 (18%) | $102.90 | 70 days | 3.5% | 🔥 Recent & Active |

**Key insight:**
- Segment 0: Budget buyers who haven't returned — need re-engagement
- Segment 1: Best customers by spend — but inactive for 9 months, win-back priority
- Segment 2: Most recent buyers — highest potential for cross-selling NOW

---

## Phase 4 Preview (What's Next)

Join segments with transactions → run Apriori/FP-Growth **per segment** → compare rules:

> *"Do high-value inactive customers (Seg 1) show different product associations than recent active ones (Seg 2)?"*

---

## Files & Locations

| What | Where |
|------|-------|
| Association rules | `phase2/new_implementation/outputs/cross_category/cross_category_rules.csv` |
| Phase 2 charts | `phase2/new_implementation/outputs/cross_category/visualizations/` |
| Customer segments | `data/customer_segments_k3.csv` |
| Cluster metrics | `data/clustering_metrics_k3.json` |
| Segment profiles | `data/segment_profiles_k3.csv` |
| Phase 3 charts | `phase3/visualizations/` |
| Run everything | `python RUN_PROJECT_COMPLETE.py` |
| Validate all | `python VALIDATE_ALL_PHASES.py` |
