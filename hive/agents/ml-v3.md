# Machine Learning Fundamentals (v3)

**Author:** Data-Analyst Agent  
**Date:** 2026-04-22  
**Topics:** Model Selection, Feature Engineering, Evaluation Metrics, Overfitting/Underfitting, Ensemble Methods, XGBoost/LightGBM

---

## 1. ML Model Selection: Classification vs. Regression vs. Clustering

Choosing the right ML approach starts with understanding your problem type. This is the most foundational decision in any ML project, and choosing incorrectly leads to wasted effort and poor results.

### 1.1 Classification

Classification is a **supervised learning** task where the goal is to predict a categorical label. The model learns from labeled training data and assigns new observations to predefined classes.

**Types of Classification:**
- **Binary Classification:** Two classes only (spam/not spam, fraud/legit, churn/no churn)
- **Multi-class Classification:** More than two classes (image recognition — cat/dog/horse, sentiment — positive/neutral/negative)
- **Multi-label Classification:** An instance can belong to multiple classes simultaneously (a news article tagged with politics AND economy)

**Common Algorithms:**
- Logistic Regression (linear decision boundary, interpretable)
- Decision Trees & Random Forests
- Support Vector Machines (SVM)
- K-Nearest Neighbors (KNN)
- Naive Bayes (probabilistic, fast, works well with text)
- Neural Networks (deep learning for complex patterns)

**Real-World Examples:**
- Credit card fraud detection (binary: fraudulent transaction or not)
- Medical diagnosis (multi-class: types of disease)
- Email spam filtering (binary classification)
- Customer churn prediction (binary classification)

### 1.2 Regression

Regression is also a **supervised learning** task, but the target variable is continuous rather than categorical. The goal is to predict a numeric value.

**Types of Regression:**
- **Linear Regression:** Simple relationship between independent and dependent variables (y = mx + c)
- **Polynomial Regression:** Captures non-linear relationships by adding polynomial terms
- **Ridge/Lasso Regression:** Linear regression with regularization (L2 for Ridge, L1 for Lasso) to prevent overfitting
- **Support Vector Regression (SVR):** Regression using support vector machine principles
- **Quantile Regression:** Predicts not just the mean but quantiles (useful for understanding distribution)

**Common Algorithms:**
- Linear Regression (OLS)
- Polynomial Regression
- Ridge, Lasso, ElasticNet
- Decision Tree Regression
- Random Forest Regression
- Gradient Boosting Regression

**Real-World Examples:**
- House price prediction (predicting exact dollar value)
- Sales forecasting (predicting next quarter's revenue)
- Demand forecasting (units sold next month)
- Risk scoring (predicting expected loss amount)

### 1.3 Clustering

Clustering is an **unsupervised learning** task where the goal is to group similar data points together without predefined labels. The model discovers natural patterns and groupings in the data.

**Key Differences from Supervised Approaches:**
- No labeled training data required
- The algorithm discovers structure autonomously
- Number of clusters is often a hyperparameter to tune
- Results can be subjective — requires domain expertise to interpret

**Common Algorithms:**
- **K-Means:** Partitions data into K clusters, each with a centroid. Works well for spherical, evenly-sized clusters. Sensitive to initialization and outliers.
- **Hierarchical Clustering:** Builds a dendrogram (tree) of clusters. Can be agglomerative (bottom-up) or divisive (top-down). No need to predefine K.
- **DBSCAN (Density-Based Spatial Clustering of Applications with Noise):** Groups points in dense regions. Automatically detects outliers as noise. Works well for arbitrary-shaped clusters.
- **Gaussian Mixture Models (GMM):** Probabilistic model assuming data is generated from a mixture of Gaussian distributions. Provides soft cluster assignments (probability of belonging to each cluster).
- **K-Medoids (PAM):** Similar to K-means but uses actual data points as cluster centers (medoids), more robust to outliers.

**Real-World Examples:**
- Customer segmentation (grouping customers by behavior for targeted marketing)
- Anomaly detection (cluster normal traffic patterns, flag deviations)
- Image compression (cluster similar colors together)
- Document organization (grouping news articles by topic)

### 1.4 Choosing the Right Approach

| Problem Type | Supervised/Unsupervised | Target Variable | Examples |
|---|---|---|---|
| Classification | Supervised | Categorical (discrete labels) | Spam detection, disease diagnosis |
| Regression | Supervised | Continuous (numeric) | Price prediction, forecasting |
| Clustering | Unsupervised | None (groups discovered) | Customer segmentation, anomaly detection |

**Decision Framework:**
1. Do you have labeled data? → Supervised (Classification/Regression)
2. Is the target a category or a number? → Classification vs. Regression
3. No labels? → Unsupervised (likely Clustering)
4. Do you need to discover hidden groups? → Clustering
5. Is interpretability critical? → Logistic Regression or Decision Trees first

---

## 2. Feature Engineering

Feature engineering is the process of transforming raw data into features that better represent the underlying problem, improving model performance. It is widely considered one of the most important factors in winning ML competitions and building production-grade models.

As noted in ML research, "feature engineering significantly enhances their predictive accuracy and decision-making capability" and is a preprocessing step in supervised machine learning and statistical modeling.

### 2.1 Feature Creation

Creating new features from existing ones is one of the highest-leverage activities in ML:

**Interaction Features:** Combine two or more features through operations:
- Multiplication: `revenue_per_user = total_revenue * num_users`
- Division: `conversion_rate = purchases / visitors`
- Ratios: `debt_to_income = debt / income`

**Aggregation Features:** Summarize group-level statistics:
- Rolling averages (last 7 days, last 30 days)
- Counts and sums per group
- Min, max, standard deviation per group

**Temporal Features:** Extract time-based signals:
- Day of week, hour of day, month, quarter, year
- Is weekend, is holiday, is business hours
- Time since last event, time between events

### 2.2 Encoding Categorical Variables

Many ML algorithms require numeric input, so categorical variables must be encoded:

**Label Encoding:** Maps each category to an integer (e.g., Low=0, Medium=1, High=2). Simple but imposes an arbitrary ordinal relationship that may not exist in the data. Use for tree-based models.

**One-Hot Encoding (OHE):** Creates binary columns for each category. Great for non-ordinal categories with few values. Risk of high dimensionality with many categories.

**Target Encoding:** Replaces categories with the mean of the target variable for that category. Particularly powerful but requires careful handling to prevent data leakage (use cross-validation or regularization).

**Ordinal Encoding:** Preserves ordering for categories with a natural order (e.g., education level: High School < Bachelor's < Master's < PhD).

### 2.3 Feature Scaling

Scale features to comparable ranges so that algorithms perform optimally:

**StandardScaler (Z-score normalization):** Transforms features to have mean=0 and std=1. Best for algorithms sensitive to feature magnitude (SVM, KNN, Neural Networks, Linear Regression without regularization).

```python
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
```

**MinMaxScaler:** Scales features to a [0, 1] range. Preserves original distribution shape but sensitive to outliers.

**RobustScaler:** Uses median and IQR instead of mean and standard deviation, making it robust to outliers.

**Log Transformation:** Compresses large values and reduces skewness in distributions. Useful for right-skewed data (e.g., income, population).

**Power Transformation (Box-Cox, Yeo-Johnson):** Stabilizes variance and makes data more normally distributed.

### 2.4 Dimensionality Reduction

When features are too many or correlated, reduce dimensionality:

**Principal Component Analysis (PCA):** Projects data onto the axes of maximum variance. Unsupervised, linear. Good for noise reduction and speeding up training.

**Linear Discriminant Analysis (LDA):** Supervised dimensionality reduction that maximizes class separability. Can be used for classification as well.

**t-SNE:** Non-linear technique for visualization in 2D/3D. Excellent for exploring high-dimensional data but not suitable as a general preprocessing step (stochastic, no inverse mapping).

**UMAP:** Faster than t-SNE, preserves more global structure, and can be used for general dimensionality reduction.

### 2.5 Handling Missing Values

Missing data is a universal challenge. Strategies include:
- **Deletion:** Row deletion (listwise) or column deletion — only when missingness is minimal and random
- **Mean/Median Imputation:** Simple but reduces variance
- **KNN Imputation:** Uses K-nearest neighbors to impute based on similar rows
- **Iterative Imputation (MICE):** Models each feature with missing values as a function of other features iteratively

### 2.6 Feature Selection

Selecting only the most relevant features prevents overfitting and reduces training time:

**Filter Methods:** Use statistical tests (chi-square, mutual information, correlation) to score features before model training. Fast but ignores feature interactions.

**Wrapper Methods:** Use the model itself to evaluate feature subsets (Recursive Feature Elimination, Forward Selection). More accurate but computationally expensive.

**Embedded Methods:** Feature selection happens inside the model training process (Lasso regularization, tree-based feature importance). Most efficient for production use.

---

## 3. Model Evaluation Metrics

Choosing the right evaluation metric is critical — optimizing for the wrong metric leads to models that are technically "good" but practically useless.

### 3.1 Classification Metrics

**Accuracy:** (TP + TN) / Total. The proportion of correct predictions. Misleading for imbalanced datasets (e.g., 99% negative class → always predicting negative gives 99% accuracy).

**Precision:** TP / (TP + FP). Of all positive predictions, how many are actually positive? Critical when false positives are costly (e.g., spam filtering — don't block legitimate emails).

**Recall (Sensitivity):** TP / (TP + FN). Of all actual positives, how many did we catch? Critical when false negatives are costly (e.g., cancer screening — don't miss actual cancer cases).

**F1 Score:** Harmonic mean of precision and recall = 2 * (Precision * Recall) / (Precision + Recall). Balances precision and recall when they're both important.

**ROC-AUC (Receiver Operating Characteristic — Area Under Curve):** Plots True Positive Rate vs. False Positive Rate at various thresholds. AUC = 1.0 is perfect, 0.5 is random. Threshold-independent, making it robust for comparing models.

**Log Loss (Binary Cross-Entropy):** Measures the quality of probabilistic predictions. Penalizes confident wrong predictions heavily. Used in logistic regression and neural networks.

**Confusion Matrix:** A table layout showing TP, TN, FP, FN. The foundation for understanding all other classification metrics.

### 3.2 Regression Metrics

**Mean Absolute Error (MAE):** Average absolute difference between predicted and actual values. Interpretable in same units as target. Treats all errors equally, not sensitive to outliers.

**Mean Squared Error (MSE):** Average squared difference. Penalizes large errors more than small ones (squaring amplifies large deviations). Commonly used but sensitive to outliers.

**Root Mean Squared Error (RMSE):** √MSE. Interpretable in same units as target. Most commonly reported regression metric.

**R² (Coefficient of Determination):** Proportion of variance explained by the model. Range: 0 to 1 (can be negative for bad models). R² = 0.8 means the model explains 80% of the variance.

**Adjusted R²:** Penalizes adding features that don't improve explanatory power. Used to compare models with different numbers of features.

**Mean Absolute Percentage Error (MAPE):** Relative error expressed as a percentage. Interpretable but can be undefined when actual values are zero.

### 3.3 Clustering Metrics

**Silhouette Score:** Measures how similar an object is to its own cluster vs. other clusters. Range: -1 to 1. Higher is better. A score near 1 means clusters are well-separated.

```python
from sklearn.metrics import silhouette_score
score = silhouette_score(X, cluster_labels)
```

**Davies-Bouldin Index:** Average similarity between each cluster and its most similar cluster. Lower is better (tighter, more separated clusters).

**Calinski-Harabasz Index:** Ratio of between-cluster dispersion to within-cluster dispersion. Higher is better.

**Inertia (K-Means):** Sum of squared distances from points to their cluster centroids. Used in the "elbow method" to choose K. Declines as K increases — find the elbow.

### 3.4 Cross-Validation

Cross-validation is the gold standard for reliable model evaluation:

**K-Fold Cross-Validation:** Data is split into K folds. Train on K-1 folds, test on 1 fold. Repeat K times. Average performance across folds.

**Stratified K-Fold:** Preserves class distribution across folds. Essential for imbalanced classification.

**Leave-One-Out (LOO):** K = n (one sample per fold). Expensive but maximally data-efficient for small datasets.

**Time Series Split:** For temporal data, use forward-chaining splits (train on past, test on future) to avoid data leakage.

---

## 4. Overfitting vs. Underfitting

Overfitting and underfitting are the two fundamental failure modes in machine learning. Understanding and diagnosing them is core to building models that generalize.

### 4.1 Overfitting

**What it is:** The model learns the training data too well — including its noise and random fluctuations — and fails to generalize to new, unseen data. The model has **high variance** and **low bias**.

**Signs:**
- Training accuracy is very high, but validation/test accuracy is significantly lower
- The validation loss curve starts increasing while training loss continues to decrease
- The model performs well on known data but poorly on held-out data

**Causes:**
- Model is too complex (too many features, too many parameters relative to training data)
- Training data is too small or unrepresentative
- Model is trained too long (too many epochs in neural networks)
- No regularization applied

**Solutions:**

**Regularization:** Adds a penalty term to the loss function to discourage large weights:
- **L1 (Lasso):** Adds sum of absolute weights. Tends to produce sparse models (feature selection built in).
- **L2 (Ridge):** Adds sum of squared weights. Shrinks weights toward zero but rarely to exactly zero.

**Cross-Validation:** Use validation performance to decide when to stop training or which hyperparameters to choose.

**Early Stopping:** Monitor validation loss and stop training when it stops improving.

**Dropout (Neural Networks):** Randomly drop neurons during training to prevent co-adaptation.

**Pruning (Decision Trees):** Limit tree depth or require minimum samples per leaf.

**Data Augmentation:** Increase effective training set size through transformations (rotations, flips for images; SMOTE for tabular data).

**Ensemble Methods:** Combine multiple models to reduce variance (see Section 5).

### 4.2 Underfitting

**What it is:** The model is too simple to capture the underlying patterns in the data. The model has **high bias** and **low variance** and fails on both training and test data.

**Signs:**
- Both training and validation accuracy are low
- Training loss is still decreasing and hasn't plateaued
- The model makes obvious errors that a human would not

**Causes:**
- Model is too simple for the complexity of the problem
- Not enough features (insufficient feature engineering)
- Model is under-trained
- Over-regularization (penalty too strong)

**Solutions:**

**Use a More Complex Model:** Switch from linear to polynomial, or from shallow to deep neural network.

**Add More Features:** Engineer new features, interaction terms, or polynomial features.

**Reduce Regularization:** If regularization terms are too strong, the model can't express the true relationship.

**Train Longer:** For neural networks, ensure sufficient training epochs.

**Ensemble with Diverse Models:** Combine diverse weak learners to boost overall performance.

### 4.3 The Bias-Variance Tradeoff

This is the fundamental tension in ML:

- **High Bias (Underfitting):** Model assumptions are too restrictive. It consistently gets things wrong in the same direction (systematic error).
- **High Variance (Overfitting):** Model is overly sensitive to training data. Small changes in training data cause large changes in predictions.

The total error = Bias² + Variance + Irreducible Error.

The goal is to find the right level of model complexity that minimizes total error on unseen data. This is why validation sets and cross-validation are essential.

---

## 5. Ensemble Methods

Ensemble methods combine multiple models to produce a better predictive performance than any individual model alone. They are among the most powerful techniques in applied ML.

### 5.1 Bagging (Bootstrap Aggregating)

**Concept:** Train multiple models independently on different bootstrap samples (random samples with replacement) of the training data, then aggregate their predictions.

**Key Benefits:**
- Reduces variance without increasing bias
- Parallelizable (each model trains independently)
- Works well with high-variance models (e.g., decision trees)

**Random Forest:** The most popular bagging method. Builds multiple decision trees on bootstrap samples. At each split, only a random subset of features is considered (adding decorrelation). Final prediction is majority vote (classification) or average (regression).

**Key hyperparameters:**
- `n_estimators`: Number of trees (more trees = less variance, but diminishing returns)
- `max_features`: Number of features to consider per split
- `max_depth`: Tree depth limit
- `min_samples_split`: Minimum samples to split a node

**Out-of-Bag (OOB) Error:** Since each tree trains on ~63% of unique samples, the remaining ~37% can be used as a built-in validation set. No separate validation set needed.

### 5.2 Boosting

**Concept:** Train models sequentially, where each new model focuses on correcting the errors of the previous ones. Weak learners are combined into a strong learner.

**Key Benefits:**
- Often achieves state-of-the-art performance
- Handles imbalanced data well
- Built-in feature selection

**AdaBoost (Adaptive Boosting):** Weights each training sample. Misclassified samples get higher weights in the next round. Simple but less commonly used in production now.

**Gradient Boosting:** Trains each new model to predict the residual (gradient) of the loss function from the previous model. Minimizes a differentiable loss function directly.

**Key difference from bagging:** Sequential (not parallel), each model depends on the previous one.

### 5.3 Stacking (Stacked Generalization)

**Concept:** Train multiple diverse models (base learners), then train a meta-learner (second-level model) on their predictions.

**Architecture:**
1. Level 0: Train multiple diverse base models (e.g., logistic regression, random forest, SVM, XGBoost)
2. Level 1: Use the predictions from Level 0 models as features for the meta-learner
3. The meta-learner learns the optimal way to combine base model predictions

**Best Practices:**
- Use cross-validation when generating base model predictions for the meta-learner to prevent data leakage
- Choose base models that are diverse (different algorithms, different feature sets)
- Keep the meta-learner simple (logistic regression or linear regression) to avoid overfitting

### 5.4 Voting Classifiers

**Hard Voting:** Multiple models vote, majority wins.

**Soft Voting:** Average predicted probabilities, pick the class with highest average probability. Better when models can output probabilities.

```python
from sklearn.ensemble import VotingClassifier
voting_clf = VotingClassifier(
    estimators=[('rf', rf_model), ('xgb', xgb_model), ('lr', lr_model)],
    voting='soft'
)
```

---

## 6. XGBoost and LightGBM

### 6.1 XGBoost (eXtreme Gradient Boosting)

XGBoost is an open-source library providing a regularizing gradient boosting framework. Originally created by Tianqi Chen at the University of Washington in 2014 as part of the DMLC group, XGBoost quickly became the dominant algorithm in ML competitions.

**Key Characteristics:**
- Written in C++, with APIs for Python, R, Java, Julia, Scala, Perl
- Compatible with distributed frameworks: Apache Hadoop, Spark, Flink, Dask
- **Regularized by default:** XGBoost adds L1 and L2 regularization directly to the objective function, making it more resistant to overfitting than standard gradient boosting
- Handles sparse/missing data natively
- Column and row sampling for memory efficiency

**Objective Functions:**
XGBoost supports multiple loss functions:
- `reg:squarederror` — regression with squared error
- `reg:logistic` — binary classification with logistic loss
- `binary:logistic` — binary classification (outputs probabilities)
- `multi:softprob` — multi-class classification

**Key Hyperparameters:**

| Parameter | Default | Description |
|---|---|---|
| `learning_rate` (eta) | 0.3 | Step size shrinkage. Lower = slower learning, more trees, less overfitting |
| `max_depth` | 6 | Maximum tree depth. Higher = more complex trees, risk of overfitting |
| `min_child_weight` | 1 | Minimum sum of instance weight needed in a child. Controls overfitting |
| `subsample` | 1.0 | Fraction of rows sampled per tree (0.5-0.8 is typical) |
| `colsample_bytree` | 1.0 | Fraction of columns sampled per tree |
| `n_estimators` | 100 | Number of boosting rounds (trees) |
| `reg_alpha` | 0 | L1 regularization term |
| `reg_lambda` | 1.0 | L2 regularization term |
| `gamma` | 0 | Minimum loss reduction required to make a split |

**Early Stopping:**
```python
xgb_model.fit(X_train, y_train, 
              eval_set=[(X_val, y_val)],
              early_stopping_rounds=10)
```
Stops training when validation performance doesn't improve for N rounds.

### 6.2 LightGBM

LightGBM (Light Gradient Boosting Machine) was developed by Microsoft Research and released in 2016. It is optimized for speed and memory efficiency and has become XGBoost's primary competitor.

**Key Differences from XGBoost:**

| Feature | XGBoost | LightGBM |
|---|---|---|
| Tree Growth Strategy | Level-wise (depth-first) | Leaf-wise (best-first) |
| Speed | Fast | **Faster** (often 10-50x faster on large datasets) |
| Memory Usage | Higher | **Lower** (uses histogram-based approach) |
| Handling Categorical Features | Needs encoding | Native categorical support |
| Big Data Performance | Good | Excellent (designed for large datasets) |
| Handling Sparse Data | Native | Native |

**Histogram-Based Splitting:** LightGBM groups continuous feature values into discrete bins (histograms). This reduces the number of split candidates from unique values to bin count, dramatically speeding up computation.

**Leaf-wise Growth:** LightGBM grows the tree by splitting at the leaf with the maximum delta loss (rather than level-wise). This can produce deeper trees faster, but may overfit on small datasets. Use `max_depth` parameter to constrain.

**Key Hyperparameters:**

| Parameter | Default | Description |
|---|---|---|
| `learning_rate` | 0.1 | Same as XGBoost |
| `num_leaves` | 31 | Maximum leaf nodes. Controls complexity (note: num_leaves ≈ 2^(max_depth-1) for XGBoost comparison) |
| `max_depth` | -1 | No limit by default |
| `min_child_samples` | 20 | Minimum data in a leaf (like XGBoost's `min_child_weight`) |
| `subsample` | 1.0 | Row sampling |
| `colsample_bytree` | 1.0 | Column sampling |
| `reg_alpha` | 0 | L1 regularization |
| `reg_lambda` | 0 | L2 regularization |
| `n_estimators` | 100 | Number of iterations |

**Categorical Feature Handling:**
```python
# LightGBM handles categorical features natively
lgb_train = lgb.Dataset(X_train, y_train, categorical_feature=['city', 'category'])
```
This avoids the need for one-hot encoding, reducing memory and speeding up training.

### 6.3 When to Use XGBoost vs. LightGBM

**Use XGBoost when:**
- You need the most robust, well-tested algorithm
- Your dataset is small to medium size
- Interpretability is important (XGBoost's feature importance is more widely understood)
- You're working in a regulated industry where well-documented algorithms are preferred

**Use LightGBM when:**
- You have very large datasets (millions of rows)
- Training speed is critical
- You have many categorical features
- You need to iterate quickly during experimentation
- You have real-time or near-real-time inference requirements

**Use CatBoost when:**
- You have many categorical features with high cardinality
- You want minimal feature engineering
- You value strong default hyperparameters
- You need built-in handling of missing values and overfitting prevention

---

## Summary: Key Takeaways

1. **Model Selection:** Start by understanding whether your problem is supervised (classification/regression) or unsupervised (clustering). Choose accordingly — this foundational decision drives everything else.

2. **Feature Engineering:** Often more impactful than model choice. Invest heavily in creating meaningful features — interaction terms, aggregations, temporal features, proper encoding, and scaling.

3. **Evaluation Metrics:** Match your metric to your business problem. Accuracy is misleading for imbalanced problems. Use ROC-AUC for ranking tasks. Use F1 when precision and recall both matter.

4. **Overfitting vs. Underfitting:** High training accuracy but low validation accuracy = overfitting (use regularization, more data, early stopping). Low accuracy on both = underfitting (use more complex model, more features, less regularization).

5. **Ensemble Methods:** Random Forests (bagging) reduce variance. Gradient Boosting (XGBoost/LightGBM) reduces bias. Stacking combines both approaches. Ensembles consistently win competitions and production deployments.

6. **XGBoost vs. LightGBM:** Both are go-to algorithms for structured/tabular data. XGBoost is the battle-tested standard. LightGBM wins on speed for large data. CatBoost is excellent for high-cardinality categoricals. For most tabular ML problems, trying all three and stacking them is the recommended approach.
