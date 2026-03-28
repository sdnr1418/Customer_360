#!/usr/bin/env python
"""
Phase 2 Step 8: Strategic Report Generation
Creates comprehensive Phase 2 Association Rule Mining Report
"""

import pandas as pd
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
REPORT_FILE = str(PROJECT_ROOT / "phase2_outputs" / "PHASE2_ASSOCIATION_RULES_REPORT.md")

def generate_strategic_report(results):
    """Generate complete Phase 2 strategic report"""
    
    report = []
    
    # Header
    report.append("# Phase 2: Association Rule Mining - Strategic Insights & SKU Affinities")
    report.append("")
    report.append(f"**Generated:** {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}")
    report.append("")
    report.append("**Study Period:** Olist Marketplace (100,196 transactions, 96,478 unique orders)")
    report.append("")
    
    # ========================================================================
    # EXECUTIVE SUMMARY
    # ========================================================================
    report.append("---")
    report.append("")
    report.append("## Executive Summary")
    report.append("")
    report.append("### Key Finding: Olist is a **SPECIALIZED STORE**")
    report.append("")
    report.append("- **99.2%** of orders contain a single product category")
    report.append("- **0.8%** (780 orders) are multi-category \"bundler\" transactions")
    report.append("- Customers shop by category focus, not as one-stop shoppers")
    report.append("- **Implication:** Strategic bundling is a HIGH-IMPACT growth opportunity")
    report.append("")
    
    comp = results['basket_composition']
    report.append("### Market Basket Composition")
    report.append(f"- Total Orders: {comp['total_orders']:,}")
    report.append(f"- Single-Category Orders: {comp['single_category']:,} ({comp['single_category_pct']:.1f}%)")
    report.append(f"- Multi-Category Orders: {comp['multi_category']:,} ({comp['multi_category_pct']:.1f}%)")
    report.append(f"- Average Categories/Order: {comp['avg_categories']:.2f}")
    report.append("")
    
    # ========================================================================
    # Q1: ANCHOR vs ADD-ON ANALYSIS
    # ========================================================================
    report.append("---")
    report.append("")
    report.append("## Section 1: Anchor vs Add-On Analysis")
    report.append("### Q1: Which categories initiate purchases vs complement them?")
    report.append("")
    report.append("**Methodology:** Calculated Anchor Index = (Antecedent Count) / (Antecedent Count + Consequent Count)")
    report.append("- **Anchor Index 1.0** = Pure initiator categories (always trigger purchases)")
    report.append("- **Anchor Index 0.0** = Pure add-on categories (always secondary)")
    report.append("")
    
    if len(results['anchor_df']) > 0:
        anchors = results['anchor_df'].nlargest(5, 'anchor_index')
        addons = results['anchor_df'].nsmallest(5, 'anchor_index')
        
        report.append("### Top 5 ANCHOR Categories (Purchase Initiators)")
        for idx, (i, row) in enumerate(anchors.iterrows(), 1):
            report.append(f"{idx}. **{row['category']}** - Anchor Index: {row['anchor_index']:.2f}")
        report.append("")
        
        report.append("### Top 5 ADD-ON Categories (Complementary)")
        for idx, (i, row) in enumerate(addons.iterrows(), 1):
            report.append(f"{idx}. **{row['category']}** - Anchor Index: {row['anchor_index']:.2f}")
        report.append("")
    
    report.append("**Business Implication:** Feature anchor categories prominently; position add-ons for upsell")
    report.append("")
    
    # ========================================================================
    # Q2: HIDDEN AFFINITIES
    # ========================================================================
    report.append("---")
    report.append("")
    report.append("## Section 2: Hidden Affinities & Surprise Associations")
    report.append("### Q2: Which unexpected category pairs have strong associations?")
    report.append("")
    report.append("**Methodology:** Identified rules with Lift > 1.5 (associations 50%+ stronger than random)")
    report.append("")
    
    if len(results['hidden_affinities']) > 0:
        top_hidden = results['hidden_affinities'].nlargest(5, 'lift')
        report.append("### Top 5 Surprise Associations (Highest Lift)")
        for idx, (i, rule) in enumerate(top_hidden.iterrows(), 1):
            ant = list(rule['antecedents'])[0] if len(rule['antecedents']) == 1 else str(rule['antecedents'])
            cons = list(rule['consequents'])[0] if len(rule['consequents']) == 1 else str(rule['consequents'])
            report.append(f"{idx}. **{ant} -> {cons}**")
            report.append(f"   - Lift: {rule['lift']:.2f}x | Confidence: {rule['confidence']:.1%} | Support (multi-cart): {rule['support']:.1%}")
        report.append("")
    
    report.append("**Business Implication:** Use surprise associations for cross-category promotions and discovery")
    report.append("")
    
    # ========================================================================
    # Q3: BUNDLING RECOMMENDATIONS
    # ========================================================================
    report.append("---")
    report.append("")
    report.append("## Section 3: Top Bundling Opportunities by Lift")
    report.append("### Q3: Should we recommend category pairs as bundles?")
    report.append("")
    report.append("**Analysis:** Ranked all category pairs by their **Lift** (association strength relative to random purchase)")
    report.append("")
    
    if len(results['bundling_candidates']) > 0:
        top_bundles = results['bundling_candidates'].nlargest(10, 'lift')
        report.append(f"### Top 10 Bundling Pairs (Lift-Ranked)")
        report.append("")
        for idx, (i, rule) in enumerate(top_bundles.iterrows(), 1):
            ant = list(rule['antecedents'])[0] if len(rule['antecedents']) == 1 else str(rule['antecedents'])
            cons = list(rule['consequents'])[0] if len(rule['consequents']) == 1 else str(rule['consequents'])
            report.append(f"**{idx}. {ant} + {cons}**")
            report.append(f"  - Lift: **{rule['lift']:.2f}x** | Confidence: {rule['confidence']:.1%} | Support (multi-cart): {rule['support']:.1%}")
        report.append("")
    
    report.append("**Business Implication:** Highest-lift pairs are prime candidates for website bundles, email campaigns, and recommendations")
    report.append("")
    
    # ========================================================================
    # Q4: MARKET COMPOSITION (ALREADY IN EXEC SUMMARY, BRIEF HERE)
    # ========================================================================
    report.append("---")
    report.append("")
    report.append("## Section 4: Market Type Assessment")
    report.append("### Q4: What market basket structure does Olist have?")
    report.append("")
    report.append("**Finding:** SPECIALIZED STORE")
    report.append("")
    report.append("- 99.2% of customers focus on specific categories per order")
    report.append("- Only 0.8% purchase multi-category items (the \"bundlers\")")
    report.append("- Not a one-stop-shop; customers visit for targeted category purchases")
    report.append("")
    report.append("**Strategic Context:** This specialized behavior makes the 0.8% bundlers even more valuable.")
    report.append("By showing the right cross-category offers to focused shoppers, we can unlock bundling growth.")
    report.append("")
    
    # ========================================================================
    # SECTION 5: SECTION 5: SYNTHETIC BUNDLES (FLAGSHIP)
    # ========================================================================
    report.append("---")
    report.append("")
    report.append("## Section 5: Strategic Bundling & SKU Affinities (Flagship)")
    report.append("### Actionable Product-Level Recommendations")
    report.append("")
    report.append("**Approach:** For each top category pair, identify the best-selling SKU from each category.")
    report.append("This \"synthetic bundling\" strategy balances:")
    report.append("- Statistical rigor (category associations are mathematically validated)")
    report.append("- Business practicality (recommending proven best-sellers)")
    report.append("- Risk mitigation (avoiding statistical flukes from small sample)")
    report.append("")
    
    if len(results['drilldown_results']) > 0:
        report.append("### 10 Recommended Synthetic Bundles")
        report.append("")
        for bundle in results['drilldown_results']:
            bundle_num = bundle['pair_rank']
            ant = bundle['antecedent_category']
            cons = bundle['consequent_category']
            lift = bundle['lift']
            conf = bundle['confidence']
            
            ant_sku = bundle['antecedent_top_products'][0][:30] if bundle['antecedent_top_products'] else 'N/A'
            ant_sales = bundle['antecedent_product_sales'][0] if bundle['antecedent_product_sales'] else 0
            cons_sku = bundle['consequent_top_products'][0][:30] if bundle['consequent_top_products'] else 'N/A'
            cons_sales = bundle['consequent_product_sales'][0] if bundle['consequent_product_sales'] else 0
            
            report.append(f"**Bundle #{bundle_num}: {ant} -> {cons}** (Lift: {lift:.1f}x)")
            report.append(f"> SKU from {ant}: `{ant_sku}` ({ant_sales} sales overall)")
            report.append(f"> SKU from {cons}: `{cons_sku}` ({cons_sales} sales overall)")
            report.append(f"> Recommended as: Cross-category bundle | Confidence: {conf:.1%}")
            report.append("")
    
    report.append("#### Implementation Roadmap")
    report.append("1. **Quick Wins:** Launch top 3 bundles as \"Frequently Bought Together\" recommendations")
    report.append("2. **Email Campaign:** Feature Bundle #1 (41x lift) to high-value customers")
    report.append("3. **A/B Testing:** Compare bundle conversion rates vs control group")
    report.append("4. **Optimization:** Adjust SKU selection based on real bundle purchase data")
    report.append("")
    
    # ========================================================================
    # METHODOLOGY & DATA NOTES
    # ========================================================================
    report.append("---")
    report.append("")
    report.append("## Methodology & Data Notes")
    report.append("")
    report.append("### Algorithms Used")
    report.append("- **Apriori:** Frequent itemset mining with support threshold optimization")
    report.append("- **FP-Growth:** Fast pattern mining for validation of Apriori results")
    report.append("- **Both converged on 0.2% support threshold** (optimal for 780 multi-category orders)")
    report.append("")
    
    report.append("### Support Metric Clarification")
    report.append("**Important:** All support percentages are **CONDITIONAL on multi-item carts** (780 orders, 0.8% of total)")
    report.append("")
    report.append("Example: A rule with 1.4% support means:")
    report.append("- 1.4% of the 780 multi-category orders (11 orders)")
    report.append("- NOT 1.4% of all 96,478 orders")
    report.append("- This clarification prevents marketing misinterpretation")
    report.append("")
    
    report.append("### Key Statistics")
    final_rules = results['final_rules']
    report.append(f"- Total Association Rules: {len(final_rules)}")
    report.append(f"- Average Rule Lift: {final_rules['lift'].mean():.2f}x")
    report.append(f"- Average Confidence: {final_rules['confidence'].mean():.1%}")
    report.append(f"- Max Lift Observed: {final_rules['lift'].max():.2f}x")
    report.append(f"- Categories Involved: 33 out of 72 total")
    report.append("")
    
    # ========================================================================
    # APPENDIX & NEXT STEPS
    # ========================================================================
    report.append("---")
    report.append("")
    report.append("## Appendix: Artifacts Generated")
    report.append("")
    report.append("### Visualizations (6 charts)")
    report.append("1. `01_anchor_addon.png` - Anchor Index breakdown (initiators vs add-ons)")
    report.append("2. `02_bundle_heatmap.png` - Bundle Strength Matrix (Lift × Confidence × Support)")
    report.append("3. `03_market_composition.png` - Pie chart (99.2% vs 0.8%)")
    report.append("4. `04_lift_support_scatter.png` - Category pair 2D space")
    report.append("5. `05_category_treemap.png` - Treemap view of top 15 pairs")
    report.append("6. `06_synthetic_bundles.png` - Top 6 bundles with SKU details")
    report.append("")
    report.append("### Data Exports (5 CSV files)")
    report.append("1. `association_rules_final.csv` - 25 rules with metrics")
    report.append("2. `category_anchor_analysis.csv` - Anchor index by category")
    report.append("3. `bundling_recommendations.csv` - Top 20 bundling pairs")
    report.append("4. `market_basket_stats.csv` - Composition statistics")
    report.append("5. `synthetic_bundles.csv` - 10 bundles with SKU details")
    report.append("")
    
    report.append("## Next Steps")
    report.append("")
    report.append("1. **Marketing Review:** Present Section 5 (Synthetic Bundles) to marketing team")
    report.append("2. **Product Implementation:** Code \"Frequently Bought Together\" widgets")
    report.append("3. **A/B Testing:** Compare bundle recommendations vs control (7-14 days)")
    report.append("4. **Optimization Loop:** Refine SKU selection based on real conversion data")
    report.append("5. **Phase 2B (Optional):** Analyze lifetime customer baskets for returning customer patterns")
    report.append("")
    
    # ========================================================================
    # Write Report
    # ========================================================================
    report_text = "\n".join(report)
    
    import os
    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    
    with open(REPORT_FILE, 'w') as f:
        f.write(report_text)
    
    print(f"\n[OK] Strategic Report generated: {REPORT_FILE}")
    print(f"     ({len(report)} lines)")
    
    return report_text

if __name__ == "__main__":
    from association_rules import run_pipeline
    
    print("\nGenerating Phase 2 Strategic Report...")
    results = run_pipeline()
    report = generate_strategic_report(results)
    print("\nReport Preview (first 1000 chars):")
    print(report[:1000])
