# APIs and AI ate my memory: relearning BM25

## Background

I interviewed for a search role.

At paralegal.lk, I work on search stuff almost daily and I also had limited time amidst a busy work week. So I did not / could not prepare thoroughly. Given the seniority of the position, I also -- wrongly -- assumed that most questions would focus on choice of search engines (Elastic vs. Algolia vs. Typesense), deployment options, etc. So in my preparation, I thought about these "higher level" engineering details.

Most questions -- quite rightly -- however, focused on search fundamentals. Stuff I know quite well. Or, as it turns out, stuff I thought I knew quite well: I could not immediately recall answers to very basic search questions. While I could visualise in each critical step up to indexing, I totally blanked on what happens from the query side.

On the documents side, you start with a bunch of documents and their document ids. You lower case them, remove unnecessary characters (like &%), delete stop words, stem, and then create a positional inverted index. I could also remember the logical layout of the positional inverted index. I recalled that, roughly it looks something like this:

```bash
{
   "some_term":
        {its_doc_id: [postions_of_the_term_in_doc]},
}
```
But this is where my "mental visualisation" of a retrieval engine more or less ended. I could not clearly picture in my mind what happens from the query side beyond the fact that we apply to queries the same preprocessing steps we apply to the documents.

Now, in 2021, I coded up a semi complex retrieval engine that could -- besides applying bm25 as the default retrieval algorithm -- automatically handled Boolean queries (ex: term A AND NOT term B), phrase queries (exact matching on: "term C term D term E") with distance tolerance.

But during the interview, I could not remember how we exactly we fetched documents. I recalled what term frequency and inverse document frequencey are as concepts. But I could not remember the exact mathematical formula or how we apply it in the retrieval process. Even with the a repo in which I had implemented bm25 screen shared, I just blanked.

I have reflected back on the interview quite a bit. Some of it below:

It is utterly baffling to me how much I have forgotten. Those that know me well would attest to my general memory powers. I am frankly quite embarrased at how much I seem to have forgotten. May be it is simply a fact of aging (I am (only?) 33, btw). May be it is something else.

If it is entirely aging related, I am not very sure what can be done. But I do think there are other factors at play. I list them below.

Although I work in search, I don't work on it. In the two years of building on Typesense, I have not once extensively inspected the Typesense search index stored index or what stop words are being removed or how the full-text retrieval relevance scoring function is done, and so on.

There are two reasons for this:

(1) Typsesense, by design, hides all the details that make or break a search engine to give you very strong baseline performance. So, I have not really had to think much about the mechanics of the search engine: I have been content to use Typesense's APIs to handle vairous aspects of paralegal.lk.

(2) The fundamental challenge with respect to returning relevant search results at paralegal.lk, to date, remains a challenge of data. In other words, you cannot retrieve that which you have not indexed. I just finished fully indexing the reported decisions from 1978 to 2021 (Sri Lanka Law Reports). Earlier reported decisions from the early 20th century (New Law Reports) are only partially collected. So, much of my time is still spent scanning or scavenging for court decisions.

The facets of (2) are purely circumstantial but (1) is somewhat depressing, sinister even.

Typesense abstracts nearly everything that matters -- all the stuff that makes or breaks a search engine -- away from me, by design. I can of course dig deep. But, I can totally not bother and still operate a fairly relevant case law search engine.