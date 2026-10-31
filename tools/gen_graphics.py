"""Generate the inline SVG graphics for index.html (same designs as the LinkedIn kit).

  python3 tools/gen_graphics.py --inject

rewrites the markup between <!-- ORBIT:START/END --> and <!-- NETWORK:START/END -->.
"""
import math, pathlib, re, sys

# ---------------------------------------------------------------- orbit (hero)
def orbit_svg():
    W, H, cx, cy = 660, 520, 330, 250
    rx, ry = 235, 82
    s = [f'<svg class="orbit" viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="The Fusion Farm atomic mark at the center, orbited by AI, Network and Field">']
    # faded dot field
    for gx in range(cx - 322, cx + 323, 14):
        for gy in range(cy - 238, cy + 239, 14):
            d = ((gx - cx) / 330) ** 2 + ((gy - cy) / 245) ** 2
            if d < 1:
                s.append(f'<circle cx="{gx}" cy="{gy}" r=".8" class="o-grid" fill-opacity="{1 - d:.2f}"/>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="104" class="o-glow"/>')
    orbits = [(-28, "ai", "AI", 0.0, 14), (28, "net", "NETWORK", 0.5, 18), (90, "field", "FIELD", 0.0, 22)]
    for ang, cls, lab, t, dur in orbits:
        path = (f"M{cx + rx},{cy} A{rx},{ry} 0 1,1 {cx - rx},{cy} "
                f"A{rx},{ry} 0 1,1 {cx + rx},{cy}")
        th = 2 * math.pi * t
        ex, ey = rx * math.cos(th), ry * math.sin(th)
        a = math.radians(ang)
        px = cx + ex * math.cos(a) - ey * math.sin(a)
        py = cy + ex * math.sin(a) + ey * math.cos(a)
        s.append(f'<g class="o-{cls}">')
        s.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" class="o-ring" '
                 f'transform="rotate({ang} {cx} {cy})"/>')
        # fixed labelled node
        s.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="15" class="o-halo"/>')
        s.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5.5" class="o-node"/>')
        s.append(f'<text x="{px + 16:.1f}" y="{py - 13:.1f}" class="o-label">{lab}</text>')
        # travelling electron
        s.append(f'<g transform="rotate({ang} {cx} {cy})"><circle r="3" class="o-electron">'
                 f'<animateMotion dur="{dur}s" repeatCount="indefinite" path="{path}"/></circle></g>')
        s.append('</g>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="64" class="o-core"/>')
    s.append(f'<text x="{cx}" y="{cy + 100}" text-anchor="middle" class="o-caption">PEOPLE AT THE CORE</text>')
    s.append('</svg>')
    return "".join(s)


# ---------------------------------------------------------------- network (reach)
W, H = 560, 360
CITIES = [("MSP", -93.3, 45.0, 1), ("CHI", -87.6, 41.9, 1), ("NYC", -74.0, 40.7, 0),
          ("MEX", -99.1, 19.4, 1), ("LON", -0.1, 51.5, 1), ("LIS", -9.1, 38.7, 1),
          ("DXB", 55.3, 25.2, 1), ("SIN", 103.8, 1.35, 1), ("TYO", 139.7, 35.7, 1),
          ("GRU", -46.6, -23.5, 1)]
HUBS = {"MSP", "CHI"}
LINKS = [("MSP", "LIS"), ("MSP", "LON"), ("CHI", "DXB"), ("MSP", "TYO"), ("CHI", "MEX"),
         ("LIS", "SIN"), ("CHI", "GRU"), ("LON", "DXB"), ("NYC", "LIS"), ("MSP", "CHI"),
         ("CHI", "NYC"), ("DXB", "SIN")]


def network_svg():
    pad = 24
    lon0, lon1, lat0, lat1 = -110, 150, 58, -30
    P = {n: (pad + (lo - lon0) / (lon1 - lon0) * (W - 2 * pad),
             pad + (lat0 - la) / (lat0 - lat1) * (H - 2 * pad), lab)
         for n, lo, la, lab in CITIES}
    s = [f'<svg class="net" viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="Network map linking Minneapolis and Chicago to cities worldwide">']
    s.append('<defs><pattern id="dots" width="12" height="12" patternUnits="userSpaceOnUse">'
             '<circle cx="1" cy="1" r=".9" class="net-grid"/></pattern></defs>')
    s.append(f'<rect width="{W}" height="{H}" fill="url(#dots)"/>')
    for i, (a, b) in enumerate(LINKS):
        (ax, ay, _), (bx, by, _) = P[a], P[b]
        mx, my = (ax + bx) / 2, (ay + by) / 2 - max(18, abs(bx - ax) * .22)
        cls = "net-link hub" if a in HUBS else "net-link"
        s.append(f'<path class="{cls}" style="--i:{i}" d="M{ax:.1f},{ay:.1f} Q{mx:.1f},{my:.1f} {bx:.1f},{by:.1f}"/>')
    for n, (x, y, lab) in P.items():
        hub = n in HUBS
        if hub:
            s.append(f'<circle class="net-halo" cx="{x:.1f}" cy="{y:.1f}" r="11"/>')
        s.append(f'<circle class="net-node{" hub" if hub else ""}" cx="{x:.1f}" cy="{y:.1f}" r="{3.6 if hub else 3}"/>')
        if lab:
            below = n in ("CHI", "GRU", "SIN", "MEX")
            dy = 18 if below else -10
            dx = -12 if n == "MSP" else 5
            s.append(f'<text class="net-label{" hub" if hub else ""}" x="{x+dx:.1f}" y="{y+dy:.1f}">{n}</text>')
    s.append("</svg>")
    return "".join(s)


if __name__ == "__main__":
    if "--inject" not in sys.argv:
        print(orbit_svg()); print(network_svg()); sys.exit()
    f = pathlib.Path(__file__).resolve().parent.parent / "index.html"
    t = f.read_text()
    for key, fn in (("ORBIT", orbit_svg), ("NETWORK", network_svg)):
        t, k = re.subn(rf"(<!-- {key}:START -->).*?(<!-- {key}:END -->)",
                       lambda m: m.group(1) + fn() + m.group(2), t, flags=re.S)
        assert k == 1, f"{key} markers not found"
    f.write_text(t)
    print("injected")
