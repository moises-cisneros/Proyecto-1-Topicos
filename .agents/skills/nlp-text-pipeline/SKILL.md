---
name: nlp-text-pipeline
description: >-
  Provides implementation, tuning, and verification standards for the Spanish NLP text
  preprocessing pipeline, including regex masking, tokenization, contextual stopwords,
  morphological normalization (stemming vs lemmatization), n-grams, TF-IDF vectorization,
  and atomic scikit-learn Pipeline serialization.
---

# NLP Text Processing Pipeline

Use this skill when developing, refactoring, or verifying text preprocessing components, tokenization routines, feature extractors, and scikit-learn pipeline serialization for SMS text classification.

## Core Technical Criteria & Specifications

### 1. Lexical Normalization & Entity Masking
- **Lowercasing & Diacritics:** Case-fold text uniformly while retaining standard Spanish characters (`ñ`, accented vowels) unless intentionally stripped by the vectorizer.
- **Security & Phishing Vector Masking:** Replace variable entities with canonical synthetic tokens before tokenization:
  - URLs / Web domains: `TOKEN_URL` (pattern: `https?://\S+|www\.\S+|\b[a-zA-Z0-9.-]+\.[a-z]{2,}(?:/\S*)?`)
  - Phone Numbers: `TOKEN_TEL` (pattern: `\+?\d{1,3}?[-.\s]?\(?\d{1,4}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}`)
  - Financial amounts / Numerics: `TOKEN_NUM` (pattern: `\b\d+([.,]\d+)?\b|\$\d+([.,]\d+)?`)
- **Punctuation & Noise:** Strip non-informative symbols while keeping punctuation marks that demarcate sentence or token boundaries.

### 2. Tokenization
- Ensure word-boundary tokenization cleanly separates lexical units without fragmenting synthetic tokens (`TOKEN_URL`, `TOKEN_TEL`, `TOKEN_NUM`).
- Retain whitespace-separated structure for subsequent sequence and n-gram analysis.

### 3. Context-Aware Stop Words Filtering
- **Base Lexicon:** Spanish stopword dictionary (e.g., `nltk.corpus.stopwords.words('spanish')`).
- **Urgency & Polarity Whitelist:** Explicitly preserve terms essential for spam/phishing and sentiment discrimination:
  - Negations: `"no"`, `"ni"`, `"tampoco"`, `"sin"`.
  - Urgency & Call-to-Action Triggers: `"urgente"`, `"inmediato"`, `"aviso"`, `"bloqueo"`, `"ya"`, `"ahora"`, `"cuenta"`.
- Document any additions or exclusions with empirical justification.

### 4. Morphological Normalization (Stemming vs. Lemmatization)
- **Stemming Implementation:** Fast algorithmic suffix stripping via `nltk.stem.SnowballStemmer('spanish')`.
- **Lemmatization Implementation:** Part-of-speech-aware canonical reduction via `spacy` (`es_core_news_sm`).
- **Benchmarking Requirement:** Compare both approaches empirically:
  - Measure inference latency (milliseconds per batch).
  - Measure impact on downstream classification metrics ($F_1$-Score).
  - Select and document the production standard based on the accuracy vs. throughput tradeoff.

### 5. N-Gram Feature Extraction
- Support configurable token grouping:
  - Unigrams: `ngram_range=(1, 1)`.
  - Unigrams + Bigrams: `ngram_range=(1, 2)`.
- Bigrams are critical for capturing high-probability phishing collocations (*"cuenta bloqueada"*, *"haga clic"*, *"premio ganado"*, *"verifique datos"*).

### 6. TF-IDF Vectorization & Atomic Serialization
- Configure `TfidfVectorizer` with controlled vocabulary hyperparameters:
  - `max_features`: Bound vocabulary between 3,000 and 5,000 to prevent overfitting and high memory footprint.
  - `min_df`: Trim low-frequency idiosyncratic terms (typically 2 to 3 occurrences).
  - `sublinear_tf=True`: Apply logarithmic term frequency scaling ($1 + \log(\text{tf})$) to dampen repetitive spam keyword stuffing.
- **Architectural Boundary:** Bundle all preprocessing transformations and the vectorizer inside a single `sklearn.pipeline.Pipeline`.
- Serialize the trained artifact to `.joblib`. The backend inference engine must load this artifact directly and must never duplicate preprocessing logic.

### 7. Step-by-Step Inspection Trace
- The pipeline module must expose an inspection method that yields intermediate transformation states for any input string:
  1. Raw input text
  2. Regex-normalized text with masked tokens
  3. Extracted tokens
  4. Tokens after stopword filtering
  5. Lemmatized / stemmed tokens
  6. Non-zero TF-IDF feature weights

