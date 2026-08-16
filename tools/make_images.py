#!/usr/bin/env python3
"""Deterministically render the site's two raster assets.

  assets/og-image.png          1200x630 — the social share card
  assets/apple-touch-icon.png  180x180  — iOS home-screen icon. It exists because
                                          Safari ignores an SVG in that slot; every
                                          other surface uses assets/favicon.svg.

The card is a calm branded composition on the Sunrise paper background: the app's
leaf mark, the "MonteSprout" wordmark in Quicksand, and the one-line value
proposition in Nunito. Both faces are vendored under tools/fonts/ (OFL, copied from
the app's DesignSystem resources) so this regenerates byte-identically on any
machine — no system font dependency, no network, no timestamp chunk (verified: two
runs hash the same).

The leaf is drawn from the **same two bezier paths** the app and the favicon use
(DesignSystem/Motifs.swift § LeafArt), flattened here rather than approximated, so
the card, the icon and the site cannot drift into three different marks.

Run:  python3 tools/make_images.py
Then commit the regenerated PNGs.

Requires Pillow. It is a build-time tool only — the site itself ships no
dependencies and no JavaScript.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OG_OUT = ROOT / "assets" / "og-image.png"
ICON_OUT = ROOT / "assets" / "apple-touch-icon.png"
ICON_SIZE = 180  # Apple's current recommended single size.
FONTS = Path(__file__).resolve().parent / "fonts"
QUICKSAND = FONTS / "Quicksand-Bold.ttf"
NUNITO = FONTS / "Nunito-Regular.ttf"

# Open Graph standard card size.
W, H = 1200, 630

# Locked Sunrise palette (MonteSprout docs/architecture.md §8).
PAPER = "#FBF6EF"
INK = "#3B362D"
INK_SOFT = "#6E6658"
SAGE = "#7C9A74"
HAIR = "#ECE4D6"

WORDMARK = "MonteSprout"
TAGLINE = "Small daily observations, turned into parent-ready reports."

# The app's leaf, as SVG path data in a 14-unit viewBox (LeafArt).
# Body: M12 2  C 5.5 2, 2 5.5, 2 12   c 6.5 0, 10 -3.5, 10 -10  Z
LEAF_BODY = [
    ((12.0, 2.0), (5.5, 2.0), (2.0, 5.5), (2.0, 12.0)),
    ((2.0, 12.0), (8.5, 12.0), (12.0, 8.5), (12.0, 2.0)),
]
# Vein: M4.5 9.5 C 6.5 8.5, 8.5 6.5, 9.5 4.5
LEAF_VEIN = [((4.5, 9.5), (6.5, 8.5), (8.5, 6.5), (9.5, 4.5))]
LEAF_VIEWBOX = 14.0


def _bezier(p0, p1, p2, p3, steps=64):
    """Flatten one cubic bezier to a point list (t in [0, 1])."""
    pts = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        x = u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0]
        y = u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1]
        pts.append((x, y))
    return pts


def _flatten(curves, ox, oy, scale):
    out = []
    for c in curves:
        seg = _bezier(*c)
        # Drop the duplicated join point between consecutive segments.
        out.extend(seg if not out else seg[1:])
    return [(ox + x * scale, oy + y * scale) for x, y in out]


def _draw_leaf(size: int) -> Image.Image:
    """Render the leaf at `size` px on a transparent canvas, supersampled 4x."""
    ss = 4
    canvas = Image.new("RGBA", (size * ss, size * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    scale = size * ss / LEAF_VIEWBOX

    # Fill only. The app strokes the same path 1.2 units wide because the glyph
    # renders at 13pt there; at this size the stroke adds nothing but a visible
    # mitre artefact where the two curves meet at the sharp tip.
    body = _flatten(LEAF_BODY, 0, 0, scale)
    d.polygon(body, fill=SAGE)

    # Pillow's line drawing has no anti-aliasing and its "curve" joint leaves
    # visible stair-steps even at 4x, so the vein is stamped as overlapping round
    # dabs along the flattened path — a round-capped stroke, smooth after the
    # LANCZOS downsample.
    r = max(1.0, 1.0 * scale) / 2
    for x, y in _flatten(LEAF_VEIN, 0, 0, scale):
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 128))

    return canvas.resize((size, size), Image.LANCZOS)


def _wrap(draw, text, font, max_width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if not cur or draw.textlength(trial, font=font) <= max_width:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def make_icon() -> Path:
    """The iOS home-screen icon: the leaf on paper, full-bleed (iOS masks it itself)."""
    img = Image.new("RGB", (ICON_SIZE, ICON_SIZE), PAPER)
    leaf_size = int(ICON_SIZE * 0.62)
    leaf = _draw_leaf(leaf_size)
    off = (ICON_SIZE - leaf_size) // 2
    img.paste(leaf, (off, off), leaf)
    img.save(ICON_OUT, "PNG", optimize=True)
    return ICON_OUT


def make_card() -> Path:
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # Subtle inset hairline frame, in the brand hairline colour.
    inset = 28
    draw.rounded_rectangle([inset, inset, W - inset, H - inset],
                           radius=24, outline=HAIR, width=2)

    # [leaf][gap][wordmark], centred as one group.
    wordmark_font = ImageFont.truetype(str(QUICKSAND), 84)
    leaf_size, gap = 104, 30

    wbox = draw.textbbox((0, 0), WORDMARK, font=wordmark_font)
    ww, wh = wbox[2] - wbox[0], wbox[3] - wbox[1]

    group_w = leaf_size + gap + ww
    left = (W - group_w) // 2
    row_cy = 250

    leaf = _draw_leaf(leaf_size)
    img.paste(leaf, (left, row_cy - leaf_size // 2), leaf)
    draw.text((left + leaf_size + gap, row_cy - wh // 2 - wbox[1]),
              WORDMARK, font=wordmark_font, fill=INK)

    # Accent rule beneath the group.
    rule_y, rule_w = 358, 96
    draw.rounded_rectangle(
        [(W - rule_w) // 2, rule_y, (W + rule_w) // 2, rule_y + 6], radius=3, fill=SAGE)

    # Tagline — wrapped, centred, soft ink.
    tag_font = ImageFont.truetype(str(NUNITO), 40)
    lines = _wrap(draw, TAGLINE, tag_font, W - 280)
    y, line_h = 412, tag_font.size + 16
    for line in lines:
        draw.text(((W - draw.textlength(line, font=tag_font)) / 2, y),
                  line, font=tag_font, fill=INK_SOFT)
        y += line_h

    img.save(OG_OUT, "PNG", optimize=True)
    return OG_OUT


if __name__ == "__main__":
    for path in (make_card(), make_icon()):
        head = path.read_bytes()[:24]
        # IHDR width/height are big-endian 32-bit ints at offsets 16 and 20.
        print(f"wrote {path.relative_to(ROOT)}  "
              f"({int.from_bytes(head[16:20], 'big')}x{int.from_bytes(head[20:24], 'big')})")
