# fusionfarm-web

Public website for Fusion Farm LLC — https://fusionfarm.net

Static site, no build step. Open `index.html` directly or serve the folder
(`python3 -m http.server`). Deploys to any static host as-is.

## Structure
- `index.html` — single page: hero, operating lines, method, domains, contact
- `404.html` — not-found page (uses absolute `/assets` paths)
- `assets/css/site.css` — all styles
- `assets/js/site.js` — email assembly + mobile nav (progressive enhancement)
- `assets/img/logo.png` — the atomic mark, white on transparent; `logo-square.png` is the black-square version for favicon/social (supplied by Pedro; do not redraw or replace)

## Design system (locked — do not change without Pedro's say-so)
- Pure black background `#000000`
- Mint accent `#7CFFB2`
- Satoshi SemiBold for the "Fusion Farm" wordmark ONLY; Inter for all other text
- Atomic mark logo always paired with wordmark text; static, never animated
- Nav reads "Fusion Farm LLC"; hero reads "Fusion Farm"
- Section headings are two lines: white headline / mint subtitle

## Content rules
- Only real, confirmed content. No placeholder copy, invented clients,
  testimonials, metrics, or marketing fluff.
- No plain-text email addresses or phone numbers in HTML. Emails are
  assembled in `site.js` from `data-mail` / `data-addr` attributes.
- Positioning: AI-native holding company (not an AI consulting shop).
- Brand voice: professional, solid tech, business-exec — not "tech bro".
