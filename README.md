# Fusion Farm — Intelligence, engineered.

A lightweight, dark-theme rebuild for Fusion Farm LLC. Plain HTML, CSS and JavaScript; no production build or CMS. DreamHost serves the pages and a small PHP contact handler.

## Pages

- `/` — world-network hero, five approved services, process, experience diagram, industries, domain portfolio and contact band.
- `/contact` — topic-routed form and four obfuscated email addresses.
- `/assets` — all four confirmed available domains. Pricing remains **Make an offer** pending approval.
- `/privacy` — privacy notice covering hosting, email and Turnstile.
- `/404.html` — branded error page; Apache returns HTTP 404 for missing paths.

Chicago is headquarters; Minneapolis and Seattle are offices. No founding year or unconfirmed LinkedIn URL is published. Fonts are self-hosted with their licenses. No analytics or advertising trackers are included.

## Local preview

Use PHP 8.1+ (the contact handler needs cURL):

```sh
php -S 127.0.0.1:8080 -t . tools/preview-router.php
```

Open `http://127.0.0.1:8080/`. This development router serves clean URLs and the 404 page; it does not reproduce Apache security headers or HTTPS redirects. With no configuration the form stays disabled and visitors can email or call directly. A plain static server can preview the design, but cannot run the contact API.

## Deploy to DreamHost

1. Back up the current web root and verify that fusionfarm.net has a valid HTTPS certificate. Use PHP 8.1+ with cURL, Apache rewrite, headers and expires support.
2. Upload **the contents** of the provided DreamHost ZIP into the site's document root, including `.htaccess`. Or upload these paths from the repository: `index.html`, `404.html`, `assets/`, `contact/`, `privacy/`, `api/`, `.htaccess`, `robots.txt`, `sitemap.xml`, and `site.webmanifest`. Do not upload `.git/`, `tools/`, `tests/`, or local configuration. The portfolio page and shared resources both use the `assets/` directory; upload all its contents.
3. Register a Cloudflare Turnstile widget for `fusionfarm.net`. Keep the hostname restricted. Copy `tools/contact-config.example.php` to **one directory above the document root** as `fusionfarm-contact-config.php`. For a root `/home/USER/fusionfarm.net`, configuration goes at `/home/USER/fusionfarm-contact-config.php`. Set restrictive filesystem permissions readable by the PHP user.
4. Fill in the public `site_key`, secret `secret_key`, and an existing authorized `from_email` mailbox at `fusionfarm.net`. Use `hostname => fusionfarm.net` and set `enabled => true` only after the inboxes and sender are ready. Never upload this configuration into the public root or commit it. The public `/api/config.php` returns only the public site key and readiness flag.
5. Verify the sender's SPF/DKIM/DMARC in DreamHost/DNS. Confirm PHP mail is enabled and the four destination inboxes exist. Test delivery to **each** topic using real inbox checks, and confirm replies address the visitor. A successful PHP `mail()` result means accepted for delivery, not proof of arrival. If delivery fails, disable the form and use the direct email links while fixing the host's mail setup.
6. Check HTTPS and www redirects, `/contact`, `/assets`, `/privacy`, and a missing URL. Check headers, mobile layout and Lighthouse on production. `.htaccess` adds a CSP, HSTS, content-type protection, referrer policy and permissions policy; verify DreamHost applies them.
7. Update the LinkedIn company “Contact us” button to `https://fusionfarm.net/contact` once the new contact page and delivery have been verified.

## Contact behavior

The browser sends to `/api/contact.php`. The server validates fields and length, rejects a filled honeypot, verifies Turnstile server-side (including hostname and `contact` action), and selects a fixed recipient based on topic:

| Topic | Inbox |
| --- | --- |
| Project | pete@fusionfarm.net |
| Research | research@fusionfarm.net |
| Digital assets | domains@fusionfarm.net |
| Support | support@fusionfarm.net |

The visitor cannot select an arbitrary recipient or sender. The email uses a fixed subject, validated Reply-To and base64-encoded text body. The endpoint reports failures honestly; the browser preserves the message on failure. No messages are saved in a database or emailed until delivery is configured. PHP and hosting providers may retain routine operational logs.

Turnstile reference: https://developers.cloudflare.com/turnstile/get-started/server-side-validation/
PHP mail reference: https://www.php.net/manual/en/function.mail.php

## Validation

```sh
node --check assets/js/site.js
php tests/contact-test.php
php -l api/contact.php
```

Contact tests cover all four routes, invalid topics, email header injection, array inputs, field lengths and disabled configuration. Browser checks cover desktop and 375px mobile layouts, menu, topic selection, domain prefill, and the honest disabled state. See `VALIDATION.md` for measured results and deployment checks that still require the host.

## Brand assets

The existing atomic logo is preserved. The handoff's `fusionfarm-linkedin` source repository was unavailable; `fusionfarm-dev/fusionfarm-linkein` was empty when checked. The map was recreated from public-domain Natural Earth 50m land on a 2.2° grid, using all fifteen named cities, Chicago as the primary hub, and Minneapolis and Seattle as secondary hubs. The orbit follows the approved Systems / Data / Field labels. `og-home.png` is a new site-specific social image, not the unavailable LinkedIn launch card. See `assets/img/README.md` and `tools/gen_graphics.py`.
