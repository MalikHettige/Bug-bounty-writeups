# Flawed Enforcement of Business Rules

**Platform:** PortSwigger Web Security Academy  
**Category:** Business Logic  
**Difficulty:** Apprentice  
**Date Solved:** 2026-09-18  
**Severity:** High

---

## Summary

The application issues two discount coupons — `NEWCUST5` (shown in site banner) and `SIGNUP30` (given on newsletter signup). While the app blocks consecutive reuse of the same coupon, it fails to detect alternating reuse between two different codes. By alternating `NEWCUST5` and `SIGNUP30` repeatedly, the total price of a $1337 jacket was reduced to $0.00.

---

## How to Find the Coupons

```
Coupon 1: site-wide banner → "New customers use code at checkout: NEWCUST5"
Coupon 2: newsletter signup at bottom of page → SIGNUP30
```

Always check:
- Page banners and announcements
- Newsletter/email signup forms
- Footer links
- Promotional emails from the app

---

## Steps to Reproduce

1. Add Lightweight "l33t" Leather Jacket to cart ($1337.00)
2. Sign up for newsletter → receive `SIGNUP30` code
3. Apply `NEWCUST5` → -$5.00
4. Apply `SIGNUP30` → -$401.10
5. Apply `NEWCUST5` again → -$5.00 (works — different from last applied)
6. Apply `SIGNUP30` again → -$401.10
7. Repeat until total = $0.00
8. Place order 

---

## Proof of Concept

<img width="1594" height="853" alt="image" src="https://github.com/user-attachments/assets/962c6c7d-eec4-4fc0-938c-b0089b8371c0" />

## Root Cause

```
Developer assumed: users won't apply the same coupon twice
Check implemented: "was the last applied coupon this same code?"
Gap:               no check for alternating pattern across sessions
                   no limit on total number of coupon applications
                   no check that total discount ≤ original price
```

---

## Real World Application

```
1. Collect all available coupon codes on the target
   → banners, newsletter, referral programs, social media
2. Apply one → try applying same one again → blocked? Note the error
3. Apply second coupon → try first again → does it work?
4. If yes → alternate until price = $0 or negative
5. Also try: same coupon in two browser tabs simultaneously
             submit coupon request twice via race condition
```

---

## Methodology Entry (add to business logic methodology)

```
### Coupon/Voucher Abuse
WHERE:  any checkout with coupon field
WHAT:   collect all codes → apply A → apply B → apply A again
        if works → alternate until $0
ALSO:   race condition (submit same coupon twice simultaneously)
        negative coupon codes if input not validated
SIGNAL: discount applied repeatedly, total drops on each application
```

---

## Remediation

1. Track all coupons applied per order — not just the last one
2. Set maximum discount cap (e.g. cannot exceed 90% of order value)
3. Mark coupons as used globally per user/order after first application
4. Validate total order value > 0 before allowing checkout

---

**Tags:** `#PortSwigger` `#BusinessLogic` `#CouponAbuse` `#PriceManipulation` `#Apprentice`
