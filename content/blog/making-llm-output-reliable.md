---
title: "Making LLM Output Reliable When the Stakes Are Real"
date: 2024-08-14
summary: "A demo only has to work once. A production system has to be trustworthy on the worst input it will ever see. The gap between those two is where most of the engineering actually lives — and where the lawsuits happen."
tags: ["LLMs", "Reliability", "Production AI"]
category: "Engineering"
draft: false
---

# The Gap Between a Demo and a System

In November 2022, a man named Jake Moffatt asked Air Canada's website chatbot about bereavement fares after his grandmother died. The bot told him he could buy a full-price ticket and apply for the discount retroactively within 90 days. That policy did not exist. When Air Canada refused the refund, Moffatt took them to the British Columbia Civil Resolution Tribunal — and in February 2024, [the tribunal ruled against the airline](https://www.americanbar.org/groups/business_law/resources/business-law-today/2024-february/bc-tribunal-confirms-companies-remain-liable-information-provided-ai-chatbot/). Air Canada had argued, remarkably, that the chatbot was "a separate legal entity responsible for its own actions." The tribunal disagreed and ordered the company to pay.

The damages were small — about CA$812. The lesson is not. A demo only has to work once: you pick the input, you run it, and if it looks good you stop. A production system has the opposite job. It has to be trustworthy on the worst input it will ever see, on a day you are not watching, for a user who will believe whatever it says and act on it.

Most of the difficulty in building with language models lives in that gap. The model is the easy part now — you can have something that sounds intelligent in an afternoon. The hard part is the part nobody films: making the output reliable enough that a person can act on it without checking your work, because a lot of the time they won't check.

When the stakes are low, you can let the model be wrong sometimes. A wrong autocomplete costs a keystroke. But the moment a human reads the output as truth and does something because of it — books a fare, files a brief, signs off on a note — "usually correct" stops being a virtue. Usually correct is just a failure you haven't met yet.

## Reliability Is Not a Bigger Model

The instinct when output is unreliable is to reach for a better model. Sometimes that helps. More often it hides the problem: the failures get rarer, so they get harder to see, so you trust the system more right as it becomes more dangerous. A 95% system fails loudly enough that you stay alert. A 99.5% system lulls you to sleep and then fails on the case you stopped watching for.

Reliability is not a property of the model. It is a property of the *system around* the model — the constraints you put on what it can say, the checks you run on what it did say, and the honesty with which you handle the cases where you simply don't know.

I think about it in three moves: **constrain the output, verify it, and make uncertainty visible.**

## Constrain Before You Generate

The cheapest failure to prevent is the one the model is never allowed to make. Free-form text is the hardest thing to trust, because anything is a valid string. The more structure you can impose, the smaller the space of ways to be wrong.

This isn't theoretical. When OpenAI shipped [Structured Outputs](https://openai.com/index/introducing-structured-outputs-in-the-api/) in August 2024 — constraining generation to a supplied JSON schema during decoding — they reported it scored **100% on their schema-compliance evals, up from under 40%** for an older model relying on prompting alone. The model didn't get smarter about the task. The output space got smaller, so a whole class of malformed-response failures simply stopped being possible.

You can lean on the same idea wherever you generate. Ask for a schema the result must conform to, and validate it before you trust it:

```python
from pydantic import BaseModel, ValidationError

class Extraction(BaseModel):
    summary: str
    amount_due: float
    due_date: str  # ISO 8601

def extract(document: str) -> Extraction | None:
    raw = model.generate(prompt(document), schema=Extraction.model_json_schema())
    try:
        return Extraction.model_validate_json(raw)
    except ValidationError:
        return None  # a caught failure beats a confident wrong answer
```

This does not make the model smarter. It makes the failure *legible*. A malformed answer becomes a `None` you can route to a fallback, a retry, or a human — instead of a plausible-looking field that quietly carries a hallucination downstream. Legible failure is worth more than rare failure, because you can build on it.

## Verify What the Model Claims

The deepest source of unreliability is that a language model has no idea whether it is right. It produces the most likely continuation, and "likely" and "true" are correlated but not the same.

The sharpest illustration I know is *Mata v. Avianca*. In 2023, a New York lawyer named Steven Schwartz used ChatGPT to research a brief, and it produced six cases — names, citations, procedural histories, quoted passages. All fabricated. Here is the part that matters for engineers: when Schwartz got nervous, [he asked ChatGPT whether the cases were real](https://en.wikipedia.org/wiki/Mata_v._Avianca,_Inc.). It said yes. He asked the unreliable system to verify itself, and it confidently confirmed its own fiction. Judge Castel sanctioned the lawyers $5,000 and made them notify every real judge they'd falsely cited.

That is the whole lesson in one anecdote: **you cannot ask the model to be correct, and you cannot ask it to confirm that it was.** You have to check it against something the model doesn't control. The most useful checks are grounded outside the model:

- **Source grounding.** If the output is supposed to come from a document, every claim should be traceable to a span of that document. A claim with no source is a guess wearing a fact's clothing. (Schwartz's six cases had no real source — a citation that resolves to nothing should have been a hard failure, not a footnote.)
- **Cross-checks.** Numbers should add up. Dates should be ordered. Entities mentioned in the conclusion should appear in the input. These are cheap, deterministic, and catch a surprising amount.
- **Adversarial reading.** A second pass — sometimes a second model — whose only job is to try to *falsify* the first answer. Not "is this good?" but "find what's wrong with this." Generation and criticism are different tasks, and asking for criticism directly catches errors that a satisfied generator never will.

None of this is glamorous. It is the boring scaffolding around the clever part. But the boring scaffolding is what lets a person trust the clever part without re-doing its work.

## Make Uncertainty Visible

The failure I respect most is the one a system admits to. A system that says "I'm not sure about this part" is more trustworthy than one that is confidently wrong, even if the confident one is right more often — because the honest one lets the human spend their attention where it's needed.

This is mostly a design decision, not a modeling one. When a check fails, when sources are thin, when the model contradicts itself across passes — surface it. Flag the field. Route it for review. Don't average the uncertainty away into a clean-looking answer that hides where the soft spots are. Air Canada's bot didn't say "I'm not certain about this policy — please confirm." It stated a refund rule with total confidence. The confidence was the failure.

There is a quiet arrogance in a system that never says "I don't know." Real expertise includes knowing the edges of what you know. We should hold our systems to the standard we'd hold a good colleague to: not flawless, but honest about where they're shaky.

## Reliability Is a Discipline, Not a Feature

You don't add reliability at the end. There's no flag to turn it on. It is the accumulated result of a hundred decisions about what the system is allowed to say, what you check before you believe it, and what you do when you're not sure — made every time, especially when it would be easier not to.

That, to me, is where engineering and character turn out to be the same thing. The discipline of building a trustworthy system is the discipline of being trustworthy yourself: doing the unglamorous work that no one sees, refusing to pass off a guess as a fact, and being honest about the limits of what you know.

A demo asks: does it work? A system asks: can someone *trust* it, on the worst day, when no one is watching? Air Canada's chatbot worked in the demo. It failed the only question that mattered. Building for that question is harder, slower, and less impressive in the room — and it is the only kind of building that matters once something real depends on the answer.
