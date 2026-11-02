# Business Logic & Auth-Adjacent Checklist

Built from documented labs: Insufficient Workflow Validation, Flawed Enforcement of Business Rules,
High-Level Logic Vulnerability, Inconsistent Handling of Exceptional Input, Inconsistent Security
Controls, Excessive Trust in Client-Side Controls, Weak Isolation on Dual-Use Endpoint, Infinite
Money Logic Flaw, Authentication Bypass via Flawed State Machine, Authentication Bypass via
Encryption Oracle.

Run this against every target before writing a finding off.

## 1. Map the workflow before touching anything

- [ ] Write down every step of the intended sequence (signup → verify → onboard, cart → checkout →
      confirm, login → role-select → home) before sending a single request.
- [ ] Identify which endpoint is the "final" or state-changing step in each flow.
- [ ] Identify every point where the client decides something the server should be deciding
      (price, role, quantity, next step).

## 2. Step-skipping / workflow bypass

- [ ] Capture the request for the **final** step of a multi-step flow and replay it directly,
      skipping all preceding steps. Does the server accept it? (Insufficient Workflow Validation)
- [ ] Intercept and **drop** one step in a multi-step flow (role selection, email verification,
      payment confirmation) instead of completing it, then navigate straight to the authenticated/
      post-flow page. Check what state the server defaults to when a step never happened.
      (Authentication Bypass via Flawed State Machine)
- [ ] For any flow with a "default" or "fallback" state, confirm the default is the *lowest*
      privilege, not an unvalidated or accidentally-elevated one.

## 3. Trust boundary / client vs server

- [ ] For every value that affects price, role, access, or limits, check whether it's validated
      server-side or only enforced in the UI/JS. Try sending it directly via the API/request.
      (Excessive Trust in Client-Side Controls)
- [ ] Check hidden form fields, disabled UI elements, and client-side validation messages — do
      any of them map to a server-side decision that isn't re-checked?

## 4. Input and exception handling

- [ ] Send negative numbers, zero, decimals, overflow-sized integers, and empty/null values into
      quantity, price, and ID fields. Note what breaks vs what the server rejects cleanly.
      (Inconsistent Handling of Exceptional Input)
- [ ] Check whether error-path behavior differs from success-path behavior in a way that's
      exploitable (e.g. error handler skips a check the success handler performs).

## 5. Inconsistent enforcement across paths

- [ ] If the same action is reachable through more than one endpoint, UI path, or API version
      (web vs mobile, v1 vs v2 API), check whether security controls are enforced identically on
      all of them. (Inconsistent Security Controls, Weak Isolation on Dual-Use Endpoint)
- [ ] Check dual-use endpoints (one endpoint serving two roles/purposes) for logic that correctly
      gates one use case but not the other.

## 6. Value-conversion mismatches (money/credit/points)

- [ ] Anywhere a discount, promo, or reduced price is applied on purchase, check whether the
      *redeemed/converted* value (gift card, refund, loyalty points, trade-in credit) is tied to
      the amount actually paid, or to the nominal/face value. (Infinite Money Logic Flaw)
- [ ] If a purchase-then-redeem cycle nets a gain, test whether it's rate-limited per account. If
      not, treat it as automatable and note severity accordingly.
- [ ] Check for a reconciliation step: does the server ever validate cumulative credited value
      against cumulative amount paid?

## 7. Reflected input / oracle pairs (auth + crypto logic)

- [ ] Find every endpoint where user input triggers a validation error. Does the error (a)
      reflect the input directly, or (b) set/update a cookie that's reflected elsewhere?
      Check: registration, profile update, contact forms, search with odd validation,
      password-reset email field, newsletter signup. (Authentication Bypass via Encryption Oracle)
- [ ] Look for any long-lived, encoded-looking cookie (long string, ends in `=`/`%3d`,
      high-entropy). If a reflection point also exists, cross-paste values between the two to
      test whether they share a key (encrypt oracle + decrypt oracle pairing).
- [ ] If both halves exist: decrypt your own legitimate token to learn its format, swap the
      privileged field, re-encrypt, strip any constant prefix to the block boundary (16 bytes for
      AES), and verify clean decryption before deploying the forged token.

## 8. General pattern questions (ask after every lab)

- [ ] What step is the server assuming already happened — and what happens if it didn't?
- [ ] Can I reach a later/privileged state by skipping, reordering, or repeating earlier steps?
- [ ] Can this be looped or automated, and is there a cap?
- [ ] What program type, pattern, and "what else shares this bug class" applies here?

## Status tracking

- [x] Insufficient Workflow Validation
- [x] Flawed Enforcement of Business Rules
- [x] High-Level Logic Vulnerability
- [x] Inconsistent Handling of Exceptional Input
- [x] Inconsistent Security Controls
- [x] Excessive Trust in Client-Side Controls
- [x] Weak Isolation on Dual-Use Endpoint
- [x] Infinite Money Logic Flaw
- [x] Authentication Bypass via Flawed State Machine
- [x] Authentication Bypass via Encryption Oracle
