# Data Visualization — Selection, Storytelling & Interactive Dashboards
## v3 — Data Analyst Agent Learning Document

---

## 1. CHART SELECTION — THE DECISION FRAMEWORK

### 1.1 Start With the Question
| Question Type | Best Chart(s) |
|---|---|
| How much? (totals, counts) | Bar chart, KPI card |
| How distributed? | Histogram, box plot, violin |
| How compared? (categories) | Bar chart, dot plot |
| How trending over time? | Line chart, area chart |
| What is the relationship? | Scatter plot, bubble |
| How composed of parts? | Stacked bar, treemap, donut |
| Where in space? | Map, choropleth |
| How correlated? | Correlation heatmap |

### 1.2 Avoid These Common Mistakes
```
❌ Pie charts with > 5 slices
❌ 3D bar charts (distorts perception)
❌ Dual-axis charts unless explicitly comparing two measures with different scales
❌ Line charts for categorical time series (use bars)
❌ Stacked bars for comparison across categories (use grouped bars)
❌ Area charts without sorting by magnitude (confusing)
```

### 1.3 The "One Chart Per Insight" Rule
- If a chart requires a legend to decode, it's too complex
- If you need to explain the chart in more than one sentence, redesign it
- Each visualization should answer exactly one question

---

## 2. VISUAL ENCODING — WHAT THE EYE SEES

### 2.1 Perceptual Accuracy (Tufte / Cleveland Hierarchy)
```
Most accurate → Least accurate:
Position > Length > Angle > Area > Color saturation > Color hue
```

- **Position**: scatter plots, bar charts — highest accuracy
- **Length**: bar charts — very accurate
- **Angle**: pie charts — moderate (humans misjudge angles)
- **Area**: bubble charts, treemaps — moderate
- **Color saturation**: choropleth maps — interpretable but prone to distortion
- **Color hue**: categorical maps — only for nominal categories

### 2.2 Gestalt Principles Applied
```
Proximity:    Elements close together are perceived as related
Similarity:   Same color/shape/style = same category
Enclosure:    Bordered groups are treated as units
Continuity:   Aligned elements are perceived as connected
Closure:      Humans close open shapes (use for loading states)
```

---

## 3. COLOR — SYSTEMATIC APPROACH

### 3.1 Color for Categorical Data
```python
import matplotlib.pyplot as plt

# Distinct, perceptually uniform colors
categorical_palette = [
    '#4E79A7',  # Blue
    '#F28E2B',  # Orange
    '#E15759',  # Red
    '#76B7B2',  # Teal
    '#59A14F',  # Green
    '#EDC948',  # Yellow
    '#B07AA1',  # Purple
    '#FF9DA7',  # Pink
]
```

### 3.2 Color for Sequential Data (Low → High)
```python
# Single-hue sequential (continuous)
sequential_blue = ['#F7FBFF', '#C6DBEF', '#6BAED6', '#2171B5', '#08306B']
# Diverging (two extremes, neutral center)
diverging = ['#2166AC', '#4393C3', '#D1E5F0', '#F7F7F7', '#FDDBC7', '#F4A582', '#D6604D', '#B2182B']
```

### 3.3 Color for Sequential / Diverging Scales
```python
import matplotlib.colors as mcolors

# Create custom colormap
cmap = mcolors.LinearSegmentedColormap.from_list(
    'custom_diverging',
    ['#2166AC', '#F7F7F7', '#B2182B']
)
```

### 3.4 Color Blindness Safety
```python
# Use pre-built safe palettes
import matplotlib.pyplot as plt
plt.style.use('tableau-colorblind10')  # Built-in safe palette

# Or use: Viridis, Plasma, Cividis (all colorblind-safe)
```

---

## 4. MATPLOTLIB — PRODUCTION QUALITY PLOTS

### 4.1 Standard Production Plot
```python
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

fig, ax = plt.subplots(figsize=(12, 7), dpi=120)

# Data
regions = ['Northeast', 'Southeast', 'Midwest', 'Southwest', 'West']
revenue = [2.1, 1.8, 1.4, 2.3, 2.8]
colors = ['#4E79A7' if r != max(revenue) else '#E15759' for r in revenue]

bars = ax.bar(regions, revenue, color=colors, edgecolor='white', linewidth=0.5, width=0.65)

# Value labels
for bar in bars:
    height = bar.get_height()
    ax.annotate(f'${height:.1f}M',
        xy=(bar.get_x() + bar.get_width() / 2, height),
        ha='center', va='bottom',
        fontsize=11, fontweight='medium', color='#333')

# Styling
ax.set_xlabel('Region', fontsize=12, labelpad=10)
ax.set_ylabel('Revenue ($M)', fontsize=12, labelpad=10)
ax.set_title('Revenue by Region — FY2024', fontsize=14, fontweight='bold', pad=15)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.1f}M'))
ax.set_ylim(0, max(revenue) * 1.15)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.tick_params(axis='both', labelsize=10)
ax.grid(axis='y', alpha=0.3, linestyle='--')

# Highlight max
ax.annotate('Top performer', xy=(4, 2.8), xytext=(3.2, 3.2),
    fontsize=9, color='#E15759',
    arrowprops=dict(arrowstyle='->', color='#E15759', lw=1.5))

plt.tight_layout()
plt.savefig('revenue_by_region.png', dpi=300, bbox_inches='tight')
plt.show()
```

### 4.2 Multi-Panel Grid
```python
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()

# Panel 1: Line chart
axes[0].plot(dates, revenue, color='#4E79A7', linewidth=2)
axes[0].fill_between(dates, revenue, alpha=0.2, color='#4E79A7')
axes[0].set_title('Revenue Trend', fontweight='bold')
axes[0].spines['top'].set_visible(False)
axes[0].spines['right'].set_visible(False)

# Panel 2: Histogram
axes[1].hist(data, bins=30, color='#F28E2B', edgecolor='white', alpha=0.8)
axes[1].set_title('Distribution', fontweight='bold')

# Panel 3: Scatter
axes[2].scatter(df['ad_spend'], df['revenue'], alpha=0.5, c=df['region'].cat.codes, cmap='tab10')
axes[2].set_xlabel('Ad Spend')
axes[2].set_ylabel('Revenue')

# Panel 4: Stacked area
axes[3].stackplot(months, product_a, product_b, product_c, labels=['A','B','C'], alpha=0.8)

for ax in axes: ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
plt.tight_layout()
```

---

## 5. SEABORN — STATISTICAL VISUALIZATIONS

### 5.1 Regression with Confidence Interval
```python
import seaborn as sns
import matplotlib.pyplot as plt

sns.set_style('whitegrid')
sns.set_context('notebook', font_scale=1.1)

fig, ax = plt.subplots(figsize=(10, 6))
sns.regplot(data=df, x='marketing_spend', y='revenue',
    scatter_kws={'alpha': 0.4, 's': 50, 'color': '#4E79A7'},
    line_kws={'color': '#E15759', 'linewidth': 2.5})
ax.set_title('Marketing Spend vs. Revenue', fontsize=14, fontweight='bold')
```

### 5.2 Box Plots for Distribution Comparison
```python
sns.boxplot(data=df, x='region', y='revenue', palette='tab10', width=0.5)
sns.stripplot(data=df, x='region', y='revenue', color='black', alpha=0.3, size=3)
# Shows median, quartiles, outliers, and individual points
```

### 5.3 Pairplot for Exploratory Analysis
```python
# Pairwise relationships in numeric columns
sns.pairplot(df[['revenue', 'quantity', 'price', 'region']], 
    hue='region', palette='tab10', diag_kind='kde',
    plot_kws={'alpha': 0.5, 's': 30})
```

### 5.4 Violin Plot (Distribution + Density)
```python
sns.violinplot(data=df, x='product_category', y='revenue_per_unit',
    inner='box', palette='Set2')
# Shows shape of distribution beyond what box plots show
```

### 5.5 Heatmap
```python
corr = df.select_dtypes('number').corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt='.2f',
    cmap='coolwarm', center=0, linewidths=0.5,
    cbar_kws={'label': 'Correlation', 'shrink': 0.8})
```

---

## 6. PLOTLY — INTERACTIVE VISUALIZATIONS

### 6.1 Interactive Line Chart
```python
import plotly.express as px
import plotly.graph_objects as go

fig = px.line(df, x='date', y='revenue', color='region',
    markers=True, line_shape='spline')
fig.update_layout(
    title='Revenue by Region Over Time',
    xaxis_title='Date',
    yaxis_title='Revenue ($)',
    legend_title='Region',
    hovermode='x unified'
)
fig.update_traces(line=dict(width=2.5))
fig.show()
```

### 6.2 Sunburst (Hierarchical Composition)
```python
fig = px.sunburst(df, path=['region', 'category', 'product'],
    values='revenue', color='revenue',
    color_continuous_scale='RdBu')
fig.update_layout(title='Revenue Breakdown')
fig.show()
```

### 6.3 Animated Scatter (Time Animation)
```python
fig = px.scatter(df, x='gdp_per_capita', y='life_expectancy',
    animation_frame='year', animation_group='country',
    size='population', color='region',
    hover_name='country', log_x=True,
    range_x=[1000, 100000], range_y=[20, 90])
fig.show()
```

### 6.4 Bullet Chart (KPI vs. Target)
```python
fig = go.Figure(go.Indicator(
    mode='number+gauge+delta',
    value=850,
    delta={'reference': 800, 'valueformat': '.0f'},
    gauge={
        'axis': {'range': [0, 1000]},
        'bar': {'color': '#4E79A7'},
        'steps': [
            {'range': [0, 600], 'color': '#E15759'},
            {'range': [600, 800], 'color': '#F28E2B'},
            {'range': [800, 1000], 'color': '#59A14F'}
        ]
    },
    title={'text': 'Revenue Target'},
    domain={'x': [0.25, 0.75], 'y': [0.25, 0.75]}
))
fig.show()
```

---

## 7. DASHBOARD DESIGN — STORYTELLING FRAMEWORK

### 7.1 Layout Hierarchy
```
┌─────────────────────────────────────────────────┐
│  HEADER: Title + Date Range + Key Metric Cards  │  ← 1-2 minutes
├─────────────────────────────────────────────────┤
│                                                 │
│  PRIMARY INSIGHT CHART (60% width)             │  ← 30 seconds
│                                                 │
├──────────────────────┬──────────────────────────┤
│  COMPARATIVE CHART   │  SECONDARY METRICS        │  ← drill-down
├──────────────────────┴──────────────────────────┤
│  DETAIL TABLE / FILTER PANEL                   │  ← exploration
└─────────────────────────────────────────────────┘

Reading pattern: F-pattern (top-left priority)
```

### 7.2 Dashboard Flow — The Narrative Arc
1. **Hook**: KPI cards with status indicators (▲▼) — immediate context
2. **Context**: Trend chart — what happened over time
3. **Comparison**: Bar/column chart — how groups differ
4. **Detail**: Table or breakdown — data for the curious
5. **Action**: Filter/selector — let user explore

### 7.3 KPI Card Design
```python
def kpi_card(title, value, delta, target=None, color='#333'):
    return f"""
    <div style="background:#f9f9f9;border-radius:8px;padding:20px;
                border-left:4px solid {color};">
        <div style="font-size:12px;color:#888;margin-bottom:4px;">{title}</div>
        <div style="font-size:28px;font-weight:bold;color:{color};">{value}</div>
        <div style="font-size:13px;color:{'#E15759' if delta<0 else '#59A14F'};">
            {'▲' if delta >= 0 else '▼'} {abs(delta)}% {'vs last period'}
        </div>
        {f'<div style="font-size:11px;color:#888;margin-top:4px;">Target: {target}</div>' if target else ''}
    </div>
    """
```

### 7.4 Dashboard Color Strategy
- **Background**: White or very light gray (#F9F9F9) — maximizes readability
- **Primary metric**: Bold, single accent color
- **Positive indicators**: Green (#59A14F)
- **Negative indicators**: Red (#E15759)
- **Neutral / baseline**: Blue (#4E79A7)
- **Grid / borders**: Very light gray — present but not distracting

---

## 8. STREAMLIT — PYTHON DASHBOARD FRAMEWORK

### 8.1 Basic Dashboard Structure
```python
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sales Dashboard", page_icon="📊", layout="wide")

# Sidebar filters
st.sidebar.header("Filters")
date_range = st.sidebar.date_input("Date Range", [])
regions = st.sidebar.multiselect("Regions", ['NE', 'SE', 'MW', 'SW', 'W'], default=['NE','SE','MW','SW','W'])

# Title
st.title("📊 Revenue Dashboard")
st.markdown(f"**{len(df)} orders** | **{df['region'].nunique()} regions**")

# KPI row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"${total_rev:.1f}M", f"{pct_chg:.1f}%")
col2.metric("Orders", f"{total_orders:,}", f"{orders_chg:.1f}%")
col3.metric("Avg Order Value", f"${avg_order:.0f}", f"{aov_chg:.1f}%")
col4.metric("Active Customers", f"{active_cust:,}", f"{cust_chg:.1f}%")

# Main chart
st.plotly_chart(px.line(df, x='date', y='revenue', color='region'), use_container_width=True)

# Data table
st.dataframe(df, use_container_width=True, hide_index=True)
```

### 8.2 Caching for Performance
```python
@st.cache_data(ttl=3600)  # 1 hour cache
def load_and_process_data():
    return pd.read_csv("sales.csv").groupby('region')['revenue'].sum()
```

### 8.3 Multi-Page Apps
```
pages/
  ├── 1_📈_Executive_Summary.py
  ├── 2_🔍_Regional_Analysis.py
  └── 3_📋_Raw_Data.py
```

---

## 9. TABLEAU & POWER BI — ENTERPRISE TOOLS

### 9.1 Tableau Quick Reference
```tableau
-- Calculated Field
[Revenue] / [Quantity]  →  [Revenue per Unit]
RUNNING_SUM(SUM([Revenue]))  →  Cumulative Revenue

-- LOD Expression (Level of Detail)
{ FIXED [Customer ID] : SUM([Revenue]) }  →  Lifetime value per customer
{ INCLUDE [Product Category] : AVG([Revenue]) }  →  Category avg, detail at row level

-- Parameters for interactivity
[Select Measure] = "Revenue" → Use in calculated fields to switch metrics

-- Sets
[Revenue] > { FIXED : PERCENTILE([Revenue], 0.9) }  →  Top 10% flag
```

### 9.2 Power BI DAX Quick Reference
```dax
-- Measure
Total Revenue = SUM(fact_orders[revenue])

-- YoY Growth
Revenue YoY = 
VAR Current = SUM(fact_orders[revenue])
VAR Prior = CALCULATE(SUM(fact_orders[revenue]), SAMEPERIODLASTYEAR(dim_date[date]))
RETURN DIVIDE(Current - Prior, Prior)

-- Running Total
Running Revenue = 
CALCULATE(
    SUM(fact_orders[revenue]),
    FILTER(
        ALL(dim_date),
        dim_date[date] <= MAX(dim_date[date])
    )
)
```

### 9.3 Power BI + Microsoft Fabric
- **Fabric** provides end-to-end analytics: data movement, lakehouse, data engineering, real-time analytics, BI
- Power BI Premium integrates with Fabric's unified capacity model
- Use **Direct Lake** mode — query data in Fabric OneLake without importing

---

## 10. STORYTELLING WITH DATA

### 10.1 The Structure of a Data Story
```
1. HOOK: Start with a surprising statistic or question
   "We lost 23% of customers in their second month. Why?"

2. CONTEXT: Set the scene with baseline numbers
   "Over the past 12 months, we acquired 10,000 customers..."

3. EXPLORATION: Show the evidence, one insight at a time
   "Breaking it down by acquisition channel: organic customers
   retention is 15 points higher than paid."

4. REVELATION: The key finding
   "Paid social customers who receive a follow-up email within
   24 hours have 40% higher 60-day retention."

5. CALL TO ACTION: What should be done
   "→ Implement automated 24h follow-up for paid social cohort"
```

### 10.2 Annotations on Charts
```python
ax.annotate('Campaign launch',
    xy=pd.Timestamp('2024-03-15'), xytext=pd.Timestamp('2024-02-20'),
    fontsize=10, fontweight='medium',
    arrowprops=dict(arrowstyle='->', color='#888', lw=1.5),
    bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFFACD', edgecolor='#DDD'))

ax.text(0.02, 0.98, 'Campaign launched\nMarch 2024',
    transform=ax.transAxes, fontsize=9, va='top',
    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
```

### 10.3 Animation Best Practices
- Use animation to show **change over time** — not for static comparison
- Keep transitions under 500ms — slow = annoying
- Pause on important frames for discussion

---

## 11. SPECIALIZED CHART TYPES

### 11.1 Pareto Chart (80/20 Analysis)
```python
# Sort descending, compute cumulative %
df_sorted = df.sort_values('complaints', ascending=False).reset_index(drop=True)
df_sorted['cumulative'] = df_sorted['complaints'].cumsum() / df_sorted['complaints'].sum() * 100

fig, ax1 = plt.subplots()
ax1.bar(df_sorted['category'], df_sorted['complaints'], color='#4E79A7')
ax2 = ax1.twinx()
ax2.plot(df_sorted['category'], df_sorted['cumulative'], color='#E15759', marker='o', linewidth=2)
ax2.axhline(80, color='#888', linestyle='--', label='80% line')
```

### 11.2 Waterfall Chart
```python
# Shows incremental contribution to a total
import plotly.graph_objects as go
fig = go.Figure(go.Waterfall(
    name="Revenue Bridge",
    x=['Start', 'New Business', 'Expansion', 'Churn', 'Contraction', 'End'],
    y=[10, 3, 2, -1.5, -0.5, 13],
    measure=['absolute', 'relative', 'relative', 'relative', 'relative', 'absolute'],
    connector={"line": {"color": "#888"}},
    increasing={"marker": {"color": "#59A14F"}},
    decreasing={"marker": {"color": "#E15759"}}
))
fig.show()
```

### 11.3 Dot Plot (Better Than Bar for Rankings)
```python
# Horizontal dot plot — excellent for ranked lists
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(10, 6))
ax.hlines(df['product'], xmin=0, xmax=df['revenue'], color='#4E79A7', linewidth=3)
ax.scatter(df['revenue'], df['product'], color='#E15759', s=100, zorder=5)
# Perceptual accuracy is higher for horizontal position than bar length
```

---

## 12. BEST PRACTICES

1. **Remove chartjunk** — borders, gridlines, 3D effects, backgrounds — keep only what aids comprehension
2. **Always label axes** — include units and clear names; avoid auto-generated labels
3. **Sort by magnitude** in categorical charts — never alphabetical unless it's a time series
4. **Choose minimum effective difference** in color — don't make everything bold
5. **Use direct labeling** over legends when few categories (≤5)
6. **Context over decoration** — every visual element should help the reader understand the data
7. **Test for accessibility** — colorblind-safe palettes, sufficient contrast, readable fonts
8. **Export at 2-3x display resolution** — 150+ dpi for web, 300+ dpi for print
9. **Title last** — write title after building the chart so it reflects what the data actually shows

---

*Last updated: 2026-04-22 | Agent: Data-Analyst | Context: Visualization, Tableau, Power BI, Streamlit, storytelling*
