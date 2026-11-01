# Validation — November 1, 2026

## Local Lighthouse, mobile configuration

| Page | Performance | Accessibility | Best practices | SEO |
| --- | ---: | ---: | ---: | ---: |
| Home | 96 | 100 | 100 | 100 |
| Contact | 100 | 100 | 100 | 100 |
| Digital assets | 100 | 100 | 100 | 100 |
| Privacy | 100 | 100 | 100 | 100 |

Measured against the local PHP development server. The portfolio was rechecked after fixing its heading hierarchy. The home brand accessible name was clarified after its audit. These are local measurements, not production guarantees. The contact audit uses the unconfigured state; enabled Turnstile must be checked on the live host. The intentionally non-indexed 404 page is excluded from the SEO score table.

## Passed checks

- Five pages have one H1, working local resource references and the approved metadata.
- Five services retain the approved order and descriptions.
- No old AI-forward positioning, third-party fonts or advertising trackers in page markup.
- Self-hosted Manrope and JetBrains Mono include licenses.
- Mobile home, contact, portfolio and privacy pages fit at a 375px viewport without horizontal scrolling.
- Mobile navigation opens, domain links preselect Digital assets and populate the named domain, email links assemble correctly.
- The original atomic mark remains intact. World network and orbit diagrams use the approved hubs and labels.
- JavaScript syntax check passed.
- All PHP files pass PHP 8.2 syntax checks.
- Sixteen contact assertions pass: all four routes, validated Reply-To, invalid topic, header injection, array input, short/oversized message, disabled configuration and unauthorized sender domain.
- `/api/config.php` returns enabled=false without configuration; POST to the contact endpoint returns an honest HTTP 503 and sends no mail.
- Canonicals, sitemap, robots, OG image, favicon set and Organization JSON-LD are included. JSON-LD has a matching CSP hash.
- Git whitespace checks pass.

## Requires deployment access or owner confirmation

- Upload to the existing DreamHost document root and verify actual Apache redirects, status codes, CSP and HTTPS headers.
- Configure a hostname-restricted Turnstile widget and an authorized sender outside the public root.
- Verify delivery and reply behavior for all four real inboxes; SPF, DKIM and DMARC were not inspected or changed.
- Test enabled Turnstile and repeat Lighthouse against production.
- Update the LinkedIn Contact us button to https://fusionfarm.net/contact after contact delivery is verified.
- Confirm the final LinkedIn URL before adding Organization sameAs. No founding year is shown.
- Owner confirmed DreamHost and all four domains remain available. Prices remain Make an offer; no old price is published.
- The approved LinkedIn source artwork was unavailable. The site uses the existing website logo and newly recreated visuals, with provenance in README.md.
