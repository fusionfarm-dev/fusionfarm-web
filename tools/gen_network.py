"""Generate the city-network SVG used in the hero (same map as the LinkedIn kit).

Run: python3 tools/gen_network.py > /tmp/net.svg  and paste between the
<!-- NETWORK:START --> / <!-- NETWORK:END --> markers in index.html,
or run with --inject to replace it in place.
"""
import pathlib, re, sys

W, H = 560, 360
CITIES = [("MSP", -93.3, 45.0, 1), ("CHI", -87.6, 41.9, 1), ("NYC", -74.0, 40.7, 0),
          ("MEX", -99.1, 19.4, 1), ("LON", -0.1, 51.5, 1), ("LIS", -9.1, 38.7, 1),
          ("DXB", 55.3, 25.2, 1), ("SIN", 103.8, 1.35, 1), ("TYO", 139.7, 35.7, 1),
          ("GRU", -46.6, -23.5, 1)]
HUBS = {"MSP", "CHI"}
LINKS = [("MSP", "LIS"), ("MSP", "LON"), ("CHI", "DXB"), ("MSP", "TYO"), ("CHI", "MEX"),
         ("LIS", "SIN"), ("CHI", "GRU"), ("LON", "DXB"), ("NYC", "LIS"), ("MSP", "CHI"),
         ("CHI", "NYC"), ("DXB", "SIN")]


def svg():
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
    out = svg()
    if "--inject" in sys.argv:
        f = pathlib.Path(__file__).resolve().parent.parent / "index.html"
        t = f.read_text()
        t, k = re.subn(r"(<!-- NETWORK:START -->).*?(<!-- NETWORK:END -->)",
                       lambda m: m.group(1) + out + m.group(2), t, flags=re.S)
        assert k == 1, "markers not found"
        f.write_text(t)
        print("injected")
    else:
        print(out)
