---
name: api-service-integration
description: >-
  Provides architectural standards and verification procedures for the REST API service (FastAPI),
  database audit logging (PostgreSQL), explainable frontend components (React/TypeScript),
  and dynamic parameter sensitivity and reconfiguration testing.
---

# API Service Integration & System Verification

Use this skill when developing, testing, or verifying the backend API, persistence layer, interactive frontend components, and live parameter reconfigurability of the SMS spam detection system.

## Core Technical Criteria & Specifications

### 1. REST API Contract & Resilience (FastAPI, Port 8090)
- **Prediction Endpoint (`POST /predict`):**
  - Accepts JSON payload: `{"text": "string"}`.
  - Returns classification label (`"ham"` | `"spam"`), calibrated probability scores (`spam_probability`, `ham_probability`), risk level (`LOW`, `MEDIUM`, `HIGH`), and response latency (ms).
- **Batch Processing (`POST /predict/batch`):**
  - Accepts array of text strings or CSV file upload.
  - Returns structured array of predictions with aggregate summary statistics.
- **Explainability Trace (`POST /nlp/debug`):**
  - Accepts text string and returns step-by-step transformation states: normalized text, tokens, filtered tokens, lemmas/stems, and active TF-IDF feature weights.
- **Metrics Endpoint (`GET /metrics`):**
  - Returns JSON payload containing holdout test metrics for production and benchmark models (Accuracy, Precision, Recall, F1, Confusion Matrix).
- **Audit History (`GET /history`):**
  - Returns paginated list of recent inference records persisted in the database.
- **Health Check (`GET /health`):**
  - Returns service status (`UP`), active model version, and database connectivity state.
- **Input Validation & Error Handling:**
  - Enforce strict Pydantic v2 schemas: reject empty text, whitespace-only input, or text exceeding reasonable length limits (e.g., > 1000 characters) with HTTP 422 Unprocessable Entity and actionable error messages.

### 2. Persistence & Audit Logging (PostgreSQL, Port 5439)
- Maintain an audit table (`predictions`) recording:
  - Timestamp, input text hash/content, prediction outcome, spam probability, processing latency, and client metadata.
- Ensure database connections use connection pooling and handle connection loss gracefully without crashing the inference API.

### 3. Frontend Architecture & Explainable UI (React + TypeScript, Port 3090)
- **Interactive Classifier Card:**
  - Real-time text input with instantaneous classification response and dynamic color-coded risk meter (Green: Ham, Red: Phishing/Spam).
- **Step-by-Step NLP Visual Inspector:**
  - Visual timeline or tabbed panel rendering each transformation stage from raw text to TF-IDF vector weights, allowing users and developers to inspect feature extraction mechanics.
- **Model Performance Dashboard:**
  - Interactive confusion matrix visualization and comparative metrics cards (Naive Bayes vs. Logistic Regression).
- **Persistent History Table:**
  - Tabular view of past classified messages fetched from `/history`.

### 4. Dynamic Parameter Sensitivity & Live Reconfiguration
Verify that the architecture supports modular adjustments without breaking service contracts:
- **Lexicon Adjustment:** Adding or removing a keyword in `src/nlp/stopwords_es.py` cleanly updates vectorization during retraining.
- **N-Gram Modification:** Switching feature extraction between unigrams and bigrams (`ngram_range=(1, 2)`) propagates predictably to the serialized pipeline.
- **Model Swapping:** Changing the production estimator (e.g., toggling between Naive Bayes and Logistic Regression) requires only re-running the training script and reloading the model in FastAPI.
- **Threshold Sensitivity:** Adjusting the classification decision threshold (e.g., lowering spam threshold from 0.50 to 0.35 to increase recall on suspicious messages) updates the risk classification cleanly.
- **API Schema Adaptation:** Modifying input validation constraints in Pydantic schemas (e.g., adding minimum character length) accurately returns HTTP 422 validation errors to the frontend.

### 5. Automated Verification & Test Suite
- **API Unit Tests (`tests/test_api.py`):**
  - Validate all endpoints against valid, invalid, and edge-case inputs using `pytest` and `httpx.AsyncClient`.
- **Pipeline Unit Tests (`tests/test_pipeline.py`):**
  - Verify deterministic output for known SMS strings, ensuring regex masking and preprocessing behave identically.

