#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RUN_PROJECT_COMPLETE.py
============================================================================
MASTER EXECUTION SCRIPT -- Customer 360 Data Mining Project
Validates environment, documents phase outputs, and prints a full summary.

Phases:
  Phase 1 -- Data Preprocessing & EDA         (outputs in data/)
  Phase 2 -- Association Rule Mining           (outputs in phase2/new_implementation/outputs/)
  Phase 3 -- Customer Segmentation             (outputs in data/ + phase3/visualizations/)
  Phase 4 -- Integration (coming next)

Run with:
    python RUN_PROJECT_COMPLETE.py
============================================================================
"""

import sys
import os
import subprocess
from pathlib import Path

# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).parent
PHASE1_DIR   = PROJECT_ROOT / "phase1"
PHASE2_DIR   = PROJECT_ROOT / "phase2"
PHASE3_DIR   = PROJECT_ROOT / "phase3"
DATA_DIR     = PROJECT_ROOT / "data"
LOGS_DIR     = PROJECT_ROOT / "logs"

P2_CROSS = PHASE2_DIR / "new_implementation" / "outputs" / "cross_category"
P2_INTRA = PHASE2_DIR / "new_implementation" / "outputs" / "intra_category"
P3_VIZ   = PHASE3_DIR / "visualizations"

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def section(title):
    print("\n" + "=" * 90)
    print("  " + title)
    print("=" * 90)

def ok(msg, detail=""):
    print("  [  OK  ] {}  {}".format(msg, detail))

def warn(msg, detail=""):
    print("  [ WARN ] {}  {}".format(msg, detail))

def fail(msg, detail=""):
    print("  [ FAIL ] {}  {}".format(msg, detail))

def check_file(label, path, min_mb=None):
    if path.exists():
        size_mb = path.stat().st_size / (1024 ** 2)
        detail  = "({:.2f} MB)".format(size_mb)
        if min_mb and size_mb < min_mb:
            warn(label, detail + " -- smaller than expected")
        else:
            ok(label, detail)
        return True
    else:
        fail(label, "(NOT FOUND)")
        return False

# ---------------------------------------------------------------------------
# BANNER
# ---------------------------------------------------------------------------

print("=" * 90)
print(" " * 15 + "CUSTOMER 360 -- DATA MINING PROJECT  |  COMPLETE EXECUTION")
print("=" * 90)

# ===========================================================================
# STEP 0: PRE-FLIGHT CHECKS
# ===========================================================================

section("STEP 0: PRE-FLIGHT CHECKS")

required_dirs = {
    "Phase 1 Folder":  PHASE1_DIR,
    "Phase 2 Folder":  PHASE2_DIR,
    "Phase 3 Folder":  PHASE3_DIR,
    "Data Folder":     DATA_DIR,
}

all_dirs_ok = True
for label, path in required_dirs.items():
    if path.exists():
        ok(label)
    else:
        fail(label)
        all_dirs_ok = False

if not LOGS_DIR.exists():
    warn("Logs Folder", "(not found -- non-critical)")

if not all_dirs_ok:
    print("\n[ERROR] Critical folders missing. Aborting.")
    sys.exit(1)

# Check .env / DB credentials
print()
try:
    from dotenv import load_dotenv
    load_dotenv()
    db_password = os.getenv("DB_PASSWORD")
    if db_password:
        ok("Database credentials loaded from .env")
    else:
        warn("No DB_PASSWORD in .env", "(CSV fallback will be used where needed)")
except ImportError:
    warn("python-dotenv not installed", "(CSV fallback will be used where needed)")

# ===========================================================================
# STEP 1: TEST DATABASE CONNECTION
# ===========================================================================

section("STEP 1: DATABASE CONNECTION CHECK")

try:
    from sqlalchemy import create_engine, text
    password = os.getenv("DB_PASSWORD", "postgres")
    DB_URI = "postgresql://postgres:{}@localhost:5432/customer_360".format(password)
    engine = create_engine(DB_URI)
    with engine.connect() as conn:
        result  = conn.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        ok("Connected to PostgreSQL", "({})".format(version.split(",")[0]))
except Exception as e:
    warn("Database connection failed", str(e))
    print("       CSV fallback will be used in phase scripts.")

# ===========================================================================
# STEP 2: VALIDATE DATA FILES (Phase 1 outputs)
# ===========================================================================

section("STEP 2: PHASE 1 -- DATA PREPARATION & EDA OUTPUTS")

print("  Core raw files:")
raw_files = [
    "olist_customers_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_products_dataset.csv",
    "product_category_name_translation.csv",
]
for fname in raw_files:
    check_file("  " + fname, DATA_DIR / fname)

print("\n  Phase 1 processed outputs:")
p1_outputs = {
    "master_cleaned.csv":               5,
    "master_df.csv":                    5,
    "customer_features_full.csv":       10,
    "customer_features_kprototypes.csv": 5,
}
for fname, min_mb in p1_outputs.items():
    check_file(fname, DATA_DIR / fname, min_mb=min_mb)

print("\n  [SKIP] Phase 1 scripts not re-run (outputs already present above)")

# ===========================================================================
# STEP 3: PHASE 2 -- ASSOCIATION RULE MINING
# ===========================================================================

section("STEP 3: PHASE 2 -- ASSOCIATION RULE MINING OUTPUTS")

print("  Output directories:")
for label, path in [
    ("cross_category outputs", P2_CROSS),
    ("intra_category outputs", P2_INTRA),
]:
    if path.exists():
        ok(label)
    else:
        fail(label)

print("\n  Rules files:")
for fname in ["cross_category_rules.csv", "intra_category_rules.csv"]:
    base_dir = P2_CROSS if "cross" in fname else P2_INTRA
    fpath = base_dir / fname
    if fpath.exists():
        import pandas as pd
        try:
            df = pd.read_csv(fpath)
            ok(fname, "({} rules)".format(len(df)))
        except Exception as e:
            warn(fname, str(e))
    else:
        fail(fname, "(NOT FOUND)")

print("\n  Visualizations:")
if P2_CROSS.exists():
    viz_dir = P2_CROSS / "visualizations"
    pngs    = sorted(viz_dir.glob("*.png")) if viz_dir.exists() else []
    ok("Phase 2 charts", "({} PNG files)".format(len(pngs)))
    for f in pngs:
        print("       - {} ({:.0f} KB)".format(f.name, f.stat().st_size / 1024))

print("\n  Exports:")
if P2_CROSS.exists():
    exp_dir = P2_CROSS / "exports"
    csvs    = sorted(exp_dir.glob("*.csv")) if exp_dir.exists() else []
    ok("Phase 2 CSV exports", "({} files)".format(len(csvs)))
    for f in csvs:
        print("       - {} ({:.0f} KB)".format(f.name, f.stat().st_size / 1024))

# ===========================================================================
# STEP 4: PHASE 3 -- CUSTOMER SEGMENTATION
# ===========================================================================

section("STEP 4: PHASE 3 -- CUSTOMER SEGMENTATION OUTPUTS")

print("  Segment data files:")
p3_data = {
    "customer_segments_k3.csv":   "Segment assignments for all customers",
    "clustering_metrics_k3.json": "Silhouette, DB, CH metrics",
    "segment_profiles_k3.csv":    "Per-segment profile summary",
}
for fname, desc in p3_data.items():
    fpath = DATA_DIR / fname
    if fpath.exists():
        size_mb = fpath.stat().st_size / (1024 ** 2)
        ok("{} -- {}".format(fname, desc), "({:.2f} MB)".format(size_mb))
    else:
        fail(fname, "(NOT FOUND)")

# Print clustering metrics
import json
metrics_path = DATA_DIR / "clustering_metrics_k3.json"
if metrics_path.exists():
    with open(metrics_path) as f:
        m = json.load(f)
    metrics = m.get("metrics", {})
    print("\n  Clustering quality metrics (K=3):")
    sil = metrics.get("silhouette")
    db  = metrics.get("davies_bouldin")
    ch  = metrics.get("calinski_harabasz")
    if sil is not None:
        quality = "EXCELLENT" if sil > 0.5 else "GOOD" if sil > 0.3 else "FAIR" if sil > 0.1 else "POOR"
        print("       Silhouette Score:        {:.4f}  [{}]".format(sil, quality))
    if db is not None:
        quality = "EXCELLENT" if db < 0.7 else "GOOD" if db < 1.0 else "FAIR" if db < 1.5 else "POOR"
        print("       Davies-Bouldin Index:    {:.4f}  [{}]".format(db, quality))
    if ch is not None:
        print("       Calinski-Harabasz Index: {:.2f}".format(ch))

    # Cluster sizes
    cluster_sizes = m.get("cluster_sizes", {})
    total = m.get("total_customers", 1)
    if cluster_sizes:
        print("\n  Cluster distribution:")
        for seg, cnt in sorted(cluster_sizes.items(), key=lambda x: int(x[0])):
            pct = cnt / total * 100
            bar = "[" + "=" * int(pct / 5) + "]"
            print("    Segment {}: {:7,} customers ({:.1f}%) {}".format(seg, cnt, pct, bar))

print("\n  Visualizations:")
if P3_VIZ.exists():
    pngs = sorted(P3_VIZ.glob("*.png"))
    ok("Phase 3 charts", "({} PNG files)".format(len(pngs)))
    for f in pngs:
        print("       - {} ({:.0f} KB)".format(f.name, f.stat().st_size / 1024))
else:
    warn("phase3/visualizations/ not found")

# ===========================================================================
# FINAL SUMMARY
# ===========================================================================

section("PROJECT SUMMARY")

print("""
  STATUS
  ------
  Phase 1 -- Data Preprocessing & EDA       [COMPLETE]
  Phase 2 -- Association Rule Mining        [COMPLETE]
  Phase 3 -- Customer Segmentation          [COMPLETE]
  Phase 4 -- Integration & Insights         [PENDING]

  DELIVERABLE LOCATIONS
  ---------------------
  Phase 1 data:          data/
  Phase 2 rules:         phase2/new_implementation/outputs/cross_category/
  Phase 2 charts:        phase2/new_implementation/outputs/cross_category/visualizations/
  Phase 3 segments:      data/customer_segments_k3.csv
  Phase 3 metrics:       data/clustering_metrics_k3.json
  Phase 3 charts:        phase3/visualizations/
  Documentation:         docs/

  NEXT STEPS -- Phase 4
  ----------------------
  1. Join customer_segments_k3.csv with master_cleaned.csv
  2. Filter transactions per segment (Segment 0, 1, 2)
  3. Run Apriori / FP-Growth independently per segment
  4. Compare rules across segments
  5. Answer: "How do product associations differ across customer segments?"

  TIP: Run VALIDATE_ALL_PHASES.py for a detailed pre-Phase-4 integrity check.
""")

print("=" * 90 + "\n")
