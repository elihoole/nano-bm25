# How ranking works

We'll use a single query to explain how retrieval works end-to-end.

## Query in question

This is the query:

```bash
Can the president of the USA rule over the constitution?
```

After applying the same preprocessing steps we applied to the document, the query looks like this:
```bash
["sident", "usa", "rule", "over", "constitu", "?"]
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

## Ranking with term frequency

Now if you actually look at the results from /fetch_all_docs, the first result (due to final sorting by doc_id) is doc_id "2":

```bash
{"2": "My objections to the current constitution of the board was overruled."}
```

As you can see, doc_id "1" is not super relevant to the query. It is about the the make up --aka, constitution -- of an institutional board not about the constitution of the USA. So fetching all docs with at least one query term (and, then, naively sorting my doc_id or similar) aligns poorly with the user's expectations of relevance.

We need a better signal for relevance. Enter term frequency (TF). The idea is simple: if a document contains a query term more often than other documents, it’s more likely to be about that term. So we score documents by counting how many times the query terms appear and prefer the ones with higher counts.

This is what the /tf_ranking endpoint does. With the current documents, the first ranked result is doc_id "4" and the second ranked result is doc_id "5":

```bash
{"4": "Donald Trump is the 45th President of the USA. He has headed the USA since November 2024. Leftists in the USA don't like Trump. Trump was born iin New York, USA."}
{"5": "The President of the USA can overrule the constitution. It has been this way since the country's founding."}
```

TF scoring for doc_id "5" is shown below:

- Query (processed): ["sident", "usa", "rule", "over", "constitu", "?"]


For doc_id "4":
- Document (matched tokens, with counts): {"sident": 1, "usa": 4}
- Score("4") = 1 + 4 = 5

For doc_id "5":
- Document (matched tokens, with counts): {"sident": 1, "usa": 1, "rule": 1, "constitu": 1}
- Score("5") = 1 + 1 + 1 + 1 = 4

## Ranking with inverse document frequency

Between "4" and "5", document "5" is much more relevant to the query. But term frequency scoring, on its own, does not surface "5" as the top document because of the following reasons:

- Common terms have low discriminatory power: If a term appears in many documents (e.g., "usa" in this case), raw TF over-rewards documents that repeat it, even when they are not aligned with the query’s intent.

- Redundancy can overshadow coverage and context: A document that repeats one query term many times can outrank one that mentions all query terms once, because TF ignores cross-term balance, proximity/co-occurrence, and length normalization.

The antidote to term frequency's weaknesses is inverse document frequency (IDF), which down-weights common terms and boosts rarer, more discriminative ones. Our `/idf_ranking` endpoint intentionally scores by IDF only (no TF multiplier):

- idf(t) = log((N + 1) / (df(t) + 1)) + 1
- IDF score(q, d) = sum over unique matched t in q of idf(t)

With the current index (N = 10), the query terms have these document frequencies (df) and IDFs (terms not present in any document—like "over" here—don’t contribute to any document’s score):
- df: sident = 2, usa = 2, rule = 1, constitu = 2, ? = 2
- idf: sident ≈ 2.2993, usa ≈ 2.2993, rule ≈ 2.7047, constitu ≈ 2.2993

Effects on our two top contenders:
- Doc 5 matches {sident, usa, rule, constitu} → idf(q, 5) ≈ 2.2993 + 2.2993 + 2.7047 + 2.2993 = 9.6026
- Doc 4 matches {sident, usa} → idf(q, 4) ≈ 2.2993 + 2.2993 = 4.5986

Result: doc_id "5" outranks doc_id "4" under IDF because it covers more discriminative terms (including the rarer “rule” and “constitu”), while doc 4 mainly repeats the common term “usa”.

## Ranking with TF-IDF

In practice, we want a balance between TF and IDF. So, we multiply the two.

Definition:

- score(d, q) = sum over matched terms t of tf(t, d) × idf(t)

Doc "5" (tf: sident=1, usa=1, rule=1, constitu=1):
- 1×2.2993 + 1×2.2993 + 1×2.7047 + 1×2.2993 = 9.6026

Doc "4" (tf: sident=1, usa=4):
- 1×2.2993 + 4×2.2993 = 11.4965

But, as you can see, through sheer repitition of "usa", doc_id "4" out ranks "5" in TF-IDF scoring. How do we fix this? Notice that

Sublinear TF (1 + ln(tf)) to reduce repetition dominance. As you know `ln` grows quickly at first and then flattens, so the first occurrence of a query term in a document contributes most and additional repeats add diminishing gains.

Doc "5":
- Same as above (all tf=1) → 9.6026

Doc "4":
- sident: (1)×2.2993 = 2.2993
- usa: (1 + ln 4 ≈ 2.3863)×2.2993 ≈ 5.4868
- Total ≈ 7.7861

Result with sublinear TF:
- doc "5" > doc "4", reflecting better term coverage and discriminative matches.

## Ranking with BM25

Even with sublinear TF, TF-IDF is still limited:

- It lacks principled document length normalization. Longer documents tend to accumulate more evidence (and more repetitions) and can be unfairly favored or penalized depending on corpus mix.
- It does not saturate TF strongly enough. Repeating the same term keeps boosting the score without a firm cap tied to document length.
- It has no tunable knobs to trade off repetition vs coverage across different corpora and query styles.

We’ll use:
- idf(t) = ln(1 + (N - df(t) + 0.5) / (df(t) + 0.5))
- score(d, q) = Σ over matched t [ idf(t) × (tf(t, d) × (k1 + 1)) / (tf(t, d) + k1 × (1 − b + b × dl/avgdl)) ]
- Parameters: k1 = 1.2, b = 0.75

Numbers for this index and query terms:
- N = 10
- df: sident = 2, usa = 2, rule = 1, constitu = 2
- idf: sident ≈ 1.4816, usa ≈ 1.4816, constitu ≈ 1.4816, rule ≈ 1.9924
- Lengths (post-processing, approximate): dl(4) ≈ 31, dl(5) ≈ 18, avgdl ≈ 20
- K(d) = k1 × (1 − b + b × dl/avgdl)
    - K(4) ≈ 1.2 × (0.25 + 0.75 × 31/20) = 1.695
    - K(5) ≈ 1.2 × (0.25 + 0.75 × 18/20) = 1.11

Doc 4 (matches: sident=1, usa=4)
- sident: contrib = 1.4816 × (1 × 2.2) / (1 + 1.695) = 1.4816 × 0.8161 ≈ 1.2095
- usa: contrib = 1.4816 × (4 × 2.2) / (4 + 1.695) = 1.4816 × 1.5459 ≈ 2.2909
- Score(4) ≈ 1.2095 + 2.2909 = 3.5004

Doc 5 (matches: sident=1, usa=1, rule=1, constitu=1)
- Common TF factor for tf=1: (1 × 2.2) / (1 + 1.11) = 1.0427
- sident: 1.4816 × 1.0427 ≈ 1.5448
- usa: 1.4816 × 1.0427 ≈ 1.5448
- constitu: 1.4816 × 1.0427 ≈ 1.5448
- rule: 1.9924 × 1.0427 ≈ 2.0777
- Score(5) ≈ 1.5448 + 1.5448 + 1.5448 + 2.0777 = 6.7121

Result and intuition:
- BM25 ranks doc 5 above doc 4 (6.71 > 3.50).
- Repetition of a common term in doc 4 saturates and is further tempered by length normalization, while doc 5’s broader coverage of discriminative terms (including rule) is rewarded.
- This demonstrates why BM25’s tunable saturation and length normalization outperform even sublinear TF-IDF.