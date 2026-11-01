#!/usr/bin/env python3
"""Render the server-rack background used behind the "How we work" section.

    python3 tools/make_rack_bg.py        # needs: playwright (python), Pillow

Original artwork (no stock imagery): network switch units with ports and green
status LEDs and patch cables, rendered crisp (no depth-of-field blur). Writes src/static/assets/img/rack-bg.webp.
"""
import pathlib, random

ROOT = pathlib.Path(__file__).resolve().parent.parent
W, H = 1600, 800
GREEN, GREEN_HI, GREEN_DIM = "#3DF59E", "#C9FFE6", "#1E7A52"


def scene():
    rnd = random.Random(7)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         '<defs>'
         '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#05080D"/><stop offset=".55" stop-color="#0A1420"/><stop offset="1" stop-color="#06101A"/></linearGradient>'
         '<linearGradient id="unit" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1B2D42"/><stop offset=".12" stop-color="#132131"/><stop offset="1" stop-color="#0B141F"/></linearGradient>'
         '<linearGradient id="port" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#020407"/><stop offset="1" stop-color="#0A121B"/></linearGradient>'
         '<filter id="bloom" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="14" result="a"/>'
         '<feGaussianBlur in="SourceGraphic" stdDeviation="4" result="b"/><feMerge><feMergeNode in="a"/><feMergeNode in="a"/><feMergeNode in="a"/><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
         '<filter id="bokeh" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3.5" result="d"/><feGaussianBlur stdDeviation="18" result="h"/><feMerge><feMergeNode in="h"/><feMergeNode in="d"/></feMerge></filter>'
         '<filter id="soft"><feGaussianBlur stdDeviation="3"/></filter>'
         '<radialGradient id="bk"><stop offset="0" stop-color="#8DFFC8"/><stop offset=".7" stop-color="#3DF59E" stop-opacity=".9"/><stop offset="1" stop-color="#22C77A" stop-opacity=".55"/></radialGradient>'
         '</defs>',
         f'<rect width="{W}" height="{H}" fill="url(#bg)"/>',
         '<radialGradient id="amb" cx=".45" cy="0" r=".7"><stop offset="0" stop-color="#2B4A78" stop-opacity=".45"/><stop offset="1" stop-color="#2B4A78" stop-opacity="0"/></radialGradient>',
         f'<rect width="{W}" height="{H}" fill="url(#amb)"/>']

    # faint top device with a cool blue-white indicator
    s.append('<rect x="0" y="40" width="1600" height="70" fill="#0C1622"/>'
             '<rect x="0" y="40" width="1600" height="2" fill="#5F86B4" fill-opacity=".25"/>'
             '<g filter="url(#bloom)"><rect x="640" y="66" width="22" height="8" rx="3" fill="#B9D4FF"/></g>')

    leds = []
    units = [(150, 150), (320, 150), (490, 150)]          # (y, height)
    for ui, (uy, uh) in enumerate(units):
        s.append(f'<rect x="0" y="{uy}" width="{W}" height="{uh}" fill="url(#unit)"/>'
                 f'<rect x="0" y="{uy}" width="{W}" height="1.5" fill="#8FB6E6" fill-opacity=".38"/>'
                 f'<rect x="0" y="{uy + uh - 2}" width="{W}" height="2" fill="#000" fill-opacity=".6"/>')
        # two rows of ports
        for row in range(2):
            py = uy + 30 + row * 60
            for i in range(26):
                px = 120 + i * 56 + (12 if i >= 13 else 0)
                s.append(f'<rect x="{px}" y="{py}" width="44" height="34" rx="3" fill="url(#port)" stroke="#3E5A7C" stroke-width="1.4"/>'
                         f'<rect x="{px + 8}" y="{py + 22}" width="28" height="8" rx="1.5" fill="#05090E"/>')
                for k in range(2):                       # two status LEDs per port
                    r = rnd.random()
                    if r < .62:
                        col, op = (GREEN_HI if rnd.random() < .18 else GREEN), 1
                    elif r < .78:
                        col, op = GREEN_DIM, .9
                    else:
                        continue
                    leds.append(f'<rect x="{px + 5 + k * 24}" y="{py - 11}" width="10" height="6" rx="2" fill="{col}" fill-opacity="{op}"/>')
        # a row of activity LEDs at the unit's edge
        for i in range(40):
            if rnd.random() < .7:
                leds.append(f'<circle cx="{110 + i * 36}" cy="{uy + uh - 14}" r="3" fill="{GREEN}"/>')
    s.append(f'<g filter="url(#bloom)">{"".join(leds)}</g>')

    # patch cables entering from the left (foreground, dark with a cool rim light)
    for i, (y0, y1, x1) in enumerate([(260, 205, 360), (330, 262, 420), (430, 375, 330), (520, 435, 470), (640, 545, 380)]):
        d = f"M-60 {y0 + 120} C 120 {y0 + 60}, {x1 - 140} {y1 + 10}, {x1} {y1}"
        s.append(f'<path d="{d}" fill="none" stroke="#04070B" stroke-width="30" stroke-linecap="round"/>'
                 f'<path d="{d}" fill="none" stroke="#6C93C4" stroke-opacity=".28" stroke-width="5" transform="translate(0,-11)"/>'
                 f'<rect x="{x1 - 6}" y="{y1 - 15}" width="58" height="30" rx="4" fill="#0B121B" stroke="#3A5576" stroke-opacity=".6"/>')

    # out-of-focus LEDs in the right foreground
    bok = []
    for row in range(5):
        for col in range(6):
            if rnd.random() < .78:
                cx = 1170 + col * 90 + row * 6
                cy = 140 + row * 130 + rnd.uniform(-8, 8)
                r = 30 + col * 5 + rnd.uniform(-4, 4)
                bok.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.0f}" fill="url(#bk)" fill-opacity="{rnd.uniform(.6, .95):.2f}"/>')
    # (out-of-focus foreground lights removed: keep the hardware crisp and readable)
    s.append("</svg>")
    return "".join(s)


def main():
    from playwright.sync_api import sync_playwright
    from PIL import Image, ImageFilter
    tmp = ROOT / "tools/.rack.html"
    tmp.write_text('<!doctype html><html><body style="margin:0">' + scene() + "</body></html>")
    png = ROOT / "tools/.rack.png"
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1.5)
        pg.goto(tmp.as_uri())
        pg.wait_for_timeout(300)
        pg.locator("svg").screenshot(path=str(png), timeout=180000)
        b.close()
    img = Image.open(png).convert("RGB")
    out = ROOT / "src/static/assets/img/rack-bg.webp"
    img.save(out, "WEBP", quality=72, method=6)
    tmp.unlink(); png.unlink()
    print(f"{out.relative_to(ROOT)}  {out.stat().st_size // 1024} KB  {img.size}")


if __name__ == "__main__":
    main()
