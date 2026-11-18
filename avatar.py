#!/usr/bin/env python3
"""
avatar.py: draws my GitHub profile picture.

Starship-style heat shield: black hexagonal tiles that end in a ragged edge,
with bare stainless steel showing beyond it (and through a few missing tiles).

    python3 avatar.py                       -> writes avatar.svg (500x500)
    python3 avatar.py --seed 7 -o mine.svg  -> same style, different tiles
    rsvg-convert -w 500 avatar.svg -o avatar.png    # optional PNG

With no options it draws exactly the original picture.
Run `python3 avatar.py --help` to see every setting.

No dependencies beyond the Python standard library.
"""
import argparse
import math
import random

SIZE = 500
TILE = 17                      # hexagon radius in px (centre to corner)
GAP = 1.2                      # dark seam between tiles
EDGE_SLOPE = 1.15              # how steep the tile line runs across the picture
EDGE_OFFSET = 60               # where the tile line sits
EDGE_WOBBLE = 12               # tiles end in a ragged line, not a straight cut
MISSING = 0.025                # share of tiles knocked off (steel shows through)
TILE_SHADES = ["#141417", "#18181c", "#1c1c21", "#121215"]
SEED = 12                      # same seed -> same picture every time


def hexagon(cx, cy, r, corners=range(6)):
    """Points of a pointy-top hexagon (Starship's tiles sit point-up)."""
    return " ".join(
        f"{cx + r * math.cos(math.radians(60 * k + 30)):.1f},"
        f"{cy + r * math.sin(math.radians(60 * k + 30)):.1f}"
        for k in corners
    )


def steel():
    """Brushed stainless steel: a diagonal sheen plus fine horizontal grain."""
    grad = (
        '<linearGradient id="steel" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#e9ebee"/><stop offset=".35" stop-color="#a9aeb5"/>'
        '<stop offset=".6" stop-color="#dfe2e6"/><stop offset="1" stop-color="#8d939b"/>'
        "</linearGradient>"
    )
    body = f'<rect width="{SIZE}" height="{SIZE}" fill="url(#steel)"/>'
    body += "".join(
        f'<line x1="0" y1="{y}" x2="{SIZE}" y2="{y}" stroke="#fff" stroke-width=".6" opacity=".35"/>'
        for y in range(3, SIZE, 5)
    )
    return grad, body


def tiles():
    random.seed(SEED)
    w = math.sqrt(3) * TILE                # horizontal distance between tile centres
    out = []
    for row in range(-1, int(SIZE / (1.5 * TILE)) + 2):
        for col in range(-1, int(SIZE / w) + 2):
            cx = col * w + (w / 2 if row % 2 else 0)   # every other row shifted half a tile
            cy = row * 1.5 * TILE
            if cx - cy * EDGE_SLOPE > EDGE_OFFSET + EDGE_WOBBLE * math.sin(cy / 40):
                continue                    # past the tile line: bare steel
            if random.random() < MISSING:
                continue                    # a missing tile
            shade = random.choice(TILE_SHADES)
            out.append(f'<polygon points="{hexagon(cx, cy, TILE - GAP)}" fill="{shade}"/>')
            # a faint highlight on the top three edges gives each tile a little depth
            out.append(
                f'<polyline points="{hexagon(cx, cy, TILE - 2.5, (3, 4, 5))}" '
                f'fill="none" stroke="#3a3a42" stroke-width="1.2"/>'
            )
    return "".join(out)


def parse_args():
    p = argparse.ArgumentParser(description="Draw a heat-shield avatar as an SVG file.")
    p.add_argument("--seed", type=int, default=SEED,
                   help=f"picks which tiles go missing and each tile's shade (default {SEED})")
    p.add_argument("--tile", type=float, default=TILE,
                   help=f"tile radius in px, centre to corner (default {TILE})")
    p.add_argument("--slope", type=float, default=EDGE_SLOPE,
                   help=f"how far the tile edge leans; lower is more upright (default {EDGE_SLOPE})")
    p.add_argument("--offset", type=float, default=EDGE_OFFSET,
                   help=f"where the tile edge sits; higher means more tiles (default {EDGE_OFFSET})")
    p.add_argument("--wobble", type=float, default=EDGE_WOBBLE,
                   help=f"how ragged the tile edge is; 0 is a straight cut (default {EDGE_WOBBLE})")
    p.add_argument("--missing", type=float, default=MISSING,
                   help=f"share of tiles knocked off, from 0 to 1 (default {MISSING})")
    p.add_argument("--size", type=int, default=SIZE,
                   help=f"width and height in px (default {SIZE})")
    p.add_argument("-o", "--out", default="avatar.svg",
                   help="file to write (default avatar.svg)")
    return p.parse_args()


def main():
    global SEED, TILE, EDGE_SLOPE, EDGE_OFFSET, EDGE_WOBBLE, MISSING, SIZE
    args = parse_args()
    SEED, TILE, EDGE_SLOPE = args.seed, args.tile, args.slope
    EDGE_OFFSET, EDGE_WOBBLE, MISSING, SIZE = args.offset, args.wobble, args.missing, args.size

    grad, steel_body = steel()
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}" '
        f'width="{SIZE}" height="{SIZE}"><defs>{grad}</defs>'
        f'<rect width="{SIZE}" height="{SIZE}" fill="#050507"/>{steel_body}{tiles()}</svg>'
    )
    with open(args.out, "w") as f:
        f.write(svg)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
