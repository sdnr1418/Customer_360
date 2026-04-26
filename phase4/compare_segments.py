import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os

# Set up paths
REPO_ROOT = Path(__file__).resolve().parents[1]
PHASE4_DIR = REPO_ROOT / 'phase4'
OUTPUTS_DIR = PHASE4_DIR / 'outputs'
VIZ_DIR = OUTPUTS_DIR / 'visualizations'
VIZ_DIR.mkdir(parents=True, exist_ok=True)

def load_rules():
    rules_dict = {}
    for i in range(3):
        path = OUTPUTS_DIR / f'segment_{i}_rules.csv'
        if path.exists():
            df = pd.read_csv(path)
            df['rule'] = df['antecedents'] + ' -> ' + df['consequents']
            rules_dict[i] = df
    return rules_dict

def compare_top_rules(rules_dict):
    # Combine all rules
    all_rules = pd.DataFrame()
    
    segment_names = {
        0: "0: Low-Value",
        1: "1: High-Value",
        2: "2: Recent-Active"
    }
    
    for seg, df in rules_dict.items():
        temp = df[['rule', 'support', 'confidence', 'lift']].copy()
        temp['segment'] = segment_names.get(seg, f'Segment {seg}')
        all_rules = pd.concat([all_rules, temp])
        
    # Get top overall rules by lift (that exist in multiple segments)
    top_rules_list = all_rules.groupby('rule')['lift'].mean().sort_values(ascending=False).head(10).index
    
    # Filter to top rules
    comparison = all_rules[all_rules['rule'].isin(top_rules_list)]
    
    # Pivot for easier viewing
    pivot_lift = comparison.pivot(index='rule', columns='segment', values='lift').fillna(0)
    
    print("\n=== RULE LIFT BY SEGMENT ===")
    print(pivot_lift)
    
    # Plotting
    sns.set_theme(style="whitegrid")
    
    # Plot 1: Heatmap of Lifts for Top Rules
    plt.figure(figsize=(10, 6))
    sns.heatmap(pivot_lift, annot=True, cmap='YlGnBu', fmt='.2f', cbar_kws={'label': 'Lift'})
    plt.title('Association Rule Lift Across Customer Segments')
    plt.tight_layout()
    plt.savefig(VIZ_DIR / 'segment_comparison_heatmap.png', dpi=300)
    plt.close()
    
    # Plot 2: Grouped Bar Chart
    plt.figure(figsize=(12, 8))
    sns.barplot(data=comparison, y='rule', x='lift', hue='segment', palette='Set2')
    plt.title('Lift of Top Association Rules per Customer Segment')
    plt.tight_layout()
    plt.savefig(VIZ_DIR / 'segment_comparison_barplot.png', dpi=300)
    plt.close()
    
    print(f"\nVisualizations saved to {VIZ_DIR}")

def main():
    rules_dict = load_rules()
    if not rules_dict:
        print("No rules found. Please run segment_arm.py first.")
        return
        
    compare_top_rules(rules_dict)

if __name__ == "__main__":
    main()
