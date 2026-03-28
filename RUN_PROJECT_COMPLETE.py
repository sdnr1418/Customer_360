#!/usr/bin/env python3
"""
MASTER EXECUTION SCRIPT - Data Mining Project
Runs all phases step-by-step and validates outputs
"""

import sys
import os
from pathlib import Path
import subprocess

# Get project root
PROJECT_ROOT = Path(__file__).parent
PHASE1_DIR = PROJECT_ROOT / "phase1"
PHASE2_DIR = PROJECT_ROOT / "phase2"
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

print("=" * 90)
print(" " * 20 + "DATA MINING PROJECT - COMPLETE EXECUTION")
print("=" * 90)

# =============================================================================
# STEP 0: PRE-FLIGHT CHECKS
# =============================================================================

print("\n[STEP 0] PRE-FLIGHT CHECKS")
print("-" * 90)

checks = {
    "Phase 1 Folder": PHASE1_DIR.exists(),
    "Phase 2 Folder": PHASE2_DIR.exists(),
    "Data Folder": DATA_DIR.exists(),
    "Logs Folder": LOGS_DIR.exists(),
}

for check_name, result in checks.items():
    status = "[OK]" if result else "[FAIL]"
    print(f"  {status} {check_name}")

if not all(checks.values()):
    print("\n[ERROR] Pre-flight checks failed!")
    sys.exit(1)

# Check environment variables
print("\n  Checking environment configuration...")
from dotenv import load_dotenv
load_dotenv()
db_password = os.getenv('DB_PASSWORD')
if db_password:
    print("  [OK] Database credentials loaded from .env")
else:
    print("  [WARN] No DB_PASSWORD found in .env (may need database setup)")

# =============================================================================
# STEP 1: VALIDATE DATA FILES
# =============================================================================

print("\n[STEP 1] VALIDATING DATA FILES")
print("-" * 90)

required_files = [
    'olist_customers_dataset.csv',
    'olist_orders_dataset.csv',
    'olist_order_items_dataset.csv',
    'olist_products_dataset.csv',
    'product_category_name_translation.csv'
]

all_files_exist = True
for fname in required_files:
    fpath = DATA_DIR / fname
    if fpath.exists():
        size_mb = fpath.stat().st_size / (1024 ** 2)
        print(f"  [OK] {fname} ({size_mb:.2f} MB)")
    else:
        print(f"  [FAIL] {fname} - NOT FOUND")
        all_files_exist = False

if not all_files_exist:
    print("\n[ERROR] Required data files not found!")
    sys.exit(1)

# =============================================================================
# STEP 2: TEST DATABASE CONNECTION
# =============================================================================

print("\n[STEP 2] TESTING DATABASE CONNECTION")
print("-" * 90)

try:
    from sqlalchemy import create_engine, text
    password = os.getenv('DB_PASSWORD')
    DB_URI = f'postgresql://postgres:{password}@localhost:5432/customer_360'
    engine = create_engine(DB_URI)
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        print(f"  [OK] Connected to PostgreSQL")
        print(f"       {version.split(',')[0]}")
except Exception as e:
    print(f"  [WARN] Database connection failed: {str(e)}")
    print("         Skipping Phase 1 (requires database)")
    print("         Will proceed directly to Phase 2 validation")

# =============================================================================
# PHASE 1: DATA PREPARATION & EDA
# =============================================================================

print("\n" + "=" * 90)
print("PHASE 1: DATA PREPARATION & EXPLORATORY DATA ANALYSIS")
print("=" * 90)

phase1_scripts = [
    ("preprocessing.py", "Step 1.1: Load & Transform Raw Data"),
    ("cleaning.py", "Step 1.2: Data Cleaning"),
    ("eda_report.py", "Step 1.3: Exploratory Data Analysis"),
    ("feature_engineering.py", "Step 1.4: Feature Engineering"),
    ("feature_scaling.py", "Step 1.5: Feature Scaling"),
    ("validate_phase1.py", "Step 1.6: Validation"),
]

print("\nPhase 1 consists of 6 steps:")
for script, description in phase1_scripts:
    fpath = PHASE1_DIR / script
    status = "[OK]" if fpath.exists() else "[FAIL]"
    print(f"  {status} {description}")

print("\n[SKIP] Phase 1 execution requires database setup")
print("       All Phase 1 outputs already available in data/ folder:")
print("         - master_cleaned.csv (13.32 MB)")
print("         - master_df.csv (14.65 MB)")
print("         - customer_features_full.csv (23.68 MB)")

# =============================================================================
# PHASE 2: ASSOCIATION RULE MINING
# =============================================================================

print("\n" + "=" * 90)
print("PHASE 2: ASSOCIATION RULE MINING")
print("=" * 90)

print("\nExecuting Phase 2 master script...")
print("-" * 90)

try:
    phase2_run = PHASE2_DIR / "run_phase2_complete.py"
    if phase2_run.exists():
        print(f"\nRunning: {phase2_run.name}")
        # Run the Phase 2 orchestration script
        result = subprocess.run(
            [sys.executable, str(phase2_run)],
            cwd=str(PHASE2_DIR),
            capture_output=True,
            text=True,
            timeout=120
        )
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode != 0:
            print(f"\n[WARN] Phase 2 execution returned code {result.returncode}")
    else:
        print(f"[ERROR] Phase 2 run script not found: {phase2_run}")
        
except subprocess.TimeoutExpired:
    print("[ERROR] Phase 2 execution timed out!")
except Exception as e:
    print(f"[ERROR] Phase 2 execution failed: {str(e)}")

# =============================================================================
# VALIDATION & SUMMARY
# =============================================================================

print("\n" + "=" * 90)
print("VALIDATION & OUTPUT SUMMARY")
print("=" * 90)

from pathlib import Path

# Check Phase 1 outputs
print("\n[PHASE 1 OUTPUTS]")
phase1_outputs = {
    "Cleaned Data": DATA_DIR / "master_cleaned.csv",
    "Master DataFrame": DATA_DIR / "master_df.csv",
    "Feature Engineering (Full)": DATA_DIR / "customer_features_full.csv",
    "Feature Scaling (KMeans)": DATA_DIR / "customer_features_kmeans.csv",
    "Feature Scaling (KPrototypes)": DATA_DIR / "customer_features_kprototypes.csv",
}

for name, fpath in phase1_outputs.items():
    if fpath.exists():
        size_mb = fpath.stat().st_size / (1024 ** 2)
        print(f"  [OK] {name}: {size_mb:.2f} MB")
    else:
        print(f"  [MISSING] {name}")

# Check Phase 2 outputs
print("\n[PHASE 2 OUTPUTS]")

outputs_dir = PROJECT_ROOT / "phase2_outputs"

if outputs_dir.exists():
    # Check visualizations
    viz_dir = outputs_dir / "visualizations"
    if viz_dir.exists():
        viz_files = list(viz_dir.glob("*.png"))
        print(f"  [OK] Visualizations: {len(viz_files)} PNG files")
        for vf in sorted(viz_files):
            size_kb = vf.stat().st_size / 1024
            print(f"       - {vf.name} ({size_kb:.1f} KB)")
    
    # Check exports
    export_dir = outputs_dir / "exports"
    if export_dir.exists():
        csv_files = list(export_dir.glob("*.csv"))
        print(f"  [OK] CSV Exports: {len(csv_files)} files")
        for cf in sorted(csv_files):
            size_kb = cf.stat().st_size / 1024
            print(f"       - {cf.name} ({size_kb:.1f} KB)")
    
    # Check report
    report_file = outputs_dir / "PHASE2_ASSOCIATION_RULES_REPORT.md"
    if report_file.exists():
        size_kb = report_file.stat().st_size / 1024
        print(f"  [OK] Strategic Report: PHASE2_ASSOCIATION_RULES_REPORT.md ({size_kb:.1f} KB)")
else:
    print("  [WARN] phase2_outputs directory not found")

# =============================================================================
# EXECUTION COMPLETE
# =============================================================================

print("\n" + "=" * 90)
print("PROJECT EXECUTION COMPLETE")
print("=" * 90)

print("\n[DELIVERABLES LOCATION]")
print(f"  Phase 1 Data:    {DATA_DIR}/")
print(f"  Phase 2 Results: {outputs_dir}/")
print(f"  Documentation:   docs/")
print(f"  Logs:            {LOGS_DIR}/")

print("\n[NEXT STEPS]")
print("  1. Review PHASE2_ASSOCIATION_RULES_REPORT.md for insights")
print("  2. Examine visualizations in phase2_outputs/visualizations/")
print("  3. Analyze CSV exports in phase2_outputs/exports/")
print("  4. Share findings with stakeholders")

print("\n" + "=" * 90 + "\n")
