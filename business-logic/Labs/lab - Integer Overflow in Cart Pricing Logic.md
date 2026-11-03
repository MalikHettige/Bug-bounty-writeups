# Integer Overflow in Cart Pricing Logic

**Platform:** PortSwigger Web Security Academy

**Category:** Business Logic

**Difficulty:** Practitioner

**Date Solved:** YYYY-MM-DD

**Severity:** High

## Summary

The application calculates cart totals as `quantity × unit_price` using a fixed-width 32-bit signed integer, with no bounds checking on the result. Repeatedly adding a high-value item accumulates a running total that crosses the integer's maximum representable value (2,147,483,647), causing it to **wrap around to a negative number**. From there, adding further units in smaller increments walks the negative total back toward zero, and a second, lower-priced item is used to fine-tune it into an affordable range. The server trusts this wrapped value at checkout without re-validating it, allowing goods of arbitrary real value to be purchased for a fraction of their cost.

This is a **low-level logic flaw**: a per-request quantity cap prevents a single request from overflowing the integer directly, but nothing independently bounds the *cumulative* total across multiple legitimate requests.

## Affected Component

```ocaml
POST /cart                 (add-to-cart endpoint)
```

Cart total calculation logic (`quantity × unit_price`, 32-bit signed integer, no range validation before use in checkout/balance comparison).

## Steps to Reproduce

1. Identify a high-unit-price item and confirm the per-request quantity field is capped (e.g. 2 digits, max 99 per request).
2. Repeatedly add the item to cart, accumulating quantity across multiple requests, until the running total crosses the 32-bit signed integer boundary (`2,147,483,647 ÷ unit_price` ≈ required unit count).
3. Observe the cart total flip from a large positive number to a large negative number once the threshold is crossed.
4. Continue adding units in smaller increments to walk the negative total back toward zero.
5. Add a second, lower-priced item in a calculated quantity to bring the total into an affordable range (between $0 and the account's available balance).
6. Complete checkout at the manipulated total and confirm the order is accepted.

## Proof of Concept

```ocaml
Unit price (jacket): $1337.00
Overflow threshold: ~1,606,196 units (2,147,483,647 ÷ 1337)

After accumulating ~32,123 units (exact wrap point may vary by run):
  cart total displayed as a small positive value due to wraparound,
  e.g. $1337.00 x 32,123 (mod 2^32) -> unexpected low total instead
  of the expected ~$42.9 million

Second item added: quantity 15 @ $85.05
  -> fine-tunes cart total to $53.79

Checkout result: order placed successfully at $53.79 for goods with
  a genuine combined value far exceeding the account's $100.00 store
  credit balance
```

> The per-request quantity cap stops a single `POST /cart` call from overflowing the integer on its own. The overflow only happens because the server sums quantity across many accepted requests without ever re-checking the running total against a sane upper bound.

<!-- Add screenshot references here, e.g. ![Cart total wrapped to negative after crossing INT_MAX](assets/<filename>.png) -->

## Root Cause

The cart total is computed and stored as a fixed-width 32-bit signed integer with no bounds checking before the value is used in payment/balance validation. A per-request quantity cap limits how much a single request can add, but does not prevent the *cumulative* total across repeated valid requests from exceeding the integer's representable range (`-2,147,483,648` to `2,147,483,647`). Once the sum exceeds `INT_MAX`, it wraps to a negative value, and the server accepts that wrapped value as-is when comparing the total against the account's available balance at checkout.

## Impact

**Technical**
- Cart total can be driven to any value, including negative or arbitrarily small positive numbers, through repeated legitimate-looking requests.
- The server performs no sanity check on the final total before accepting payment, so a wrapped or negative value is trusted outright.
- Requires no payload or injection — only repeated use of the standard add-to-cart flow.

**Business / Real-World**
- Any authenticated user can acquire goods of arbitrary real value for negligible or zero actual cost.
- If goods are physically fulfilled based on the manipulated total, this is direct, unbounded financial loss with no theoretical ceiling.
- The attack is mechanical and repeatable against any sufficiently high-priced item, making it scriptable.

**Scope**
- Affects the cart/checkout pricing pipeline for any item whose price and attainable quantity allow the cumulative total to approach `INT_MAX`.
- Affects every account able to place orders, since no special privilege is required.

## Remediation

1. **Use a wider or arbitrary-precision type for monetary totals.** A 64-bit integer (or a decimal/arbitrary-precision type) removes the practical overflow threshold for any realistic cart.
2. **Bound the cumulative total server-side, independent of per-request limits.** Reject any total exceeding a sane, business-defined ceiling before it can wrap, not just the per-request quantity.
3. **Validate the computed total before checkout, regardless of how it was derived.** Reject negative totals or totals outside an expected range, even if the server itself produced them.
4. **Re-derive the total at checkout from line items**, rather than trusting an accumulated running value carried across requests.

```ocaml
if cart_total < 0 or cart_total > MAX_SANE_ORDER_VALUE:
    reject_checkout()

otherwise:
    proceed_to_payment(cart_total)
```

## Lessons Learned & Patterns

- **Per-request caps are not the same as cumulative bounds checking.** A field limited to 2 digits per request says nothing about what happens after the 500th accepted request.
- Any `quantity x price` (or similarly multiplied/summed) value that accumulates across multiple requests for the same high-value item is worth testing for integer overflow, especially where the underlying type is likely to be fixed-width (32-bit signed is the classic case, wrapping at ~2.1 billion).
- After triggering a wrap to negative, look for a second lever (another item, a discount, a quantity field) to fine-tune the value into a usable range rather than stopping once the overflow is merely demonstrated.
- General pattern question: *does this app ever trust an accumulated value without re-validating it against a sane range at the point of use?* Applies equally to balances, loyalty points, and rate-limit counters, not just cart totals.

## References

- [PortSwigger — Business logic vulnerabilities](https://portswigger.net/web-security/logic-flaws)
- [OWASP — Business Logic Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Business_Logic_Security_Cheat_Sheet.html)
- [MITRE CWE-190 — Integer Overflow or Wraparound](https://cwe.mitre.org/data/definitions/190.html)
- [MITRE CWE-191 — Integer Underflow](https://cwe.mitre.org/data/definitions/191.html)

**Tags:** #PortSwigger #BusinessLogic #IntegerOverflow #PricingLogic #FinancialLogic
