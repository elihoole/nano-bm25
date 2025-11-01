"""Minimal, self-contained BM25 ranker

This follows naturally from the sublinear TF-IDF discussion in RANKING.md.

Key ideas (why BM25?):
- Still uses IDF to down-weight common terms (same spirit as TF-IDF)
- Uses a saturating TF factor so repetition helps but with diminishing returns
- Adds document-length normalization so long docs don't get an unfair boost

Formula (Okapi BM25):
  score(d, q) = sum over matched terms t of
          IDF(t) * ((tf(t,d) * (k1 + 1)) / (tf(t,d) + k1 * (1 - b + b * dl/avgdl)))

Where:
- tf(t, d) is the term frequency of t in doc d
- dl is the length of document d (token count after preprocessing)
- avgdl is the average document length across the collection
- k1 controls TF saturation (typical ~1.2 to 2.0)
- b controls length normalization (0 = none, 1 = full), typical 0.75
- IDF is Robertson–Sparck Jones style; we add +1 inside log to keep it positive

"""

from __future__ import annotations


def _collect_doc_lengths(positional_inverted_index):
    """Compute document lengths (dl) as total token counts from the index.

    We sum term positions across all terms for each doc.
    This matches the tokenization used to build the positional index.
    """
    from collections import defaultdict

    doc_lengths = defaultdict(int)
    for term, posting in positional_inverted_index.items():
        for doc_id, positions in posting.items():
            doc_lengths[doc_id] += len(positions)
    return dict(doc_lengths)


def _collect_doc_count(positional_inverted_index):
    """Count unique documents present in the positional index.
    Here, the value is just 10 (number of lines in docs/docs.txt).
    """
    doc_ids = {
        doc_id
        for posting in positional_inverted_index.values()
        for doc_id in posting.keys()
    }
    return len(doc_ids)


def rank_with_bm25(
    query_terms,
    positional_inverted_index,
    k1=1.2,
    b=0.75,
):
    """Rank documents using BM25.

    Inputs:
    - query_terms: list of tokens (preprocessed the same way as the index)
    - positional_inverted_index: { term: { doc_id: [pos, ...], ... }, ... }

    Returns:
    - ranked list of (doc_id, score) sorted by score desc

    Notes:
    - We use unique query terms (like tfidf_ranker.py) for clarity.
      This matches the pedagogy-first approach used elsewhere in this repo.
    - IDF uses a smoothed Robertson–Sparck Jones flavor:
            idf(t) = ln(((N - df + 0.5) / (df + 0.5)) + 1)
      The +1 keeps it positive and easy to reason about in small corpora.
    """
    import math
    from collections import defaultdict

    # Unique query terms only (pedagogical consistency with tfidf_ranker.py)
    query_terms = list(set(query_terms))

    # Document stats
    N = _collect_doc_count(positional_inverted_index)
    doc_lengths = _collect_doc_lengths(positional_inverted_index)
    avgdl = (sum(doc_lengths.values()) / N) if N > 0 else 0.0

    print("Total documents (N):", N)
    print("Document lengths (dl):", doc_lengths)
    print("Average document length (avgdl):", avgdl)

    # Precompute simple per-doc term frequencies limited to the query terms
    doc_term_freq = defaultdict(lambda: defaultdict(int))
    for term in query_terms:
        if term in positional_inverted_index:
            for doc_id, positions in positional_inverted_index[term].items():
                doc_term_freq[doc_id][term] = len(positions)
    print("Document Term Frequencies (for query terms):", dict(doc_term_freq))

    # Compute per-term IDF
    term_idf = {}
    for term in query_terms:
        if term in positional_inverted_index:
            df = len(positional_inverted_index[term])
            # Smoothed RSJ IDF; +1 inside log for small collections/positivity
            idf = math.log(((N - df + 0.5) / (df + 0.5)) + 1)
            term_idf[term] = idf
    print("Term IDFs:", term_idf)

    # BM25 scoring
    doc_scores = defaultdict(float)
    for doc_id, tf_map in doc_term_freq.items():
        dl = doc_lengths.get(doc_id, 0) or 0
        for term, tf in tf_map.items():
            idf = term_idf.get(term)
            if idf is None:
                continue
            # Saturating TF with length normalization
            denom = tf + k1 * (1 - b + b * (dl / avgdl if avgdl > 0 else 0))
            score_t = idf * ((tf * (k1 + 1)) / denom)
            doc_scores[doc_id] += score_t

    print("Document BM25 Scores:", dict(doc_scores))

    ranked_docs = sorted(doc_scores.items(), key=lambda item: item[1], reverse=True)
    return ranked_docs


if __name__ == "__main__":
    # Load positional inverted index (PII)
    import json
    from pathlib import Path

    INDEX_PATH = Path("index/positional_inverted_index.json")
    if INDEX_PATH.exists():
        with INDEX_PATH.open("r", encoding="utf-8") as f:
            positional_inverted_index = json.load(f)
    else:
        positional_inverted_index = {}

    # Example query (from RANKING.md, after preprocessing)
    query_terms = ["sident", "usa", "rule", "over", "constitu", "?"]

    ranked_documents = rank_with_bm25(query_terms, positional_inverted_index)
    print("Ranked Documents (BM25):", ranked_documents)
