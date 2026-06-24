---
title: "synopso: A Daily AI Paper Briefing, Built as a Pipeline"
date: 2024-12-01
summary: "A pipeline I built that wakes up each morning, finds the day's most-discussed AI papers on HuggingFace, downloads and reads them, and delivers a Telegram briefing — without me lifting a finger."
tags: ["LLMs", "Pipelines", "Automation"]
category: "Work"
draft: false
---

# synopso

**synopso** is a pipeline I built to solve a specific kind of fatigue: the feeling of perpetually falling behind on AI research. Not because papers aren't interesting — they are — but because there are too many of them and no clean way to triage. synopso runs daily, scrapes HuggingFace's trending papers page, downloads and reads each PDF, summarizes the work using an LLM, and pushes a structured briefing to a Telegram channel. By the time I make coffee, the relevant papers from the day before are already waiting.

- **Code:** [github.com/karanjakhar7/synopso](https://github.com/karanjakhar7/synopso)

## Start downstream of the firehose

The first design decision was where to get papers from. ArXiv publishes hundreds of papers a day across cs.AI, cs.LG, cs.CL, and related categories. Ingesting all of them and then filtering is a tractable problem, but it's the wrong problem — most of those papers don't matter to most people.

HuggingFace's papers page is a better signal. It surfaces papers that researchers are actively bookmarking and discussing, which means the community has already done the first pass. synopso begins there: scrape the page for ArXiv IDs, fetch titles and authors directly from each paper's ArXiv HTML, then download the PDFs in parallel. The source isn't raw volume — it's the subset that's already earned attention.

## Two concurrency models, each in its right place

The download and summarization stages both want concurrency, but for different reasons, and the wrong model makes things slower, not faster.

PDF downloads are blocking HTTP requests. `asyncio` is the wrong tool there — it can't actually parallelize synchronous I/O, it just interleaves waits. Instead, a `ThreadPoolExecutor` with eight workers downloads all PDFs truly in parallel. Each thread blocks independently; no one waits for the others.

Summarization flips the picture. LLM API calls are async-native, and running them with threads would mean spinning up a thread per request and blocking on a coroutine — wasteful. Here, `asyncio.gather` fans out five papers concurrently, each awaiting its LLM response. Batch size of five is a deliberate pact with the rate limit: fast enough to finish a full day's papers quickly, conservative enough to stay inside per-minute quotas without special-casing anything.

The rule I ended up with: thread pools for blocking I/O, async for I/O-bound coroutines. Mixing them is where things get slow.

## The LLM as a one-job contractor

The summarization step is intentionally narrow. The model receives a paper's title, authors, and full extracted text, and it returns a summary. That's it. It doesn't decide which papers are important (the HuggingFace signal does that), it doesn't format the Telegram message (the delivery layer does that), and it doesn't retry its own failures (the router does that). Giving the model a single, well-defined job keeps the prompt stable and makes failures easy to diagnose — a bad summary means a bad paper or a bad prompt, not an entangled failure across multiple responsibilities.

LiteLLM handles the provider side. The model is a single environment variable — `gemini/gemini-3.1-flash-lite` today, something else tomorrow, no code change required. The router also manages retries and optional RPM/TPM ceilings, so the rate-limit contract from the download stage holds through summarization too.

## The stack

Python 3.12, `asyncio` and `ThreadPoolExecutor` for the two concurrency layers, [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for scraping HuggingFace and ArXiv HTML, [PyPDF](https://pypdf.readthedocs.io/) for text extraction, [LiteLLM](https://docs.litellm.ai/) for model routing and retries, and [python-telegram-bot](https://python-telegram-bot.org/) for delivery. No database — papers live in a local directory per run, and output is ephemeral by design. Deployment is a single GitHub Actions workflow: a `schedule: cron` trigger, API keys stored as repository secrets, and `uv run python -m core.main`. The pipeline runs in a few minutes and sits comfortably inside the free tier — zero infrastructure, zero maintenance.

---

*If you're building research tooling or personal automation pipelines on top of LLMs, I'd enjoy comparing notes — [reach out](/#contact).*