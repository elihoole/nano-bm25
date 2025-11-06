# Craft over output

A reflection on the effects of abstraction, AI, and disembodiment.

## Background

I interviewed for a search engineering role. Since I work on search stuff everyday at [paralegal.lk](https://www.paralegal.lk), I assumed that my relevant technical knowledge is up to scratch. A busy work week meant that I went in a underprepared. Rust from not having interviewed for technical roles for nearly two years had a compounding impact.

 At the interview, most questions focused on search fundamentals: preprocessing, indexing, general purpose retrieval algorithms, etc. Stuff I know quite well. Or, stuff I thought I knew quite well. It turned out that I could not, infact, answer some basic questions.

I could visualise the critical steps up to indexing. Start with a bunch of documents, lower case the text, strip away punctuation, delete stop words, stem, and then create a positional inverted index. I could also picture the logical layout of a typical positional inverted index.

But this is where my mental model of a search engine just . . . blanked. Beyond applying the same document preprocessing steps to queries, my head was empty. The query-side mechanics - i.e., the process of retrieval - had evaporated from my memory. Even the bits that I remembered were patchy. I could, for instance, conceptually explain term frequency (TF) and inverse document frequencey (IDF). But although I recalled that IDF is a logarithmic function, the structure of its smoothed form typically implemented in retrieval engines evaded my mind.

Now, the humiliating bit. I had linked a repo from January 2023 in my CV, a Django-based case law retrieval service I'd built for a Colombo university law professor. The application used BM25 for full-text search, handled Boolean queries (ex: term A AND NOT term B), phrase queries (exact matches of the form "term C term D term E") with distance tolerance, and a few other custom retrieval mechanisms. During the online interview, I had the code open in front of me via screen share with my interviewers. Even so, I couldn't recall the basic mechanics of BM25 or how it addresses the limitations of TF-IDF scoring.

## Coda

While the constraints of the interview format -- the pressure to reply instantly, the absence of access to our primary recall mechanism in 2025, ChatGPT, and the inability to consult reference materials -- certainly didn't help me, they are merely proximate causes.

It's been two weeks since the interview and I am still astonished at how much of my "education" I seem to have forgotten. This is altogether more sobering because a not-so-small part of my identity is built on a reputation for not forgetting.

Is such forgetfulness just a fact of aging? I (only?) turned thirty-three last month. Should I resign myself to the slow and inevitable dying of the light?

I have reflected on my interview failure since. And the good news is that is that it isn't aging. The bad news is that it's just me. My subpar performance at the interview is a function of how I work. In particular, there are three factors.

### Rising abstraction

I work *with* search. I don't work on it.

[paralegal.lk](https://www.paralegal.lk) is built on the open-source search engine Typesense. In the two years of building on top of Typesense, I have never peered into the stored index structure, never audited which stop words get stripped from queries, never traced through the relevance scoring calculations that determine which cases surface first.

There are two reasons why this is the case:

(1) Typesense, by design, conceals critical detail that makes or breaks a search engine to deliver excellent out-of-the-box performance. But this convenience comes at a cost. I have not needed to think about underlying search mechanics: instead, I have been a content Typesense API monkey.

(2) The primary challenge at paralegal.lk isn't retrieval algorithms, it is data. You can't retrieve what you haven't indexed. I've spent so much of my past twelve months collecting the full corpus of Sri Lanka's reported decisions starting from the late 19th Century and I am still not done. I just completed Sri Lanka Law Reports collection which covers the period between 1978-2021, but earlier decisions, published in New Law Reports, remain incomplete. So I am still scraping and scanning, not tuning algorithms.

While the second cause is circumstantial, the first raises deeper questions about how abstraction shapes our everyday work.

In Grady Booch’s words, the story of software is one of rising abstraction. We see it most clearly in the evolution of programming languages. Today, hardly anyone writes Assembly. Even C programmers rarely think in terms of registers, flags, or instruction timing. Compilers and runtimes decide register allocation, instruction selection, inlining, and vectorization. In the 1980s, every software engineer would have had to worry about memory management. We no longer do. The same pattern repeats across the stack:

- UI: HTML/CSS/JS → component frameworks (React, Vue, Svelte)
- Hosting/Compute: bare metal → cloud VMs → serverless
- Build/Deploy: custom bash scripts → push-to-deploy (Heroku/Render) → auto-deploy with previews (Vercel/Netlify)

Now, this very march of abstraction is why software runs the world: it frees up our cognition for composition and enables API monkeys like me to write and run software that doesn't break. Yet it also means that many of us are out of touch with the low-level machinery of how software actually works.

Is there’s a point on the curve of abstraction where we stop doing our jobs as engineers? Questions once rooted in technology are now questions of economics, and in most production systems, we simply choose between "managed" services. Is a "search engineer" who simply picks between Typesense Cloud vs. Algolia for building an e-commerce site, largely basing the choice on projected monthly cost, actually doing search engineering?

### {} AI

AI, of course, didn't directly cause me to fail the interview. But over the past two years, code assistants have quietly restructured my cognitive habits. On reflection, at least some of my struggles trace back to this shift.

The interview crystallised something I have been increasingly aware of. The further I progress in my career, the less I engage the cognitive machinery that builds real understanding and deep recall. This isn't AI's fault alone. Working in a narrow machine learning (ML) domain where I already know the patterns, I can autopilot through entire weeks without straining my brain. When the path forward is reasonably obvious, there's no demand to command my full cognition.

My strength as an engineer is big-picture thinking; many observant senior engineers, to whom I’ve reported, have told me this. Details though have always required effort. Yet here’s the irony: to truly understand big pictures — ones built on mathematical insight or years of experimental results,  ones worth knowing, ones that blow your mind — I’ve had to work through the details. Symbolic reasoning only emerged from manipulating raw numerics, working through toy problems, and tracing patterns across them. Slowly, line by line, on paper. Lectures felt like wasted time. Real learning, to me, meant sitting down with a textbook, a few sheets of paper, a pen, and a calculator, and grinding through the particulars. Similarly, when it came to understanding large software systems, I had to step through the debugger and inspect intermediate values.

Early in my programming career, typing out every line forced that same focus on details. Auto-complete eroded it slightly. AI code assistants have nearly eliminated it. Now I write high-level requirements, sketch some instructions, specify critical edge cases, then watch my inanimate AI "agents" thrash out the code. Such "vibe coding" in known domains requires virtually no thinking. Before production, I just test thoroughly with tests that, again, the same agents write for me.

AI has had a similar effect as abstraction: it distances me from the details that matter. These are the details that give rise to higher-level reasoning and ground big-picture thinking. Without engaging with them, critical cognitive muscles atrophy. This has had a debilitating effect on my general intellectual sharpness and the interview exposed this viscerally. Rust has set in where there was once a well-oiled machine. Even on questions I answered correctly, thought lagged intention. Answers came slower than I would have liked.

### Losing embodied practice

A question on reciprocal rank fusion (RRF) at the interview reminded me how conceptual knowledge slips when I don’t work it by hand. To execute paralegal.lk's hybrid mode queries, Typesense fuses custom text-match scores with vector similarity using RRF. I’ve known this since the beginning, but I never had to revisit the math, for reasons I set out under the ill effects of abstraction.

Three days before the interview, I skimmed a ChatGPT explainer on RRF, and it all felt clear.
But, at the interview, it fell apart. I mistakenly recalled that the denominator  term adds a constant to raw scores from the different search components, when in fact it adds a constant to the rank assigned by each component (i.e., constant + rank k(d)).

My earlier quip on learning with paper, pen, and a calculator was a callback to my university days. As an electrical engineering undergraduate, in exams, I could only answer questions I had worked through by hand. Many modules ran on gnarly equations; writing them out was how they stuck. There was a suspect quality to formulae or sample problems I merely read.

Now, I almost never write on paper. My handwriting is both slower and more incomprehensible than ever.

There’s a parallel in code. Typing every line, as a junior engineer, burned Python’s syntax and idioms into memory. More recently, I write a lot more JavaScript but rely on AI assistants and nothing seems to stick.

In a recent interview, DHH, the creator of Ruby on Rails, had this to say:

> Where I felt this the most was, I did this remix of Ubuntu called Omakub when I switched to Linux. It's all written in Bash. I'd never written any serious amount of code in Bash before, so I was using AI to collaborate, to write a bunch of Bash with me, because I needed all this. I knew what I wanted, I could express it in Ruby, but I thought it was an interesting challenge to filter it through Bash... But what I found myself doing was asking AI for the same way of expressing a conditional, for example, in Bash over and over again. That by not typing it, I wasn't learning it. I was using it, I was getting the expression I wanted, but I wasn't learning it. I got a little scared.

Stepping away from pen, paper, and keyboard means losing touch with the essence of craft. My RRF stumble was not an isolated mistake but a symptom of disembodied practice.

## Raging against the dying of the light

Sure, a few hours of hard-nosed prep would have saved me some embarrassment. But that's not the story here. This isn't a how-to for interviews—it's a manifesto for staying sharp. How do I keep learning while building? How do I hold onto what matters beyond the next sprint? How do I keep my mind fierce and alive when APIs do the thinking and AI does the typing? This is my rallying cry. Rage, rage against the dying of the light.

### Against abstraction: getting my hands dirty in what matters

While I can't avoid abstraction, I can be conscious about what I abstract and by how much.

I don't really care that I don't know React well. Building frontends is a purely utilitarian endeavour for me. Similarly, using WSO2's Asgardeo for identity management at [paralegal.lk](https://www.paralegal.lk) is one of my better technical decisions: it saved me at least two months of development and helped avoid endless security nightmares.

But I actually love search as a computing problem. It is at the heart of everything I do at [paralegal.lk](https://www.paralegal.lk). Did I err in offloading search to Typesense APIs? It has clearly had its downsides but the losses are mostly personal. I still think I made the right call when I decided to build [paralegal.lk](https://www.paralegal.lk) on Typesense in April 2024. Monkeying around with BM25's k1 and b values when I only had a fraction of the reported case law would not have made any sense.

Now that I've finally plugged nearly every data hole, it's time to shake things up and migrate [paralegal.lk](https://www.paralegal.lk). Will I be hand-tuning how bits are packed into SSD pages? Absolutely not. The heuristic for the right level abstraction is this: am I elbow-deep in the code that actually makes or breaks what I care about?

In search, that means relevance and speed. The scoring functions that determine which document surfaces first. The index structures that decide whether a query takes milliseconds or minutes. These are the levers that actually move the needle on search quality. It is time to get my hands dirty on those parts. I will be migrating to a platform that, by design, forces me to think about the details of search. It could be Elasticsearch, it may be Lucene. I will update this post when I do make the call.

### Against AI: keeping my fingers in the sauce

Stack Overflow isn't coming back. AI isn't going away. But the real question was never "AI or no AI." The tension is a philosophical one: output or craft, productivity or competence. If I optimize purely for velocity—for pumping out as much working code as fast as possible—AI agents win every time. But if I care about my craft, if I care about sharpening my competence as an engineer, then I must deliberately slow down.

DHH articulates this beautifully:

> Now, I actually love collaborating with AI too. (But) I love chiseling my code (more), and the way I use AI is in a separate window. I don't let it drive my code. I've tried that. I've tried the Cursors and the Windsurfs and I don't enjoy that way of writing. One of the reasons I don't enjoy that way of writing is, I can literally feel competence draining out of my fingers. That level of immediacy with the material disappears . . . If you're learning how to play the guitar, you can watch as many YouTube videos as you want, you're not going to learn the guitar. You have to put your fingers on the strings to actually learn the motions. There is a parallel here to programming, where programming has to be learned in part by the actual typing.

My job interview merely confirmed what I had been sensing for some time: my skills were slowly corroding. As you become a senior engineer, you kind of assume it's normal to code less and manage more—but you rarely acknowledge or accept that this means losing competence. Each time I summoned agents to pump out another feature, I whispered to myself the same comforting lie: *I already know enough. I'm senior enough. I can become sharp when I want to.* This is the seductive danger of early promotion—the false confidence that lets competence quietly drain away:

> The joy of a programmer is to type the code myself. If I promote myself out of programming, I turn myself into a project manager, a project manager of a murder of AI crows. If you don't have your fingers in the sauce (the source) you are going to lose touch with it. There's just no other way.

What does this mean for my everyday? Following DHH's advice, I am going to stop letting AI drive my code. My immediate plan is to avoid working in "agent mode" and to keep AI tools in a separate window. Eventually, as I become a super user of vi (I'm currently using it more and more, though I'm not yet very competent), I want to move away from IDEs and just use a vi variant (like neovim) text editor to write code. The goal is to use AI only for second opinions, to look up things, and to ask embarrassing questions—but never to let AI write code for the things I care about.

### Against disembodiment: finding my pen and paper

After reflecting on how much I've lost by moving away from hands-on practice, I decided to deliberately return to more tactile, focused forms of learning. I wanted to see if reconnecting with the physical process of working through problems could help restore some of the sharpness and satisfaction I'd been missing.

Last Saturday, I took the train back from Jaffna to Colombo. Before leaving, I dusted up my copy of *Introduction to Information Retrieval* textbook by Manning et al. after four years. My scientific calculator had run out of battery; I got a new Casio ES-991 Plus from Poobalsingham Bookstore. During the journey, I hand computed BM25 scores for a query against a toy corpus I created. I turned it into a repo: [nano-bm25](https://github.com/elihoole/nano-bm25).

What surprised me most was how this process seemed to reawaken parts of my cognition that had been dormant. Working through the math by hand, I felt myself accessing the deeper symbolic reasoning I had described earlier—those faculties that only emerge when manipulating raw numerics and tracing patterns line by line. The deliberate pace and tactile satisfaction of pen on paper forced me to engage my full attention, and I could sense the difference: the quiet joy of the math on paper matching the math on code, and the unmistakable feeling of marshalling more than an ounce of my cognition, rather than just coasting on autopilot.

This was embodied learning. And I am going to do more of it.

