#!/usr/bin/env python3
"""Render the static night-Earth layer of the hero map to WebP.

    python3 tools/make_hero_layer.py      # needs: playwright (python), Pillow

Draws the continents (Natural Earth 50m, cropped in src/data/land-crop.json),
faint coastlines and glowing city lights in the hero's projection, renders it
with Chromium at 8 px per degree, and writes src/static/assets/img/hero-earth.webp.
Arcs, nodes and pulses are drawn live on top by tools/build.py.
"""
import json, math, pathlib, random, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from build import NODES, HUBS, LON0, LON1, LAT_TOP, LAT_BOT  # one source of truth for the projection

PX = 6                                   # pixels per degree in the raster
W, H = LON1 - LON0, LAT_TOP - LAT_BOT
X = lambda lon: (lon - LON0)
Y = lambda lat: (LAT_TOP - lat)


def land_path():
    polys = json.loads((ROOT / "src/data/land-crop.json").read_text())
    return "".join("M" + "L".join(f"{X(lo):.2f} {Y(la):.2f}" for lo, la in ring) + "Z" for ring in polys)


def city_lights():
    """Deterministic speckle: dense around network nodes, sparse over populated land."""
    rnd = random.Random(42)
    land = json.loads((ROOT / "src/data/world-dots.json").read_text())
    land = [(lo, la) for lo, la in land if LON0 <= lo <= LON1 and LAT_BOT <= la <= LAT_TOP]
    land_set = {(round(lo / 2.2), round(la / 2.2)) for lo, la in land}
    on_land = lambda lo, la: (round(lo / 2.2), round(la / 2.2)) in land_set
    pts = []
    for n, (lo, la) in NODES.items():
        count = 160 if n in HUBS else 90
        spread = 2.4 if n in HUBS else 1.9
        for _ in range(count):
            a, b = rnd.gauss(lo, spread), rnd.gauss(la, spread * .7)
            if on_land(a, b):
                d = math.hypot(a - lo, b - la)
                pts.append((a, b, max(.1, 1 - d / (spread * 2.0)) ** 1.6, n in HUBS))
    for lo, la in land:                   # background lights, mostly mid-latitudes
        # sparse, dim background lights; fewer in the big empty interiors
        near = min(math.hypot(lo - a, la - b) for a, b in NODES.values())
        p = .4 if near < 12 else .14
        if -40 < la < 62 and rnd.random() < p:
            pts.append((lo + rnd.uniform(-1.1, 1.1), la + rnd.uniform(-1.1, 1.1), rnd.uniform(.08, .26), False))
    return pts


def svg():
    lights = []
    for lo, la, k, hub in city_lights():
        r = .12 + .14 * k
        col = "#FFC9AE" if k > .8 else "#FF6A4D"
        lights.append(f'<circle cx="{X(lo):.2f}" cy="{Y(la):.2f}" r="{r:.2f}" fill="{col}" fill-opacity="{min(.95, .2 + .7 * k):.2f}"/>')
    hub_glow = "".join(
        f'<circle cx="{X(lo):.1f}" cy="{Y(la):.1f}" r="{9 if n == "CHI" else 6}" fill="url(#hg)"/>'
        for n, (lo, la) in NODES.items() if n in HUBS)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W * PX:.0f}" height="{H * PX:.0f}" viewBox="0 0 {W:.0f} {H:.0f}">
<defs>
 <linearGradient id="landg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2B3746"/><stop offset="1" stop-color="#1C2530"/></linearGradient>
 <radialGradient id="hg"><stop offset="0" stop-color="#FF4A36" stop-opacity=".45"/><stop offset="1" stop-color="#FF4A36" stop-opacity="0"/></radialGradient>
 <filter id="glow" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation=".3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
 <filter id="soft"><feGaussianBlur stdDeviation=".6"/></filter>
</defs>
<path d="{land_path()}" fill="url(#landg)" fill-opacity=".92" stroke="#8FB0D0" stroke-opacity=".22" stroke-width=".12"/>
<g filter="url(#soft)" opacity=".9">{hub_glow}</g>
<g filter="url(#glow)">{"".join(lights)}</g>
</svg>"""


def main():
    from playwright.sync_api import sync_playwright
    from PIL import Image
    tmp = ROOT / "tools/.hero-layer.html"
    tmp.write_text('<!doctype html><html><body style="margin:0;background:transparent">' + svg() + "</body></html>")
    png = ROOT / "tools/.hero-layer.png"
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": int(W * PX), "height": int(H * PX)})
        pg.goto(tmp.as_uri())
        pg.wait_for_timeout(500)
        pg.locator("svg").screenshot(path=str(png), omit_background=True, timeout=180000)
        b.close()
    out = ROOT / "src/static/assets/img/hero-earth.webp"
    Image.open(png).save(out, "WEBP", quality=74, method=6)
    tmp.unlink(); png.unlink()
    print(f"{out.relative_to(ROOT)}  {out.stat().st_size // 1024} KB  ({int(W * PX)}x{int(H * PX)})")


if __name__ == "__main__":
    main()
