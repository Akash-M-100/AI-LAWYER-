# Case 03 - Paid event cancelled and refund still pending

**Synthetic test scenario.** The dates, organizer, platform, and amount below are invented for testing.

## First message to the assistant

> I paid for an event ticket, but the organizer cancelled the event. The ticketing app says a refund was started, but I still don't see the money. Help me prepare a clear summary and tell me what details to check.

## Reveal only if the assistant asks for details

- The buyer is in India and paid INR 2,500 by UPI through a ticketing platform.
- The event was scheduled for 25 April 2026. The organizer sent a cancellation email on 19 April 2026.
- The platform showed “refund initiated” on 21 April, but the buyer's bank account does not show a matching credit as of 2 May.
- The buyer has the ticket confirmation, cancellation email, UPI debit confirmation, and a screenshot of the refund status.
- The platform's refund terms, UPI reference number for any refund, organizer's registered details, and any support-ticket reply are not yet known.

## What to check in the answer

- Does it separate the event cancellation date from the platform's refund-status date?
- Does it ask for the ticket terms, platform/organizer identity, transaction references, support case number, and bank statement evidence?
- Does it avoid asserting that the refund was completed just because the app says it was initiated?
- Does it avoid making up a processing deadline or legal remedy, and cite retrieved material only when the source supports it?
