def rank_with_tf(query_terms, positional_inverted_index):
    """Rank documents basked purely on TF (term frequency)."""
    from collections import defaultdict

    # Initialize a dictionary to hold term frequencies for each document
    doc_term_freq = defaultdict(lambda: defaultdict(int))

    # Calculate term frequencies for each document
    for term in query_terms:
        if term in positional_inverted_index:
            for doc_id, positions in positional_inverted_index[term].items():
                doc_term_freq[doc_id][term] += len(positions)

    print("Document Term Frequencies:", dict(doc_term_freq))

    # Calculate total term frequency for each document
    doc_scores = {}
    for doc_id, term_freqs in doc_term_freq.items():
        total_tf = sum(term_freqs.values())
        doc_scores[doc_id] = total_tf

    # Sort documents by their scores in descending order
    ranked_docs = sorted(doc_scores.items(), key=lambda item: item[1], reverse=True)

    return ranked_docs


def rank_with_idf(query_terms, positional_inverted_index):
    """Rank documents based on IDF scores."""
    import math
    from collections import defaultdict

    # Initialize a dictionary to hold IDF scores for each document
    doc_idf_scores = defaultdict(float)
    total_docs = len(
        {
            doc_id
            for term_postings in positional_inverted_index.values()
            for doc_id in term_postings.keys()
        }
    )
    # Calculate IDF scores for each document
    for term in query_terms:
        if term in positional_inverted_index:
            df = len(positional_inverted_index[term])  # Document frequency
            idf = math.log((total_docs + 1) / (df + 1)) + 1  # Smoothed IDF
            for doc_id, positions in positional_inverted_index[term].items():
                doc_idf_scores[doc_id] += idf

    print("Document IDF Scores:", dict(doc_idf_scores))

    # Sort documents by their IDF scores in descending order
    ranked_docs = sorted(doc_idf_scores.items(), key=lambda item: item[1], reverse=True)

    return ranked_docs


if __name__ == "__main__":
    # load pii
    import json
    from pathlib import Path

    INDEX_PATH = Path("index/positional_inverted_index.json")

    if INDEX_PATH.exists():
        with INDEX_PATH.open("r", encoding="utf-8") as f:
            positional_inverted_index = json.load(f)
    else:
        positional_inverted_index = {}

    # Example query
    query_terms = ["sident", "usa", "rule", "constitu", "?"]

    ranked_documents = rank_with_tf(query_terms, positional_inverted_index)
    print("Ranked Documents (TF):", ranked_documents)
