---
title: "Marvix AI: Building an Ambient Scribe from Scratch"
date: 2024-09-03
summary: "What I'm building at Marvix AI — an ambient scribe that listens, understands, and writes so people don't have to — and what it takes to make AI dependable enough to disappear into someone's workflow."
tags: ["Marvix AI", "Ambient Scribe", "LLMs"]
category: "Work"
draft: false
---

# Building an Ambient Scribe

I'm the founding engineer at [Marvix AI](https://marvix.ai), where we're building an ambient scribe: software that quietly listens to a conversation and turns it into accurate, structured notes, so the people in the room can stay in the room instead of typing.

I joined when the repository was empty. Since then I've owned the parts that turn a promising demo into something people can actually depend on — the language-model pipeline that does the understanding, the retrieval layer that grounds it in real context, and the backend that has to be fast and correct every single time, not just when someone is watching.

## What "ambient" actually demands

The word *ambient* hides how hard the problem is. To disappear into someone's workflow, the system has to clear a bar that a flashy demo never has to:

- **It has to be trusted.** The output is read as truth and acted on. "Usually right" isn't good enough when a person stops double-checking.
- **It has to be fast.** Ambient means nobody waits for it. The work happens at the speed of the conversation, not after it.
- **It has to fail honestly.** When the system isn't sure, it has to say so, instead of smoothing over the gap with a confident guess.

Most of the engineering lives in those three constraints, not in the model itself. The model is the easy part now. Making its output dependable — constrained, verified, and honest about its own uncertainty — is the actual work. (I wrote more about that craft in [Making LLM Output Reliable When the Stakes Are Real](/blog/making-llm-output-reliable/).)

## What I've owned

Building this from scratch has meant working across the whole stack rather than a slice of it:

- The **LLM pipeline** that listens, understands, and structures — and the evaluation harness that tells us when it's drifting.
- The **retrieval layer** that grounds the output in the right context so it isn't guessing.
- The **production backend** — the APIs, the data flow, the system design that keeps it reliable under real-world load.

Taking a product from an empty repo to something people rely on teaches you things that no individual ticket does: where the system breaks under real input, what reliability actually costs, and which corners you can never cut. That's the part of this work I care about most.

---

*If you're working on something in this space, or just want to compare notes on building dependable AI systems, I'd genuinely enjoy the conversation — [reach out](/#contact).*
