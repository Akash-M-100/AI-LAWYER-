# Case 02 - Appliance stopped working shortly after purchase

**Synthetic test scenario.** The dates, seller, and amount below are invented for testing.

## First message to the assistant

> I bought a new appliance and it stopped working a few days later. The shop says I have to deal with the manufacturer, and the manufacturer has not fixed it yet. Help me organize the facts before I decide what to ask for.

## Reveal only if the assistant asks for details

- The buyer is in India and purchased a washing machine on 3 March 2026 for INR 31,500.
- The machine stopped powering on on 8 March 2026 during ordinary use.
- The buyer contacted the shop on 9 March and the manufacturer service centre on 10 March.
- A service visit was booked, but no visit date or repair report has been provided yet.
- The invoice exists. The warranty document and the seller's written response have not yet been located.
- The buyer has not said whether they prefer repair, replacement, or refund. The city/state and seller's registered name are unknown.

## What to check in the answer

- Does it preserve the purchase, defect, and contact dates in order?
- Does it ask for the invoice, model/serial number, warranty terms, service request number, repair notes, seller response, and desired outcome?
- Does it avoid assuming the defect is covered, that a refund is legally required, or that a fixed repair deadline applies?
- Does it distinguish what the seller said from what the law or retrieved sources support?
