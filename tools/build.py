#!/usr/bin/env python3
"""Build fusionfarm.net into public/.

    python3 tools/build.py          # writes public/
    python3 -m http.server -d public 8080

Pages live in src/pages/*.html as body fragments with {{TOKENS}}; this script
wraps them in the shared layout, renders the brand SVGs (world network map and
fusion orbit, ported from the fusionfarm-linkedin build.py), builds the domain
cards from src/data/domains.json, and writes sitemap, robots and host headers.
Standard library only.
"""
import html, json, math, pathlib, shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / "src", ROOT / "public"
CFG = json.loads((SRC / "site.json").read_text())
ORIGIN = CFG["origin"].rstrip("/")
DOMAINS = json.loads((SRC / "data/domains.json").read_text())
LISTED = [d for d in DOMAINS if d.get("listed")]

JADE, SIGNAL, TEXT = "#5ED6AA", "#7FB8FF", "#EEF1F4"
esc = html.escape

# --------------------------------------------------------------------------
# Global network map: dot-matrix land + a backbone mesh of network nodes
# (equirectangular, 1 unit = 1 degree). Links follow plausible terrestrial
# and subsea routes; transpacific links run off the map edges.
# --------------------------------------------------------------------------
NODES = {
    # North America
    "SEA": (-122.3, 47.6), "SFO": (-122.4, 37.8), "LAX": (-118.2, 34.1), "MSP": (-93.3, 45.0),
    "CHI": (-87.6, 41.9), "DFW": (-96.8, 32.8), "ATL": (-84.4, 33.7), "TOR": (-79.4, 43.7),
    "NYC": (-74.0, 40.7), "MIA": (-80.2, 25.8), "MEX": (-99.1, 19.4),
    # South America
    "BOG": (-74.1, 4.7), "LIM": (-77.0, -12.0), "SCL": (-70.7, -33.4), "EZE": (-58.4, -34.6),
    "GRU": (-46.6, -23.5), "FOR": (-38.5, -3.7),
    # Europe
    "LON": (-0.1, 51.5), "AMS": (4.9, 52.4), "FRA": (8.7, 50.1), "PAR": (2.35, 48.9),
    "MAR": (5.4, 43.3), "MAD": (-3.7, 40.4), "LIS": (-9.1, 38.7), "STO": (18.1, 59.3), "IST": (29.0, 41.0),
    # Africa and Middle East
    "LOS": (3.4, 6.5), "CPT": (18.4, -33.9), "JNB": (28.0, -26.2), "MBA": (39.7, -4.0),
    "DJI": (43.1, 11.6), "CAI": (31.2, 30.0), "DXB": (55.3, 25.2),
    # Asia-Pacific
    "BOM": (72.9, 19.1), "DEL": (77.2, 28.6), "MAA": (80.3, 13.1), "SIN": (103.8, 1.35),
    "HKG": (114.2, 22.3), "SEL": (127.0, 37.6), "TYO": (139.7, 35.7), "PER": (115.9, -31.9),
    "SYD": (151.2, -33.9),
}
EDGES = [
    # North America
    ("SEA", "SFO"), ("SFO", "LAX"), ("SEA", "MSP"), ("MSP", "CHI"), ("CHI", "TOR"), ("TOR", "NYC"),
    ("CHI", "NYC"), ("SFO", "DFW"), ("LAX", "DFW"), ("DFW", "CHI"), ("DFW", "ATL"), ("CHI", "ATL"),
    ("ATL", "NYC"), ("ATL", "MIA"), ("LAX", "MEX"), ("DFW", "MEX"), ("MSP", "DFW"),
    # Latin America
    ("MEX", "BOG"), ("MIA", "BOG"), ("BOG", "LIM"), ("LIM", "SCL"), ("SCL", "EZE"), ("EZE", "GRU"),
    ("GRU", "FOR"), ("MIA", "FOR"),
    # Atlantic
    ("NYC", "LON"), ("NYC", "MAD"), ("FOR", "LIS"),
    # Europe
    ("LON", "AMS"), ("LON", "PAR"), ("AMS", "FRA"), ("PAR", "FRA"), ("AMS", "STO"), ("FRA", "STO"),
    ("PAR", "MAR"), ("PAR", "MAD"), ("MAD", "LIS"), ("FRA", "IST"), ("MAR", "IST"),
    # Africa and Middle East
    ("LIS", "LOS"), ("LOS", "CPT"), ("CPT", "JNB"), ("JNB", "MBA"), ("MBA", "DJI"), ("DJI", "CAI"),
    ("MAR", "CAI"), ("IST", "CAI"), ("CAI", "DXB"), ("DJI", "DXB"),
    # Asia-Pacific
    ("DXB", "BOM"), ("DJI", "BOM"), ("BOM", "DEL"), ("BOM", "MAA"), ("DEL", "MAA"), ("MAA", "SIN"),
    ("SIN", "HKG"), ("HKG", "SEL"), ("HKG", "TYO"), ("SEL", "TYO"), ("SIN", "PER"), ("PER", "SYD"),
    ("SIN", "SYD"),
]
# links that leave the map edge (they continue across the Pacific)
STUBS = [("SEA", -1, 44.0), ("LAX", -1, 30.0), ("TYO", 1, 40.0), ("SYD", 1, -30.0), ("HKG", 1, 18.0)]
HUBS = ("CHI", "MSP", "SEA")
# a few packets moving along links out of the hubs (pulse animation)
PULSES = [("CHI", "NYC"), ("NYC", "LON"), ("MSP", "CHI"), ("SEA", "SFO"), ("CHI", "DFW"), ("LON", "AMS"),
          ("FRA", "IST"), ("DXB", "BOM"), ("MAA", "SIN"), ("SIN", "HKG"), ("FOR", "LIS"), ("MIA", "BOG"),
          ("SEA", "MSP"), ("NYC", "MAD"), ("CAI", "DXB"), ("HKG", "TYO"), ("GRU", "FOR"), ("LIS", "LOS"),
          ("PER", "SYD"), ("ATL", "MIA")]
LON0, LAT_TOP, LAT_BOT, LON1 = -132.0, 73.0, -47.0, 160.0  # crop: Alaska to Sydney


LONGHAUL = [("CHI", "LON"), ("CHI", "FRA"), ("CHI", "DXB"), ("CHI", "GRU"), ("MSP", "LIS"), ("SEA", "LON"),
            ("NYC", "DXB"), ("LON", "SIN"), ("FRA", "HKG"), ("DXB", "SIN"), ("LON", "JNB"), ("MIA", "MAD")]


def world_svg():
    X = lambda lon: lon - LON0
    Y = lambda lat: LAT_TOP - lat
    w, h = LON1 - LON0, LAT_TOP - LAT_BOT
    P = {n: (X(lo), Y(la)) for n, (lo, la) in NODES.items()}

    def curve(x1, y1, x2, y2, lift=.16, cap=9.0):
        # quadratic bow, bending poleward like a great-circle route on a flat map
        dx, dy = x2 - x1, y2 - y1
        d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d
        my = (y1 + y2) / 2
        pole = -1 if Y(0) > my else 1
        if ny * pole < 0:
            nx, ny = -nx, -ny
        k = min(cap, lift * d)
        return f"M{x1:.1f} {y1:.1f}Q{(x1 + x2) / 2 + nx * k:.1f} {my + ny * k:.1f} {x2:.1f} {y2:.1f}"

    seg = lambda a, b: curve(P[a][0], P[a][1], P[b][0], P[b][1])
    arc = lambda a, b: curve(P[a][0], P[a][1], P[b][0], P[b][1], lift=.34, cap=26.0)
    mesh = "".join(seg(a, b) for a, b in EDGES)
    longs = "".join(arc(a, b) for a, b in LONGHAUL)
    stubs = "".join(curve(P[n][0], P[n][1], 0 if d < 0 else w, Y(la)) for n, d, la in STUBS)
    out = [f'<svg class="world" viewBox="0 0 {w:.0f} {h:.0f}" role="img" '
           f'aria-label="Global network map: Chicago headquarters with Minneapolis and Seattle offices, '
           f'connected to a worldwide network" preserveAspectRatio="xMidYMid meet">',
           '<defs><radialGradient id="nodeg"><stop offset="0" stop-color="#FF6A4D" stop-opacity=".75"/>'
           '<stop offset="1" stop-color="#FF3B2F" stop-opacity="0"/></radialGradient>'
           '<radialGradient id="hubg"><stop offset="0" stop-color="#FF8A6B" stop-opacity=".9"/>'
           '<stop offset=".45" stop-color="#FF3B2F" stop-opacity=".35"/><stop offset="1" stop-color="#FF3B2F" stop-opacity="0"/></radialGradient></defs>',
           f'<image href="/assets/img/hero-earth.webp" x="0" y="0" width="{w:.0f}" height="{h:.0f}" preserveAspectRatio="none"/>',
           f'<path class="net__stub" d="{stubs}"/>',
           f'<path class="net__glow" d="{mesh}{longs}"/>',
           f'<path class="net__mesh" d="{mesh}"/>',
           f'<path class="net__long" d="{longs}"/>',
           '<g class="net__pulses">']
    for a, b in PULSES:
        out.append(f'<path class="pulse" pathLength="1" d="{seg(a, b)}"/>')
    for a, b in LONGHAUL[:8]:
        out.append(f'<path class="pulse pulse--long" pathLength="1" d="{arc(a, b)}"/>')
    out.append('</g><g class="net__nodes">')
    for n, (x, y) in P.items():
        if n in HUBS:
            continue
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.2" fill="url(#nodeg)"/>')
        out.append(f'<circle class="node" cx="{x:.1f}" cy="{y:.1f}" r=".55"/>')
    for n in HUBS:                       # hubs last so they sit on top
        x, y = P[n]
        r = 5.2 if n == "CHI" else 3.8
        out.append(f'<circle class="hubglow{" hubglow--hq" if n == "CHI" else ""}" cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="url(#hubg)"/>')
        out.append(f'<circle class="node node--hub" cx="{x:.1f}" cy="{y:.1f}" r="{1.15 if n == "CHI" else .95}"/>')
    for n, dx, dy, anchor in (("CHI", 2.2, 5.4, "start"), ("MSP", -1.4, -3.0, "end"), ("SEA", 1.4, -3.0, "start")):
        x, y = P[n]
        out.append(f'<text class="hublabel" x="{x + dx:.1f}" y="{y + dy:.1f}" text-anchor="{anchor}">{n}</text>')
    out.append("</g></svg>")
    return "".join(out)


# --------------------------------------------------------------------------
# Fusion orbit diagram
# --------------------------------------------------------------------------
def orbit_svg():
    W, H = 660, 560
    cx, cy = W // 2, 270
    out = [f'<svg class="orbit" viewBox="0 0 {W} {H}" role="img" '
           f'aria-label="Fusion diagram: experience at the core, with Systems, Data and Field in orbit">']
    # dot grid fading toward the edge, binned into a few round-capped paths
    bins = {}
    for gx in range(cx - 322, cx + 330, 14):
        for gy in range(cy - 252, cy + 260, 14):
            dd = ((gx - cx) / 330) ** 2 + ((gy - cy) / 250) ** 2
            if dd < 1:
                bins.setdefault(min(4, int(dd * 5)), []).append(f"M{gx} {gy}h0")
    for b, segs in sorted(bins.items()):
        out.append(f'<path d="{"".join(segs)}" stroke="#2A3746" stroke-width="1.6" stroke-linecap="round" '
                   f'stroke-opacity="{1 - b / 5:.1f}"/>')
    for ang, col, lab, t in [(-28, JADE, "SYSTEMS", 0.0), (28, SIGNAL, "DATA", 0.5), (90, TEXT, "FIELD", 0.0)]:
        rx, ry = 235, 82
        out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="{col}" '
                   f'stroke-opacity=".55" stroke-width="1.4" transform="rotate({ang} {cx} {cy})"/>')
        th = 2 * math.pi * t
        ex, ey = rx * math.cos(th), ry * math.sin(th)
        a = math.radians(ang)
        px, py = cx + ex * math.cos(a) - ey * math.sin(a), cy + ex * math.sin(a) + ey * math.cos(a)
        out.append(f'<circle class="orbit__halo" cx="{px:.1f}" cy="{py:.1f}" r="14" fill="{col}" fill-opacity=".14"/>')
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5.5" fill="{col}"/>')
        tx = px + 14 if lab != "DATA" else px - 14
        anchor = "start" if lab != "DATA" else "end"
        out.append(f'<text x="{tx:.1f}" y="{py - 12:.1f}" text-anchor="{anchor}" class="orbit__label" fill="{col}">{lab}</text>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="96" fill="{JADE}" fill-opacity=".06"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="62" fill="#0B0F14" stroke="{JADE}" stroke-opacity=".35"/>')
    out.append(f'<image href="/assets/img/mark-white.png" x="{cx - 38}" y="{cy - 46}" width="77" height="92"/>')
    out.append(f'<text x="{cx}" y="{cy + 92}" text-anchor="middle" class="orbit__caption">EXPERIENCE AT THE CORE</text>')
    out.append("</svg>")
    return "".join(out)


# --------------------------------------------------------------------------
# Domain cards
# --------------------------------------------------------------------------
def domain_card(d, head="h3"):
    price = esc(d["price"]) if d.get("price") else "Make an offer"
    terms = f'<p class="asset__terms">{esc(d["terms"])}</p>' if d.get("terms") else ""
    subj = f"/contact/?topic=domains&amp;about={esc(d['domain'])}"
    return f"""<article class="asset">
  <p class="asset__cat mono">{esc(d['category'])}</p>
  <{head} class="asset__name">{esc(d['domain'])}</{head}>
  <p class="asset__pitch">{esc(d['pitch'])}</p>
  <div class="asset__foot">
    <p class="asset__price">{price}</p>
    {terms}
    <div class="asset__links">
      <a class="link" href="{esc(d['url'])}" rel="noopener" target="_blank">View<span class="sr"> {esc(d['domain'])} (opens in a new tab)</span> <span aria-hidden="true">↗</span></a>
      <a class="link" href="{subj}">Inquire<span class="sr"> about {esc(d['domain'])}</span> <span aria-hidden="true">→</span></a>
    </div>
  </div>
</article>"""


def domain_grid(teaser=False):
    items = [d for d in LISTED if d.get("teaser")][:4] if teaser else LISTED
    return "\n".join(domain_card(d, "h3" if teaser else "h2") for d in items)


# --------------------------------------------------------------------------
# Layout
# --------------------------------------------------------------------------
NAV = [("/#services", "Services"), ("/#process", "How we work"), ("/domains/", "Domains")]


def jsonld():
    org = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": CFG["name"],
        "alternateName": "Fusion Farm",
        "url": ORIGIN + "/",
        "logo": ORIGIN + "/icon-512.png",
        "slogan": "Intelligence, engineered.",
        "description": "Fusion Farm designs and builds intelligence systems: the technology that turns "
                       "scattered data, documents and signals into clear, decision-ready answers.",
        "address": [
            {"@type": "PostalAddress", "addressLocality": "Chicago", "addressRegion": "IL", "addressCountry": "US"},
            {"@type": "PostalAddress", "addressLocality": "Minneapolis", "addressRegion": "MN", "addressCountry": "US"},
            {"@type": "PostalAddress", "addressLocality": "Seattle", "addressRegion": "WA", "addressCountry": "US"},
        ],
        "areaServed": "Worldwide",
        "sameAs": [CFG["linkedin"]],
    }
    return '<script type="application/ld+json">' + json.dumps(org, separators=(",", ":")) + "</script>"


def layout(page):
    path, title, desc = page["path"], page["title"], page["desc"]
    canonical = ORIGIN + path
    current = ' aria-current="page"'
    nav = "".join(
        f'<a href="{href}"{current if href == path else ""}>{label}</a>' for href, label in NAV)
    robots = '<meta name="robots" content="noindex">' if page.get("noindex") else ""
    canon = "" if page.get("noindex") else f'<link rel="canonical" href="{canonical}">'
    extra = page.get("head", "")
    return f"""<!doctype html>
<html lang="en" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{canon}{robots}
<meta name="theme-color" content="#0B0F14">
<meta name="color-scheme" content="dark">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Fusion Farm">
<meta property="og:title" content="{esc(page.get('og_title', title))}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{ORIGIN}/assets/img/og-fusionfarm-1200x627.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="627">
<meta property="og:image:alt" content="Fusion Farm — Intelligence, engineered.">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/assets/fonts/manrope-latin-800-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/manrope-latin-500-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/site.css">
{jsonld() if path == "/" else ""}{extra}
</head>
<body class="page-{page['slug']}">
<a class="skip" href="#main">Skip to content</a>
<header class="nav">
  <div class="wrap nav__inner">
    <a class="brand brand--nav" href="/" aria-label="Fusion Farm, home">
      <img class="brand__mark" src="/assets/img/mark-white.png" alt="" width="40" height="48">
      <img class="brand__word" src="/assets/img/wordmark.svg" alt="" width="248" height="19">
    </a>
    <button class="nav__toggle" type="button" aria-expanded="false" aria-controls="nav-links">
      <span class="sr">Menu</span><span class="bar"></span><span class="bar"></span>
    </button>
    <nav id="nav-links" class="nav__links" aria-label="Primary">
      {nav}<a class="btn btn--sm" href="/contact/">Start a project</a>
    </nav>
  </div>
</header>
<main id="main">
{page['body']}
</main>
<footer class="foot">
  <div class="wrap foot__stack">
    <a class="brand brand--foot" href="/" aria-label="Fusion Farm, home">
      <img class="brand__mark" src="/assets/img/mark-white.png" alt="" width="44" height="53">
      <img class="brand__word" src="/assets/img/wordmark.svg" alt="" width="272" height="20">
    </a>
    <p class="foot__tag">Intelligence, engineered.</p>
    <dl class="foot__desks">
      <div><dt class="mono">Projects, research &amp; engagements</dt><dd><a class="link" data-mail="research" href="/contact/"><span data-addr="research">Contact form</span></a></dd></div>
      <div><dt class="mono">Digital assets &amp; domains</dt><dd><a class="link" data-mail="domains" href="/contact/"><span data-addr="domains">Contact form</span></a></dd></div>
      <div><dt class="mono">Client support</dt><dd><a class="link" data-mail="support" href="/contact/"><span data-addr="support">Contact form</span></a></dd></div>
      <div><dt class="mono">Contact</dt><dd><a class="link" data-tel href="/contact/">Call us</a></dd></div>
    </dl>
    <p class="foot__cities mono"><span>Chicago <em>HQ</em></span> · Minneapolis · Seattle</p>
  </div>
  <div class="wrap foot__base">
    <p class="foot__links"><a class="link" href="{CFG['linkedin']}" rel="noopener">LinkedIn</a><span aria-hidden="true">·</span><a class="link" href="/privacy/">Privacy</a></p>
    <p>© <span data-year>2026</span> Fusion Farm LLC</p>
  </div>
</footer>
<script src="/assets/js/site.js" defer></script>
{page.get('scripts', '')}
</body>
</html>
"""


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------
TITLE_HOME = "Fusion Farm — Intelligence systems, research & technology solutions"
DESC_HOME = ("Fusion Farm designs and builds intelligence systems that turn scattered data into decision-ready "
             "answers. Research, due diligence and technology solutions. Chicago · Minneapolis · Seattle.")

PAGES = [
    dict(slug="home", src="home.html", path="/", title=TITLE_HOME, desc=DESC_HOME,
         og_title="Fusion Farm — Intelligence, engineered."),
    dict(slug="contact", src="contact.html", path="/contact/", title="Contact — Fusion Farm",
         desc="Start a project with Fusion Farm. Tell us the decision you're trying to make, and we'll route it to the right desk."),
    dict(slug="domains", src="domains.html", path="/domains/", title="Digital assets — Fusion Farm",
         desc="Premium domains from the Fusion Farm digital asset portfolio, available direct or via Escrow.com."),
    dict(slug="privacy", src="privacy.html", path="/privacy/", title="Privacy — Fusion Farm",
         desc="How Fusion Farm handles the information you send us. No cookies, no trackers."),
    dict(slug="notfound", src="404.html", path="/404.html", title="Not found — Fusion Farm",
         desc="That page isn't on the map.", noindex=True),
]


def render_tokens(text):
    tokens = {
        "{{WORLD}}": world_svg(),
        "{{ORBIT}}": orbit_svg(),
        "{{DOMAINS_TEASER}}": domain_grid(teaser=True),
        "{{DOMAINS_ALL}}": domain_grid(),
        "{{DOMAIN_OPTIONS}}": "".join(f'<option value="{esc(d["domain"])}">{esc(d["domain"])}</option>' for d in LISTED),
    }
    for k, v in tokens.items():
        text = text.replace(k, v)
    assert "{{" not in text, f"unrendered token in page: {text[text.index('{{'):text.index('{{') + 40]}"
    return text


def csp():
    # Turnstile is loaded only when the server-side contact config is enabled,
    # but the policy always allows it so turning the form on needs no rebuild.
    ts = "https://challenges.cloudflare.com"
    parts = [
        "default-src 'self'",
        f"script-src 'self' {ts}",
        "style-src 'self'",
        "img-src 'self' data:",
        "font-src 'self'",
        f"connect-src 'self' {ts}",
        f"frame-src {ts}",
        "form-action 'self' mailto:",
        "base-uri 'self'",
        "object-src 'none'",
        "frame-ancestors 'none'",
        "upgrade-insecure-requests",
    ]
    return "; ".join(parts)


SEC_HEADERS = lambda: {
    "Content-Security-Policy": csp(),
    "Strict-Transport-Security": "max-age=31536000",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Cross-Origin-Opener-Policy": "same-origin",
}


def write_hosting_files():
    h = SEC_HEADERS()
    # Cloudflare Pages / Netlify
    lines = ["/*"] + [f"  {k}: {v}" for k, v in h.items()]
    lines += ["", "/assets/*", "  Cache-Control: public, max-age=31536000, immutable",
              "/assets/css/*", "  Cache-Control: public, max-age=86400",
              "/assets/js/*", "  Cache-Control: public, max-age=86400", ""]
    (OUT / "_headers").write_text("\n".join(lines))
    # Apache (DreamHost)
    ht = ["# Generated by tools/build.py", "Options -Indexes", "ErrorDocument 404 /404.html", "",
          "# contact form: only the two endpoints are reachable",
          '<FilesMatch "^(common)\\.php$">', "  Require all denied", "</FilesMatch>", "",
          "RewriteEngine On", "RewriteCond %{HTTPS} off",
          "RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]",
          "RewriteCond %{HTTP_HOST} ^www\\.(.+)$ [NC]",
          "RewriteRule ^ https://%1%{REQUEST_URI} [L,R=301]",
          "RewriteRule ^(contact|domains|privacy)$ /$1/ [L,R=301]",
          "RewriteRule ^assets/?$ /domains/ [L,R=301]", "",
          "<IfModule mod_headers.c>"]
    ht += [f'  Header always set {k} "{v}"' for k, v in h.items()]
    ht += ['  <FilesMatch "\\.(woff2|png|jpg|ico|svg)$">',
           '    Header set Cache-Control "public, max-age=31536000, immutable"', "  </FilesMatch>",
           "</IfModule>", "",
           "<IfModule mod_deflate.c>",
           "  AddOutputFilterByType DEFLATE text/html text/css application/javascript application/json image/svg+xml",
           "</IfModule>", "AddType application/manifest+json .webmanifest", ""]
    (OUT / ".htaccess").write_text("\n".join(ht))
    (OUT / "_redirects").write_text("/assets /domains/ 301\n/contact /contact/ 301\n/domains /domains/ 301\n/privacy /privacy/ 301\n")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SRC / "static", OUT)
    for p in PAGES:
        p["body"] = render_tokens((SRC / "pages" / p["src"]).read_text())
        rel = p["path"].strip("/")
        dest = OUT / (rel if rel.endswith(".html") else (rel + "/index.html" if rel else "index.html"))
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(layout(p))
    urls = [p["path"] for p in PAGES if not p.get("noindex")]
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{ORIGIN}{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {ORIGIN}/sitemap.xml\n")
    (OUT / "site.webmanifest").write_text(json.dumps({
        "name": "Fusion Farm", "short_name": "Fusion Farm", "start_url": "/", "display": "browser",
        "background_color": "#0B0F14", "theme_color": "#0B0F14",
        "icons": [{"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"}]}, indent=1))
    write_hosting_files()
    print(f"built {len(PAGES)} pages -> {OUT.relative_to(ROOT)}/  ({len(LISTED)} domains listed)")


if __name__ == "__main__":
    main()
