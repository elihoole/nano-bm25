# APIs and AI ate my memory: relearning BM25

## Background

I interviewed for a search role. Since I work on search stuff everyday at [paralegal.lk](https://www.paralegal.lk), I assumed my background technical knowledge is up to scratch. It was also a busy work week and I did not have much time to prepare.

Most questions at the interview focused on search fundamentals: preprocessing, indexing, basic retrieval algorithms, etc. Stuff I know quite well. Or, stuff I thought I knew quite well. As it turns out, I was totally unable to recall answers to some of these foundational questions.

Specifically, while I could visualise in each critical step up to indexing, I totally blanked on what happens from the query side. On the documents side, you start with a bunch of documents and their document ids. You lower case the text, strip away punctuation, delete stop words, stem, and then create a positional inverted index. I could also in my head picture the logical layout of the positional inverted index.

But this is where my mental model of a search engine just . . . blanked. Beyond the fact that you apply the same preprocessing steps to queries, I had nothing. The query-side mechanics had completely evaporated from my memory. I could not recall how we fetched documents. I remembered what term frequency (TF) and inverse document frequencey (IDF) are as concepts. I vaguely remembered that idf is a log function but its smoothed form we typically implement in retrieval engines did not come to my mind.


Now, the humiliating bit. My CV linked to a repo from January 2023: a Django-based case law retrieval system I'd built for a Colombo law professor. That system used BM25, handled Boolean queries (term A AND NOT term B), phrase queries ("term C term D term E") with distance tolerance, and other custom retrieval functions. During the online interview, I had the code open in front of me via screen share with my interviewers. I still couldn't recall the basic mechanics of BM25 or how it addresses the limitations of TF-IDF scoring.

## Coda

I am astonished at how much of my "education" I appear to have forgotten. This is altogether more sobering because a not so small part of my identity is built on a reputation for not forgetting. Is such forgetfulness simply a fact of aging? I (only?) turned thirty-three last month. At the risk of sounding dramatic, is there much to be done besides raging against the dying of the light?

I have reflected on my failure to recall technical details on basic search questions quite a lot since the interview and I have a degree of confidence in pronouncing that 'no, it isn't primarily a case of aging'.

Also, while the constraints of the interview format -- the pressure to reply instantly, the absence of access to our primary recall mechanism in 2025, ChatGPT, and the inability to consult reference materials -- certainly didn't help me, they are merely proximate causes.

My subpar performance at the interview is primarily a function of the peculiarities of our present-day working processes. In particular, there are three elements to it.

### Abstraction

Although I work in search, I don't work on it. Paralegal.lk is built on the open-source search engine Typesense. In the two years of building on Typesense, I have never peered into the stored index structure, never audited which stop words get stripped from queries, never traced through the relevance scoring calculations that determine which cases surface first.

There are two reasons for this:

(1) Typesense, by design, conceals every detail that makes or breaks a search engine to deliver excellent out-of-the-box performance. But this convenience comes at a cost. I have not needed to think about the underlying search mechanics: instead, I have been a content Typesense API monkey.

(2) The real problem at paralegal.lk isn't search mechanics—it's data. You can't retrieve what you haven't indexed. I've just finished indexing 1978–2021 (Sri Lanka Law Reports), but earlier 20th-century decisions (New Law Reports) remain scattered and incomplete. Most of my time goes to hunting down cases, not tuning algorithms.

While the second cause is purely circumstantial, the first cause raises questions about the effect of abstraction on our everyday work.

In Grady Booch’s words, the story of software is one of rising abstraction. You see it most clearly in the evalution of programming languages. Almost no one writes Assembly. Even C programmers rarely think in terms of registers, flags, or instruction timing. Compilers and runtimes decide register allocation, instruction selection, inlining, and vectorization. In the 1980s, every software engineer would have had to worry about memory management. The vast majority no longer does so. The same pattern repeats across the stack:

- UI: HTML/CSS/JS → component frameworks (React, Vue, Svelte)
- Hosting/Compute: bare metal → cloud VMs → serverless
- Build/Deploy: custom bash scripts → push-to-deploy (Heroku/Render) → auto-deploy with previews (Vercel/Netlify)

Now, this very march of abstraction is why software runs the world: it frees up our cognition for composition and enables API monkeys to write and run software that does't break. Yet it also means that many of us — including me — are out of touch with the low-level machinery of how software actually works. Questions once rooted in technology are now questions of economics, and for nearly every requirement we simply choose between "managed" services.

It appears to me that there is a threshold of abstraction at which point we essentially cease doing our jobs. Is a data engineer who simply picks between Amazon Lake Formation vs. Google Cloud Dataplex for building a centralised data lake with fine-grained access control, choosing primarily on projected monthly cost, really doing data engineering?

### AI

