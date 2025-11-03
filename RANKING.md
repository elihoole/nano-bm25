# How ranking works

We'll use a single query to explain how ranked retrieval works end-to-end.

Before you start reading, make sure that the server is running:

```bash
uv run uvicorn main:app --host 127.0.0.1 --port 8000
```

This is the query we'll be using throughout:

```text
Can the president of the USA overrule the constitution?
```

Keep in mind that after applying the same preprocessing steps we applied to the document, the query looks like this:
```json
["sident", "usa", "rule", "constitu", "?"]
```

To run the query against any scoring endpoint:

```bash
curl -s "http://127.0.0.1:8000/tf_ranking?query=Can%20the%20president%20of%20the%20USA%20overrule%20the%20constitution%3F" | python -m json.tool
```

Just replace `tf_ranking` with your desired ranking endpoint.

## Fetching all postings that match the query

Recall that our positional index looks like this:

```json
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

Each term maps to a postings list (doc_id -> positions). Each entry in that list is a posting. For example, for term `rule`, the entry `"4": [2]` is a posting indicating document 4 with a hit at position 2.

So fetching all documents for the query is simply a matter of:

1) Looking up the positional inverted index and fetching the posting for each matched term in the query.
2) Taking the union of all document IDs of the fetched postings.

Here's a deliberately verbose way of doing this:

```python
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

This is what the `/fetch_all_docs` endpoint does. You can ping the endpoint like so:

```bash
curl -s "http://127.0.0.1:8000/fetch_all_docs?query=Can%20the%20president%20of%20the%20USA%20overrule%20the%20constitution%3F" | python -m json.tool
```

Now if you actually look at the results from `/fetch_all_docs`, the first result (due to final sorting by doc_id) is doc_id "10":

```json
{"10": "Do unborn children have natural rights?"}
```

As you can see, doc_id "10" is in fact not relevant to the query at all. It got fetched because it shares the term `?` with the query. So fetching all docs with at least one query term aligns poorly with the user's expectations of relevance.

Note also in standard search settings, we will usually strip `?` alongside other non-alphanumerics as part of preprocessing. We have a small set of short documents. So some punctuation marks - i.e., `. , : ; ! ?` - are indexed as individual tokens.

## Ranking with term frequency

Enter term frequency (TF). The idea is simple: if a document contains a query term more often than other documents, it’s more likely to be about that term. So we score documents by counting how many times the query terms appear in them and prefer the ones with higher counts.

This is what the `/tf_ranking` endpoint does. With the current documents, the first ranked result is doc_id "4" and the second ranked result is doc_id "5":

```json
{"4": "Donald Trump is the 45th President of the USA. He has headed the USA since November 2024. Leftists in the USA don't like Trump. Trump was born in New York, USA."}
{"5": "The President of the USA can overrule the constitution. It has been this way since the country's founding."}
```

TF scoring for doc_id "5" is shown below:

- Query (processed): `["sident", "usa", "rule", "constitu", "?"]`


For doc_id "4":
- Document (matched tokens, with counts): `{"sident": 1, "usa": 4}`

$$
\mathrm{TF}(q, 4) = 1 + 4 = 5
$$

For doc_id "5":
- Document (matched tokens, with counts): `{"sident": 1, "usa": 1, "rule": 1, "constitu": 1}`

$$
\mathrm{TF}(q, 5) = 1 + 1 + 1 + 1 = 4
$$

So relevance scoring purely on term frequency ranks document "4" over "5".

You can verify this by running:

```bash
curl -s "http://127.0.0.1:8000/tf_ranking?query=Can%20the%20president%20of%20the%20USA%20overrule%20the%20constitution%3F" | python -m json.tool
```

But if you look at the contents of the documents, between documents "4" and "5", the latter — i.e., `doc_id` "5" — is much more relevant to the query. But term frequency scoring, on its own, does not surface "5" as the top document because of the following reasons:

- **Common terms have low discriminatory power**: If a term appears in many documents (e.g., "usa" in this case), raw TF over-rewards documents that repeat it, even when they are not aligned with the query’s intent.

- **Redundancy can overshadow coverage and context**: A document that repeats one query term many times can outrank one that mentions all query terms once, because TF ignores cross-term balance, proximity/co-occurrence, and length normalization.

## Ranking with inverse document frequency

The antidote to term frequency's weaknesses is inverse document frequency (IDF), which down-weights common terms and boosts rarer, more discriminative ones. This is what our `/idf_ranking` endpoint does.

IDF contribution of a matched term is:

$$
\mathrm{idf}(t) = \ln\left(\frac{N + 1}{\mathrm{df}(t) + 1}\right) + 1
$$

Without smoothing, it is just $\ln\left(\frac{N}{\mathrm{df}(t)}\right)$ (defined only when $\mathrm{df}(t) > 0$). The added 1 terms in the smoothed IDF formula serve the following functions:

- numerator +1: part of add-one (Laplace) smoothing; keeps the log argument finite even for degenerate corpora (e.g., $N=0$) and, together with the denominator +1, ensures the ratio is always >= 1.
- denominator +1: prevents division by zero when $\mathrm{df}(t)=0$ (term not observed) and is the other half of Laplace smoothing.
- outer +1 (the addition outside the log): shifts the value upward so IDF is strictly positive (>= 1) even when $\mathrm{df}(t)=N$ (term appears in every document), ensuring every matched term contributes a small, non-zero weight.

To get the relevance score of a document against a query based on IDF, we simply sum over $\mathrm{idf}(t)$ for each matched term $t$:

$$
\mathrm{IDF}(q, d) = \sum_{t \in (q \cap d)} \mathrm{idf}(t)
$$

Where $(q \cap d)$ denotes the set of unique query terms that appear in document $d$.

With the current index ($N = 10$), the query terms have these document frequencies ($\mathrm{df}$) and IDFs:
- df: "sident" $= 2$, "usa" $= 2$, "rule" $= 1$, "constitu" $= 2$, "?" $= 2$
- idf: "sident" $\approx 2.2993$, "usa" $\approx 2.2993$, "rule" $\approx 2.7047$, "constitu" $\approx 2.2993$

Note that while I showed "?" $= 2$ in df, I ignored "?" in idf. This is so because "?" is not a term that appears in the documents 4 or 5, so it does not affect the idf scores. In other words, "?" is not a matched term $t$.

Considering our top two contenders from TF scoring:

- Doc 4 matches `["sident", "usa"]`

$$
\text{IDF}(q, 4) \approx 2.2993 + 2.2993 = 4.5986
$$

- Doc 5 matches `["sident", "usa", "rule", "constitu"]`

$$
\text{IDF}(q, 5) \approx 2.2993 + 2.2993 + 2.7047 + 2.2993 = 9.6026
$$

Great: doc_id "5" outranks doc_id "4" under IDF because it covers more query terms and also contains the more discriminative term “rule”, which only appears in the corpus once, while doc "4" mainly repeats the common term “usa”.

You can verify this by running:
```bash
curl -s "http://127.0.0.1:8000/idf_ranking?query=Can%20the%20president%20of%20the%20USA%20overrule%20the%20constitution%3F" | python -m json.tool
```

While IDF produces the correct ranking in this particular case, it is still limited on its own. Term frequency is as important a component of relevance.


## Ranking with TF-IDF

In practice, we want a balance between TF and IDF. So we multiply the two. The contribution of a single matched term $t$ to the relevance score of a document, therefore:

$$
\mathrm{contrib}(t, d) = \mathrm{idf}(t) \times \mathrm{tf}(t, d)
$$

Thus, the relevance score of a document against the query is:
$$
\text{TF-IDF}(q, d) = \sum_{t\,\in\,(q\,\cap\,d)}  \mathrm{idf}(t) \times \mathrm{tf}(t, d)
$$

Doc "4" (tf: sident=1, usa=4):
$$
1 \times 2.2993 + 4 \times 2.2993 = 11.4965
$$

Doc "5" (tf: sident=1, usa=1, rule=1, constitu=1):
$$
1 \times 2.2993 + 1 \times 2.2993 + 1 \times 2.7047 + 1 \times 2.2993 = 9.6026
$$

But, as you can see, through sheer repetition of "usa", doc_id "4" outranks "5" in TF-IDF scoring.

You can try the `tf_idf_ranking` endpoint for verification:

```bash
 curl -s "http://127.0.0.1:8000/tf_idf_ranking?query=Can%20the%20president%20of%20the%20USA%20overrule%20the%20constitution%3F" | python -m json.tool
```

## Ranking with sublinear TF-IDF

How do we fix this?

A simple solution is sublinear TF $\big(1 + \ln(\mathrm{tf})\big)$ to reduce repetition dominance. Since $\ln$ grows quickly at first and then flattens, under sublinear TF, the first occurrence of a query term in a document contributes the most while additional repeats add diminishing gains.

Doc "5":
- Same as above (all $\mathrm{tf}=1$) = $9.6026$

Doc "4":
- sident: $(1)\times 2.2993 = 2.2993$
- usa: $\big(1 + \ln(4)\big) \times 2.2993  \approx 2.3863 \times 2.2993 \approx 5.4868$
- Total $2.2993 + 5.4868 \approx 7.7861$

Result with sublinear TF:
- doc "5" > doc "4", reflecting better term coverage and discriminative matches.

But, even with sublinear TF, TF-IDF is still limited:

- It lacks principled document length normalisation. Longer documents tend to accumulate more matching term occurrences (i.e., raw TF) and more repetitions and can be unfairly favoured or penalised depending on corpus mix.
- It does not saturate TF strongly enough. Repeating the same term keeps boosting the score without a firm cap tied to document length.
- It has no tunable knobs to trade off repetition vs coverage across different corpora and query styles.

## Ranking with BM25

This is where BM25 enters the picture. Under BM25, we weight TF with a damping factor for repetition as well as a correction factor for document length.

The contribution of a matched term in a document to the relevance score looks like this:

$$
\mathrm{contrib}(t,d)=\mathrm{idf}(t) \times \left[\frac{(k_1+1)}{\mathrm{tf}(t,d)+k_1\,C} \right] \cdot \mathrm{tf}(t,d)
$$

$$
------- (*)
$$

Where,

$$
C = (1 - b) + b \times \frac{dl}{avgdl}
$$


<div align="center">

$dl$: document length; $avgdl$: average document length; and $k_1, b$ are constants.

</div>

To understand BM25, we need to look at the factor that is scaling $\mathrm{tf}(t, d)$ shown within the square brackets in the $\mathrm{contrib}(t, d)$ equation above. Namely:

$$
\frac{k_1 + 1}{\mathrm{tf}(t, d) + k_1 \times C}
$$

Let's unpack this.

$C$ here is a document length correction, when expanded looks like so:

$$
C = (1 - b) + b \times \frac{dl}{avgdl}
$$

At a glance, you can see that the larger the document length compared to the average length of the corpus, the greater the $C$ term, resulting in greater penalisation of $\mathrm{tf}(t, d)$'s contribution. Notice that $C$ is part of the denominator of the scaling factor.

The constant $b$ in $C$ is a tunable knob: if you set it to $0$, BM25 does not apply any document length correction to $\mathrm{tf}(t, d)$; conversely, the larger the $b$, the greater the length penalty.

$k_1$ is the repetition damping parameter. To understand what $k_1$ does, it is instructive to think in limits.

As $k_1$ tends to infinity,

$$
\lim_{k_1 \to \infty} \frac{k_1 + 1}{\mathrm{tf}(t, d) + k_1 C} \to \lim_{k_1 \to \infty} \frac{1 + \frac{1}{k_1}}{\frac{\mathrm{tf}(t, d)}{k_1} + C} \approx \frac{1}{C}
$$

That is, as $k_1 \to \infty$ the damping effect on repetition is gradually eliminated, effectively preserving the raw TF with document length correction. Consequently, a large $k_1$ results in $\mathrm{contrib}(t, d)$ being a linear TF–IDF contribution for each matched term.

What happens when $k_1$ is very small? As $k_1$ tends to $0$,

$$
\lim_{k_1 \to 0} \frac{k_1 + 1}{\mathrm{tf}(t, d) + k_1 C} \approx \frac{1}{\mathrm{tf}(t, d)}
$$

That is, as $k_1 \to 0$ the damping effect gets severe: the scaling factor actually cancels out $\mathrm{tf}(t, d)$ altogether. In other words, a small $k_1$ makes $\mathrm{contrib}(t, d) \approx \mathrm{idf}(t)$.

### BM25 calculation

Now, let's work through BM25 calculation for documents "4" and "5".

Recall $\mathrm{contrib}(t, d)$ given in $-------(*)$:

$$
\text{contrib-bm25}(t,d)=\mathrm{idf}(t) \times \left[\frac{(k_1+1)}{\mathrm{tf}(t,d)+k_1\,C} \right] \cdot \mathrm{tf}(t,d)
$$

Here, we use the typical formula used for $\mathrm{idf}(t)$ in BM25 implementations:

$$
\mathrm{idf}(t) = \ln\left(\frac{N - df(t) + 0.5}{df(t) + 0.5} + 1\right)
$$

This is not all that different from the earlier $\mathrm{idf}(t)$ formula. $+0.5$ and $+1$ in this equation play analogous roles to the $+1$ in the earlier equation. This particular form of $\mathrm{idf}(t)$, derived from work in probability, is verified to be better in empirical studies.

Note: In the earlier IDF/TF-IDF sections, we used the smoothed IDF $\ln\!\left(\frac{N+1}{df(t)+1}\right) + 1$. For BM25, it's common to use the probabilistic IDF above; both serve to downweight common terms and upweight rarer ones.

To score the relevance of a document under BM25 weighting against a given query:

$$
\text{BM25}(q, d) = \sum_{t\,\in\,(q\,\cap\,d)} \text{contrib-bm25}(t, d)
$$


- Numbers for this index and query terms:

$N = 10$

- Document frequencies for matched terms:

$sident = 2; usa = 2; rule = 1; constitu = 2$

- Inverse document frequencies for the same terms under new formula above:

$sident ≈ 1.4816; usa ≈ 1.4816; constitu ≈ 1.4816; rule ≈ 1.9924$

- Document lengths:

$dl(4) = 26; dl(5) = 12; avgdl = 9.0$

- Constants:

$k_1 = 1.2$; $b = 0.75$

#### Relevance score of doc_id "4" against query: BM25(q, 4)

Document length correction factor for "4" is:

$$
C = 1 − b + b × \frac{dl}{avgdl} = 1 - 0.75 + 0.75 × \frac{26}{9} ≈ 2.4167
$$

Matched terms in 4 are `["sident", "usa"]`. Let's calculate the BM25-weighted $\mathrm{tf}(t, 4)$ for both matched terms.

"sident":

$$
	\text{bm25-weighted-tf}(\texttt{sident}, 4) = \frac{(k_1+1)}{\mathrm{tf}(t,d)+k_1\,C}\,\mathrm{tf}(t,d) = \left(\frac{1.2 + 1}{1 + 1.2 \times 2.4167}\right)\cdot 1 \approx 0.5641
$$

"usa":

$$
	\text{bm25-weighted-tf}(\texttt{usa}, 4) = \frac{(k_1+1)}{\mathrm{tf}(t,d)+k_1\,C}\,\mathrm{tf}(t,d) = \left(\frac{1.2 + 1}{4 + 1.2 \times 2.4167}\right)\cdot 4 \approx 1.2754
$$

So the relevance score of document "4" against the query becomes:

$$
BM25(q, 4) \approx \mathrm{idf}(`sident') \times \text{bm25-weighted-tf}(`sident`, 4) + \mathrm{idf}(`usa') \times \text{bm25-weighted-tf}(`usa', 4)
$$

$$
BM25(q, 4) \approx 1.4816 \times 0.5641 + 1.4816 \times 1.2754 \approx 2.7252
$$

#### Relevance score of doc_id "5" against query: BM25(q, 5)

If you repeat the steps above you would find that:

$$
BM25(q, 5) = 5.6648
$$

We can be happy: with our defaults for $k_1$ and $b$, BM25 ranks doc 5 above doc 4 (5.6648 > 2.7254). Repetition of a common term in doc 4 ("usa") saturates and is further tempered by length normalisation, while doc 5’s broader coverage of discriminative terms (including rule) is rewarded.

To verify, run:

```bash
curl -s "http://127.0.0.1:8000/bm25_ranking?query=Can%20the%20president%20of%20the%20USA%20overrule%20the%20constitution%3F" | python -m json.tool
```

To get debug prints run:
```bash
uv run bm25.py
```



