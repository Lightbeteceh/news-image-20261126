#!/usr/bin/env python3
"""The World in One Day -- 26 November 2026.

Renders one 1024x1024 PNG newspaper front page summing up the world news
of Thursday 26 November 2026. Deterministic: no network, no clock, no
randomness. Run twice and the bytes are identical.

    python3 main.py            # writes entry.png next to this file
    python3 main.py out.png    # writes to the given path instead

Data lives in stories.json beside this file: 38 verified stories
(27 CONFIRMED / 4 OFFICIAL / 7 REPORTED, 0 FORECAST), 3 lead cards,
10 small cards, 25 more under "Also on". Every story was verified
against a named real news source on 26 Nov 2026 (prep cut-off 09:00 UTC).
"""

import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024
PAPER = (247, 240, 220)
INK = (25, 23, 19)
FAINT = (90, 82, 68)
RULE = (25, 23, 19)
RED = (163, 22, 33)
NAVY = (31, 78, 121)
GREEN = (30, 107, 52)
SEA = (38, 84, 124)
SKY = (214, 228, 235)
ORANGE = (214, 110, 44)
GOLD = (198, 154, 52)
TEAL = (42, 122, 110)
RUST = (172, 84, 52)

TAG_FILL = {"CONFIRMED": GREEN, "OFFICIAL": NAVY, "REPORTED": RED}


def font(name, size):
    return ImageFont.truetype(os.path.join(HERE, "fonts", name), size)


SERIF = "DejaVuSerif.ttf"
SERIF_B = "DejaVuSerif-Bold.ttf"
SANS = "DejaVuSans.ttf"
SANS_B = "DejaVuSans-Bold.ttf"


def wrap(draw, text, fnt, width, max_lines=None):
    """Greedy word wrap; returns a list of lines (truncated with ...)."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and draw.textlength(lines[-1] + "...", font=fnt) > width:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1].rstrip() + "..."
    return lines


def draw_lines(draw, lines, x, y, fnt, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def tag_chip(draw, x, y, tag):
    """Small filled tag chip; returns its width."""
    fnt = font(SANS_B, 9)
    label = " " + tag + " "
    w = int(draw.textlength(label, font=fnt)) + 8
    h = 14
    draw.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=TAG_FILL[tag])
    draw.text((x + 4, y + 2), label, font=fnt, fill=(255, 255, 255))
    return w


# ---------------------------------------------------------------- illustrations
def draw_tanker(draw, x, y, w, h):
    """Strait of Hormuz: tanker, naval mines, one burst of fire."""
    draw.rectangle([x, y, x + w, y + h], fill=SKY)
    draw.rectangle([x, y + h - 34, x + w, y + h], fill=SEA)
    draw.rectangle([x, y + h - 38, x + w, y + h - 34], fill=(120, 160, 185))
    # tanker hull
    hx, hy, hw, hh = x + 28, y + h - 62, w - 90, 26
    draw.rectangle([hx, hy, hx + hw, hy + hh], fill=(30, 30, 34))
    draw.rectangle([hx, hy, hx + hw, hy + 6], fill=(200, 60, 44))
    draw.rectangle([hx + hw - 34, hy - 12, hx + hw - 10, hy], fill=(30, 30, 34))
    draw.rectangle([hx + hw - 34, hy - 22, hx + hw - 10, hy - 12], fill=(220, 220, 210))
    # funnel smoke (kept inside the illustration box)
    for cx, cy, r in [(hx + 40, hy - 4, 7), (hx + 56, hy - 10, 8), (hx + 74, hy - 12, 8)]:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 118, 112))
    # spiked mines
    for mx, my in [(x + 22, y + h - 18), (x + w - 60, y + h - 14), (x + w // 2 + 30, y + h - 22)]:
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
            draw.line([mx, my, mx + dx * 10, my + dy * 10], fill=(20, 20, 22), width=2)
        draw.ellipse([mx - 7, my - 7, mx + 7, my + 7], fill=(20, 20, 22))
    # explosion burst over the stern (kept inside the illustration box)
    bx, by = hx + 18, hy - 6
    for dx, dy, ln in [(-1, -1, 11), (0, -1, 13), (1, -1, 11), (-1, 0, 11),
                       (1, 0, 11), (-1, 1, 9), (0, 1, 9), (1, 1, 9)]:
        draw.line([bx, by, bx + dx * ln, by + dy * ln], fill=ORANGE, width=4)
    draw.ellipse([bx - 8, by - 8, bx + 8, by + 8], fill=(240, 180, 40))


def draw_refinery(draw, x, y, w, h):
    """Ras Tanura: refinery towers, flame, black smoke column."""
    draw.rectangle([x, y, x + w, y + h], fill=(238, 214, 170))
    draw.ellipse([x + w - 52, y + 10, x + w - 16, y + 46], fill=(240, 190, 90))
    # ground
    draw.rectangle([x, y + h - 22, x + w, y + h], fill=(70, 60, 48))
    # towers
    for tx, tw, th in [(x + 24, 26, 62), (x + 60, 20, 62), (x + 190, 30, 56)]:
        draw.rectangle([tx, y + h - 22 - th, tx + tw, y + h - 22], fill=(52, 48, 44))
        for ly in range(y + h - 22 - th + 8, y + h - 22 - 4, 10):
            draw.line([tx, ly, tx + tw, ly], fill=(120, 112, 100), width=1)
    # pipes
    draw.rectangle([x + 86, y + h - 40, x + 186, y + h - 34], fill=(52, 48, 44))
    draw.rectangle([x + 120, y + h - 58, x + 126, y + h - 22], fill=(52, 48, 44))
    # flame
    fx = x + 133
    draw.polygon([(fx - 14, y + h - 58), (fx, y + h - 84), (fx + 14, y + h - 58)],
                 fill=ORANGE)
    draw.polygon([(fx - 7, y + h - 58), (fx, y + h - 72), (fx + 7, y + h - 58)],
                 fill=(240, 180, 40))
    # smoke column
    for cx, cy, r in [(x + 210, y + 26, 12), (x + 222, y + 44, 15),
                      (x + 206, y + 62, 13), (x + 224, y + 76, 10)]:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(48, 46, 44))


def draw_tariffs(draw, x, y, w, h):
    """Tariffs: stacked shipping containers under a crane hook."""
    draw.rectangle([x, y, x + w, y + h], fill=(228, 232, 226))
    # crane line + hook
    draw.line([x + w // 2, y + 6, x + w // 2, y + 26], fill=INK, width=2)
    draw.rectangle([x + w // 2 - 8, y + 26, x + w // 2 + 8, y + 34], outline=INK, width=2)
    cols = [RUST, TEAL, GOLD, NAVY, (120, 90, 60), (90, 110, 90)]
    labels = ["20%", "$", "%", "14", "CN", "EU"]
    cw, chh = 84, 26
    positions = [(x + 16, y + h - 28), (x + 108, y + h - 28), (x + 200, y + h - 28),
                 (x + 62, y + h - 56), (x + 154, y + h - 56),
                 (x + 108, y + h - 82)]
    for i, (cx, cy) in enumerate(positions):
        draw.rectangle([cx, cy, cx + cw, cy + chh], fill=cols[i % len(cols)])
        draw.rectangle([cx, cy, cx + cw, cy + chh], outline=(255, 255, 255), width=1)
        for vx in range(cx + 12, cx + cw, 12):
            draw.line([vx, cy, vx, cy + chh], fill=(255, 255, 255), width=1)
        fnt = font(SANS_B, 13)
        lab = labels[i % len(labels)]
        tw = draw.textlength(lab, font=fnt)
        draw.text((cx + (cw - tw) / 2, cy + 5), lab, font=fnt, fill=(255, 255, 255))


ILLUSTRATIONS = [draw_tanker, draw_refinery, draw_tariffs]


# ------------------------------------------------------------------- page
def render(data):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 28  # side margin
    # outer double border
    d.rectangle([12, 12, W - 13, H - 13], outline=RULE, width=2)
    d.rectangle([17, 17, W - 18, H - 18], outline=RULE, width=1)

    y = 26
    # masthead
    title = "THE WORLD IN ONE DAY"
    tf = font(SERIF_B, 50)
    d.text(((W - d.textlength(title, font=tf)) / 2, y), title, font=tf, fill=INK)
    y += 60
    d.line([mx, y, W - mx, y], fill=RULE, width=2)
    y += 6
    d.line([mx, y, W - mx, y], fill=RULE, width=1)
    y += 8
    df = font(SANS_B, 13)
    left = "THURSDAY, 26 NOVEMBER 2026"
    right = "38 STORIES  •  7 REGIONS"
    mid = "THE DAY IN ONE PAGE"
    d.text((mx, y), left, font=df, fill=INK)
    d.text(((W - d.textlength(mid, font=df)) / 2, y), mid, font=df, fill=FAINT)
    d.text((W - mx - d.textlength(right, font=df), y), right, font=df, fill=INK)
    y += 20
    d.line([mx, y, W - mx, y], fill=RULE, width=2)
    y += 8

    # ---- UTC strip: 2 rows x 4 columns, time stacked above the text
    lf = font(SANS_B, 10)
    d.text((mx, y), "THE DAY IN UTC", font=lf, fill=RED)
    y += 14
    strip = data["utc_strip"]
    col_w = (W - 2 * mx) // 4
    row_h = 36
    for i, (when, what) in enumerate(strip):
        cx = mx + (i % 4) * col_w
        cy = y + (i // 4) * row_h
        wf = font(SANS_B, 10)
        d.text((cx, cy), when, font=wf, fill=RED)
        tf2 = font(SANS, 10)
        lines = wrap(d, what, tf2, col_w - 12, max_lines=2)
        draw_lines(d, lines, cx, cy + 12, tf2, INK, 11)
    y += 2 * row_h + 4
    d.line([mx, y, W - mx, y], fill=RULE, width=1)
    y += 6

    # ---- numbers strip: 6 cells
    nf = font(SERIF_B, 20)
    labf = font(SANS_B, 9)
    delf = font(SANS, 10)
    cell_w = (W - 2 * mx) // 6
    for i, (label, value, delta) in enumerate(data["numbers"]):
        cx = mx + i * cell_w
        if i:
            d.line([cx, y - 2, cx, y + 44], fill=(180, 172, 150), width=1)
        d.text((cx + 8, y), label, font=labf, fill=FAINT)
        d.text((cx + 8, y + 12), value, font=nf, fill=INK)
        d.text((cx + 8, y + 34), delta, font=delf, fill=FAINT)
    y += 46
    d.line([mx, y, W - mx, y], fill=RULE, width=2)
    y += 8

    # ---- 3 lead cards
    lead_w = (W - 2 * mx - 2 * 10) // 3
    lead_h = 232
    for i, story in enumerate(data["lead"]):
        x0 = mx + i * (lead_w + 10)
        d.rectangle([x0, y, x0 + lead_w, y + lead_h], outline=RULE, width=1)
        ILLUSTRATIONS[i](d, x0 + 1, y + 1, lead_w - 2, 88)
        d.line([x0, y + 89, x0 + lead_w, y + 89], fill=RULE, width=1)
        ty = y + 96
        tag_chip(d, x0 + 10, ty, story["tag"])
        rf = font(SANS, 9)
        d.text((x0 + 10, ty + 18), story["region"].upper() + "  •  " + story["source"].upper(),
               font=rf, fill=FAINT)
        hf = font(SERIF_B, 18)
        lines = wrap(d, story["headline"], hf, lead_w - 20, max_lines=3)
        by = draw_lines(d, lines, x0 + 10, ty + 34, hf, INK, 20)
        bf = font(SANS, 12)
        blines = wrap(d, story["body"], bf, lead_w - 20, max_lines=4)
        draw_lines(d, blines, x0 + 10, by + 4, bf, INK, 14)
    y += lead_h + 8

    # ---- small stories: header + 2 rows x 5
    hf2 = font(SANS_B, 11)
    d.text((mx, y), "MORE OF THE DAY", font=hf2, fill=RED)
    d.line([mx + 130, y + 7, W - mx, y + 7], fill=RULE, width=1)
    y += 13
    small_w = (W - 2 * mx - 4 * 8) // 5
    small_h = 98
    for i, story in enumerate(data["small"]):
        x0 = mx + (i % 5) * (small_w + 8)
        yy = y + (i // 5) * (small_h + 6)
        d.rectangle([x0, yy, x0 + small_w, yy + small_h], outline=(150, 142, 122), width=1)
        tag_chip(d, x0 + 8, yy + 7, story["tag"])
        sf = font(SANS_B, 11)
        lines = wrap(d, story["headline"], sf, small_w - 16, max_lines=2)
        ly = draw_lines(d, lines, x0 + 8, yy + 25, sf, INK, 12)
        bf = font(SANS, 10)
        blines = wrap(d, story["body"], bf, small_w - 16, max_lines=3)
        draw_lines(d, blines, x0 + 8, ly + 2, bf, INK, 10)
        rf = font(SANS, 8)
        d.text((x0 + 8, yy + small_h - 12), story["source"].upper(), font=rf, fill=FAINT)
    y += 2 * small_h + 6 + 8

    # ---- also on: 2 columns
    d.text((mx, y), "ALSO ON — 25 MORE", font=hf2, fill=RED)
    d.line([mx + 150, y + 7, W - mx, y + 7], fill=RULE, width=1)
    y += 14
    also = data["also"]
    col_w2 = (W - 2 * mx - 16) // 2
    af = font(SANS, 11)
    tagf = font(SANS_B, 9)
    rows = (len(also) + 1) // 2
    for i, story in enumerate(also):
        col = i % 2
        row = i // 2
        ax = mx + col * (col_w2 + 16)
        ay = y + row * 14
        tag = "[" + story["tag"] + "]"
        tw = d.textlength(tag, font=tagf)
        d.text((ax, ay), "• " + story["headline"], font=af, fill=INK)
        d.text((ax + col_w2 - tw, ay + 1), tag, font=tagf, fill=TAG_FILL[story["tag"]])
    y += rows * 14 + 6

    # ---- footer: region counts + date check + credits
    d.line([mx, y, W - mx, y], fill=RULE, width=2)
    y += 6
    regs = data["regions"]
    reg_line = "  •  ".join(f"{r} {n}" for r, n in regs.items())
    rf2 = font(SANS, 10)
    d.text((mx, y), "WHERE IT HAPPENED:  " + reg_line, font=rf2, fill=INK)
    y += 16
    box = "DATE CHECK — Thursday 26 November 2026  •  38 stories, 7 regions, 0 forecasts. Every figure checked against a named source."
    bf3 = font(SANS_B, 10)
    d.rectangle([mx, y, W - mx, y + 22], outline=RED, width=1)
    d.text((mx + 8, y + 5), box, font=bf3, fill=RED)
    y += 28
    cf = font(SANS, 9)
    credit = "Sources: Reuters, AP, CNN, France 24, Le Monde, ESA, UEFA, Bank of Korea, UKMTO, Farm Bureau.  Rendered by main.py — deterministic, no network."
    d.text((mx, y), credit, font=cf, fill=FAINT)
    return img


def main():
    with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    img = render(data)
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "entry.png")
    img.save(out, format="PNG", optimize=True)
    if os.path.isdir("/output"):
        img.save("/output/entry.png", format="PNG", optimize=True)
    print("wrote", out, img.size)


if __name__ == "__main__":
    main()
