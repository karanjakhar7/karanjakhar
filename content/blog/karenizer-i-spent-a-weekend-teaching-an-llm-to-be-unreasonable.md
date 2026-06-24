---
title: "karenizer: I Spent a Weekend Teaching an LLM to Be Unreasonable"
date: 2026-06-25
summary: "A web app that turns your boring complaints into increasingly unhinged Karen-level letters — because sometimes the cold, factual version just doesn't capture how you truly feel about a lukewarm latte."
tags: ["LLMs", "Prompt Engineering", "FastAPI", "Irrationality"]
category: "Work"
draft: false
---

# karenizer

**karenizer** is a web app that takes your ordinary grievance — the wrong order, the rude rep, the package that arrived looking like it was delivered by a trebuchet — and transforms it into a full-throated, theatrically escalating complaint letter. You pick how unhinged you want it: from "Politely Disappointed" (a calm adult) all the way to "PEAK KAREN" (an entity addressing the CEO of a coffee chain as though they personally wronged the founding fathers). It is a deeply silly project. I am not sorry.

- **Live demo:** [karenizer.vercel.app](https://karenizer.vercel.app)
- **Code:** [github.com/karanjakhar7/karenizer](https://github.com/karanjakhar7/karenizer)

## The whole thing is a prompt engineering exercise dressed as a joke

There are six Karen levels. Each one is a distinct system prompt, hand-tuned until it hit the right note. Level 0 is professional and measured. Level 3 has the LLM demand a manager, threaten Yelp, and deploy strategic capital letters FOR EMPHASIS. Level 5 — Peak Karen — instructs the model to invoke "the spirit of every wronged customer in history" and implies the grievance will be discussed on national television.

Writing six system prompts that produce reliably *different* tones without bleeding into each other is actually non-trivial. Level 2 needs to feel annoyed-but-controlled; Level 3 needs the switch to have flipped but not melted. Getting that gradient right meant a lot of test complaints about cold soup. Science demands sacrifice.

The intensity scale isn't cosmetic — it's the product. The same "my pizza was cold" turns into a completely different artifact at each level, and watching the tone shift is what makes it funny. The UI has a slider with an emoji that updates as you drag, because if you're building something this ridiculous, the feedback loop should be immediate.

## The model does drama. The code does nothing interesting.

There's no ranking, no scoring, no multi-stage pipeline here. This is one API call, which is actually the correct choice. The job is purely expressive: take a description and produce theatrical text. There's no deterministic logic to offload, no place where code is more reliable than the model.

What the code *does* handle: building the user prompt from the form fields (company name, category, the specific grievance), picking the right system prompt from a dictionary keyed by level, and validating the request so nobody submits a 10,000-character rant that costs me real money. Pydantic handles the typing. FastAPI handles the routing. LiteLLM handles talking to whatever model is configured via environment variable — I ran on Claude during development and swapped to another provider for deployment with a one-line change. That abstraction earns its keep on a project like this where the model is literally the entire product.

Temperature is `0.85`. High enough that two identical complaints generate meaningfully different letters; low enough that Level 5 doesn't veer into actual gibberish. It took about four tries to land on that number, which I mention only because "tune your temperature" is advice that sounds obvious until you're reading output that's either too stiff or has started making up legal citations.

## No framework, no database, no problem

The frontend is vanilla HTML, CSS, and about a hundred lines of JavaScript. No React. No build step. No `node_modules` folder to make the repo feel heavy. A form submits to `/api/generate`, a hidden div swaps in with the result, a button copies it to clipboard. That's the whole interaction.

This was deliberate. When the entire product is one API call and one text box, a frontend framework is a solution looking for a problem. The constraint of "no framework" also made deployment on Vercel's Python runtime almost trivially easy — there's no build pipeline to configure, just a FastAPI app with an `api/index.py` entry point and a twelve-line `vercel.json`.

## The stack

Python 3.12, [FastAPI](https://fastapi.tiangolo.com/) for the API and Jinja2 templating, [LiteLLM](https://docs.litellm.ai/) for model routing, [Pydantic v2](https://docs.pydantic.dev/) for request validation, and plain HTML/CSS/JS for the UI. Deployed on Vercel. Three runtime dependencies. No database — there's nothing to persist; the letter exists, you copy it, it's gone. I like systems with no state to corrupt.

---

*If you've built something equally useless but technically honest, I'd enjoy hearing about it — [reach out](/#contact).*
