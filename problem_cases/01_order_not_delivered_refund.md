# Case 01 - Order not delivered and refund not received

**Synthetic test scenario.** The dates, seller, and amount below are invented for testing.

## First message to the assistant

> I ordered something online, but it never arrived. I asked for my money back and still haven't received it. What information should I collect, and what can I do next?

## Reveal only if the assistant asks for details

- The order was placed on 14 February 2026 for INR 4,800.
- Payment was made by UPI; the bank transaction is visible in the app.
- The order page estimated delivery by 20 February 2026.
- The buyer sent refund requests through the seller's website on 25 February and 2 March; neither received a human reply.
- The marketplace is called **SampleCart** in this fictional scenario. The legal seller name and registered address are not known.
- The buyer is in India. State/city, order number, exact delivery/refund terms, and current order status are not yet known.

## What to check in the answer

- Does it create a timeline without filling in the missing seller identity or order number?
- Does it ask for the invoice/order ID, exact seller identity, promised delivery/refund terms, transaction reference, and copies of requests/replies?
- Does it distinguish general information from a conclusion about entitlement or deadlines?
- Does it avoid inventing a statutory period, chargeback window, agency, or court?
