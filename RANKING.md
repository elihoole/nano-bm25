# How ranking works

We'll use a single query to explain how retrieval works end-to-end. Before you start reading, make sure that the server is running:

```bash
uv run uvicorn main:app --host 127.0.0.1 --port 8000
```

## Query in question

Here's is the query:

```bash
Can the president of the USA rule over the constitution?
```

After applying the same preprocessing steps we applied to the document, the query looks like this:
```bash
["sident", "usa", "rule", "over", "constitu", "?"]
```

## Fetching all postings that match the query

Recall that our position index looks like this:

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

This is what the `/fetch_all_docs` end point does.

## Ranking with term frequency

Now if you actually look at the results from `/fetch_all_docs`, the first result (due to final sorting by doc_id) is doc_id "2":

```bash
{"2": "My objections to the current constitution of the board was overruled."}
```

As you can see, doc_id "1" is not super relevant to the query. It is about the the make up --aka, constitution -- of an institutional board not about the constitution of the USA. So fetching all docs with at least one query term (and, then, naively sorting by doc_id or similar) aligns poorly with the user's expectations of relevance.

Enter term frequency (TF). The idea is simple: if a document contains a query term more often than other documents, it’s more likely to be about that term. So we score documents by counting how many times the query terms appear in them and prefer the ones with higher counts.

This is what the `/tf_ranking` endpoint does. With the current documents, the first ranked result is doc_id "4" and the second ranked result is doc_id "5":

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

You can verify this by running

```bash
curl -s "http://127.0.0.1:8000/tf_ranking?query=Can%20the%20president%20of%20the%20USA%20overrule%20the%20constitution%3F" | python -m json.tool
```

## Ranking with inverse document frequency

Between "4" and "5", document "5" is much more relevant to the query. But term frequency scoring, on its own, does not surface "5" as the top document because of the following reasons:

- Common terms have low discriminatory power: If a term appears in many documents (e.g., "usa" in this case), raw TF over-rewards documents that repeat it, even when they are not aligned with the query’s intent.

- Redundancy can overshadow coverage and context: A document that repeats one query term many times can outrank one that mentions all query terms once, because TF ignores cross-term balance, proximity/co-occurrence, and length normalization.

The antidote to term frequency's weaknesses is inverse document frequency (IDF), which down-weights common terms and boosts rarer, more discriminative ones. This is what our `/idf_ranking` endpoint does:

$$
\mathrm{idf}(t) = \ln\!\left(\frac{N + 1}{\mathrm{df}(t) + 1}\right) + 1
$$

$$
	ext{IDFScore}(q, d) = \sum_{t\,\in\,(q\,\cap\,d)^{\*}} \mathrm{idf}(t)
$$

Where $(q\,\cap\,d)^{\*}$ denotes the set of unique query terms that appear in document $d$.

With the current index ($N = 10$), the query terms have these document frequencies ($\mathrm{df}$) and IDFs:
- df: "sident" $= 2$, "usa" $= 2$, "rule" $= 1$, "constitu" $= 2$, "?" $= 2$
- idf: "sident" $\approx 2.2993$, "usa" $\approx 2.2993$, "rule" $\approx 2.7047$, "constitu" $\approx 2.2993$

Effects on our two top contenders:
- Doc 4 matches {"sident", "usa"} → $\text{IDFScore}(q, 4) \approx 2.2993 + 2.2993 = 4.5986$
- Doc 5 matches {"sident", "usa", "rule", "constitu"} → $\text{IDFScore}(q, 5) \approx 2.2993 + 2.2993 + 2.7047 + 2.2993 = 9.6026$

Result: doc_id "5" outranks doc_id "4" under IDF because it covers more discriminative terms (including the rarer “rule” and “constitu”), while doc "4" mainly repeats the common term “usa”.

While IDF produces the correct ranking here, it is limited on its own as it completely ignores term frequency which is an essential measure of relative relevance between documents.

## Ranking with TF-IDF

In practice, we want a balance between TF and IDF. So, we multiply the two.

Definition:

$$
\mathrm{score}(q, d) = \sum_{t\,\in\,(q\,\cap\,d)} \mathrm{tf}(t, d) \times \mathrm{idf}(t)
$$


Doc "4" (tf: sident=1, usa=4):
- 1×2.2993 + 4×2.2993 = 11.4965

Doc "5" (tf: sident=1, usa=1, rule=1, constitu=1):
- 1×2.2993 + 1×2.2993 + 1×2.7047 + 1×2.2993 = 9.6026


But, as you can see, through sheer repetition of "usa", doc_id "4" outranks "5" in TF-IDF scoring. You can try the `tf_idf_ranking` endpoint for verification.

## Ranking with SublinearTF-IDF

How do we fix this? A simple fix is sublinear TF $\big(1 + \ln(\mathrm{tf})\big)$ to reduce repetition dominance. As you know, $\ln$ grows quickly at first and then flattens, so under sublinear TF, the first occurrence of a query term in a document contributes most and additional repeats add diminishing gains.

Doc "5":
- Same as above (all $\mathrm{tf}=1$) → $9.6026$

Doc "4":
- sident: $(1)\times 2.2993 = 2.2993$
- usa: $\big(1 + \ln 4 \approx 2.3863\big)\times 2.2993 \approx 5.4868$
- Total $\approx 7.7861$

Result with sublinear TF:
- doc "5" > doc "4", reflecting better term coverage and discriminative matches.

## Ranking with BM25

But, even with sublinear TF, TF-IDF is still limited:

- It lacks principled document length normalization. Longer documents tend to accumulate more matching term occurrences (i.e., raw TF) and more repetitions and can be unfairly favored or penalized depending on corpus mix.
- It does not saturate TF strongly enough. Repeating the same term keeps boosting the score without a firm cap tied to document length.
- It has no tunable knobs to trade off repetition vs coverage across different corpora and query styles.

This is where BM25 enters the picture. BM25 is simply an extension of the sublinear TF idea which accounts for document length.

Under BM25, we weight TF with a damping factor for repetition as well as a correction factor for document length. The contribution of a matched term in a document to the relevance score looks like this:

$$
\mathrm{contrib}(t, d) = \mathrm{idf}(t) \times \frac{(k_1 + 1)}{\mathrm{tf}(t, d) + k_1 \times C} \times \mathrm{tf}(t, d)
$$

Where

$$
C = (1 - b) + b \times \frac{dl}{avgdl}
$$

$dl$ = document length, $avgdl$ = average document length, and $k_1, b$ are constants.

To understand BM25, we need to look at the factor that is scaling $\mathrm{tf}(t, d)$. Namely:

$$
\frac{k_1 + 1}{\mathrm{tf}(t, d) + k_1 \times C}
$$

Let's unpack this.

C here is a document length correction.

$$
C = (1 - b) + b \times \frac{dl}{\overline{dl}}
$$

At a glance, you can see that the larger the document length compared to the average length of the corpus, the greater the $C$ term, resulting in greater penalization of $\mathrm{tf}(t, d)$'s contribution (notice that it is part of the denominator of the scaling factor). The constant $b$ is a tunable knob: if you set it to $0$, BM25 does not apply any document length correction to $\mathrm{tf}(t, d)$; the larger the $b$, the greater the length penalty.

$k_1$ is the repetition damping parameter. To understand what $k_1$ does, let's think in limits.

As $k_1$ tends to infinity,

$$
\frac{k_1 + 1}{\mathrm{tf}(t, d) + k_1 C} \to \frac{1 + 1/k_1}{\mathrm{tf}(t, d)/k_1 + C} \to\ \frac{1}{C}
$$

That is, as $k_1 \to \infty$ the damping effect on repetition is progressively removed, essentially preserving TF but for a correction for document length, making $\mathrm{contrib}(t, d)$ for a given term a linear TF–IDF contribution.

As $k_1$ tends to $0$,

$$
\frac{k_1 + 1}{\mathrm{tf}(t, d) + k_1 C} \to \frac{1}{\mathrm{tf}(t, d)}
$$

That is, as $k_1 \to 0$ the damping effect gets severe, essentially canceling out $\mathrm{tf}(t, d)$. This makes $\mathrm{contrib}(t, d) \approx \mathrm{idf}(t)$.





