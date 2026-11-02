# Infinite Money Logic Flaw

**Platform:** PortSwigger Web Security Academy

**Category:** Business Logic

**Difficulty:** Practitioner

**Date Solved:** YYYY-MM-DD

**Severity:** High

## Summary

The application lets users buy gift cards at a discounted price using a promotional coupon, then redeem those gift cards for their full, undiscounted face value as store credit. The discount applied at checkout and the value credited at redemption are calculated independently, with no cross-validation between them. Each purchase-and-redeem cycle therefore nets the user more store credit than they spent.

The cycle has no upper bound and is fully automatable, allowing unlimited store credit to be generated from a single account. This is a **value-conversion mismatch** business logic flaw.

## Affected Component

```ocaml
POST /cart/coupon           (discount application)
POST /cart/checkout         (order completion)
POST /gift-card             (gift card redemption)
```

```ocaml
https://[LAB-ID].web-security-academy.net/cart
```

## Steps to Reproduce

1. Log in to a standard account.
2. Sign up for the newsletter (or an equivalent promotional action) to obtain a discount coupon, e.g. `SIGNUP30` (30% off).
3. Add a gift card (face value: $10.00) to the cart.
4. Apply the coupon at checkout. The total due drops to $7.00.
5. Complete the order, then redeem the resulting gift card code through the account's gift-card redemption feature.
6. Observe that store credit increases by $10.00 even though only $7.00 was paid, a net gain of **$3.00 per cycle**.
7. Repeat steps 3-6. Each cycle yields the same $3.00 net gain indefinitely, with no server-side limit encountered.
8. Automate the loop (see Proof of Concept) and accumulate enough credit to buy the target item outright.

## Proof of Concept

#### Manual verification (single cycle)

```ocaml
Starting store credit: $100.00

POST /cart                                     -> add gift card ($10.00)
POST /cart/coupon                              -> apply SIGNUP30, total reduced to $7.00
POST /cart/checkout                            -> order placed, $7.00 deducted
GET  /cart/order-confirmation?order-confirmed=true
                                               -> returns gift card code
POST /gift-card                                -> gift-card=<code> redeemed

Resulting store credit: $103.00  (net +$3.00)
```

#### Automated repetition

The sequence above was replayed using a Burp **session handling rule with a macro**, driven by **Intruder with null payloads and 1 concurrent request**. Store credit climbed by $3.00 per cycle across 16+ consecutive automated cycles, with no rate limit or usage cap encountered. The run was stopped manually once sufficient credit had accumulated to purchase a high-value item outright.

<!-- Add screenshot references here, e.g. ![Store credit after automated cycles](assets/<filename>.png) -->

## Root Cause

The discount applied during checkout and the value credited during gift card redemption are computed by two independent code paths with no reconciliation between them:

- **Checkout pricing logic** correctly applies the coupon to the **amount charged**.
- **Redemption logic** credits the gift card's **original face value**, with no reference to what was actually paid for it.

The implicit assumption that "amount paid" equals "amount redeemable" holds only when no discount is applied. Introducing a coupon broke that invariant, and no corresponding check was added to redemption to cap the credited value at the amount actually paid.

In addition, no server-side limit exists on how many times one account can purchase and redeem discounted gift cards, so the per-cycle gain compounds without bound.

## Impact

**Technical**
- Unlimited store credit can be generated from a single account.
- The attack is repeatable and automatable with standard tooling (Burp macro + Intruder), with no rate limit encountered.
- Requires only a low-privilege account and a publicly obtainable coupon.

**Business / Real-World**
- Free acquisition of arbitrarily expensive goods or services; given enough cycles this scales to any purchase amount the platform offers.
- Direct and significant financial loss, with no upper bound beyond how long the attacker runs the loop.
- Fraud scales easily because the loop can be scripted and run in parallel across many accounts.

**Scope**
- Affects any user who can obtain the discount coupon and purchase gift cards.
- Affects the full checkout-to-redemption pipeline for gift card products.

## Remediation

1. **Tie redeemable value to the amount actually paid.** When a discount was applied at purchase, the gift card's redeemable value must reflect the discounted price, not the nominal face value.
2. **Exclude gift cards from coupons.** Alternatively, disallow discount coupons on gift card purchases entirely.
3. **Rate-limit the loop.** Add server-side limits on gift card purchase and redemption frequency per account within a time window, to reduce the blast radius of any similar logic gap discovered later.
4. **Reconcile at redemption time.** Validate that cumulative credited value does not exceed cumulative amount paid across the user's gift card transaction history.

```ocaml
if credited_value > amount_paid_for_card:
    reject_redemption()

otherwise:
    credit_account(credited_value)
```

## Lessons Learned & Patterns

- This is a general **value-conversion mismatch** pattern. Any feature where a discount or promotion applies to an item that is later converted into currency or equivalent value should be checked for the same flaw: gift cards, refunds, loyalty points, trade-in credit.
- Redemption value should always be tied to the amount paid, not the nominal or face value, whenever discounting is possible on the purchase side.
- Pattern question to ask on every target: *can I buy something for less than it is worth when converted back to money, and can I loop it?*
- A $3 gain per cycle is trivial alone. Business logic severity usually comes from **repeatability**, so always test whether the cycle can be automated.

## References

- [PortSwigger — Infinite money logic flaw](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-infinite-money)
- [PortSwigger — Business logic vulnerabilities](https://portswigger.net/web-security/logic-flaws)
- [OWASP — Business Logic Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Business_Logic_Security_Cheat_Sheet.html)
- [OWASP WSTG — Business Logic Testing](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/10-Business_Logic_Testing/)

**Tags:** #PortSwigger #BusinessLogic #InfiniteMoney #CouponAbuse #FinancialLogic
