#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VALIDATE_ALL_PHASES.py
============================================================================
Pre-Phase 4 validation: checks all outputs from Phases 1, 2, and 3.
Does NOT re-run anything -- purely reads and validates existing files.

Run with:
    python VALIDATE_ALL_PHASES.py
============================================================================
"""

import json
import sys
import os
from pathlib import Path

import pandas as pd
import numpy as np

ROOT     = Path(__file__).parent
DATA     = ROOT / "data"

# Phase 2 actual output locations
P2_CROSS = ROOT / "phase2" / "new_implementation" / "outputs" / "cross_category"
P2_INTRA = ROOT / "phase2" / "new_implementation" / "outputs" / "intra_category"

# Phase 3 output locations
PHASE3_VIZ = ROOT / "phase3" / "visualizations"

PASS  = "[  OK  ]"
WARN  = "[ WARN ]"
FAIL  = "[ FAIL ]"

errors   = []
warnings = []


def section(title):
    print("\n" + "=" * 72)
    print("  " + title)
    print("=" * 72)


def check(label, ok, detail="", warn_only=False):
    if ok:
        print("  {} {}  {}".format(PASS, label, detail))
    elif warn_only:
        print("  {} {}  {}".format(WARN, label, detail))
        warnings.append(label)
    else:
        print("  {} {}  {}".format(FAIL, label, detail))
        errors.append(label)


# ============================================================================
# PHASE 1 VALIDATION
# ============================================================================

section("PHASE 1 -- Data Preparation & Feature Engineering")

p1_files = {
    "master_cleaned.csv":               5,
    "master_df.csv":                    5,
    "customer_features_full.csv":       1,
    "customer_features_kprototypes.csv": 1,
}

for fname, min_mb in p1_files.items():
    fpath = DATA / fname
    if fpath.exists():
        size_mb = fpath.stat().st_size / (1024 ** 2)
        check(fname, size_mb >= min_mb, "({:.2f} MB)".format(size_mb),
              warn_only=size_mb < min_mb)
    else:
        check(fname, False, "(NOT FOUND)")

# Row/column checks on master_cleaned
print()
try:
    mc = pd.read_csv(DATA / "master_cleaned.csv")
    check("master_cleaned: row count >= 90,000",
          len(mc) >= 90_000, "({:,} rows)".format(len(mc)))
    required_cols = {"customer_unique_id", "order_id", "category", "price"}
    missing = required_cols - set(mc.columns)
    check("master_cleaned: key columns present",
          len(missing) == 0,
          "(missing: {})".format(missing) if missing else "")
except Exception as e:
    check("master_cleaned: load & check", False, str(e))

try:
    cf = pd.read_csv(DATA / "customer_features_full.csv")
    check("customer_features_full: row count >= 80,000",
          len(cf) >= 80_000, "({:,} rows)".format(len(cf)))
    for col in ["customer_unique_id", "recency", "frequency", "monetary"]:
        check("  column '{}' exists".format(col), col in cf.columns)
    rfm_nulls = cf[["recency", "frequency", "monetary"]].isnull().sum().sum()
    check("customer_features_full: no NaNs in RFM columns",
          rfm_nulls == 0, "({} nulls)".format(rfm_nulls))
except Exception as e:
    check("customer_features_full: load & check", False, str(e))


# ============================================================================
# PHASE 2 VALIDATION
# ============================================================================

section("PHASE 2 -- Association Rule Mining")

check("phase2/new_implementation/outputs/cross_category/ exists", P2_CROSS.exists())
check("phase2/new_implementation/outputs/intra_category/ exists", P2_INTRA.exists())

# Cross-category rules
cross_rules = P2_CROSS / "cross_category_rules.csv"
if cross_rules.exists():
    df = pd.read_csv(cross_rules)
    check("cross_category_rules.csv loaded", True, "({} rows)".format(len(df)))
    check("Rules: at least 5 cross-category rules", len(df) >= 5,
          "({} rules)".format(len(df)))
    for col in ["support", "confidence", "lift"]:
        check("  column '{}' present".format(col), col in df.columns)
    if "lift" in df.columns:
        check("Rules: all lift > 1",
              (df["lift"] > 1).all(),
              "(min lift = {:.2f})".format(df["lift"].min()))
else:
    check("cross_category_rules.csv exists", False, "(NOT FOUND)")

# Intra-category rules
intra_rules = P2_INTRA / "intra_category_rules.csv"
if intra_rules.exists():
    df2 = pd.read_csv(intra_rules)
    check("intra_category_rules.csv loaded", True, "({} rows)".format(len(df2)))
else:
    check("intra_category_rules.csv exists", False, "(NOT FOUND)", warn_only=True)

# Visualizations
p2_pngs = list(P2_CROSS.glob("visualizations/*.png")) if (P2_CROSS / "visualizations").exists() else []
check("Phase 2 visualizations: >= 4 PNG files",
      len(p2_pngs) >= 4, "({} files)".format(len(p2_pngs)))
for f in sorted(p2_pngs):
    size_kb = f.stat().st_size / 1024
    print("       - {} ({:.0f} KB)".format(f.name, size_kb))

# Exports
p2_exports = list(P2_CROSS.glob("exports/*.csv")) if (P2_CROSS / "exports").exists() else []
check("Phase 2 exports: >= 1 CSV", len(p2_exports) >= 1,
      "({} files)".format(len(p2_exports)))

# Summary files
for txt in ["cross_category_summary.txt", "cross_category_arm.log"]:
    fpath = P2_CROSS / txt
    check("  {} exists".format(txt), fpath.exists(),
          "({:.1f} KB)".format(fpath.stat().st_size / 1024) if fpath.exists() else "")


# ============================================================================
# PHASE 3 VALIDATION
# ============================================================================

section("PHASE 3 -- Customer Segmentation (K-Prototypes)")

seg_csv = DATA / "customer_segments_k3.csv"
if seg_csv.exists():
    segs = pd.read_csv(seg_csv)
    check("customer_segments_k3.csv exists",
          True, "({:,} rows)".format(len(segs)))
    check("Segment assignments: >= 80,000 rows",
          len(segs) >= 80_000, "({:,})".format(len(segs)))
    check("'customer_unique_id' column present",
          "customer_unique_id" in segs.columns)
    check("'segment_k3' column present",
          "segment_k3" in segs.columns)
    check("No NaN segment values",
          segs["segment_k3"].isnull().sum() == 0,
          "({} nulls)".format(segs["segment_k3"].isnull().sum()))
    n_clusters = segs["segment_k3"].nunique()
    check("Exactly 3 clusters produced",
          n_clusters == 3, "({} unique labels)".format(n_clusters))
    sizes = segs["segment_k3"].value_counts(normalize=True)
    min_pct = sizes.min() * 100
    check("All clusters >= 5% of customers (not degenerate)",
          min_pct >= 5, "(smallest = {:.1f}%)".format(min_pct))
    print()
    print("  Cluster distribution:")
    for seg_id, cnt in segs["segment_k3"].value_counts().sort_index().items():
        pct = cnt / len(segs) * 100
        bar = "[" + "=" * int(pct / 5) + "]"
        print("    Segment {}: {:7,} customers ({:.1f}%) {}".format(
            seg_id, cnt, pct, bar))
else:
    check("customer_segments_k3.csv exists", False, "(NOT FOUND)")

# Clustering metrics JSON
print()
metrics_json = DATA / "clustering_metrics_k3.json"
if metrics_json.exists():
    with open(metrics_json) as f:
        m = json.load(f)
    metrics = m.get("metrics", {})
    sil = metrics.get("silhouette")
    db  = metrics.get("davies_bouldin")
    ch  = metrics.get("calinski_harabasz")

    check("clustering_metrics_k3.json exists", True)
    if sil is not None:
        check("Silhouette score > 0.1 (fair+)",
              sil > 0.1, "({:.4f})".format(sil), warn_only=sil <= 0.1)
    if db is not None:
        check("Davies-Bouldin index < 2.0",
              db < 2.0, "({:.4f})".format(db), warn_only=db >= 2.0)
    if ch is not None:
        check("Calinski-Harabasz index computed",
              ch is not None, "({:.2f})".format(ch))
else:
    check("clustering_metrics_k3.json exists", False, "(NOT FOUND)")

# Segment profiles CSV
profiles_csv = DATA / "segment_profiles_k3.csv"
if profiles_csv.exists():
    prof = pd.read_csv(profiles_csv)
    check("segment_profiles_k3.csv exists",
          True, "({} segments)".format(len(prof)))
    check("Profiles: 3 rows (one per segment)", len(prof) == 3)
    for col in ["segment", "size", "avg_spending", "top_category"]:
        check("  column '{}' present".format(col), col in prof.columns)
else:
    check("segment_profiles_k3.csv exists", False, "(NOT FOUND)")

# Phase 3 visualizations
print()
p3_pngs = list(PHASE3_VIZ.glob("*.png")) if PHASE3_VIZ.exists() else []
check("phase3/visualizations/ exists", PHASE3_VIZ.exists())
check("Phase 3 visualizations: >= 4 PNGs",
      len(p3_pngs) >= 4, "({} files)".format(len(p3_pngs)))
expected_charts = [
    "segment_distribution_k3.png",
    "segment_profiles_k3.png",
    "evaluation_metrics_k3.png",
    "spending_distribution_k3.png",
    "consensus_k_selection.png",
    "evaluation_metrics_comparison.png",
]
for chart in expected_charts:
    fpath = PHASE3_VIZ / chart
    size_kb = fpath.stat().st_size / 1024 if fpath.exists() else 0
    check("  {}".format(chart), fpath.exists(),
          "({:.0f} KB)".format(size_kb) if fpath.exists() else "")


# ============================================================================
# CROSS-PHASE CONSISTENCY
# ============================================================================

section("CROSS-PHASE CONSISTENCY CHECKS")

try:
    cf   = pd.read_csv(DATA / "customer_features_full.csv")
    segs = pd.read_csv(DATA / "customer_segments_k3.csv")
    cf_ids  = set(cf["customer_unique_id"].astype(str))
    seg_ids = set(segs["customer_unique_id"].astype(str))
    overlap  = len(cf_ids & seg_ids)
    coverage = overlap / len(cf_ids) * 100 if cf_ids else 0
    check("Segment IDs match feature IDs (>= 95% overlap)",
          coverage >= 95,
          "({:.1f}% of {:,} customers)".format(coverage, len(cf_ids)))
except Exception as e:
    check("Cross-phase ID consistency", False, str(e))

try:
    rules = pd.read_csv(P2_CROSS / "cross_category_rules.csv")
    segs  = pd.read_csv(DATA / "customer_segments_k3.csv")
    check("Phase 2 rules + Phase 3 segments ready for Phase 4 integration",
          len(rules) > 0 and len(segs) > 0,
          "({} rules, {:,} segmented customers)".format(len(rules), len(segs)))
except Exception as e:
    check("Phase 2 + Phase 3 outputs available for integration", False, str(e))


# ============================================================================
# SUMMARY
# ============================================================================

section("VALIDATION SUMMARY")

print("\n  Errors   : {}".format(len(errors)))
print("  Warnings : {}".format(len(warnings)))

if errors:
    print("\n  {} ISSUES FOUND -- fix before Phase 4:".format(FAIL))
    for e in errors:
        print("       - " + e)
elif warnings:
    print("\n  {} Minor warnings (non-blocking):".format(WARN))
    for w in warnings:
        print("       - " + w)
    print("\n  [READY] All critical checks passed -- safe to proceed to Phase 4.")
else:
    print("\n  {} ALL CHECKS PASSED -- ready to proceed to Phase 4!".format(PASS))
    print("""
  Phase 4 goal: Segment-specific association rule mining
    - Filter master_cleaned.csv by segment labels (customer_segments_k3.csv)
    - Re-run Apriori/FP-Growth per segment (Segment 0, 1, 2)
    - Compare rules across segments to answer:
      "How do product associations differ across customer segments?"
""")

print("=" * 72 + "\n")
sys.exit(1 if errors else 0)
