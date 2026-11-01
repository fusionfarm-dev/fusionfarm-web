# fusionfarm-web

Website for **Fusion Farm LLC** — [fusionfarm.net](https://fusionfarm.net). **Intelligence, engineered.**

Static site. A small Python generator (standard library only) renders the pages
and brand graphics into `public/`, which is what gets deployed. `public/` is
committed, so a deploy never needs a build machine.

## Build and preview

```bash
python3 tools/build.py                  # src/ -> public/
python3 -m http.server -d public 8080   # open http://localhost:8080
```

## Structure

| Path | What it is |
|---|---|
| `src/pages/*.html` | Page bodies: `home`, `contact`, `domains`, `privacy`, `404` |
| `src/site.json` | Origin, LinkedIn URL, form endpoint, Turnstile site key |
| `src/data/domains.json` | Domain portfolio. `listed: false` hides a name; `price: null` shows "Make an offer" |
| `src/data/world-dots.json` | Land dots for the network map (Natural Earth 50m, 2.2° grid, from the LinkedIn kit) |
| `src/static/` | Copied as-is: CSS, JS, self-hosted fonts, mark, favicons, OG image |
| `tools/build.py` | Layout, world-network map and fusion-orbit SVGs, domain cards, sitemap, robots, host headers |
| `worker/` | Cloudflare Worker that receives the contact form and emails the right desk |
| `public/` | Build output. Deploy this folder |

Pages: `/`, `/contact/`, `/domains/` (`/assets` redirects here), `/privacy/`, `404.html`.

## Deploy

### DreamHost (upload)
1. `python3 tools/build.py`
2. Upload the **contents** of `public/` to the fusionfarm.net web root (SFTP or the file manager), including the hidden `.htaccess`.
   `.htaccess` forces HTTPS, strips `www`, serves `404.html`, and sets HSTS, CSP and cache headers.
3. In the DreamHost panel make sure HTTPS (Let's Encrypt) is on for fusionfarm.net before relying on HSTS.

### Cloudflare Pages (if moving)
1. Create a Pages project from this repo. Build command: `python3 tools/build.py`, output directory: `public`.
   (Or leave the build command empty: `public/` is committed.)
2. `_headers` and `_redirects` in `public/` are picked up automatically.
3. Add `fusionfarm.net` as a custom domain.

## Contact form

The form routes by topic: Project → pete@, Research → research@, Digital assets → domains@, Support → support@.

- **Now (no backend):** `form_endpoint` is empty, so Send opens the visitor's email app with a pre-addressed, pre-filled message to the right desk. Works on any host.
- **With the Worker:**
  1. Create a free [Resend](https://resend.com) account and verify `fusionfarm.net` (adds SPF/DKIM TXT records; MX is not touched, so existing mailboxes keep working).
  2. `cd worker && npx wrangler deploy`, then `npx wrangler secret put RESEND_API_KEY`.
  3. Optional spam check: create a Turnstile widget for fusionfarm.net, `npx wrangler secret put TURNSTILE_SECRET`, and put the site key in `src/site.json` → `turnstile_sitekey`.
  4. Put the Worker URL in `src/site.json` → `form_endpoint`, rebuild, redeploy. CSP is regenerated to allow it.
- Formspree also works: paste a Formspree form URL as `form_endpoint` (one inbox only; filter by subject).

A honeypot field runs in every mode. No reCAPTCHA, no trackers.

## Brand and content rules
See `CLAUDE.md`. Source of truth for copy and visuals: the LinkedIn kit (`fusionfarm-linkedin`: `PAGE-COPY.md`, `build.py`).

## Checks before a deploy
- Emails and the phone number never appear as plain text in HTML (assembled in `assets/js/site.js`).
- No third-party requests except Turnstile when it is enabled.
- Lighthouse 95+ in all four categories; no horizontal scroll at 375px.

© Fusion Farm LLC
