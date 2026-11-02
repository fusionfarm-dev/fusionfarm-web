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
import hashlib, html, json, math, pathlib, re, shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / "src", ROOT / "public"
CFG = json.loads((SRC / "site.json").read_text())
ORIGIN = CFG["origin"].rstrip("/")
DOMAINS = json.loads((SRC / "data/domains.json").read_text())
LISTED = [d for d in DOMAINS if d.get("listed")]

JADE, SIGNAL, TEXT = "#5ED6AA", "#7FB8FF", "#EEF1F4"
esc = html.escape

# --------------------------------------------------------------------------
# Hero map: supplied network image (assets/img/hero-map.webp, 450x253 source
# upscaled) with the three offices marked. Positions are in source-image units.
# --------------------------------------------------------------------------
MAP_W, MAP_H = 450, 253
OFFICES = [  # (code, x, y, label dx, label dy, anchor)
    ("SEA", 33.3, 87.5, -2.4, -3.2, "end"),
    ("MSP", 57.5, 92.6, -0.5, -4.0, "middle"),
    ("CHI", 63.2, 97.6, 2.6, 4.6, "start"),
]


def world_svg():
    out = [f'<svg class="world" viewBox="0 0 {MAP_W} {MAP_H}" role="img" '
           f'aria-label="Global network map with offices in Chicago, Minneapolis and Seattle" '
           f'preserveAspectRatio="xMidYMid meet">',
           '<defs><radialGradient id="hubg"><stop offset="0" stop-color="#FFE3D6" stop-opacity=".95"/>'
           '<stop offset=".35" stop-color="#FF5A3C" stop-opacity=".6"/><stop offset="1" stop-color="#FF3B2F" stop-opacity="0"/></radialGradient></defs>',
           f'<image href="/assets/img/hero-map.webp" x="0" y="0" width="{MAP_W}" height="{MAP_H}"/>']
    lines = json.loads((SRC / "data/hero-lines.json").read_text())
    out.append('<path class="hero__lines" fill="none" stroke="#50FFA0" stroke-opacity=".9" stroke-width="1.2" '
               'stroke-linecap="round" vector-effect="non-scaling-stroke" d="' + "".join(
        f"M{x0} {y0}Q{cx} {cy} {x1} {y1}" for x0, y0, cx, cy, x1, y1 in lines) + '"/>')
    out.append('<g class="offices">')
    for code, x, y, dx, dy, anchor in OFFICES:
        out.append(f'<circle class="hubglow" cx="{x}" cy="{y}" r="7" fill="url(#hubg)"/>')
        out.append(f'<circle class="node--hub" cx="{x}" cy="{y}" r="1.7" fill="#FFFFFF"/>')
    for code, x, y, dx, dy, anchor in OFFICES:
        out.append(f'<text class="hublabel" x="{x + dx:.1f}" y="{y + dy:.1f}" text-anchor="{anchor}" fill="#FFE3D6" font-size="5.4">{code}</text>')
    out.append("</g></svg>")
    return "".join(out)


# --------------------------------------------------------------------------
# Fusion orbit diagram
# --------------------------------------------------------------------------
def orbit_svg():
    W, H = 660, 560
    cx, cy = W // 2, 270
    out = [f'<svg class="orbit" viewBox="0 0 {W} {H}" role="img" '
           f'aria-label="Fusion diagram: Fusion Farm at the core, with Systems, Data and Field in orbit">']
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
    # each data point travels around its own orbit (SMIL animateMotion; paused for reduced motion in site.js)
    points = []   # drawn after the core so the electrons pass over the FF mark
    for ang, col, lab, t, dur in [(-28, JADE, "SYSTEMS", 0.0, 6), (28, SIGNAL, "DATA", 0.5, 8), (90, TEXT, "FIELD", 0.0, 10)]:
        rx, ry = 235, 82
        out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="{col}" '
                   f'stroke-opacity=".55" stroke-width="1.4" transform="rotate({ang} {cx} {cy})"/>')
        orbit = (f"M{cx + rx} {cy}A{rx} {ry} 0 1 1 {cx - rx} {cy}A{rx} {ry} 0 1 1 {cx + rx} {cy}")
        tx, anchor = (-14, "end") if lab == "DATA" else (14, "start")
        points.append(f'<g transform="rotate({ang} {cx} {cy})"><g class="orbit__point">'
                   f'<circle class="orbit__halo" r="14" fill="{col}" fill-opacity=".14"/>'
                   f'<circle r="5.5" fill="{col}"/>'
                   f'<text transform="rotate({-ang})" x="{tx}" y="-12" text-anchor="{anchor}" class="orbit__label" fill="{col}">{lab}</text>'
                   f'<animateMotion dur="{dur}s" begin="{-t * dur:.1f}s" repeatCount="indefinite" path="{orbit}"/>'
                   f'</g></g>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="96" fill="{JADE}" fill-opacity=".06"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="62" fill="#0B0F14" stroke="{JADE}" stroke-opacity=".35"/>')
    out.append(f'<image href="/assets/img/mark-white.png" x="{cx - 38}" y="{cy - 46}" width="77" height="92"/>')
    out.extend(points)
    out.append("</svg>")
    return "".join(out)


# --------------------------------------------------------------------------
# Domain cards
# --------------------------------------------------------------------------
def domain_card(d, head="h3"):
    price = esc(d["price"]) if d.get("price") else "Make an offer"
    terms = f'<p class="asset__terms">{esc(d["terms"])}</p>' if d.get("terms") else ""
    subj = f"/contact/?topic=domains&amp;about={esc(d['domain'])}"
    view = (f'<a class="link" href="{esc(d["url"])}" rel="noopener" target="_blank">View<span class="sr"> {esc(d["domain"])} '
            f'(opens in a new tab)</span> <span aria-hidden="true">↗</span></a>' if d.get("url")
            else '<span class="asset__soon mono">Site coming soon</span>')
    return f"""<article class="asset">
  <p class="asset__cat mono">{esc(d['category'])}</p>
  <{head} class="asset__name">{esc(d['domain'])}</{head}>
  <p class="asset__pitch">{esc(d['pitch'])}</p>
  <div class="asset__foot">
    <p class="asset__price">{price}</p>
    {terms}
    <div class="asset__links">
      {view}
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
<meta name="author" content="fusionfarm.net">
{canon}{robots}
<meta name="theme-color" content="#0B0F14">
<meta name="color-scheme" content="dark">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Fusion Farm">
<meta property="og:title" content="{esc(page.get('og_title', title))}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{ORIGIN}/assets/img/og-fusionfarm-v2-1200x627.jpg">
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
      <img class="brand__mark" src="/assets/img/mark-white.png" alt="" width="52" height="62">
      <span class="brand__text"><img class="brand__word" src="/assets/img/wordmark.svg" alt="" width="280" height="21"><span class="brand__cities mono">Chicago · Minneapolis · Seattle</span></span>
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
      <img class="brand__mark" src="/assets/img/mark-white.png" alt="" width="60" height="72">
      <span class="brand__text"><img class="brand__word" src="/assets/img/wordmark.svg" alt="" width="320" height="24"><span class="brand__cities mono">Chicago · Minneapolis · Seattle</span><span class="brand__tag">Intelligence, engineered.</span></span>
    </a>
    <dl class="foot__desks">
      <div><dt class="mono">Projects, research &amp; engagements</dt><dd><a class="link" data-mail="research" href="/contact/"><span data-addr="research">Contact form</span></a></dd></div>
      <div><dt class="mono">Digital assets &amp; domains</dt><dd><a class="link" data-mail="domains" href="/contact/"><span data-addr="domains">Contact form</span></a></dd></div>
      <div><dt class="mono">Client support</dt><dd><a class="link" data-mail="support" href="/contact/"><span data-addr="support">Contact form</span></a></dd></div>
      <div><dt class="mono">Contact</dt><dd><a class="link" data-tel href="/contact/">Call us</a></dd></div>
    </dl>
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


def _ver(rel):
    f = OUT / rel.lstrip("/")
    return hashlib.sha1(f.read_bytes()).hexdigest()[:10] if f.is_file() else None


def bust_caches():
    """Append ?v=<content hash> to every /assets/ URL so a deploy never serves stale CSS, JS or images.
    CSS is rewritten first (its own hash then reflects the new font and image URLs)."""
    css_ref = re.compile(r"url\((/assets/[^)?#]+)\)")
    for css in (OUT / "assets/css").glob("*.css"):
        text = css.read_text()
        css.write_text(css_ref.sub(lambda m: f"url({m.group(1)}?v={_ver(m.group(1))})" if _ver(m.group(1)) else m.group(0), text))
    attr_ref = re.compile(r'((?:href|src)=")(/assets/[^"?#]+)(")')
    for page in OUT.rglob("*.html"):
        text = page.read_text()
        page.write_text(attr_ref.sub(lambda m: f"{m.group(1)}{m.group(2)}?v={_ver(m.group(2))}{m.group(3)}" if _ver(m.group(2)) else m.group(0), text))


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
    bust_caches()
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
