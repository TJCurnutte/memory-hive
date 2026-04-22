# Data Playbook v2
**Session**: data-analyst  
**Date**: 2026-04-22  
**Purpose**: 15+ Core Data Skills Reference Guide

---

## SKILL 1: Descriptive Statistics

### Fundamentals
```python
import pandas as pd
import numpy as np

# Central tendency
df['col'].mean()      # Average
df['col'].median()    # Middle value
df['col'].mode()      # Most frequent

# Dispersion
df['col'].std()       # Standard deviation
df['col'].var()       # Variance
df['col'].min()       # Minimum
df['col'].max()       # Maximum
df['col'].quantile(0.25)  # Quartiles
```

### When to use
- Initial data exploration
- Summarizing distributions
- Identifying outliers
- Setting baseline metrics

---

## SKILL 2: Correlation Analysis

### Pearson vs Spearman
```python
# Pearson: Linear relationships, normal distribution
df.corr(method='pearson')

# Spearman: Monotonic relationships, non-parametric
df.corr(method='spearman')

# Kendall: Small datasets, many ties
df.corr(method='kendall')
```

### Interpretation
- |r| > 0.7: Strong correlation
- 0.4 < |r| < 0.7: Moderate
- |r| < 0.4: Weak correlation
- r < 0: Negative relationship

---

## SKILL 3: Chart Selection Guide

### The Right Chart for Every Data Type

| **Data Type** | **Goal** | **Best Chart** | **Example** |
|--------------|----------|----------------|-------------|
| Time series | Trend | Line | Sales over months |
| Categorical | Compare | Bar (horizontal) | Revenue by region |
| Part-to-whole | Composition | Pie / Donut | Market share |
| Distribution | Spread | Histogram / Box | Age distribution |
| Two continuous | Relationship | Scatter | Height vs weight |
| One continuous | Frequency | Histogram | Test scores |
| Geographic | Location | Choropleth Map | Sales by state |
| Hierarchy | Nested parts | Treemap | Budget breakdown |
| Flow/Process | Movement | Sankey | User journeys |
| Network | Connections | Force-directed | Social graph |

### Color Palette Best Practices
- Sequential: One hue, light→dark (for ordered data)
- Diverging: Two hues (for data with meaningful midpoint)
- Categorical: Distinct hues (max 7 categories)
- Use colorblind-safe palettes (viridis, colorblind)

---

## SKILL 4: A/B Test Execution

### Test Selection Flowchart
```
START
  ↓
Is data normally distributed?
  → YES → Is variance known? → YES → Z-test
  → YES → NO → Welch's t-test
  → NO → Is data ordinal? → YES → Mann-Whitney U
  → NO → Is data count-based? → YES → Poisson test
  → NO → Chi-squared test
```

### Python Implementation
```python
from scipy import stats

# Two-sample t-test (Welch's)
t_stat, p_value = stats.ttest_ind(group_a, group_b, equal_var=False)

# Fisher's exact (for proportions)
# Use for click-through rates, conversion rates
from scipy.stats import fisher_exact
odds_ratio, p_value = fisher_exact([[a_convert, a_total], 
                                     [b_convert, b_total]])

# Chi-squared (for multiple categories)
chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
```

### Minimum Sample Size Calculator
```python
import numpy as np
from scipy.stats import norm

def sample_size(mde, baseline, alpha=0.05, power=0.8):
    """Calculate required sample size per variant"""
    z_alpha = norm.ppf(1 - alpha/2)
    z_beta = norm.ppf(power)
    p1, p2 = baseline, baseline * (1 + mde)
    pooled = (p1 + p2) / 2
    n = ((z_alpha * np.sqrt(2*pooled*(1-pooled)) + 
          z_beta * np.sqrt(p1*(1-p1) + p2*(1-p2)))**2 / (p2-p1)**2)
    return int(np.ceil(n))

# Example: 10% MDE on 5% baseline conversion
n = sample_size(mde=0.10, baseline=0.05)
print(f"Need {n:,} per variant = {2*n:,} total")
```

---

## SKILL 5: Statistical Significance

### Key Formulas
```python
import numpy as np
from scipy import stats

def significance_test(data1, data2, alpha=0.05):
    """Complete statistical test wrapper"""
    # T-test
    t_stat, p_value = stats.ttest_ind(data1, data2)
    
    # Confidence interval
    mean_diff = np.mean(data1) - np.mean(data2)
    se = np.sqrt(np.var(data1)/len(data1) + np.var(data2)/len(data2))
    ci_lower = mean_diff - 1.96 * se
    ci_upper = mean_diff + 1.96 * se
    
    # Effect size (Cohen's d)
    pooled_std = np.sqrt((np.var(data1) + np.var(data2)) / 2)
    cohens_d = mean_diff / pooled_std
    
    return {
        'p_value': p_value,
        'significant': p_value < alpha,
        'ci': (ci_lower, ci_upper),
        'effect_size': cohens_d,
        'interpretation': 'small' if abs(cohens_d) < 0.5 else 
                         'medium' if abs(cohens_d) < 0.8 else 'large'
    }
```

### Effect Size Interpretations
- Cohen's d: 0.2 = small, 0.5 = medium, 0.8 = large
- Pearson r: 0.1 = small, 0.3 = medium, 0.5 = large
- Cramér's V: 0.1 = small, 0.3 = medium, 0.5 = large

---

## SKILL 6: Anomaly Detection

### Methods Comparison
| Method | Best For | Pros | Cons |
|--------|----------|------|------|
| Z-score | Normal distribution | Simple | Sensitive to outliers |
| IQR | Skewed data | Robust | Only univariate |
| Isolation Forest | Multivariate | Fast | Needs tuning |
| LOF | Density-based | Handles varying density | Slow on large data |
| DBSCAN | Clusters with noise | No pre-set k | Sensitive to params |

### Implementation
```python
# Z-score method
def z_score_anomaly(data, threshold=3):
    z_scores = np.abs(stats.zscore(data))
    return z_scores > threshold

# IQR method
def iqr_anomaly(data, multiplier=1.5):
    q1, q3 = np.percentile(data, [25, 75])
    iqr = q3 - q1
    lower, upper = q1 - multiplier*iqr, q3 + multiplier*iqr
    return (data < lower) | (data > upper)

# Isolation Forest
from sklearn.ensemble import IsolationForest
iso = IsolationForest(contamination=0.05, random_state=42)
anomalies = iso.fit_predict(data.reshape(-1, 1))
```

---

## SKILL 7: Time Series Analysis

### Essential Techniques
```python
import pandas as pd
import matplotlib.pyplot as plt

# Moving averages
df['ma7'] = df['value'].rolling(window=7).mean()
df['ma30'] = df['value'].rolling(window=30).mean()

# Exponential smoothing
df['ema'] = df['value'].ewm(span=30).mean()

# Year-over-year comparison
df['yoy_growth'] = df['value'].pct_change(periods=365)

# Decomposition
from statsmodels.tsa.seasonal import seasonal_decompose
result = seasonal_decompose(df['value'], model='additive', period=365)

# Trend detection
from scipy.stats import linregress
slope, intercept, r_value, p_value, std_err = linregress(
    range(len(df)), df['value']
)
```

---

## SKILL 8: Cohort Analysis

### Implementation
```python
def cohort_analysis(df, user_col, date_col, period='M'):
    """Create retention cohort table"""
    df = df.copy()
    df['cohort'] = df.groupby(user_col)[date_col].transform('min')
    df['cohort_period'] = (df[date_col].dt.to_period(period) - 
                           df['cohort']).apply(lambda x: x.n)
    
    cohort_table = df.groupby(['cohort_period']).agg(
        {user_col: 'nunique'}
    ).reset_index()
    cohort_table.columns = ['CohortPeriod', 'Users']
    
    cohort_table['Retention'] = cohort_table['Users'] / cohort_table['Users'].iloc[0]
    
    return cohort_table
```

### Retention Matrix Pattern
```
Cohort   Jan  Feb  Mar  Apr  May
2024-01  100% 45%  32%  28%  25%
2024-02  100% 48%  35%  30%   -
2024-03  100% 46%  33%   -    -
2024-04  100% 47%   -    -    -
```

---

## SKILL 9: Funnel Analysis

### Implementation
```python
def funnel_analysis(steps, total_users):
    """Calculate drop-off at each step"""
    funnel = pd.DataFrame({
        'step': steps,
        'users': total_users,
    })
    
    funnel['conversion_rate'] = funnel['users'] / funnel['users'].iloc[0]
    funnel['drop_off'] = funnel['users'].diff(-1)
    funnel['drop_off_pct'] = (funnel['drop_off'] / funnel['users'] * 100)
    
    return funnel

# Example: E-commerce funnel
funnel_analysis(
    steps=['Visit', 'View', 'AddCart', 'Checkout', 'Purchase'],
    total_users=[100000, 45000, 12000, 8000, 5000]
)
```

---

## SKILL 10: Metric Frameworks

### AARRR Implementation Template

```python
AARRR_METRICS = {
    'Acquisition': {
        'CAC': lambda df: df['marketing_spend'].sum() / df['new_users'].sum(),
        'ChannelMix': lambda df: df.groupby('channel')['new_users'].sum(),
        'ConversionRate': lambda df: df['visitors'].pct_change()
    },
    'Activation': {
        'SignupRate': lambda df: df['signups'] / df['visitors'],
        'FeatureAdoption': lambda df: df.groupby('feature')['users'].count(),
        'TimeToValue': lambda df: df['first_value'].mean()
    },
    'Retention': {
        'DAU/MAU': lambda df: df['dau'] / df['mau'],
        'ChurnRate': lambda df: 1 - df['retention'].mean(),
        'SessionFreq': lambda df: df['sessions'] / df['users']
    },
    'Referral': {
        'ViralCoeff': lambda df: df['invites'] / df['users'],
        'NPS': lambda df: (df['promoters'] - df['detractors']) / df['total'],
        'KFactor': lambda df: df['invites'] * df['conversion'] / df['users']
    },
    'Revenue': {
        'ARPU': lambda df: df['revenue'].sum() / df['users'].sum(),
        'LTV': lambda df: df['arpu'] / df['churn_rate'],
        'LTV_CAC_ratio': lambda df: df['ltv'] / df['cac']
    }
}
```

### HEART Metrics Template

```python
HEART_METRICS = {
    'Happiness': ['NPS', 'CSAT', 'CES'],
    'Engagement': ['DAU', 'MAU', 'SessionLength', 'PageViews'],
    'Adoption': ['NewUsers', 'ActivationRate', 'FeatureUsage'],
    'Retention': ['D1/D7/D30', 'ChurnRate', 'WinBackRate'],
    'TaskSuccess': ['CompletionRate', 'TimeOnTask', 'ErrorRate']
}
```

---

## SKILL 11: Dashboard Design

### Layout Principles
1. **Top**: Primary KPIs (1-3 metrics)
2. **Middle**: Trend charts and comparisons
3. **Bottom**: Detailed breakdowns

### Component Hierarchy
```
┌─────────────────────────────────────┐
│         EXECUTIVE SUMMARY           │  ← 1 metric
├─────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐          │
│  │  KPI 1  │  │  KPI 2  │          │  ← 4-6 KPIs
│  └─────────┘  └─────────┘          │
├─────────────────────────────────────┤
│         TREND CHART                 │  ← Time series
├─────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐          │
│  │  Break │  │  Break │           │  ← Breakdown
│  │   down │  │   down │           │
│  └─────────┘  └─────────┘          │
└─────────────────────────────────────┘
```

### Color Coding
- Green: Positive / On target
- Yellow: Warning / Needs attention
- Red: Alert / Below threshold
- Blue: Neutral / Informational

---

## SKILL 12: Reporting Best Practices

### Report Structure
1. **Executive Summary** (3 bullets)
2. **Key Metrics** (actual vs target)
3. **Trends** (with context)
4. **Anomalies** (explained)
5. **Recommendations** (actionable)

### Frequency Guide
| Report Type | Frequency | Audience |
|------------|-----------|----------|
| Daily pulse | Daily | Ops team |
| Weekly snapshot | Weekly | Managers |
| Monthly business review | Monthly | Leadership |
| Quarterly board deck | Quarterly | Board |

---

## SKILL 13: Data Quality Checks

### Quality Framework
```python
def data_quality_check(df):
    """Comprehensive data quality report"""
    report = {
        'shape': df.shape,
        'missing': df.isnull().sum(),
        'duplicates': df.duplicated().sum(),
        'dtypes': df.dtypes,
        'numeric_stats': df.describe(),
        'categorical_counts': {col: df[col].nunique() 
                               for col in df.select_dtypes('O')}
    }
    
    # Missing data assessment
    missing_pct = df.isnull().sum() / len(df) * 100
    high_missing = missing_pct[missing_pct > 5].index.tolist()
    
    if high_missing:
        print(f"⚠️ Columns with >5% missing: {high_missing}")
    
    return report
```

### Common Issues Checklist
- [ ] Check for null/missing values
- [ ] Validate date ranges
- [ ] Verify referential integrity
- [ ] Look for duplicate records
- [ ] Check for negative values where inappropriate
- [ ] Validate unique identifiers
- [ ] Check for inconsistent formatting

---

## SKILL 14: Pandas Alternatives

### When to Use What

| Scenario | Tool | Why |
|----------|------|-----|
| <1GB data, interactive | Pandas | Familiar API |
| >1GB data, performance | Polars | 10x faster, less memory |
| SQL-like queries | DuckDB | SQL interface |
| Parallel processing | Dask | Scales to clusters |
| Large Excel files | OpenPyXL | Memory efficient |
| Streaming data | Polars LazyFrame | Lazy evaluation |

### Polars Quick Reference
```python
import polars as pl

# Same operations, different speed
df = pl.read_csv('data.csv')
df.select(['col1', 'col2']).filter(pl.col('col1') > 100).group_by('col2').agg(
    pl.col('col1').mean()
)

# Lazy evaluation for large data
df_lazy = pl.scan_csv('large_file.csv')
result = df_lazy.filter(pl.col('value') > 0).group_by('category').agg(
    pl.col('value').sum()
).collect()
```

---

## SKILL 15: AI Data Analysis Tools

### Tool Integration
```python
# Modern AI-assisted workflow

# 1. Automated EDA
from ydata_profiling import ProfileReport
profile = ProfileReport(df, title="Data Profile")
profile.to_file("report.html")

# 2. AI-assisted queries
# BamboolAI: Natural language to SQL/Pandas

# 3. Automated visualization
# Chartify: Pythonic chart creation
import chartify
ch = chartify.Chart(blank_labels=True)
ch.plot.scatter(
    data_frame=df,
    x_columns=['x_col'],
    y_columns=['y_col']
)
ch.show()

# 4. AutoML for predictions
from flaml import AutoML
automl = AutoML()
automl.fit(df[X_cols], df['target'], task='classification')
```

### AI Tool Comparison
| Tool | Focus | Integration |
|------|-------|-------------|
| ChatGPT/Claude | General analysis | API |
| BamboolAI | SQL/Pandas queries | Local |
| Hex | Collaborative notebooks | Cloud |
| Hex | SQL + AI | Cloud |
| Julius | Spreadsheet AI | Excel/Sheets |

---

## Quick Reference Cards

### Statistical Tests Cheat Sheet
```
Question → Test
─────────────────────────────
Compare 2 means → t-test
Compare >2 means → ANOVA
Compare proportions → Chi-square
Predict value → Regression
Find clusters → K-means/DBSCAN
Detect anomalies → Z-score/IForest
Measure relationship → Correlation
Test independence → Chi-square
```

### Visualization Decision Tree
```
Is it over time?
  YES → Line chart
  NO → Is it comparing categories?
    YES → Bar chart
    NO → Is it part of whole?
      YES → Pie chart
      NO → Is it distribution?
        YES → Histogram
        NO → Scatter plot
```

---

*Playbook Version: 2.0 | Updated: 2026-04-22*
*Data-Analyst Agent | OpenClaw Hive*
