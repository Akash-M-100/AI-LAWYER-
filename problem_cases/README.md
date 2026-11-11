# Sample legal problem cases

Use these synthetic scenarios to try the legal assistant. Each file contains a first message, additional facts to reveal only if the assistant asks, and a checklist for reviewing the response. They are prompts, not legal advice or verified legal conclusions.

To run all three first messages through the bot and save the actual terminal transcripts, open PowerShell at the project root and run:

```powershell
.\problem_cases\run_problem_cases.ps1
```

The script starts a fresh `agent.py` process for each case and writes each unedited transcript to a timestamped folder under `problem_cases/outputs/`. It uses the local `.env` and Chroma database in the project root. Build the knowledge base first if `chroma_db` is missing. Output files are ignored by Git by default so you can review them before sharing.

| Case | Issue | What to check |
| --- | --- | --- |
| [01 - Order not delivered](01_order_not_delivered_refund.md) | Online purchase and missing refund | Does the assistant organize the order/payment/contact timeline and ask for the seller, terms, and proof? |
| [02 - Product stopped working](02_defective_product.md) | Defective appliance and seller/manufacturer response | Does it distinguish the defect from the seller's response and ask for invoice, warranty, repair history, and desired remedy? |
| [03 - Cancelled event](03_cancelled_event_refund.md) | Cancelled paid event and delayed refund | Does it separate organizer cancellation from the platform's refund status and ask for ticket terms and transaction evidence? |

## Shared review checklist

- Restates only facts the user gave; keeps unknown dates and terms unknown.
- Asks focused follow-up questions when key facts are missing.
- Uses only relevant retrieved legal material and names its source when available.
- Does not invent refund deadlines, limitation periods, agencies, court forums, or guaranteed outcomes.
- Gives a practical evidence checklist and says when the local knowledge base does not support a legal conclusion.
