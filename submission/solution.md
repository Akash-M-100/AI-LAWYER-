# Kuku Consumer Dispute Intake Assistant

**Problem 2: AI lawyer | One step: prepare a clear intake note for an Indian consumer purchase or paid-service dispute.**

## The situation and problem I chose

A person may know what happened but not know which details matter: purchase and delivery dates, payment proof, seller responses, refund status, or warranty records. A scattered story slows the next conversation with a support team or lawyer. I chose intake preparation for issues such as a missing delivery, defective product, or cancelled event. The project already contains a local legal search pipeline and a large legal/case-material collection; this makes intake a concrete and checkable use of the existing work.

### The output

The user's stated facts, an ordered timeline, important unanswered questions, relevant retrieved legal material when available, and an evidence checklist. It does not decide liability, guarantee a refund, predict an outcome, or replace a lawyer.

## Assumptions and guardrails

- The user asks about an Indian consumer purchase or paid service and provides relevant facts.
- The local corpus may be incomplete or out of date. Unknown details stay unknown.
- The assistant should ask for missing facts, use retrieved context, and avoid inventing deadlines, contract terms, evidence, statutes, or outcomes.
- A qualified human reviews consequential legal conclusions. The output is general legal information, not legal advice.
- Kuku's assignment input pack is confidential and must stay out of public repositories.

## How the prototype works

`build_knowledge_base.py` reads authorized local JSON records, chunks text at 1,600 characters with 180-character overlap, and stores it in a persistent Chroma collection. The person describes the issue in the Python command-line chat. `agent.py` retrieves three passages per step and can perform up to three steps. `agent_multirag.py` searches the original question and up to three complementary query formulations, retrieving three passages per query. `llm_client.py` sends the question and retrieved passages to configured Groq models. Prompts request plain language, source grounding, explicit uncertainty, and no unsupported legal claims. Conversation history lasts for the current process.

The prototype is local CLI software, not a deployed web app. The public repository link is the prototype; the repository README contains setup instructions.

## How I would know it works with a real team

Run a consented pilot with 20 anonymized cases across non-delivery, defective products, and cancelled paid services. Preserve the original account, retrieved passages, answer, and reviewer score for each. A lawyer or trained reviewer checks whether material facts were retained without invention, whether the timeline and missing questions are useful, whether sources support legal references, and whether the note saves intake-preparation time.

**Proposed pilot gate:** at least 18/20 notes rated usable, no material invented fact in the reviewed sample, and a measured reduction in preparation time. These are proposed targets, not achieved results. Track retrieval misses and unsupported claims, and route weak or consequential answers to a human.

## Scaling across Kuku's work

Reuse the intake workflow for a new issue only after adding a reviewed source set, issue-specific questions, and an evaluation set. Version sources by jurisdiction and date; test updates before re-indexing. At higher volume, add managed vector storage, secure per-case storage, access controls, and a reviewer queue. Monitor retrieval relevance, reviewer scores, latency, and model spend. Calls are bounded: up to three for iterative retrieval, or typically a query-generation call plus an answer call for multi-query mode. Actual spend depends on tokens and provider pricing.

## Current result and limitations

The prototype runs locally with Groq and produced responses for all three synthetic prompts. One raw answer generalized a six-month limitation concept from unrelated railway material after acknowledging that the corpus did not directly cover event-ticket refunds. This is a grounding failure and shows why source relevance must be checked by a human. The main remaining limitation is deployment: the working CLI has not yet been made available as a hosted app. The proposed pilot above is the next way to measure performance with a real team at broader scale.

**Prototype:** https://github.com/Akash-M-100/AI-LAWYER-

