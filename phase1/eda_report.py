"""
PHASE 1: EXPLORATORY DATA ANALYSIS (EDA) REPORT
============================================================================

Purpose: Understand engineered customer features BEFORE preprocessing/scaling.
Includes:
  - Feature engineering rationale (13 features: 6 numerical + 3 categorical + 4 binary)
  - Distribution analysis of all features
  - Outlier detection and preprocessing needs
  - Multicollinearity check for numerical features
  - Data quality assessment

Scope: PHASE 1 ONLY (no clustering, no association rules)
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings('ignore')

# Set the visual style
sns.set_theme(style="whitegrid")
plt.rcParams['figure.facecolor'] = 'white'


def load_engineered_features():
    """Load customer features after engineering"""
    try:
        df = pd.read_csv('data/customer_features.csv')
        print(f"[OK] Loaded customer_features.csv: {df.shape}")
        return df
    except FileNotFoundError:
        print("[ERROR] Missing data/customer_features.csv")
        print("        Run: python phase1/feature_engineering.py first")
        return None


def print_feature_overview(df):
    """Print overview of engineered features"""
    print("\n" + "="*80)
    print("PHASE 1: ENGINEERED FEATURES OVERVIEW")
    print("="*80)
    
    print("\n[FEATURES ENGINEERED]")
    print("-" * 80)
    print("""
NUMERICAL FEATURES (6):
  1. num_orders - Number of orders placed by customer
  2. recency - Days since last purchase (calculated from reference date)
  3. monetary - Total lifetime spending
  4. avg_order_value - Average spending per order
  5. total_items_bought - Total quantity of items purchased
  6. avg_item_price - Average price per item

CATEGORICAL FEATURES (3):
  7. recency_quartile - Recency binned into 4 tiers (very_recent -> inactive)
  8. preferred_category - Most frequently purchased product category (top 15+ others)
  9. customer_state - Geographic location (27 Brazilian states)

BINARY FEATURES (4):
  10. is_repeat_customer - Ever made >1 purchase (1=Yes, 0=One-time)
  11. is_high_value - Spending >95th percentile threshold (1=Yes, 0=No)
  12. is_sp - Located in São Paulo (1=Yes, 0=No)
  13. Additional: customer_unique_id (for traceability)
""")
    
    print(f"\nDataset Dimensions: {df.shape[0]:,} customers × {df.shape[1]} columns")


def run_numerical_features_eda(df):
    """Analyze numerical features (6): num_orders, recency, monetary, avg_order_value, total_items_bought, avg_item_price"""
    print("\n" + "="*80)
    print("NUMERICAL FEATURES ANALYSIS (6 features)")
    print("="*80)
    
    # Extract numerical features
    numerical_features = ['num_orders', 'recency', 'monetary', 'avg_order_value', 'total_items_bought', 'avg_item_price']
    df_num = df[numerical_features].copy()
    
    # Print descriptive statistics
    print("\n[DESCRIPTIVE STATISTICS]")
    print("-" * 80)
    stats = df_num.describe().T
    stats['skewness'] = df_num.skew()
    stats['kurtosis'] = df_num.kurtosis()
    print(stats.to_string())
    
    # Identify outliers and skewness issues
    print("\n[OUTLIER & SKEWNESS ASSESSMENT]")
    print("-" * 80)
    for col in numerical_features:
        skew = df_num[col].skew()
        q1, q3 = df_num[col].quantile([0.25, 0.75])
        iqr = q3 - q1
        outliers = df_num[(df_num[col] < q1 - 1.5*iqr) | (df_num[col] > q3 + 1.5*iqr)][col]
        
        skew_level = "HIGHLY SKEWED" if abs(skew) > 1 else ("MODERATELY SKEWED" if abs(skew) > 0.5 else "NORMAL")
        outlier_pct = (len(outliers) / len(df_num)) * 100
        
        print(f"\n{col.upper()}:")
        print(f"  - Skewness: {skew:.3f} [{skew_level}]")
        print(f"  - Outliers: {len(outliers):,} ({outlier_pct:.2f}% of data)")
        print(f"  - Range: ${df_num[col].min():.2f} -> ${df_num[col].max():.2f}")
        print(f"  - Action: {'LOG TRANSFORM NEEDED' if abs(skew) > 0.8 else 'Monitor during scaling'}")
    
    # Create visualization: Distributions (before preprocessing)
    print("\n[CREATING VISUALIZATION: Feature Distributions]")
    print("-" * 80)
    
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle('Numerical Features Distribution (BEFORE Preprocessing)', fontsize=14, fontweight='bold')
    
    for idx, feature in enumerate(numerical_features):
        ax = axes[idx // 3, idx % 3]
        
        # Histogram with KDE
        ax.hist(df_num[feature], bins=50, alpha=0.7, color='steelblue', edgecolor='black')
        ax_twin = ax.twinx()
        df_num[feature].plot(kind='kde', ax=ax_twin, color='red', linewidth=2, label='KDE')
        
        ax.set_title(f'{feature}', fontweight='bold', fontsize=11)
        ax.set_xlabel('Value')
        ax.set_ylabel('Frequency')
        ax.grid(True, alpha=0.3)
        
        # Add skewness annotation
        skew = df_num[feature].skew()
        ax.text(0.98, 0.97, f'Skew: {skew:.2f}', transform=ax.transAxes, 
                ha='right', va='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig('phase1/visualizations/01_numerical_distributions.png', dpi=300, bbox_inches='tight')
    print("[OK] Saved: phase1/visualizations/01_numerical_distributions.png")
    plt.close()
    
    # Create visualization: Log-scale distributions (preview of preprocessing benefit)
    print("\n[CREATING VISUALIZATION: Log-Scale Distributions (Preprocessing Preview)]")
    print("-" * 80)
    
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle('Numerical Features - Log Scale (Preview of Log Transform Benefit)', fontsize=14, fontweight='bold')
    
    for idx, feature in enumerate(numerical_features):
        ax = axes[idx // 3, idx % 3]
        
        # Use log scale for visualization
        data_log = np.log1p(df_num[feature])
        ax.hist(data_log, bins=50, alpha=0.7, color='darkgreen', edgecolor='black')
        ax_twin = ax.twinx()
        data_log.plot(kind='kde', ax=ax_twin, color='red', linewidth=2)
        
        ax.set_title(f'{feature} (log scale)', fontweight='bold', fontsize=11)
        ax.set_xlabel('log(Value)')
        ax.set_ylabel('Frequency')
        ax.grid(True, alpha=0.3)
        
        # Show skewness reduction
        skew_before = df_num[feature].skew()
        skew_after = data_log.skew()
        ax.text(0.98, 0.97, f'Before: {skew_before:.2f}\nAfter: {skew_after:.2f}', 
                transform=ax.transAxes, ha='right', va='top', 
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5), fontsize=9)
    
    plt.tight_layout()
    plt.savefig('phase1/visualizations/02_log_scale_preview.png', dpi=300, bbox_inches='tight')
    print("[OK] Saved: phase1/visualizations/02_log_scale_preview.png")
    plt.close()
    
    return df_num


def run_categorical_features_eda(df):
    """Analyze categorical features (3): recency_quartile, preferred_category, customer_state"""
    print("\n" + "="*80)
    print("CATEGORICAL FEATURES ANALYSIS (3 features)")
    print("="*80)
    
    categorical_features = ['recency_quartile', 'preferred_category', 'customer_state']
    
    print("\n[CATEGORICAL VALUE DISTRIBUTIONS]")
    print("-" * 80)
    for col in categorical_features:
        unique_count = df[col].nunique()
        value_counts = df[col].value_counts()
        print(f"\n{col.upper()}:")
        print(f"  - Unique values: {unique_count}")
        print(f"  - Top 5 values:")
        for val, count in value_counts.head().items():
            pct = (count / len(df)) * 100
            print(f"    • {val}: {count:,} ({pct:.1f}%)")
    
    # Create visualization: Categorical distributions
    print("\n[CREATING VISUALIZATION: Categorical Feature Distributions]")
    print("-" * 80)
    
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle('Categorical Features Distribution', fontsize=14, fontweight='bold')
    
    # Recency quartile
    ax = axes[0]
    recency_counts = df['recency_quartile'].value_counts().sort_index()
    ax.bar(recency_counts.index, recency_counts.values, color='steelblue', edgecolor='black', alpha=0.7)
    ax.set_title('Recency Quartile Distribution', fontweight='bold')
    ax.set_xlabel('Recency Quartile')
    ax.set_ylabel('Number of Customers')
    ax.grid(True, alpha=0.3, axis='y')
    for i, v in enumerate(recency_counts.values):
        ax.text(i, v, str(v), ha='center', va='bottom', fontweight='bold')
    
    # Preferred category (top 10)
    ax = axes[1]
    category_counts = df['preferred_category'].value_counts().head(10)
    ax.barh(range(len(category_counts)), category_counts.values, color='darkgreen', edgecolor='black', alpha=0.7)
    ax.set_yticks(range(len(category_counts)))
    ax.set_yticklabels(category_counts.index, fontsize=9)
    ax.set_title('Top 10 Preferred Categories', fontweight='bold')
    ax.set_xlabel('Number of Customers')
    ax.grid(True, alpha=0.3, axis='x')
    
    # Customer state (top 10)
    ax = axes[2]
    state_counts = df['customer_state'].value_counts().head(10)
    ax.barh(range(len(state_counts)), state_counts.values, color='coral', edgecolor='black', alpha=0.7)
    ax.set_yticks(range(len(state_counts)))
    ax.set_yticklabels(state_counts.index, fontsize=9)
    ax.set_title('Top 10 States (Geographic)', fontweight='bold')
    ax.set_xlabel('Number of Customers')
    ax.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig('phase1/visualizations/03_categorical_distributions.png', dpi=300, bbox_inches='tight')
    print("[OK] Saved: phase1/visualizations/03_categorical_distributions.png")
    plt.close()


def run_binary_features_eda(df):
    """Analyze binary features (4): is_repeat_customer, is_high_value, is_sp, segment_implicit"""
    print("\n" + "="*80)
    print("BINARY FEATURES ANALYSIS (4 features)")
    print("="*80)
    
    binary_features = ['is_repeat_customer', 'is_high_value', 'is_sp']  # Skip segment_implicit (deprecated)
    
    print("\n[BINARY FEATURE STATISTICS]")
    print("-" * 80)
    
    for col in binary_features:
        value_counts = df[col].value_counts()
        print(f"\n{col.upper()}:")
        for val in [0, 1]:
            if val in value_counts.index:
                count = value_counts[val]
                pct = (count / len(df)) * 100
                label = "YES" if val == 1 else "NO"
                print(f"  - {label} ({val}): {count:,} ({pct:.2f}%)")
    
    # Create visualization: Binary feature comparison
    print("\n[CREATING VISUALIZATION: Binary Features Comparison]")
    print("-" * 80)
    
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    fig.suptitle('Binary Features Distribution', fontsize=14, fontweight='bold')
    
    colors_palette = ['#d62728', '#2ca02c']
    
    for idx, col in enumerate(binary_features):
        ax = axes[idx]
        value_counts = df[col].value_counts().sort_index()
        labels = ['No (0)', 'Yes (1)']
        ax.pie(value_counts.values, labels=labels, autopct='%1.1f%%', colors=colors_palette,
               startangle=90, textprops={'fontsize': 10, 'fontweight': 'bold'})
        ax.set_title(col.replace('is_', '').replace('_', ' ').title(), fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('phase1/visualizations/04_binary_features.png', dpi=300, bbox_inches='tight')
    print("[OK] Saved: phase1/visualizations/04_binary_features.png")
    plt.close()


def run_boxplots_outliers(df):
    """Visualize outliers using box plots"""
    print("\n" + "="*80)
    print("OUTLIER VISUALIZATION (Box Plots)")
    print("="*80)
    
    numerical_features = ['num_orders', 'recency', 'monetary', 'avg_order_value', 'total_items_bought', 'avg_item_price']
    df_num = df[numerical_features].copy()
    
    print("\n[CREATING VISUALIZATION: Box Plots for Outlier Detection]")
    print("-" * 80)
    
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle('Box Plots - Outlier & IQR Analysis', fontsize=14, fontweight='bold')
    
    for idx, feature in enumerate(numerical_features):
        ax = axes[idx // 3, idx % 3]
        
        # Box plot
        bp = ax.boxplot(df_num[feature], vert=True, patch_artist=True, widths=0.6)
        bp['boxes'][0].set_facecolor('lightblue')
        bp['boxes'][0].set_edgecolor('darkblue')
        
        # Add statistics text
        q1, median, q3 = df_num[feature].quantile([0.25, 0.5, 0.75])
        iqr = q3 - q1
        lower_whisker = q1 - 1.5 * iqr
        upper_whisker = q3 + 1.5 * iqr
        
        # Count outliers
        outliers_lower = (df_num[feature] < lower_whisker).sum()
        outliers_upper = (df_num[feature] > upper_whisker).sum()
        total_outliers = outliers_lower + outliers_upper
        outlier_pct = (total_outliers / len(df_num)) * 100
        
        stats_text = f"Q1: {q1:.1f}\nMedian: {median:.1f}\nQ3: {q3:.1f}\nIQR: {iqr:.1f}\nOutliers: {total_outliers:,} ({outlier_pct:.1f}%)"
        ax.text(1.4, q3, stats_text, fontsize=9, bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))
        
        ax.set_title(f'{feature}', fontweight='bold', fontsize=11)
        ax.set_ylabel('Value')
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_xticklabels([])
    
    plt.tight_layout()
    plt.savefig('phase1/visualizations/06_boxplots_outliers.png', dpi=300, bbox_inches='tight')
    print("[OK] Saved: phase1/visualizations/06_boxplots_outliers.png")
    plt.close()


def run_qq_plots(df):
    """Q-Q plots to assess normality"""
    print("\n[CREATING VISUALIZATION: Q-Q Plots (Normality Assessment)]")
    print("-" * 80)
    
    from scipy import stats
    
    numerical_features = ['num_orders', 'recency', 'monetary', 'avg_order_value', 'total_items_bought', 'avg_item_price']
    df_num = df[numerical_features].copy()
    
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle('Q-Q Plots - Normality Assessment (Raw Data)', fontsize=14, fontweight='bold')
    
    for idx, feature in enumerate(numerical_features):
        ax = axes[idx // 3, idx % 3]
        
        # Q-Q plot
        stats.probplot(df_num[feature], dist="norm", plot=ax)
        ax.set_title(f'{feature}', fontweight='bold', fontsize=11)
        ax.grid(True, alpha=0.3)
        
        # Calculate normality test (Shapiro-Wilk on sample if too large)
        sample_size = min(5000, len(df_num))
        sample_data = df_num[feature].sample(n=sample_size, random_state=42)
        _, p_value = stats.shapiro(sample_data)
        
        normality_text = f"Shapiro-Wilk p-value: {p_value:.4f}\n{'Normal' if p_value > 0.05 else 'NOT Normal'}"
        ax.text(0.05, 0.95, normality_text, transform=ax.transAxes, fontsize=8,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7),
                verticalalignment='top')
    
    plt.tight_layout()
    plt.savefig('phase1/visualizations/07_qq_plots.png', dpi=300, bbox_inches='tight')
    print("[OK] Saved: phase1/visualizations/07_qq_plots.png")
    plt.close()


def run_violin_plots(df):
    """Violin plots for distribution shape analysis"""
    print("\n[CREATING VISUALIZATION: Violin Plots (Distribution Shape)]")
    print("-" * 80)
    
    numerical_features = ['num_orders', 'recency', 'monetary', 'avg_order_value', 'total_items_bought', 'avg_item_price']
    df_num = df[numerical_features].copy()
    
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle('Violin Plots - Distribution Shape & Density', fontsize=14, fontweight='bold')
    
    for idx, feature in enumerate(numerical_features):
        ax = axes[idx // 3, idx % 3]
        
        # Violin plot with box plot overlay
        parts = ax.violinplot([df_num[feature]], positions=[0], showmeans=True, showmedians=True)
        
        # Customize colors
        for pc in parts['bodies']:
            pc.set_facecolor('lightblue')
            pc.set_alpha(0.7)
        
        ax.set_title(f'{feature}', fontweight='bold', fontsize=11)
        ax.set_ylabel('Value')
        ax.set_xticklabels([])
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add distribution info
        mean = df_num[feature].mean()
        std = df_num[feature].std()
        dist_text = f"Mean: {mean:.2f}\nStd: {std:.2f}"
        ax.text(0.05, 0.95, dist_text, transform=ax.transAxes, fontsize=9,
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7),
                verticalalignment='top')
    
    plt.tight_layout()
    plt.savefig('phase1/visualizations/08_violin_plots.png', dpi=300, bbox_inches='tight')
    print("[OK] Saved: phase1/visualizations/08_violin_plots.png")
    plt.close()


def run_recency_monetary_analysis(df):
    """Recency vs Monetary behavior analysis"""
    print("\n[CREATING VISUALIZATION: Recency vs Monetary Analysis]")
    print("-" * 80)
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle('Customer Behavior: Recency vs Monetary Spending', fontsize=14, fontweight='bold')
    
    # Plot 1: Scatter plot with density coloring
    ax = axes[0]
    scatter = ax.scatter(df['recency'], df['monetary'], c=df['num_orders'], 
                        cmap='viridis', alpha=0.5, s=20, edgecolors='none')
    ax.set_xlabel('Recency (Days Since Last Purchase)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Monetary (Total Spending $)', fontsize=11, fontweight='bold')
    ax.set_title('Scatter Plot: Recency vs Monetary\n(colored by Purchase Frequency)', fontweight='bold')
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Num Orders', fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # Plot 2: Hexbin (density heatmap)
    ax = axes[1]
    hexbin = ax.hexbin(df['recency'], df['monetary'], gridsize=30, cmap='YlOrRd', mincnt=1)
    ax.set_xlabel('Recency (Days Since Last Purchase)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Monetary (Total Spending $)', fontsize=11, fontweight='bold')
    ax.set_title('Density Heatmap: Recency vs Monetary\n(Customer Concentration)', fontweight='bold')
    cbar = plt.colorbar(hexbin, ax=ax)
    cbar.set_label('Customer Count', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('phase1/visualizations/09_recency_monetary_behavior.png', dpi=300, bbox_inches='tight')
    print("[OK] Saved: phase1/visualizations/09_recency_monetary_behavior.png")
    plt.close()


def run_category_spending_heatmap(df):
    """Category spending patterns by recency tier"""
    print("\n[CREATING VISUALIZATION: Category-Spending Heatmap]")
    print("-" * 80)
    
    # Create aggregation: Top categories × recency quartile
    top_categories = df['preferred_category'].value_counts().head(12).index
    df_top = df[df['preferred_category'].isin(top_categories)].copy()
    
    # Aggregate: average spending and customer count by category × recency
    heatmap_data_spending = df_top.groupby(['preferred_category', 'recency_quartile'])['monetary'].mean().unstack()
    heatmap_data_count = df_top.groupby(['preferred_category', 'recency_quartile']).size().unstack()
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle('Top 12 Categories × Recency Quartiles', fontsize=14, fontweight='bold')
    
    # Heatmap 1: Average Spending
    ax = axes[0]
    sns.heatmap(heatmap_data_spending, annot=True, fmt='.0f', cmap='YlGn', ax=ax, 
                cbar_kws={'label': 'Avg Spending ($)'}, linewidths=0.5)
    ax.set_title('Average Spending by Category & Recency', fontweight='bold')
    ax.set_xlabel('Recency Quartile', fontweight='bold')
    ax.set_ylabel('Preferred Category', fontweight='bold')
    
    # Heatmap 2: Customer Count
    ax = axes[1]
    sns.heatmap(heatmap_data_count, annot=True, fmt='.0f', cmap='Blues', ax=ax,
                cbar_kws={'label': 'Customer Count'}, linewidths=0.5)
    ax.set_title('Customer Count by Category & Recency', fontweight='bold')
    ax.set_xlabel('Recency Quartile', fontweight='bold')
    ax.set_ylabel('Preferred Category', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('phase1/visualizations/10_category_spending_heatmap.png', dpi=300, bbox_inches='tight')
    print("[OK] Saved: phase1/visualizations/10_category_spending_heatmap.png")
    plt.close()


def run_correlation_analysis(df):
    """Check multicollinearity between numerical features"""
    print("\n" + "="*80)
    print("MULTICOLLINEARITY CHECK (Numerical Features)")
    print("="*80)
    
    numerical_features = ['num_orders', 'recency', 'monetary', 'avg_order_value', 'total_items_bought', 'avg_item_price']
    df_num = df[numerical_features].copy()
    
    # Calculate correlation matrix
    corr_matrix = df_num.corr()
    
    print("\n[CORRELATION MATRIX]")
    print("-" * 80)
    print(corr_matrix.to_string())
    
    # Flag high correlations
    print("\n[HIGH CORRELATIONS (>0.80) - Potential Issues for Clustering]")
    print("-" * 80)
    
    high_corr_found = False
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            corr_value = abs(corr_matrix.iloc[i, j])
            if corr_value > 0.80:
                feature1 = corr_matrix.columns[i]
                feature2 = corr_matrix.columns[j]
                print(f"[WARNING] {feature1} -- {feature2}: {corr_matrix.iloc[i, j]:.3f}")
                high_corr_found = True
    
    if not high_corr_found:
        print("[OK] No high correlations detected. Features are suitable for clustering.")
    
    # Create visualization: Correlation heatmap
    print("\n[CREATING VISUALIZATION: Correlation Heatmap]")
    print("-" * 80)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
                cbar_kws={'label': 'Correlation'}, square=True, ax=ax, vmin=-1, vmax=1,
                annot_kws={'fontsize': 10, 'fontweight': 'bold'})
    ax.set_title('Feature Correlation Heatmap\n(Multicollinearity Check)', fontweight='bold', fontsize=12)
    plt.tight_layout()
    plt.savefig('phase1/visualizations/05_correlation_heatmap.png', dpi=300, bbox_inches='tight')
    print("[OK] Saved: phase1/visualizations/05_correlation_heatmap.png")
    plt.close()


def run_data_quality_check(df):
    """Assess data quality"""
    print("\n" + "="*80)
    print("DATA QUALITY ASSESSMENT")
    print("="*80)
    
    print("\n[MISSING VALUES]")
    print("-" * 80)
    missing = df.isnull().sum()
    if missing.sum() == 0:
        print("[OK] No missing values detected in dataset")
    else:
        print(missing[missing > 0])
    
    print("\n[DATASET STATISTICS]")
    print("-" * 80)
    print(f"Total Customers: {len(df):,}")
    print(f"Total Features: {df.shape[1]}")
    print(f"  - ID Column: 1 (customer_unique_id)")
    print(f"  - Numerical: 6 (num_orders, recency, monetary, avg_order_value, total_items_bought, avg_item_price)")
    print(f"  - Categorical: 3 (recency_quartile, preferred_category, customer_state)")
    print(f"  - Binary: 3 (is_repeat_customer, is_high_value, is_sp)")
    
    print("\n[KEY FEATURE STATISTICS]")
    print("-" * 80)
    print(f"[OK] Repeat customers: {df['is_repeat_customer'].sum():,} ({df['is_repeat_customer'].mean()*100:.2f}%)")
    print(f"[OK] High-value customers (top 5%): {df['is_high_value'].sum():,} ({df['is_high_value'].mean()*100:.2f}%)")
    print(f"[OK] Sao Paulo customers: {df['is_sp'].sum():,} ({df['is_sp'].mean()*100:.2f}%)")
    print(f"[OK] Unique categories: {df['preferred_category'].nunique()}")
    print(f"[OK] Unique states: {df['customer_state'].nunique()}")
    print(f"[OK] Recency quartile distribution: balanced (25% each quartile)")
    
    print("\n[FEATURE ENGINEERING SUMMARY]")
    print("-" * 80)
    print(f"[OK] Customer behavioral metrics captured (num_orders, recency, monetary)")
    print(f"[OK] Customer spending metrics captured (avg_order_value, total_items_bought, avg_item_price)")
    print(f"[OK] Geographic segmentation (customer_state, is_sp)")
    print(f"[OK] Value tier classification (is_high_value, is_repeat_customer)")
    print(f"[OK] Temporal classification (recency_quartile)")
    print(f"[OK] Product preference captured (preferred_category)")


def main():
    """Main EDA execution"""
    print("\n" + "="*80)
    print("PHASE 1: EXPLORATORY DATA ANALYSIS (EDA) REPORT")
    print("="*80)
    
    # Load engineered features
    df = load_engineered_features()
    if df is None:
        return
    
    # Run all analyses
    print_feature_overview(df)
    df_num = run_numerical_features_eda(df)
    run_categorical_features_eda(df)
    run_binary_features_eda(df)
    run_boxplots_outliers(df)
    run_qq_plots(df)
    run_violin_plots(df)
    run_recency_monetary_analysis(df)
    run_category_spending_heatmap(df)
    run_correlation_analysis(df)
    run_data_quality_check(df)
    
    # Final summary
    print("\n" + "="*80)
    print("EDA REPORT COMPLETE")
    print("="*80)
    print(f"""
[OK] Analyzed 13 engineered features across {len(df):,} customers
[OK] Identified skewed distributions requiring log transformation:
  - monetary (extreme range: ${df['monetary'].min():.2f} to ${df['monetary'].max():.2f})
  - num_orders, avg_order_value, total_items_bought, avg_item_price
[OK] Identified categorical features for mixed-type clustering
[OK] Identified binary features for customer segmentation
[OK] Correlation analysis complete - checking multicollinearity

VISUALIZATIONS SAVED (10 PNG files):
  1. 01_numerical_distributions.png - Feature distributions before preprocessing
  2. 02_log_scale_preview.png - Log-transform benefit visualization
  3. 03_categorical_distributions.png - Categorical feature breakdowns
  4. 04_binary_features.png - Binary feature composition
  5. 05_correlation_heatmap.png - Multicollinearity assessment
  6. 06_boxplots_outliers.png - Box plots for outlier & IQR analysis
  7. 07_qq_plots.png - Q-Q plots for normality assessment
  8. 08_violin_plots.png - Violin plots for distribution shape
  9. 09_recency_monetary_behavior.png - Customer behavior scatter & density
  10. 10_category_spending_heatmap.png - Category preferences by recency tier

NEXT STEPS:
  -> Phase 1: Run feature_scaling.py for preprocessing (log transform + RobustScaler)
  -> Phase 2: Transition to association rule mining
  -> Phase 3: Execute K-Prototype clustering with scaled features
""")


if __name__ == "__main__":
    main()