# Methodology: JS Bundle Endpoint Leakage Recon

**Source:** Real bug bounty finding (tweet) — unauthenticated GET on an endpoint discovered in a JS file returned 216 applicants' CVs. Classic Broken Access Control via an endpoint never exposed in the visible UI.

**Phase:** Static recon, before/alongside active endpoint probing — same stage as checking robots.txt / sitemap.

**Trigger:** Any target with a JS-heavy frontend (SPA, React/Vue/Angular bundle) — especially when no GraphQL/REST endpoint is visibly called from normal UI browsing.

**Actions:**
1. Pull all JS files the page loads (view-source, Burp's site map, or a JS crawler).
2. Grep/search them for string patterns:
   - `/api/`
   - `/v1/`
   - `/graphql`
   - `.json`
   - `fetch(`
   - `axios.`
   - `endpoint`
   - `baseURL`
   - Even in minified bundles, these paths often survive as plain strings.
3. For every path found, send a plain **unauthenticated GET** first before anything else — zero-auth is the cheapest and most commonly missed test.

**Backup (if nothing found in JS):**
- Check Burp's passive site map after just browsing the app normally — endpoints hit by background XHR/fetch calls that never render visibly in the UI still show up there.
- Try Wayback Machine / `gau` for historically exposed paths no longer linked from the current site.
