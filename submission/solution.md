# Kuku Legal Intake Assistant

**Problem chosen: Problem 2 - AI lawyer**

## Problem and scope

People facing a rental or eviction dispute often contact a lawyer with a long, incomplete story. Important dates, payment records, messages, and lease details can be hard to assemble. I chose one step of that problem: help a tenant prepare a clear intake note before speaking with a lawyer. The prototype organizes the facts the person supplied, builds a timeline, identifies missing details, and points to relevant retrieved material when available.

I chose this scope because the existing project already has a legal-document retrieval pipeline and a terminal interface. A structured intake note is narrow enough to review against the user's original facts. It does not decide whether the landlord acted lawfully, predict a court result, or replace a lawyer.

## Assumptions

- The user is asking about a rental or eviction concern in India.
- The user provides the facts; the system must label unknowns instead of filling them in.
- The local knowledge base contains the legal materials that may support an answer. Missing or stale material must be disclosed.
- A lawyer or trained human reviews important conclusions. The prototype provides general information only.
- Kuku's assignment input pack is confidential. It is used locally and is excluded from the public repository.

## How the prototype works

`build_knowledge_base.py` reads authorized local JSON and compressed JSONL files, splits text into overlapping chunks, and stores them in a persistent Chroma collection. `agent.py` retrieves three passages at a time and can ask for up to two follow-up searches. `agent_multirag.py` generates complementary search queries before retrieving. `llm_client.py` sends the question and retrieved passages to Groq. The prompt asks for a concise intake note, separates stated facts from gaps, and forbids unsupported legal claims.

The current interface is a Python CLI, not a deployed web app. The public prototype link is the repository; setup and run instructions are in its README. No user identity or case file is persisted by the current CLI beyond the process's in-memory conversation history.

## Scale and human review

To support more Kuku legal issue types, keep the same intake step and add a reviewed source collection and output checklist for each issue type. Store source version and jurisdiction metadata, test new sources before indexing, and route low-confidence or unsupported questions to a human. At higher volume, move Chroma to a managed vector store, add per-session storage and access controls, and monitor retrieval quality, latency, and model spend. The present prototype makes roughly two model calls in multi-query mode, or up to three in iterative mode; actual cost depends on current provider rates and token volume.

## How I would judge it

Run a pilot with 20 consented, anonymized rental-intake cases. Have a lawyer or trained reviewer compare each generated note with the source facts and retrieved provisions. Track: (1) key facts retained, (2) timeline order, (3) missing questions that matter, (4) unsupported legal claims, (5) source relevance, and (6) time saved versus the team's current intake. A reasonable launch gate is at least 18/20 notes rated usable with no material invented fact, plus a measured reduction in intake preparation time. These are proposed thresholds, not achieved results.

## Current result and known failures

The code and retrieval flow are present, but this submission run did not produce a successful AI answer: the supplied live run returned Groq HTTP 403, “Access denied. Please check your network settings.” The current environment also lacks a usable Python interpreter, so I could not rerun the app or produce successful raw model outputs here. The exact reported error and three reproducible test prompts are included in `raw_outputs/`. After Groq access and local Python are available, run `run_test_cases.ps1` to capture unedited per-case outputs. Do not claim the quality targets above until those runs and human review are complete.

**Prototype:** https://github.com/Akash-M-100/AI-LAWYER-
