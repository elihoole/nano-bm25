We’ll use:
- idf(t) = ln(1 + (N - df(t) + 0.5) / (df(t) + 0.5))
- score(d, q) = Σ over matched t [ idf(t) × (tf(t, d) × (k1 + 1)) / (tf(t, d) + k1 × (1 − b + b × dl/avgdl)) ]
- Parameters: k1 = 1.2, b = 0.75

Numbers for this index and query terms:
- N = 10
- df: sident = 2, usa = 2, rule = 1, constitu = 2
- idf: sident ≈ 1.4816, usa ≈ 1.4816, constitu ≈ 1.4816, rule ≈ 1.9924
- doc lengths (dl): dl("4") = 26, dl("5") = 12, avgdl = 9.0

Doc 4 (matches: sident=1, usa=4)
- C4 = 1 − b + b × dl/avgdl = 0.25 + 0.75 × (26/9) ≈ 2.4167
- sident: weighted_tf = (1 × 2.2) / (1 + 1.2 × C4) = 2.2 / (1 + 2.9000) ≈ 0.5641; contrib = 1.4816 × 0.5641 ≈ 0.8358
- usa:    weighted_tf = (4 × 2.2) / (4 + 1.2 × C4) = 8.8 / (4 + 2.9000) ≈ 1.2754; contrib = 1.4816 × 1.2754 ≈ 1.8896
- Score(4) ≈ 0.8358 + 1.8896 = 2.7254

Doc 5 (matches: sident=1, usa=1, rule=1, constitu=1)
- C5 = 1 − b + b × dl/avgdl = 0.25 + 0.75 × (12/9) = 1.25
- For tf=1: weighted_tf = 2.2 / (1 + 1.2 × 1.25) = 2.2 / 2.5 = 0.88
- sident:   1.4816 × 0.88 ≈ 1.3038
- usa:      1.4816 × 0.88 ≈ 1.3038
- constitu: 1.4816 × 0.88 ≈ 1.3038
- rule:     1.9924 × 0.88 ≈ 1.7533
- Score(5) ≈ 1.3038 + 1.3038 + 1.3038 + 1.7533 = 5.6648

Result and intuition:
- BM25 ranks doc 5 above doc 4 (5.6648 > 2.7254).
- Repetition of a common term in doc 4 saturates and is further tempered by length normalization, while doc 5’s broader coverage of discriminative terms (including rule) is rewarded.
- This demonstrates why BM25’s tunable saturation and length normalization outperform even sublinear TF-IDF.

Verification snapshot (from the script run used above):

```bash
Total documents (N): 10
Document lengths (dl): {'1': 4, '2': 7, '3': 9, '4': 26, '5': 12, '6': 9, '7': 9, '9': 5, '8': 4, '10': 5}
Average document length (avgdl): 9.0
Document Term Frequencies (for query terms): {'4': defaultdict(<class 'int'>, {'usa': 4, 'sident': 1}), '5': defaultdict(<class 'int'>, {'usa': 1, 'constitu': 1, 'rule': 1, 'sident': 1}), '2': defaultdict(<class 'int'>, {'constitu': 1}), '8': defaultdict(<class 'int'>, {'?': 1}), '10': defaultdict(<class 'int'>, {'?': 1})}
Term IDFs: {'usa': 1.4816045409242156, 'constitu': 1.4816045409242156, '?': 1.4816045409242156, 'rule': 1.992430164690206, 'sident': 1.4816045409242156}
Length normalization factors (C): {'1': '0.5833', '2': '0.8333', '3': '1.0000', '4': '2.4167', '5': '1.2500', '6': '1.0000', '7': '1.0000', '9': '0.6667', '8': '0.5833', '10': '0.6667'}
Doc 4, Term 'usa': denom=6.9, c=2.4167, tf=4, idf=1.4816, bm25_weighted_tf=1.2754, score_t=1.8896
---
Doc 4, Term 'sident': denom=3.9, c=2.4167, tf=1, idf=1.4816, bm25_weighted_tf=0.5641, score_t=0.8358
---
Doc 5, Term 'usa': denom=2.5, c=1.2500, tf=1, idf=1.4816, bm25_weighted_tf=0.8800, score_t=1.3038
---
Doc 5, Term 'constitu': denom=2.5, c=1.2500, tf=1, idf=1.4816, bm25_weighted_tf=0.8800, score_t=1.3038
---
Doc 5, Term 'rule': denom=2.5, c=1.2500, tf=1, idf=1.9924, bm25_weighted_tf=0.8800, score_t=1.7533
---
Doc 5, Term 'sident': denom=2.5, c=1.2500, tf=1, idf=1.4816, bm25_weighted_tf=0.8800, score_t=1.3038
---
BM25 Weighted TFs: {('4', 'usa'): 1.2753623188405798, ('4', 'sident'): 0.5641025641025642, ('5', 'usa'): 0.8800000000000001, ('5', 'constitu'): 0.8800000000000001, ('5', 'rule'): 0.8800000000000001, ('5', 'sident'): 0.8800000000000001}
Document BM25 Scores: {'4': 2.725359523439193, '5': 5.664774532967311}
Ranked Documents (BM25): [('5', 5.664774532967311), ('4', 2.725359523439193)]
```


### Exploring the effects of BM25 knobs (k1 and b)

Here’s the precise math and how it plays out on this repo’s tiny corpus and the running example query.

BM25 per-term weight in this repo is:

- idf(t) = ln(1 + (N - df(t) + 0.5) / (df(t) + 0.5))
- tf-saturation f(tf) = tf (k1+1) / (tf + k1 C), where C = 1 - b + b · dl/avgdl
- score(d, q) = Σ over matched t [ idf(t) · f(tf(t, d)) ]

Corpus stats for the demo query ["sident", "usa", "rule", "constitu"]:
- N = 10
- df: sident=2, usa=2, rule=1, constitu=2
- idf: sident≈1.4816, usa≈1.4816, rule≈1.9924, constitu≈1.4816
- doc lengths (dl): dl(4)=26, dl(5)=12, avgdl=9.0

Term frequencies for the two most relevant docs:
- doc 4: {sident:1, usa:4}
- doc 5: {sident:1, usa:1, rule:1, constitu:1}

1) What k1 does (TF saturation)
- Small k1 → early saturation (repetition flattens quickly)
- Large k1 → slower saturation (behaves more like linear TF)

On this corpus (b=0.75):
- k1=0.3 → score(4)≈2.7471, score(5)≈6.0861
- k1=1.2 → score(4)≈2.7254, score(5)≈5.6648
- k1=4.0 → score(4)≈2.8627, score(5)≈5.3644
- k1→∞ → score(4)≈3.0654, score(5)≈5.1498

Take the limit as k1→∞ for a fixed document (C fixed):
- f(tf) = tf (k1+1) / (tf + k1 C) → tf / C
- So w(t,d) → idf(t) · tf / C, i.e., linear TF×IDF scaled by 1/C.

Intuition here: increasing k1 raises the ceiling on how much repetition can help, but doc 5 still wins because it matches more discriminative terms; doc 4’s repetition of a common term (usa) saturates and never catches up.

2) What b does (length normalization)
- b=0.0 → no length normalization (C=1 for all docs)
- b=1.0 → full normalization by dl/avgdl
- Higher b penalizes longer-than-average docs more (and helps shorter ones)

On this corpus (k1=1.2):
- b=0.0 → score(4)≈3.9889, score(5)≈6.4372
- b=0.75 → score(4)≈2.7254, score(5)≈5.6648
- b=1.0 → score(4)≈2.4759, score(5)≈5.4469

Why: C = 1 - b + b · dl/avgdl. With dl(4)=26, dl(5)=12, avgdl=9:
- C4≈0.25 + 0.75·(26/9)≈2.4167 (larger denom → stronger dampening)
- C5≈0.25 + 0.75·(12/9)≈1.25

As b increases, doc 4 (longer) is penalized more than doc 5 (closer to average), widening the gap in favor of doc 5. With b=0, both behave like unnormalized TF×IDF with saturation, so absolute scores rise for both.

3) Visual-style reasoning (fixed doc)
- For tf ≪ k1·C: f(tf) ≈ tf · (k1+1)/(k1·C) (almost linear in tf)
- For tf ≫ k1·C: f(tf) ≈ k1+1 (saturates to a plateau)

So:
- k1 small → early plateau; model behaves closer to binary presence
- k1 large → nearly linear TF (until very large tf); model behaves closer to TF×IDF

Bottom line for this repo’s example:
- Reasonable defaults (k1≈1.2, b≈0.75) make doc 5 outrank doc 4 because it covers more discriminative terms. Repetition of a common term in a longer doc can’t overpower that coverage due to saturation and length normalization.



Cognitive offloading is now the default interaction pattern. Instead of retrieving from memory, I prompt. Instead of reconstructing an algorithm, I confirm a snippet. Retrieval practice — the thing that actually consolidates knowledge — is replaced by quick lookups that feel like understanding but never cross the threshold into long-term memory.

The workflow has shifted from modeling to orchestration. I used to keep a compact mental model and consult docs at the margins. Now I iterate prompts until something runs. I get the result faster, but I stop earlier, before the invariants stick: why saturation matters in BM25, where length normalization bites, how idf is actually smoothed. The job gets done; the schema never forms.

AI also floods me with plausible alternatives. Ten acceptable variants later, I have built nothing durable. The stack traces, the dead ends, the hard-won edges that anchor a concept — all evaporate with the tab. Throughput rises; retention craters.

And AI reduces friction everywhere. The very difficulty that once carved memory — the pause to derive, to test, to write by hand — is abstracted away. In production this is a feature. In an interview without the prosthesis, it is a cliff.



AI changed the cost model of thinking. I optimized for latency and got amnesia as a side effect. The fix is not abstinence; it’s paying some latency back where memory actually forms.


## notes
### Fighting abstraction: Touching the parts that make or break that which we do

Thesis: we can't avoid abstraction. But we can be conscious about what we abstract and how much we abstract. I don't really care that I don't know React well. Building frontends is not something I see myself doing . it does not really interest me beyond its immediate utility. But I love search and the core of paralegal.lk is search. So I should not really off load too much of search if I want paralegal.lk to teach me about search. Good heuristic to know what level of abstraction is a good level of abstraction: are we actively touching parts of the code that make or break that which we care about. so in search stff that matters to final search relevance - stuff that determines whether search is taking milliseconds or minutes -- we must be getting our hands dirty on those. This is how we fight abstraction.

### Fighting AI:


Thesis: there's no going back to the good old days of Stack Overflow. There is no turning off AI. Can we still not use agent mode? Can we have . In the words of DHH:

Now, I actually love collaborating with AI too. I love chiseling my code, and the way I use AI is in a separate window. I don’t let it drive my code. I’ve tried that. I’ve tried the Cursors and the Windsurfs and I don’t enjoy that way of writing.
(01:29:03) One of the reasons I don’t enjoy that way of writing is, I can literally feel competence draining out of my fingers. That level of immediacy with the material disappears.

9:03) One of the reasons I don’t enjoy that way of writing is, I can literally feel competence draining out of my fingers. That level of immediacy with the material disappears. Where I felt this the most was, I did this remix of Ubuntu called Omakub when I switched to Linux. It’s all written in Bash. I’d never written any serious amount of code in Bash before, so I was using AI to collaborate, to write a bunch of Bash with me, because I needed all this. I knew what I wanted, I could express it in Ruby, but I thought it was an interesting challenge to filter it through Bash. Because what I was doing was setting up a Linux machine, that’s basically what Bash was designed for. It’s a great constraint. But what I found myself doing was asking AI for the same way of expressing a conditional, for example, in Bash over and over again. That by not typing it, I wasn’t learning it. I was using it, I was getting the expression I wanted, but I wasn’t learning it. I got a little scared.
(01:30:08) I got a little scared, is this the end of learning? Am I no longer learning if I’m not typing? The way I, for me, recast that was, I don’t want to give up on the AI. It’s such a better experience as a programmer to look up APIs, to get a second opinion on something, to do a draft, but I have to do the typing myself because you learn with your fingers. If you’re learning how to play the guitar, you can watch as many YouTube videos as you want, you’re not going to learn the guitar. You have to put your fingers on the strings to actually learn the motions. I think there is a parallel here to programming, where programming has to be learned in part by the actual typing.

But I think the more crucial aspect for me is, I really care about the competence. I’ve seen what happens to even great programmers the moment they put away the keyboard, because even before AI, this would happen as soon as people would get promoted.

 If you don’t have your fingers in the sauce (the source) you are going to lose touch with it. There’s just no other way. I don’t want that because I enjoy it too much. … The joy of a programmer, … is to type the code myself

So time to switch to neovim or some text editor and AI on browser.

### Fighting anti embodiment


Parts covered earlier also. We'll end with a story. Last saturday I took the train back from jaffna to colombo. And I  had Information Retrieval text book (physical) by Manning et al. I opened that book after four years. I worked through BM25 by hand on a toy corpus I created. I wrote nano-bm25 repo. I have had the book since my edinburgh uni days. My calculators had run out of battery. I got a new Es 991 plus casio.

I did the math by hand. On paper.  step by step. It was slow at the start but I tasted some of the joys of my engineering undergraduate days. :)
https://github.com/elihoole/nano-bm25