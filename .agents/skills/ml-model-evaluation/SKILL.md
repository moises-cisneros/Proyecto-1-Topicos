---
name: ml-model-evaluation
description: >-
  Provides implementation, validation, and benchmarking criteria for machine learning models,
  reproducible stratified partitioning, baseline comparison, cross-validated hyperparameter
  tuning, comprehensive evaluation metrics, and qualitative error analysis.
---

# Machine Learning Model Evaluation & Benchmarking

Use this skill when developing training pipelines, running model benchmarks, tuning hyperparameters, calculating evaluation metrics, or diagnosing classification errors.

## Core Technical Criteria & Specifications

### 1. Data Integrity & Stratified Partitioning
- **Exploratory Data Analysis (EDA):**
  - Verify class distributions (`ham` vs. `spam`) and report class imbalance ratios.
  - Profile text length distributions (character and token counts).
  - Extract top discriminant terms per class to confirm feature separation.
  - Verify zero unhandled missing values or unintended duplicates.
- **Stratified Partitioning:**
  - Execute strict 80/20 train/test partitioning: `train_test_split(stratify=y, test_size=0.2, random_state=42)`.
  - **Holdout Immutability:** The test set (`test.csv` or test split) must remain strictly isolated. Never tune hyperparameters or fit vectorizers on the test partition.

### 2. Model Selection & Comparative Architecture
Implement and compare three distinct modeling tiers:
- **Baseline Tier:** `DummyClassifier(strategy='most_frequent')` evaluated on the holdout test set to establish the minimum performance floor.
- **Production Classifier:** `MultinomialNB()` with Laplace smoothing parameter $\alpha$. Ideal for high-dimensional sparse TF-IDF text features.
- **Challenger Classifier:** `LogisticRegression(max_iter=1000, random_state=42)` with $L_2$ regularization parameter $C$. Provides calibrated class probabilities and interpretable linear decision boundaries.

### 3. Hyperparameter Tuning & Cross-Validation
- Perform hyperparameter optimization using 5-Fold Stratified Cross-Validation (`StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`) on the training partition only.
- Parameter spaces to evaluate:
  - Naive Bayes: $\alpha \in [0.01, 0.1, 0.5, 1.0, 2.0]$.
  - Logistic Regression: $C \in [0.01, 0.1, 1.0, 10.0, 50.0]$ and penalty formulations.
- Select the optimal estimator optimizing for macro $F_1$-score or spam class $F_1$-score.

### 4. Comprehensive Evaluation Metrics
Report the full spectrum of classification metrics on the holdout test set:
- **Confusion Matrix:** True Positives (TP), False Positives (FP), True Negatives (TN), False Negatives (FN).
- **Class-Level Metrics:** Precision, Recall, and $F_1$-Score for each class (`ham` and `spam`).
  - *Critical Criterion:* Monitor and minimize the **False Positive Rate** ($FP / (FP + TN)$) to prevent false alerts on legitimate user messages.
- **Aggregate Metrics:** Macro-averaged $F_1$-Score, Weighted $F_1$-Score, and Global Accuracy.
- **Tabular Comparison:** Generate a side-by-side comparative table summarizing Baseline vs. Naive Bayes vs. Logistic Regression.

### 5. Qualitative Error Analysis
- Programmatically extract misclassified samples from the test holdout:
  - At least 3 to 5 **False Positives** (legitimate messages flagged as spam).
  - At least 3 to 5 **False Negatives** (spam/phishing messages that evaded detection).
- Document a technical diagnosis for each failure category:
  - Sub-vocabulary gaps (slang, uncommon abbreviations, typos).
  - Deceptive phrasing (polite greetings concealing phishing intent).
  - Truncated or overly brief messages lacking sufficient TF-IDF signal.

### 6. Reproducible Training Pipeline
- Package the end-to-end training process into a single executable command (e.g., `python src/models/train.py`).
- The script must:
  1. Ingest raw datasets.
  2. Execute stratified partitioning with locked seeds (`random_state=42`).
  3. Fit the complete NLP vectorization and classification pipeline.
  4. Evaluate on holdout data and emit metrics artifacts (`metrics.json`).
  5. Serialize the ready-for-production model to `models/spam_detector_pipeline.joblib`.

