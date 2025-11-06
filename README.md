# Nano BM25

A minimal, from-scratch implementation of a BM25 search engine to rebuild and reinforce information retrieval fundamentals.

## Navigation

This repository is organized into three parts: a search engine, an explainer on rankings, and some reflections on the why of this repo.

1. **[README.md](README.md)** (this file) — How to run the repository
2. **[RANKING.md](RANKING.md)** — Deep dive into BM25 and ranking algorithms
3. **[REFLECTIONS.md](REFLECTIONS.md)** — The motivation and philosophical reflections behind this project

## Overview

This repo implements a complete text retrieval pipeline:
- Positional inverted index
- Multiple ranking algorithms (TF, IDF, TF-IDF, BM25)
- FastAPI-based HTTP endpoints
- Intentionally minimal dependencies to force understanding over abstraction

## Project Structure

```
engine/
├── indexer.py              # Document preprocessing and positional inverted index builder
├── query_processor.py      # Query preprocessing pipeline
├── stemmer.py             # Toy affix-based stemmer
├── bm25_ranker.py         # BM25 scoring implementation
└── tfidf_ranker.py        # TF-IDF scoring variants

main.py                    # FastAPI server with ranking endpoints
docs/docs.txt              # Toy corpus (one document per line)
index/positional_inverted_index.json  # Generated index artifact
stopwords/stopwords.txt    # Stop words list
```

## The Preprocessing Pipeline

**Document side (indexing):**
1. Preprocess: lowercase, strip, keep only word chars and `. , : ; ! ?`
2. Tokenize: split on whitespace, treat allowed punctuation as separate tokens
3. Remove stop-words from `stopwords/stopwords.txt`
4. Stem: crude affix stripper (intentionally simple to surface tradeoffs)
5. Build positional inverted index: `{ term: { doc_id: [positions...] } }`

**Query side:**
- Apply the same preprocessing pipeline
- Returns normalized terms ready for ranking

The positions enable phrase queries, proximity queries, and provide per-(term, doc) term frequency as `len(positions)` for BM25.

## Quick Start

Note: this is proejct was developed and tested on Ubuntu 24.04.

###  Preliminary: setup the project

If you don't have uv, follow the instructions here: [install-uv](https://docs.astral.sh/uv/getting-started/installation/)

To setup the project:

```bash
uv sync
```

### 1. Build the Index

Generate the positional inverted index from the document corpus:

```bash
uv run engine/indexer.py
```

This creates `index/positional_inverted_index.json`.

### 2. Start the API Server

Launch the FastAPI server:

```bash
uv run uvicorn main:app --host 127.0.0.1 --port 8000
```

### 3. Query the Endpoints

The server exposes several ranking endpoints. Example query:

```bash
curl -s "http://127.0.0.1:8000/bm25_ranking?query=Can%20the%20President%20of%20the%20USA%20overrule%20the%20constitution%3F" | python -m json.tool
```

## Available Endpoints

The API provides several ranking methods, from basic to sophisticated:

### `/fetch_all_docs`
Retrieves all documents containing at least one query term (union of postings).

```bash
curl -s "http://127.0.0.1:8000/fetch_all_docs?query=Can%20the%20President%20overrule%20the%20constitution%3F" | python -m json.tool
```

### `/tf_ranking`
Ranks by raw term frequency (count of query term occurrences).

```bash
curl -s "http://127.0.0.1:8000/tf_ranking?query=Can%20the%20President%20overrule%20the%20constitution%3F" | python -m json.tool
```

### `/idf_ranking`
Ranks by inverse document frequency (boosts rare terms, ignores common ones).

```bash
curl -s "http://127.0.0.1:8000/idf_ranking?query=Can%20the%20President%20overrule%20the%20constitution%3F" | python -m json.tool
```

### `/tf_idf_ranking`
Traditional TF-IDF scoring (linear or sublinear TF × IDF).

```bash
curl -s "http://127.0.0.1:8000/tf_idf_ranking?query=Can%20the%20President%20overrule%20the%20constitution%3F" | python -m json.tool
```

### `/bm25_ranking`
State-of-the-art BM25 scoring with length normalization and saturation.

```bash
curl -s "http://127.0.0.1:8000/bm25_ranking?query=Can%20the%20President%20overrule%20the%20constitution%3F" | python -m json.tool
```

### `/string_search`
Debug endpoint: shows processed query terms and raw index lookups.

```bash
curl -s "http://127.0.0.1:8000/string_search?query=Can%20the%20President%20overrule%20the%20constitution%3F" | python -m json.tool
```

## Understanding Ranking

For detailed mathematical explanations, worked examples, and step-by-step BM25 calculations, see **[RANKING.md](RANKING.md)**.

## Why This Project Exists

This isn't just a toy implementation—it's a deliberate exercise in fighting abstraction rot.

> "Abstractions are wonderful... until they atrophy the muscles they replace."

Working with high-level search APIs (Typesense) made shipping easy but left me unable to answer basic questions about how search actually works. This project is my reset: rebuild the fundamentals, end to end, in a few files, with no dependencies.

For a rather long reflection on the effects of abstraction, AI-assisted coding, and the disembodiment of practice, read **[REFLECTIONS.md](REFLECTIONS.md)**.

## What's Deliberately Simple

- **Stemmer**: A crude affix stripper that turns "president" into "sident". This is intentionally transparent to show what real stemmers (Porter, Snowball) do better.
- **Corpus**: 10 documents, one per line in `docs/docs.txt`. Just enough to demonstrate ranking differences.
- **Dependencies**: FastAPI, uvicorn, and Python standard library. No external search libraries.

The simplicity is the point.

## Future Work

The main thing I want to implement is document vector model. And then and add reciprocal rank fusion to combine bm25 with vector similarity.

## License

This is a learning project. Use it, fork it, learn from it.

---

**Start here**: [README.md](README.md) → [RANKING.md](RANKING.md) → [REFLECTIONS.md](REFLECTIONS.md)
