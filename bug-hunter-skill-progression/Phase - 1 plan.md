# Timeline (these must be done by mid-oct)

**Page created: september 10th 2026**
### Learning paths to do on portswigger (update methodology in every single lab)

- [x]  BAC
- [x]  Auth
- [x]  Information Disclosure
- [ ]  Business-logic (financial manipulation)
- [ ]  Race-conditions
- [ ]  JWT (algorithm confusion / JWKS)
- [ ]  API Testing (mass assignment / BOLA)
- [ ]  OAuth (token leakage via redirect_uri/Referer)
- [ ]  CORS
- [ ]  WebSockets
- [ ]  HTTP request smuggling
- [ ]  Insecure desensitization

### **Disclosed Report Analysis (50+)**

- [x]  25+ reports analyzed across Access Control, Business Logic, JWT, API/BOLA, Race Conditions (mix, not all one type)

### **Blog / Research Reading (minimum 30 must be read)**

- [x]  JWKS confusion
- [ ]  Single-packet race attacks (Kettle's technique)
- [ ]  Mass assignment on privileged fields
- [ ]  Response-manipulation MFA bypass
- [ ]  For each topic: can I explain the exploit out loud, from memory, to someone with no context, in under 2 minutes? If not, not done.

### **Custom Lab Execution (the actual bar)**

> Don't build all 7 labs from scratch in week 1-3 as scheduled. Use OWASP Juice Shop and crAPI
> 
- [ ]  Access Control, Business and auth: cold exploit (unfamiliar lab, no notes) in under 30 min
- [ ]  Build my own deliberately-broken Flask/Django app
- [ ]  OWASP Juice Shop
- [ ]  Almost all the disclosed reports and blogs ever read must be exploited in custom labs and publicly documented
- [ ]  Business Logic (price/quantity manipulation, negative values, coupon stacking): cold in under 30 min
- [ ]  JWT (alg confusion RS256→HS256, JWKS/kid manipulation): cold in under 45 min.
- [ ]  API Testing (mass assignment on privileged field via mobile/internal route): cold in under 30 min
- [ ]  Race Conditions (single-packet/multi-threaded TOCTOU on a check-then-act endpoint): cold in under 45 min — this one's allowed to be slower, tooling setup eats time\
- [ ]  Authentication (response-manipulation MFA bypass): cold in under 20 min
- [ ]  OAuth (redirect_uri/Referer token leakage): cold in under 30 min
- [ ]  One combined lab with 2-3 of the above seeded together, unlabeled — When I don't know which bug types are present going in,
- [ ]  I find and exploit all of them in one session

---

#### Critical but single exploitations

- [ ]  **IDOR on password reset/account recovery** — swap the user identifier in a reset token request, take over any account. Often full ATO with zero auth needed.
- [ ]  **IDOR on admin/internal API endpoints exposed to regular users** — mobile apps and SPAs frequently leak internal endpoints in JS bundles; an IDOR there can mean full admin panel access.
- [ ]  **Mass IDOR via GraphQL `node(id:)` or batch endpoints** — one query enumerates thousands of objects across tenants; turns a "low" single-object leak into a critical data breach.
- [ ]  **IDOR on financial/payment objects** — invoice IDs, payout IDs, bank account IDs. Direct financial impact means direct bounty impact.
- [ ]  **IDOR + PII export/report generation** — trigger another user's data export and access it via a predictable/second-order storage path.

#### Chains

**IDOR + Authentication**

- [ ]  **IDOR in "impersonate user" or support/admin tooling** — swap the target user ID in an impersonation request as a low-priv or unauthenticated actor, become anyone including admins.
- [ ]  **IDOR on session/device management endpoints** — view or revoke another user's active sessions, or worse, pull their session token.
- [ ]  **IDOR on MFA/2FA enrollment or reset endpoints** — disable or reset another user's 2FA by ID, then chain into account takeover.

**IDOR + OAuth**

- [ ]  **IDOR in OAuth token exchange/linking endpoints** — swap a `user_id`/`account_id` parameter during the OAuth callback or account-linking flow to bind an attacker's OAuth identity to a victim's account, or vice versa.
- [ ]  **State parameter + IDOR combo** — predictable or reusable OAuth `state` lets me replay another user's authorization code; pair with IDOR on the callback's user-binding step for full ATO.
- [ ]  **IDOR on OAuth app/consent management** — revoke, modify, or view another user's connected third-party apps and their scopes.

**IDOR + JWT**

- [ ]  **JWT with weak/no signature verification (alg:none, key confusion) + IDOR** — forge a JWT for arbitrary `user_id`, then hit an endpoint that trusts the ID from the token but the endpoint also has a secondary IDOR check that I can bypass. Doubly critical because it's both an auth bypass and a BOLA.
- [ ]  **IDOR via JWT `kid` header injection (SQLi/path traversal in `kid`) leading to signature forgery** — forge tokens for any user ID, and every IDOR-protected endpoint falls at once.
- [ ]  **Refresh token IDOR** — swap a refresh token's associated user/device ID to mint access tokens for other accounts.

**IDOR + API Testing / BOLA (this overlaps IDOR heavily, but escalation patterns matter)**

- [ ]  **BOLA through nested/nested-object nested references** — endpoint checks ownership of the top-level object but not the nested sub-object ID (e.g., `/orders/{id}/items/{item_id}` checks order ownership, not item).
- [ ]  **API versioning IDOR** — v1 endpoint deprecated but still live and unprotected while v2 has the fix; classic and still very common in bounty programs.
- [ ]  **Mass assignment + IDOR** — send an extra `user_id` or `owner_id` field in a request body that the API doesn't strip, reassigning ownership of an object to myself or changing another user's object.
- [ ]  **HTTP method/verb tampering + IDOR** — GET is protected, but PUT/PATCH/DELETE on the same object ID isn't checked the same way.

**IDOR + Race Conditions**

- [ ]  **TOCTOU on object ownership transfer** — race a "transfer ownership" or "claim" endpoint between two IDs to claim an object twice or claim someone else's object mid-transfer.
- [ ]  **Race condition + IDOR in invite/redeem flows** — redeem the same invite/coupon/voucher ID from multiple accounts simultaneously before the "used" flag commits.
- [ ]  **Race condition on rate-limited ID enumeration** — parallel requests to bypass per-ID rate limiting on sensitive lookups (e.g., verification codes tied to a user ID).

#### PortSwigger **API Testing**

- [ ]  **The Critical Outcome:** **Mass Unauthenticated Data Mass-Assignment (BOLA/BADA)**
- [ ]  Mass assignment on a privileged field through an internal/mobile-only API route that lacks the authz check present on the web-UI equivalent — e.g. `role` or `isAdmin` accepted in a request body the frontend never exposes.

#### PortSwigger **Authentication**

- [ ]  **The Critical Outcome:** **Global MFA Bypass / Zero-Interaction Account Takeover**
- [ ]  Response-manipulation MFA bypass: intercept the auth response and flip `"success": false` → `true` (or the equivalent status/redirect field) client-side, skipping the second factor entirely. Zero-interaction, full account access.

#### PortSwigger **OAuth Authentication**

- [ ]  **The Critical Outcome:** **Pre-Auth Account Hijacking via Token Leakage**
- [ ]  Authorization-code or access-token leakage via open redirect on `redirect_uri`, or via `Referer` header leakage to a third-party resource loaded post-auth. Pre-auth takeover with a single crafted link.

#### PortSwigger **JWT**

- [ ]  **The Critical Outcome:** **Cryptographic Signature Spoofing via JWKS / Key Confusion**
- [ ]  Algorithm confusion: server expects RS256, I resign the token as HS256 using the server's own public key as the HMAC secret. Full signature bypass — forge any user, including admin, without ever needing a real secret.

#### Relevant **race-condition** labs

- [ ]  **The Critical Outcome:** **Sub-Millisecond Multi-Request Asset Theft (Limit Over-Drafting)**
- [ ]  Single-packet/multi-threaded attack against any "check-then-act" limited-use endpoint (coupon redemption, password reset, balance transfer) — classic TOCTOU window, most reliable class of race bug to actually land.

#### Exceptions

- [ ]  Multi-step workflow: call the finalize/approve endpoint directly, skipping earlier steps, check if authz re-fires
- [ ]  Bulk endpoint (bulk-delete/export/assign): confirm the single-item version checks ownership per-item in the loop, not once
- [ ]  Nested resource permission inheritance: child resource's permission either missing or stale from a changed parent
- [ ]  Impersonation/support-login: does the "login as customer" session actually scope down, or silently retain admin claims
- [ ]  Second-order authz: user-controlled input from a low-trust context reappearing in a high-trust context (admin dashboard, automation) without re-verification
- [ ]  Type-coercion bypass: role/ID fields with loose typing — test negative IDs, arrays instead of scalars, null vs missing, string-vs-int

---

### **Recon Skill Stack**

- [ ]  CORS misconfig: can identify and confirm (Origin reflection + credentials:true) in under 5 min on any target
- [ ]  Use practice programs and do recon + read everything
- [ ]  Source map `/.git`exposure: automated check running (script or one-liner) I can point at any URL
- [ ]  JS bundle analysis: can pull, deobfuscate, and extract endpoints/feature-flags from a minified bundle in under 15 min
- [ ]  Automation tools installed and run at least once each: nuclei, subfinder, httpx, gau, LinkFinder — not just installed, actually run against a real (non-scope, practice) domain with output I understood

### **Pattern Recognition Habit**

- [ ]  The "what program type / what pattern / what else shares it" question is now automatic after every lab and every report
- [ ]  From doing practice recon, document everything and try to learn enough to teach
- [ ]  By doing custom labs, click every single thing and note down everything to the point the whole app is 100% explainable

**Read program guidelines and be able to become an expert in**

- [ ]  Inventory in-scope domains, APIs, integrations, upload features, and worker-backed functionality.
- [ ]  Identify technology clues from public documentation and normal application behavior.
- [ ]  Map features that process URLs, files, templates, archives, or jobs.
- [ ]  Identify cloud, container, webhook, import, and export functionality.

### Skill stack

- [ ]  **Source map exploitation** — Production JS builds sometimes ship `.map` files by accident, which unminify the entire original source: internal comments, unused admin routes, hardcoded API structure, sometimes literal secrets. A five-minute check (`curl` the JS bundle URL + `.map`) that most hunters skip because it feels too easy to be real.
- [ ]  **Exposed `.git` directory / git history mining** — Misconfigured deployments occasionally leave `.git/` publicly accessible, letting me pull the entire commit history — including secrets committed and later "deleted" (which git history still contains). Pair with GitHub dorking on the target's own public repos for the same pattern in commits that predate a cleanup.
- [ ]  **Mobile APK/IPA static decompilation** — This is the natural partner to my mobile recon plan, one layer deeper: `jadx`/`apktool` on the APK (or `class-dump` on iOS) pulls hardcoded API keys, undocumented endpoints, and feature flags that never appear in live traffic because the UI never triggers them. Traffic proxying shows me what the app *does*; decompilation shows me what it *can* do.
- [ ]  **Parameter mining** — Tools like Arjun or param-miner brute-force undocumented request parameters on known endpoints. A huge fraction of debug modes, admin overrides, and hidden business-logic branches are gated behind a parameter that's never in any docs and never sent by the normal UI.
- [ ]  **CORS misconfiguration hunting** — Specifically: does the target reflect an arbitrary `Origin` header back in `Access-Control-Allow-Origin` while also setting `Access-Control-Allow-Credentials: true`? That combination means any attacker-controlled page can read authenticated responses cross-origin. Mechanical, fast to check, still shockingly common.
- [ ]  **Feature-flag / dead-route discovery via JS bundle analysis** — Search minified JS for flag-like strings (`enableAdminPanel`, `betaFeature_export`) and route definitions that never render in the current UI. The frontend code is flagged off; the backend route it calls often isn't.
- [ ]  **Webhook signature bypass** — For any endpoint receiving webhooks (Stripe, GitHub, internal service-to-service callbacks), check whether the HMAC/signature verification is actually enforced, or just logged/optional. A common, distinct oversight from any auth bug I'm already testing for.
- [ ]  API enumeration
- [ ]  Package Hijacking
- [ ]  JWKS spoofing
- [ ]  Learn OSIENT ‣
- [x]  JWT handbook
- [x]  Read these once: Bugcrowd VRT / HackerOne mediation docs

### **Phase 1 exit gate — all of these true, or Phase 1 isn't done regardless of date:**

- [ ]  Every core-path lab passes its cold-execution time bar
- [ ]  25+ disclosed reports logged with transferable patterns extracted
- [ ]  Combined/unlabeled lab passed
- [ ]  Recon stack tools all run at least once successfully

So: hunt my seven chains as trained, report everything valid at whatever severity it lands — let criticals be upside when they land, not the dependency. That's not a downgrade of ambition, it's the version of the plan that actually respects "strictly June" as a constraint.

Shortlist-luck question is correctly parked — that's a Phase 2 problem, not a Phase 1 one.
Each and every single aspect is built to lead me to 10K by mid 2027.
