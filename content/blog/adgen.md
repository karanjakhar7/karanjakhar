---
title: "adgen: From a One-Line Brief to a Ranked Ad Campaign"
date: 2026-06-24
summary: "A system I built that turns a one-sentence business description into ranked publisher recommendations, persona-tuned ad creative, and a structured campaign config — and is honest enough to recommend nothing when the fit isn't there."
tags: ["LLMs", "Ad Tech", "Pipelines"]
category: "Work"
draft: false
---

# adgen

**adgen** is a system I built that takes a single sentence about a business — *"We sell premium dog food for senior dogs, for owners who care about joint health"* — and turns it into a working ad campaign: a ranked list of publishers to run on, three to five ad variants written for specific audience personas, and a structured campaign config with budget allocation, targeting, and bid strategy.

Advertisers usually wrestle with three tangled questions at once: *where* to run, *what* copy will actually land, and *how* to structure the whole thing into something a campaign tool can ingest. adgen answers all three from one line of input, against a catalog of publishers and personas the user supplies (or the bundled sample data).

- **Live demo:** [adgen-puce.vercel.app](https://adgen-puce.vercel.app)
- **Code:** [github.com/karanjakhar7/adgen](https://github.com/karanjakhar7/adgen)

## Code does math, the model does judgment

The cleanest decision in the whole system was deciding what the language model is *not* allowed to do. Anything mechanical — AOV ratios, demographic overlap, category matching, budget arithmetic, serializing the final config — is deterministic, testable code. The model is reserved for the things only it can do: reading a messy human brief, judging qualitative fit, and writing copy.

Ranking is where this pays off. Instead of a pure weighted formula or a pure "ask the LLM to rank everything," it's a hybrid: code precomputes the hard signals, then the model scores each publisher in `[0,1]` using those signals *plus* the publisher's qualitative notes, and explains itself. One publisher's note says its "playful, impulse-driven voice converts best" — for a clinical, premium senior-dog-food brand that's a tone clash, and the model catches it where an embedding-similarity match never would. Every score ships with a `fit_reasons` field, so nothing is a black box.

## A pipeline split by temperature

adgen runs as six stages, and the reason they're separate calls is almost embarrassingly simple: different jobs want different temperatures. Ranking needs to be deterministic, so it runs at temperature ≈ 0. Creative needs variety, so it runs at ≈ 0.8. Once you split for that reason, everything else falls out for free — per-stage model routing, independent retries, and the ability to evaluate each stage on its own.

The creative stage fans out across personas in parallel (`asyncio.gather`), generating one headline/body/CTA per persona. Each variant is conditioned on three things: the persona, a distinct single-minded message angle assigned upstream, and the *placement* — the same product gets pitched differently on a $28-AOV late-night impulse site than on an affluent, considered one.

## Honest about bad fit

The part I'm most proud of is what adgen does when the answer is "no." Most systems force-fit a recommendation. adgen can recommend *zero* publishers if the catalog genuinely doesn't suit the advertiser, flag a weak price-fit instead of pretending, gate off-topic briefs before they waste a pipeline run, and surface the assumptions it made rather than quietly inventing facts. Recommendations are threshold-based, not top-K, so a bad catalog produces an honest empty list — not a confidently wrong one. I [wrote separately](/blog/making-llm-output-reliable/) about why that kind of honesty is the actual engineering, not a nicety.

## The stack

Python 3.12 with `asyncio`, [FastAPI](https://fastapi.tiangolo.com/) serving a server-sent-events UI that streams progress stage by stage, [LiteLLM](https://docs.litellm.ai/) so the model provider is pure config (swap Gemini for Claude with an env var), and [Pydantic v2](https://docs.pydantic.dev/) as the typed contract between stages with a validate-and-repair loop. No database by design — the catalog fits in context, and per-run output is written to flat files. There's also an evaluation harness that checks the deterministic invariants (allocations sum to 100%, ceilings respected) and pits the LLM ranker against a trivial category-match baseline. Deployed on Vercel.

---

*If you're building generative systems that have to be trusted, not just demoed, I'd enjoy comparing notes — [reach out](/#contact).*
