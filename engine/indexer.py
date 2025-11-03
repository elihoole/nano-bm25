import json
import os
import re
from pathlib import Path

from .stemmer import stem


def read_docs(filepath: Path):
    """
    Reads documents from a file and returns a dictionary mapping indices  to documents.
    Make sure to id from 1 onwards.
    """
    with open(filepath, "r") as file:
        doc_list = file.readlines()
    return {doc_id + 1: doc for doc_id, doc in enumerate(doc_list) if doc.strip()}


def preprocess(text: str) -> str:
    """
    These are the preprocessing steps.
    1. Strip and lowercase
    2. Remove punctuation other than .,:;!?
    """

    # Lowercase the text
    text = text.strip().lower()

    # Remove unwanted punctuation
    text = re.sub(r"[^\w\s\.\,\:\;\!\?]", "", text)
    text = re.sub(r"\s+", " ", text)

    return text


def tokenize(text: str) -> list[str]:
    """
    Rules:
    1. Split on whitespace
    2. Allowed punctuations become separate tokens.
    3. Remove empty tokens "".
    4. Strip leading/trailing spaces.
    """
    return [
        token.strip()
        for token in re.split(r"(\s+|[.,:;!?])", text)
        if token.strip() and not token.isspace()
    ]


def remove_stop_words(words: list[str]) -> list[str]:
    """
    Given a list of words, remove stopwords
    """
    # Resolve stopwords path relative to the project root/package
    base_dir = Path(__file__).resolve().parent.parent  # repo root when run via main.py
    stopwords_path = base_dir / "stopwords" / "stopwords.txt"
    if not stopwords_path.exists():
        # Fallback to current working directory style path
        stopwords_path = Path("stopwords/stopwords.txt")
    with stopwords_path.open("r", encoding="utf-8") as f:
        stop_words = f.readlines()
    stop_words = [word.strip() for word in stop_words]
    return [word for word in words if word not in stop_words]


def create_positional_inverted_index(
    docs: dict[int, str],
) -> dict[str, dict[int, list[int]]]:
    """
    Creates a positional inverted index from the given documents.
    """
    index = {}
    for doc_id, doc in docs.items():
        tokens = [stem(token) for token in remove_stop_words(tokenize(preprocess(doc)))]
        for position, token in enumerate(tokens):
            if token not in index:
                index[token] = {}
            if doc_id not in index[token]:
                index[token][doc_id] = []
            index[token][doc_id].append(position)
    return index


if __name__ == "__main__":
    docs = read_docs(Path("docs/docs.txt"))
    for doc_id, doc in docs.items():
        print(f"Document {doc_id}: {doc.strip()}")
        preprocessed_doc = preprocess(doc)
        print(f"Preprocessed Document {doc_id}: {preprocessed_doc}")
        tokens = tokenize(preprocessed_doc)
        print(f"Tokens Document {doc_id}: {tokens}")
        filtered_tokens = remove_stop_words(tokens)
        print(f"Filtered Tokens Document {doc_id}: {filtered_tokens}")
        stemmed_tokens = [stem(token) for token in filtered_tokens]
        print(f"Stemmed Tokens Document {doc_id}: {stemmed_tokens}\n")

    index = create_positional_inverted_index(docs)
    print("Positional Inverted Index:")
    for term, postings in index.items():
        print(f"Term: {term} -> Postings: {postings}")

    os.makedirs("index", exist_ok=True)
    with open("index/positional_inverted_index.json", "w") as f:
        json.dump(index, f, indent=4)
