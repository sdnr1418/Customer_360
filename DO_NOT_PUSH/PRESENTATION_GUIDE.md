# Customer 360 — Presentation Guide

---

## Story Arc (Use This Structure)

1. **Problem** — "E-commerce businesses collect data but struggle to turn it into action"
2. **Approach** — "We answer two questions: what products go together + who are our customers"
3. **Phase 2 Finding** — "25 rules. Top: children's clothes → bags at 41x lift. Industry does 1.5–3x."
4. **Phase 3 Finding** — "93,398 customers in 3 segments. Segment 2 is recent & active — prime target now"
5. **Integration (Phase 4)** — "Combining both: segment-specific product recommendations"
6. **Action** — "A/B test Bundle #1 on Segment 2 first — highest ROI, lowest risk"

---

## Timing (15 min)

| Section | Time |
|---------|------|
| Opening + problem statement | 2 min |
| Phase 1 (data prep, briefly) | 1 min |
| Phase 2 (association rules, charts) | 4 min |
| Phase 3 (segments, profiles) | 4 min |
| Phase 4 preview + recommendation | 2 min |
| Q&A buffer | 2 min |

---

## Common Questions & Answers

**"How do you know the rules aren't just coincidence?"**
> "Two independent algorithms — Apriori and FP-Growth — produced identical 25 rules. They're mathematically different approaches. 100% convergence rules out coincidence."

**"What does lift actually mean?"**
> "It compares observed vs expected. Lift of 41 means: if we randomly picked customers, 1 would buy bags. When they've already bought children's clothes, 41 do. That's the signal."

**"Only 0.8% buy multiple categories — is that worth it?"**
> "Exactly — that's the insight. That 0.8% tells us where customers *want* to go. It's a low-risk signal to test, and if even 10% of the remaining 99.2% convert on a recommendation, the revenue impact is large."

**"How confident are you this will increase sales?"**
> "Confident in the pattern — not in causation yet. That's what A/B testing proves. We recommend: show Bundle #1 to 10% of Segment 2 customers for 4 weeks, measure vs control."

**"Why K=3 clusters?"**
> "We ran K=2 through 6 and measured Silhouette, Davies-Bouldin, Calinski-Harabasz, and the Elbow method. All four metrics pointed to K=3 as the optimal balance."

**"What's the business value of segmentation?"**
> "Different segments need different strategies. Segment 1 (high-value, inactive) needs a win-back campaign. Segment 2 (recent, active) is ready for cross-sell recommendations now. One-size-fits-all marketing wastes budget."

**"What's Phase 4?"**
> "We re-run the association rule mining independently per segment. This answers the core question: do high-value customers show different product associations than budget buyers?"

---

## Day-Of Checklist

**Before:**
- [ ] Know the 41.05x lift number cold — it's your headline
- [ ] Know the 3 segment labels: Churned / High-value Inactive / Recent Active
- [ ] Have `QUICK_REFERENCE.md` open on a hidden tab
- [ ] Have `RUN_PROJECT_COMPLETE.py` ready if asked for a live demo
- [ ] Test that phase2 & phase3 visualization folders open correctly

**During:**
- [ ] Lead with the big number (41x)
- [ ] Use the segment table from `QUICK_REFERENCE.md` when presenting Phase 3
- [ ] If asked anything outside scope: *"That's exactly what Phase 4 answers"*

**If tech fails:**
- Speak to the numbers in `QUICK_REFERENCE.md` — you don't need the slides
- Run `python RUN_PROJECT_COMPLETE.py` as a live proof of reproducibility

---

## Limitations to Acknowledge (Shows Maturity)

- Association rules are correlational — A/B testing needed for causal proof
- 99.2% of orders are single-category, so the training set for rules is small (780 orders)
- Segments were trained on 15% sample (stratified) for speed — quality verified via metrics
- Phase 4 (segment-specific rules) not yet complete — that's the next step
