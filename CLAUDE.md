# fusionfarm-web

Public website for Fusion Farm LLC — https://fusionfarm.net

Static site, no build step. Open `index.html` directly or serve the folder
(`python3 -m http.server`). Deploys to any static host as-is.

## Structure
- `index.html` — single page: hero (+ network map), service strip, services,
  statement, approach, experience, digital assets, contact
- `404.html` — not-found page (uses absolute `/assets` paths)
- `assets/css/site.css` — all styles
- `assets/js/site.js` — email assembly + mobile nav (progressive enhancement)
- `assets/img/logo.png` — the atomic mark, white on transparent; `logo-square.png`
  is the black-square version for favicon/social (do not redraw or replace)
- `tools/gen_network.py` — regenerates the hero city-network SVG
  (`python3 tools/gen_network.py --inject` rewrites it between the NETWORK markers)

## Brand system (shared with the LinkedIn kit, fusionfarm-linkedin)
- Ink background `#0B0F14`, panels `#121821`, lines `#223040`
- Text `#EEF1F4`, muted `#8C98A6`
- Jade accent `#5ED6AA`, signal blue secondary `#7FB8FF`
- Manrope (headlines/body), JetBrains Mono uppercase for labels/eyebrows
- Atomic mark always paired with "Fusion Farm" wordmark; mark itself static
- Signature graphic: MSP/CHI hub network map to LIS, LON, DXB, SIN, TYO, MEX, GRU, NYC
- Headline: "Ground truth. Anywhere."; jade/blue gradient rule

## Positioning
- Independent research & AI solutions firm — NOT a web design studio.
- Services: field intelligence, asset discovery, due diligence, operational
  assessments, AI design & implementation, special projects worldwide.
- Industry experience (aviation aftermarket, hospitality, CRE research, asset
  recovery) is credibility, not the offer.

## Content rules
- Only real, confirmed content. No placeholder copy, invented clients,
  testimonials, metrics, or marketing fluff.
- No plain-text email addresses or phone numbers in HTML. Emails are
  assembled in `site.js` from `data-mail` / `data-addr` attributes.
- Brand voice: professional, solid tech, business-exec — not "tech bro".
