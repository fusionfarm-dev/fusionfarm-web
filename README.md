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
| `src/static/api/` | PHP contact endpoint (`contact.php`, `config.php`, `common.php`) |
| `tests/contact-test.php` | Routing, validation and header-injection tests for the form |
| `public/` | Build output. Deploy this folder |

Pages: `/`, `/contact/`, `/domains/` (`/assets` redirects here), `/privacy/`, `404.html`.

## Deploy

### DreamHost (upload)
1. `python3 tools/build.py`
2. Upload the **contents** of `public/` to the fusionfarm.net web root (SFTP or the file manager), including the hidden `.htaccess`.
   `.htaccess` forces HTTPS, strips `www`, serves `404.html`, and sets HSTS, CSP and cache headers.
3. In the DreamHost panel make sure HTTPS (Let's Encrypt) is on for fusionfarm.net before relying on HSTS.

### Cloudflare Pages (if moving)
Note: Pages does not run PHP, so the contact form would fall back to email links there.
1. Create a Pages project from this repo. Build command: `python3 tools/build.py`, output directory: `public`.
   (Or leave the build command empty: `public/` is committed.)
2. `_headers` and `_redirects` in `public/` are picked up automatically.
3. Add `fusionfarm.net` as a custom domain.

## Contact form

The form routes by topic: Projects, research & engagements → research@, Digital assets → domains@, Support → support@.
It runs on DreamHost's PHP (`public/api/`), with Cloudflare Turnstile as the spam check and a honeypot field.

- **Until it is configured**, `/api/config.php` reports the form as off, and Send opens the visitor's
  email app with a pre-addressed, pre-filled message to the right desk. Nothing breaks.
- **To turn it on:**
  1. In Cloudflare (free account, no DNS move needed): Turnstile → Add widget → hostname `fusionfarm.net`.
     Copy the site key and secret key.
  2. In DreamHost, make sure a sender mailbox exists, e.g. `web@fusionfarm.net`.
  3. Copy `tools/contact-config.example.php` to **`/home/USER/fusionfarm-contact-config.php`**
     (one level above the `fusionfarm.net` web folder, so it is never web-reachable).
     Fill in the keys and `from_email`, set `'enabled' => true`.
  4. Reload `/contact/`: the Turnstile check appears and messages are mailed directly.
- Requires PHP 8.1+ with curl (DreamHost default). `api/common.php` is blocked from the web by `.htaccess`.
- Tests: `php tests/contact-test.php`.

## Brand and content rules
See `CLAUDE.md`. Source of truth for copy and visuals: the LinkedIn kit (`fusionfarm-linkedin`: `PAGE-COPY.md`, `build.py`).

## Checks before a deploy
- Emails and the phone number never appear as plain text in HTML (assembled in `assets/js/site.js`).
- No third-party requests except Turnstile when the form is enabled.
- Lighthouse 95+ in all four categories; no horizontal scroll at 375px.

© Fusion Farm LLC
