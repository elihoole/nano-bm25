import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query

from query import process_query

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


@app.get("/string_search")
def string_search(query: str = Query(..., min_length=1)):
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

    # Print the full index and query to stdout (as requested)
    print("PII:", pii)
    print("QUERY:", query)

    processed_query = process_query(query)
    print("PROCESSED QUERY:", processed_query)

    # Just fetch postings for the processed query terms
    for term in processed_query:
        postings = pii.get(term, {})
        print(f"Postings for term '{term}': {postings}")

    # Return a tiny summary instead of the entire index
    return {
        "status": "ok",
        "query": query,
        "processed_query": processed_query,
        "postings_found": {
            term: list(pii.get(term, {}).keys()) for term in processed_query
        },
    }


# Export helpers for quick local sanity checks
def get_index_path() -> Path:
    return INDEX_PATH
