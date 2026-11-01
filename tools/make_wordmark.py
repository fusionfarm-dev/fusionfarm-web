#!/usr/bin/env python3
"""Outline the FUSION FARM wordmark (Michroma) into SVG files.

    pip install fonttools brotli
    python3 tools/make_wordmark.py

Writes src/static/assets/img/wordmark.svg (light, for dark backgrounds) and
wordmark-ink.svg (dark, for light backgrounds), plus copies in brand/.
The site uses these files, so visitors never download the font.
Font: brand/fonts/michroma-latin-400-normal.woff2 (SIL OFL 1.1).
"""
import pathlib
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONT = ROOT / "brand/fonts/michroma-latin-400-normal.woff2"
TEXT = "FUSION FARM"
TRACKING = 0.06          # letter-spacing in em, as approved in the font comparison
COLORS = {"wordmark.svg": "#EEF1F4", "wordmark-ink.svg": "#0E1116"}


def outline():
    font = TTFont(FONT)
    upm = font["head"].unitsPerEm
    cmap, glyphs, hmtx = font.getBestCmap(), font.getGlyphSet(), font["hmtx"]
    track = TRACKING * upm
    svg_pen = SVGPathPen(glyphs)
    bounds = BoundsPen(glyphs)
    x = 0.0
    for i, ch in enumerate(TEXT):
        name = cmap[ord(ch)]
        # flip y (font units are y-up) and advance along the baseline
        glyphs[name].draw(TransformPen(svg_pen, (1, 0, 0, -1, x, 0)))
        glyphs[name].draw(TransformPen(bounds, (1, 0, 0, -1, x, 0)))
        x += hmtx[name][0] + (track if i < len(TEXT) - 1 else 0)
    xmin, ymin, xmax, ymax = bounds.bounds
    return svg_pen.getCommands(), (xmin, ymin, xmax - xmin, ymax - ymin)


def main():
    d, (vx, vy, vw, vh) = outline()
    out_dirs = [ROOT / "src/static/assets/img", ROOT / "brand"]
    for name, color in COLORS.items():
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vx:.0f} {vy:.0f} {vw:.0f} {vh:.0f}" '
               f'role="img" aria-label="Fusion Farm"><path fill="{color}" d="{d}"/></svg>\n')
        for o in out_dirs:
            o.mkdir(parents=True, exist_ok=True)
            (o / name).write_text(svg)
    print(f"wordmark aspect {vw / vh:.3f}:1  ({vw:.0f}x{vh:.0f} font units)")


if __name__ == "__main__":
    main()
