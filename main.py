import json
import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query

from query import process_query
from tfidf_ranker import rank_with_idf, rank_with_tf

logger = logging.getLogger("nano_bm25")
logger.setLevel(logging.DEBUG)

app = FastAPI()

# Resolve the positional inverted index file relative to this file
INDEX_PATH = Path(__file__).parent / "index" / "positional_inverted_index.json"


def load_pii(path: Path) -> dict:
    """Load the positional inverted index JSON into memory."""
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


@app.on_event("startup")
def _load_index_on_startup() -> None:
    """Load the index at app startup if available."""
    if INDEX_PATH.exists():
        app.state.pii = load_pii(INDEX_PATH)
    else:
        # Leave uninitialized; the endpoint will surface a helpful error
        app.state.pii = None


@app.get("/fetch_all_docs")
def fetch_all_docs(query: str = Query(..., min_length=1)):
    """
    Minimal plumbing endpoint:
    - ensures the positional inverted index is in memory
    - prints the index and the incoming query
    - returns a small acknowledgement payload
    """
    pii = getattr(app.state, "pii", None)

    if pii is None:
        if not INDEX_PATH.exists():
            raise HTTPException(
                status_code=500,
                detail=f"Index not found at {INDEX_PATH}. Generate it first (run index.py).",
            )
        pii = load_pii(INDEX_PATH)
        app.state.pii = pii

    # Print the first posting in PII and the query to stdout (as requested)
    print("PII:", list(pii.items())[:3])  # print only first
    print("QUERY:", query)

    processed_query = process_query(query)
    print("PROCESSED QUERY:", processed_query)

    #  fetch all postings for the processed query terms
    postings = []
    for term in processed_query:
        if term in pii:
            posting_for_term = pii.get(term, {})
            postings.append({term: posting_for_term})
            print(f"POSTINGS FOR '{term}': {posting_for_term}")

    relevant_docs = set()
    for term_postings in postings:
        for term, docs in term_postings.items():
            relevant_docs.update(docs.keys())

    # Return a tiny summary instead of the entire index
    return {
        "status": "ok",
        "query": query,
        "processed_query": processed_query,
        "number_of_postings_found": len(postings),
        "postings": postings,
        # Expose union of docs across all query term postings
        "relevant_documents": sorted(relevant_docs),
    }


@app.get("/tf_ranking")
def tf_ranking(query: str = Query(..., min_length=1)):
    """
    Endpoint to rank documents based on term frequency (TF) for the given query.
    """
    pii = getattr(app.state, "pii", None)

    if pii is None:
        if not INDEX_PATH.exists():
            raise HTTPException(
                status_code=500,
                detail=f"Index not found at {INDEX_PATH}. Generate it first (run index.py).",
            )
        pii = load_pii(INDEX_PATH)
        app.state.pii = pii

    processed_query = process_query(query)
    try:
        ranked_docs = rank_with_tf(processed_query, pii)
    except Exception as e:
        logger.error(f"Error occurred while ranking documents: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return {
        "status": "ok",
        "query": query,
        "processed_query": processed_query,
        "ranked_documents": ranked_docs,
    }


@app.get("/idf_ranking")
def idf_ranking(query: str = Query(..., min_length=1)):
    """
    Endpoint to rank documents based on IDF scores for the given query.
    """
    pii = getattr(app.state, "pii", None)

    if pii is None:
        if not INDEX_PATH.exists():
            raise HTTPException(
                status_code=500,
                detail=f"Index not found at {INDEX_PATH}. Generate it first (run index.py).",
            )
        pii = load_pii(INDEX_PATH)
        app.state.pii = pii

    processed_query = process_query(query)

    try:
        ranked_docs = rank_with_idf(processed_query, pii)
    except Exception as e:
        logger.error(f"Error occurred while ranking documents: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return {
        "status": "ok",
        "query": query,
        "processed_query": processed_query,
        "ranked_documents": ranked_docs,
    }


# Export helpers for quick local sanity checks
def get_index_path() -> Path:
    return INDEX_PATH
