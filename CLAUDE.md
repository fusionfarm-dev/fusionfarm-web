# fusionfarm-web

Public website for Fusion Farm LLC — https://fusionfarm.net

Static site, no build step. Open `index.html` directly or serve the folder
(`python3 -m http.server`). Deploys to any static host as-is.

## Structure
- `index.html` — single page: hero (+ orbit graphic), service strip, the fusion
  (Field / AI / Network), what we do, why (before capital moves), AI design &
  implementation, who we are (+ network map), specialties, digital assets, contact
- `404.html` — not-found page (uses absolute `/assets` paths)
- `assets/css/site.css` — all styles
- `assets/js/site.js` — email assembly + mobile nav (progressive enhancement)
- `assets/img/logo.png` — the atomic mark, white on transparent; `logo-square.png`
  is the black-square version for favicon/social (do not redraw or replace)
- `tools/gen_graphics.py` — regenerates the orbit and city-network SVGs
  (`python3 tools/gen_graphics.py --inject` rewrites them between the ORBIT / NETWORK markers)

## Brand system (shared with the LinkedIn kit, fusionfarm-linkedin)
- Ink background `#0B0F14`, panels `#121821`, lines `#223040`
- Text `#EEF1F4`, muted `#8C98A6`
- Jade accent `#5ED6AA`, signal blue secondary `#7FB8FF`
- Manrope (headlines/body), JetBrains Mono uppercase for labels/eyebrows
- Atomic mark always paired with "Fusion Farm" wordmark; mark itself static
- Jade = AI, signal blue = Network, white = Field (orbit color coding)
- Orbit graphic: atomic mark at center ("People at the core"), orbits AI / Network / Field
- Network map: MSP/CHI hubs to LIS, LON, DXB, SIN, TYO, MEX, GRU, NYC
- Jade/blue gradient rule under the hero

## Identity (source of truth: LinkedIn kit, fusionfarm-linkedin PAGE-COPY.md)
- Headline: "Field-proven. AI-powered."  Eyebrow: "Fusion Farm LLC · Human + AI Intelligence"
- Secondary line: "Boots on the ground. AI in the cloud."
- Positioning: "Fusion Farm combines seasoned field operators with AI and a global
  network to find, verify and build what your decisions depend on."
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
