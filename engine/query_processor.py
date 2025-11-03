from .indexer import (
    preprocess,
    remove_stop_words,
    tokenize,
)
from .stemmer import stem


def process_query(query: str) -> list[str]:
    """
    Process the input query string through preprocessing, tokenization,
    stop-word removal, and stemming.
    """
    preprocessed_query = preprocess(query)
    tokens = tokenize(preprocessed_query)
    filtered_tokens = remove_stop_words(tokens)
    stemmed_tokens = [stem(token) for token in filtered_tokens]
    return stemmed_tokens
