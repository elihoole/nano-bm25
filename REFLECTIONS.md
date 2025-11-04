# APIs and AI ate my memory: relearning BM25

## Background

I interviewed for a search role. Since I work on search stuff everyday at [paralegal.lk](https://www.paralegal.lk), I assumed my background technical knowledge is up to scratch. It was also a busy work week and I did not have much time to prepare. I also carried some rust as this was my first technical interview in over two years.

Most questions at the interview focused on search fundamentals: preprocessing, indexing, basic retrieval algorithms, etc. Stuff I know quite well. Or, stuff I thought I knew quite well. As it turns out, I was totally unable to recall answers to some of these foundational questions.

Specifically, while I could visualise in each critical step up to indexing, I totally blanked on what happens from the query side. On the documents side, you start with a bunch of documents and their document ids. You lower case the text, strip away punctuation, delete stop words, stem, and then create a positional inverted index. I could also in my head picture the logical layout of the positional inverted index.

But this is where my mental model of a search engine just . . . blanked. Beyond the fact that you apply the same preprocessing steps to queries, I had nothing. The query-side mechanics had completely evaporated from my memory. I could not recall how we fetched documents. I remembered what term frequency (TF) and inverse document frequencey (IDF) are as concepts. I vaguely remembered that idf is a log function but its smoothed form we typically implement in retrieval engines did not come to my mind.


Now, the humiliating bit. My CV linked to a repo from January 2023: a Django-based case law retrieval system I'd built for a Colombo law professor. That system used BM25, handled Boolean queries (term A AND NOT term B), phrase queries ("term C term D term E") with distance tolerance, and other custom retrieval functions. During the online interview, I had the code open in front of me via screen share with my interviewers. I still couldn't recall the basic mechanics of BM25 or how it addresses the limitations of TF-IDF scoring.

## Coda

I am astonished at how much of my "education" I appear to have forgotten. This is altogether more sobering because a not so small part of my identity is built on a reputation for not forgetting. Is such forgetfulness simply a fact of aging? I (only?) turned thirty-three last month. At the risk of sounding dramatic, is there much to be done besides raging against the dying of the light?

I have reflected on my failure to recall technical details on basic search questions quite a lot since the interview and I have a degree of confidence in pronouncing that 'no, it isn't primarily a case of aging'.

Also, while the constraints of the interview format -- the pressure to reply instantly, the absence of access to our primary recall mechanism in 2025, ChatGPT, and the inability to consult reference materials -- certainly didn't help me, they are merely proximate causes. My subpar performance at the interview is primarily a function of the peculiarities of our present-day working processes. In particular, there are three elements to it.

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

AI didn't directly cause me to fail the interview. But over the past two years, code assistants have quietly restructured my cognitive habits. On reflection, it is clear to me that at least some of my struggles trace back to this shift.

First, it has been evident to me, for sometime, that I have stopped accessing certain parts of my brain (or certain cognitive abilities). Now this is not simply down to AI per se. I have noticed this as a machine learning engineer working in a narrow domain: I already know what needs to be done. So I don't actually think too much. There is no demand to marshall all of my cognition: I can more less autopilot my way through a work week without really straining my brain.

My stronger area has always been big picture stuff: I typically require more effort to focus on the details. But, ironically, to truly understand something -- I mean the stuff that actually requires such understanding , understanding that entails a high degree of mathematical logic, symbolic reasoning etc -- I have absolutely always have had to get down to the details. I have always had to

In my early days of programming, where I had to write every line, I was forced to focus on the each minor detail.


Second, with AI code assistants, I can quite comfortably just write out requirements, provide a few high level instructions and specifiy what I consider to be critical edge cases to test against and more or less sit back and watch my inanimate "agents" thrash out the code.

This has resulted in my not accessing the part of my cogitive abilities that are



Cognitive offloading is now the default interaction pattern. Instead of retrieving from memory, I prompt. Instead of reconstructing an algorithm, I confirm a snippet. Retrieval practice — the thing that actually consolidates knowledge — is replaced by quick lookups that feel like understanding but never cross the threshold into long-term memory.

The workflow has shifted from modeling to orchestration. I used to keep a compact mental model and consult docs at the margins. Now I iterate prompts until something runs. I get the result faster, but I stop earlier, before the invariants stick: why saturation matters in BM25, where length normalization bites, how idf is actually smoothed. The job gets done; the schema never forms.

AI also floods me with plausible alternatives. Ten acceptable variants later, I have built nothing durable. The stack traces, the dead ends, the hard-won edges that anchor a concept — all evaporate with the tab. Throughput rises; retention craters.

And AI reduces friction everywhere. The very difficulty that once carved memory — the pause to derive, to test, to write by hand — is abstracted away. In production this is a feature. In an interview without the prosthesis, it is a cliff.



AI changed the cost model of thinking. I optimized for latency and got amnesia as a side effect. The fix is not abstinence; it’s paying some latency back where memory actually forms.


### Atropy


## Antidote

### Obvious one: prepare better for interviews

### Touching the parts that make or break

We must actively choose to work on stuff that makes or breaks our thing: critical stuff.

### Turning off AI

Using something like neovim while keeping AI open on browser, typing up what AI suggests in neovim instead of copy pasting?

I don’t think the remedy is “use less AI.” It is to reintroduce productive friction on purpose:
- Carve no-AI blocks for first-principles work; implement core algorithms from scratch.
- Write short, self-contained notes that explain a thing as if to future me; no links, only derivations.
- Use spaced repetition for primitives (formulas, edge cases, invariants).
- Prefer terminal and docs over chat for routine lookups.
- Time-box “prompting” and require a pen-and-paper sketch before coding.