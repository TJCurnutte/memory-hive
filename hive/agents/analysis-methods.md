# Data Analysis Methods — Modern Approaches

## Statistical Methods

### Descriptive Statistics
- **Central tendency**: mean, median, mode — know when each applies
- **Spread**: variance, standard deviation, IQR — watch for outliers skewing mean
- **Shape**: skewness, kurtosis — understand distribution tails

### Inferential Statistics
- **Hypothesis testing**: p-values, t-tests, chi-square, ANOVA — always check assumptions
- **Confidence intervals**: prefer over p-values when communicating uncertainty
- **Bayesian inference**: updating beliefs with evidence — useful when data is sparse

### Regression & Modeling
- **Linear regression**: start here, check assumptions (linearity, homoscedasticity, normality)
- **Logistic regression**: binary outcomes, interpret odds ratios
- **Regularization**: Ridge/Lasso when you have many features or multicollinearity
- **Tree-based models**: Random Forest, XGBoost — handle non-linearity well, less feature engineering needed

### Time Series
- **Decomposition**: trend, seasonality, residuals
- **ARIMA/SARIMA**: classical approach, requires stationarity
- **Prophet**: good for business metrics with strong seasonality
- **Exponential smoothing**: Holt-Winters for trend + seasonality

## Visualization Best Practices

### Choosing the Right Chart
| Data Type | Best Chart |
|-----------|------------|
| Categorical comparisons | Bar chart |
| Part-to-whole | Pie chart (avoid if >5 segments), stacked bar |
| Trends over time | Line chart |
| Distribution | Histogram, box plot, violin plot |
| Correlation | Scatter plot, heatmap |
| Two numeric variables | Scatter plot |

### Design Principles
- **Maximize data-ink ratio**: remove chartjunk, gridlines, 3D effects
- **Use color purposefully**: sequential for magnitude, diverging for above/below基准
- **Label directly**: avoid legends when possible, annotate directly
- **Show uncertainty**: error bars, confidence bands, distribution viz
- **Start Y-axis at zero**: unless the data genuinely requires it (log scales, bounded metrics)
- **Order meaningfully**: alphabetically is rarely the best choice — order by value

### Common Pitfalls
- **Simpson's paradox**: aggregated data can reverse individual trends
- **Correlation ≠ causation**: always flag when presenting correlations
- **Overfitting**: model fits training data but fails on new data
- **Selection bias**: non-random samples skew results
- **Survivorship bias**: only looking at what's still present
- **Base rate fallacy**: ignoring how common/rare the outcome is
- **Multiple comparisons**: more tests = more false positives, use corrections

## Data Quality Checks
1. **Completeness**: % missing, pattern of missingness (MCAR, MAR, MNAR)
2. **Consistency**: duplicate rows, conflicting values, invalid ranges
3. **Currency**: data refresh lag, backfill patterns
4. **Granularity**: right level for the question (daily vs monthly aggregates)

## Exploratory Data Analysis Checklist
- [ ] Shape and size of dataset
- [ ] Data types are correct
- [ ] Summary statistics for numeric columns
- [ ] Value counts for categorical columns
- [ ] Missing data pattern and extent
- [ ] Outliers — are they errors or real signal?
- [ ] Correlations between variables
- [ ] Segmentations by key categorical variables

## Tools
- **Python**: pandas, scipy, statsmodels, scikit-learn
- **R**: tidyverse, caret, ggplot2
- **BI**: Tableau, Looker, Metabase, Grafana
- **Statistical rigor**: always report effect size, confidence intervals, sample size

---

*Auto-generated: 2026-04-22*
