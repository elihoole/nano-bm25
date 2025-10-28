# How ranking works

We'll use a single query to explain how retrieval works end-to-end.

## Query in question

This is the query:

```bash
Can the president of the USA overrule the constitution?
```

After applying the same preprocessing steps we applied to the document, the query looks like this:
```bash
["sident", "usa", "sident", "rule", "constitu", "?"]
```

## Fetching all postings that match the query

Remember that our position index looks like this:

```bash
 "like": {
        "3": [
            12
        ]
    },
"rule": {
        "4": [
            2
        ]
    },
...
```

We call each term dictionary object a posting.

So fetching all documents for the query is simply a matter of

1) looking up the positional inverted index and fetching the posting for each matched term in the query.
2) taking the union of all document ids of the feteched postings

Here's a deliberately verbose way of doing this:

```bash
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
```

This is what the /fetch_all_docs end point does.

## Ranking with term frequencies

We call all


