# Business Logic Vulnerabilities

Part of SecurityOS — knowledge/business-logic.md
Sibling files: knowledge/idor.md · knowledge/authentication.md

## What it actually is
The app does exactly what it was coded to do. No broken auth check, no injected
payload — the workflow, limits, or sequencing just weren't built to survive
being used in an order or a way the developer didn't picture.

## Focus areas
- Race conditions (check-then-act gaps — balance checked, then debited, with a gap between)
- Amount/quantity manipulation (negative values, zero, overflow, unit confusion)
- Workflow/step-skipping (hitting step 3 of a process directly, skipping the step
  that actually enforces something)
- State abuse (replaying a one-time token, rewinding a status, reusing a coupon)
- Chaining — business logic bugs are frequently only reachable *through* an
  IDOR or auth gap first; rarely standalone

## Methodology
1. Map the full intended workflow before sending a single request — what's
   supposed to happen, in what order, under what limits
2. For every constraint enforced in the UI (min/max, one-time-use, ordered
   steps), test whether the server enforces it too, independent of the client
3. Anywhere state changes based on a prior check, test concurrency — fire
   requests before the first one's effect commits
4. Look for the chain before writing off a finding as "just" access control
   or "just" a race condition — the real severity is usually in the combination

## Labs
- PortSwigger — Business Logic Vulnerabilities module
- 

## Disclosed reports studied
- 

## Notes / gotchas
- 
