# Nano BM25

Date: 2025-10-28

TL;DR
- I blanked on the query side of classic IR during an interview. So I rebuilt a tiny retrieval stack from scratch here to refresh the fundamentals.
- This repo builds a positional inverted index, exposes a minimal HTTP endpoint, and sets the stage for adding BM25 ranking next.
- It’s intentionally tiny and dependency-light to force understanding over abstraction.

## Why I’m writing this

I interviewed for a search role. I work with search every day, but mostly via high-level APIs (Typesense, etc.). In the interview, questions rightly targeted fundamentals. I could visualize indexing, but on the query side I froze. I recalled “term frequency” and “inverse document frequency,” but not the exact flow or formula under pressure.

Abstractions are wonderful . . . until they atrophy the muscles they replace. This project is my reset: rebuild the basics, end to end, in a few files.

## What this repo contains

- Documents: `docs/docs.txt` (one document per line)
- Indexer: `index.py` (preprocess → tokenize → stopword removal → stem → positional inverted index)
- Query processing: `query.py` (same preprocessing pipeline for queries)
- HTTP API: `main.py` (FastAPI; a simple `/string_search` endpoint that introspects the index and terms)
- Index artifact: `index/positional_inverted_index.json`
- Toy stemmer: `stemmer.py` (intentionally simple, to surface tradeoffs)

## Rebuilding the pipeline

Document side (indexing):
1) Preprocess: lowercase, strip, keep only word chars and . , : ; ! ?
2) Tokenize: split on whitespace and treat the allowed punctuation as separate tokens
3) Remove stop-words: from `stopwords/stopwords.txt`
4) Stem: crude affix stripper in `stemmer.py`
5) Build positional inverted index: `{ term: { doc_id: [positions...] } }`

Example (shape, not actual values):
{
        "usa": { "3": [4], "4": [1] },
        "trump": { "2": [6], "3": [1, 13] }
}

The positions make phrase queries and proximity queries possible later; they also give us per-(term, doc) term frequency as `len(positions)` for BM25.

## Query side, minimally

`process_query()` applies the same pipeline to the input text and returns normalized terms. Because the stemmer removes prefixes like "pre-", the word "president" becomes `sident`. That’s not “correct,” but it’s deliberate: it keeps the system transparent and reminds me what real stemmers do better.

`/string_search` currently:
- loads `index/positional_inverted_index.json` into memory
- prints the index and the incoming query
- returns a tiny JSON summary of which docs contain the processed terms

This is the plumbing you need right before adding ranking.

## How to run it

1) Build the index (creates `index/positional_inverted_index.json`):

```bash
python3 index.py
```

2) Start the API server (any ASGI runner works):

```bash
uvicorn main:app --reload --port 8000
```

3) Try a query:

```bash
curl "http://localhost:8000/string_search?query=Can%20the%20President%20of%20the%20USA%20overrule%20the%20constitution%3F"
```

You’ll see which normalized terms were found and in which documents. That’s our jumping-off point for ranking.

## Fetch all docs that contain at least one query term

The most basic notion of relevance is that a document contains at least one of the query terms. To fetch all docs that contain at least one term in the query:

```bash
curl "http://localhost:8000/fetch_all_docs?query=Can%20the%20President%20of%20the%20USA%20overrule%20the%20constitution%3F"
```

## Ranked retrieval with just term frequency

We introduce the idea that documents where query terms occur more . . . are more relevant than others. To retrieve a ranked list of documents based on how many times a query term occured in the document.

```bash

```

## Retrieval with TF-IDF

We'll first do ranked retrieval with TF-IDF only.





## BM25, in one screen

For a query Q and document D, the BM25 score is the sum over query terms q of:

score(D, Q) = sum over q in Q of [ IDF(q) * ((tf(q, D) * (k1 + 1)) / (tf(q, D) + k1 * (1 - b + b * |D|/avgdl))) ]

Where:
- tf(q, D): term frequency of q in D (here: length of the positions list for q in D)
- |D|: document length in tokens after preprocessing
- avgdl: average document length across the corpus
- k1: saturation parameter, usually ~1.2–1.5
- b: length normalization, usually ~0.75
- IDF(q): log((N - n(q) + 0.5) / (n(q) + 0.5) + 1)
        - N: total number of documents
        - n(q): number of documents containing q

Why this matters: tf alone rewards verbosity; IDF rewards rarity; b and |D|/avgdl avoid penalizing or over-rewarding long documents.

## What I’ll add next

- BM25 scoring and ranking endpoint:
        - precompute: doc lengths, avgdl, N
        - query-time: for each term, compute tf from positions, n(q) from postings, then sum per-doc
        - return top-k results with simple scores
- Phrase and proximity queries (thanks to positions)
- Boolean operators (AND, OR, NOT) as minimal set operators over posting lists
- Small test corpus and unit tests over tokenization/stemming/IDF/score
- A better stemmer (Porter) or just plug in a library with a clear flag to keep it deterministic

## A note on abstractions

APIs made shipping search easy enough that I stopped thinking about the mechanics. That’s a gift—and a trap. This repo’s goal is humility and clarity: get the fundamentals back into muscle memory, then bring the right abstractions back in with intention.

## File map (quick reference)

- `index.py`: read docs → preprocess → tokenize → stopwords → stem → build PII → write JSON
- `query.py`: `process_query()` for normalized query terms
- `main.py`: FastAPI app with `/fetch_all_relevant_docs` and other end points
- `docs/docs.txt`: toy corpus (one document per line)
- `index/positional_inverted_index.json`: generated index
- `stemmer.py`: toy affix-based stemmer

That’s the core. Next commit: actual BM25 ranking.





































































































+