#!/usr/bin/env python3
"""Render the 26 November 2026 world-news front page.

Deterministic: same input files always produce the same entry.png bytes.
Reads stories.json next to this file, draws a 1024x1024 newspaper front
page with three illustrated lead stories, ten small cards, an also-on list,
a numbers strip and a UTC timeline, and writes entry.png next to this file.

Layout rules enforced here (measured with PIL, never eyeballed):
  * every illustration is drawn on its own layer exactly the size of its
    box and pasted in, so no shape can cross the box edge;
  * every body is wrapped and, if it would overflow, shortened by whole
    sentences (then whole words) so it ends on a full stop, never "...";
  * every body ends at least 4 px above the source line under it.
"""

import hashlib
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024

PAPER = (246, 241, 227)
CARD = (255, 253, 246)
INK = (22, 21, 19)
GRAY = (107, 101, 90)
RULE = (60, 56, 48)
RED = (163, 22, 33)
BLUE = (31, 78, 121)
SKY = (215, 227, 232)
SEA = (46, 95, 122)
SAND = (232, 224, 204)

MARGIN = 24
CONTENT_W = W - 2 * MARGIN


def load_font(name, size):
    path = os.path.join(HERE, "fonts", name)
    return ImageFont.truetype(path, size)


SERIF_B = lambda s: load_font("DejaVuSerif-Bold.ttf", s)
SANS = lambda s: load_font("DejaVuSans.ttf", s)
SANS_B = lambda s: load_font("DejaVuSans-Bold.ttf", s)


def wrap(draw, text, font, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def sentences(text):
    parts = [p.strip() for p in text.split(". ") if p.strip()]
    return [p if p.endswith(".") else p + "." for p in parts]


def fit_body(draw, text, font, max_w, max_lines):
    """Wrap a body to at most max_lines; shorten by whole sentences first,
    then whole words, always ending on a full stop. Returns (lines, used)."""
    cur = text
    while True:
        lines = wrap(draw, cur, font, max_w)
        if len(lines) <= max_lines:
            return lines, cur
        sents = sentences(cur)
        if len(sents) > 1:
            cur = " ".join(sents[:-1])
        else:
            words = cur.split()
            if len(words) <= 1:
                return lines[:max_lines], cur
            cur = " ".join(words[:-1])
            if not cur.endswith("."):
                cur += "."


def fit_headline(draw, text, font, max_w, max_lines):
    lines = wrap(draw, text, font, max_w)
    assert len(lines) <= max_lines, "headline too long: %r -> %d lines" % (text, len(lines))
    return lines


def draw_card(draw, x, y, w, h):
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=CARD, outline=RULE, width=1)


def draw_source(draw, x, y, w, story):
    """Source + tag line, right-aligned tag. Returns its top y."""
    f = SANS(9)
    tag = story["tag"]
    src = story["source"].upper()
    tw = draw.textlength(tag, font=f)
    draw.text((x + w - tw, y), tag, font=f, fill=RED)
    draw.text((x, y), src, font=f, fill=GRAY)
    return y


# ---------------------------------------------------------------- illustrations
# Each draws on its own layer exactly the size of its box; every shape stays
# at least 6 px inside the layer edges, so nothing can poke out of the box.

def illus_tanker(bw, bh):
    layer = Image.new("RGB", (bw, bh), SKY)
    d = ImageDraw.Draw(layer)
    d.rectangle([0, 62, bw - 1, bh - 1], fill=SEA)
    # mine with spikes, lower left in the water
    mx, my, mr = 44, 76, 8
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1)):
        d.line([mx, my, mx + dx * (mr + 5), my + dy * (mr + 5)], fill=INK, width=2)
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=INK)
    # hull
    d.rounded_rectangle([34, 44, 262, 66], radius=4, fill=(34, 38, 43))
    d.rectangle([34, 44, 262, 50], fill=(52, 58, 64))
    # bridge tower, kept below the top edge
    d.rectangle([210, 22, 238, 44], fill=(52, 58, 64))
    d.rectangle([214, 27, 234, 33], fill=(180, 200, 210))
    # funnel + smoke
    d.rectangle([150, 30, 166, 44], fill=RED)
    for cx, cy, r in ((146, 20, 5), (156, 14, 6), (168, 18, 5)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 118, 112))
    # flame licking the deck
    d.polygon([(120, 44), (130, 30), (140, 44)], fill=(230, 120, 30))
    return layer


def illus_refinery(bw, bh):
    layer = Image.new("RGB", (bw, bh), SAND)
    d = ImageDraw.Draw(layer)
    d.rectangle([0, 78, bw - 1, bh - 1], fill=(168, 156, 132))
    # distillation towers
    d.rectangle([40, 30, 64, 78], fill=(70, 74, 80))
    d.rectangle([90, 18, 118, 78], fill=(52, 58, 64))
    d.rectangle([150, 38, 172, 78], fill=(70, 74, 80))
    d.polygon([(90, 18), (104, 8), (118, 18)], fill=(52, 58, 64))
    # smoke above the middle tower, top kept inside the layer
    for cx, cy, r in ((100, 13, 5), (112, 11, 4)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(110, 108, 102))
    # storage tank, right side
    d.rectangle([200, 52, 260, 78], fill=(120, 116, 108))
    d.ellipse([200, 46, 260, 58], fill=(140, 136, 128))
    # connecting pipe
    d.rectangle([64, 66, 200, 70], fill=(90, 94, 100))
    # flame at the right tower
    d.polygon([(156, 38), (164, 26), (172, 38)], fill=(230, 120, 30))
    return layer


def illus_tariffs(bw, bh):
    layer = Image.new("RGB", (bw, bh), (230, 226, 212))
    d = ImageDraw.Draw(layer)
    # axes
    d.line([30, 78, 280, 78], fill=INK, width=2)
    d.line([30, 10, 30, 78], fill=INK, width=2)
    # four bars, tallest top kept inside the layer
    bars = [(50, 58, BLUE), (95, 44, BLUE), (140, 30, BLUE), (185, 16, RED)]
    for x0, top, col in bars:
        d.rectangle([x0, top, x0 + 30, 78], fill=col)
    # rising arrow over the bars
    d.line([40, 66, 228, 20], fill=RED, width=3)
    d.polygon([(228, 20), (214, 22), (224, 32)], fill=RED)
    return layer


ILLUSTRATIONS = {"L1": illus_tanker, "L2": illus_refinery, "L3": illus_tariffs}


# ------------------------------------------------------------------- sections

def draw_masthead(draw):
    title = "THE WORLD IN ONE DAY"
    f = SERIF_B(40)
    tw = draw.textlength(title, font=f)
    draw.text(((W - tw) / 2, 16), title, font=f, fill=INK)
    left = "THURSDAY 26 NOVEMBER 2026"
    right = "38 STORIES  •  FULL-DAY EDITION"
    lf, rf = SANS_B(12), SANS(11)
    draw.text((MARGIN, 66), left, font=lf, fill=INK)
    rw = draw.textlength(right, font=rf)
    draw.text((W - MARGIN - rw, 67), right, font=rf, fill=GRAY)
    draw.line([MARGIN, 90, W - MARGIN, 90], fill=RULE, width=2)


def draw_numbers(draw, numbers):
    y0, y1 = 96, 142
    draw.line([MARGIN, y0, W - MARGIN, y0], fill=RULE, width=1)
    draw.line([MARGIN, y1, W - MARGIN, y1], fill=RULE, width=1)
    cell = CONTENT_W / len(numbers)
    for i, (label, value, sub) in enumerate(numbers):
        x = MARGIN + i * cell
        if i:
            draw.line([x, y0 + 4, x, y1 - 4], fill=(200, 194, 178), width=1)
        lf, vf, sf = SANS_B(9), SANS_B(15), SANS(9)
        draw.text((x + 8, y0 + 4), label, font=lf, fill=GRAY)
        sw = draw.textlength(sub, font=sf)
        draw.text((x + cell - 8 - sw, y0 + 5), sub, font=sf, fill=RED)
        draw.text((x + 8, y0 + 20), value, font=vf, fill=INK)


def draw_lead(draw, img, story, x, y, w, h, report):
    draw_card(draw, x, y, w, h)
    bw, bh = w - 16, 96
    layer = ILLUSTRATIONS[story["id"]](bw, bh)
    img.paste(layer, (x + 8, y + 8))
    draw.rectangle([x + 8, y + 8, x + 8 + bw - 1, y + 8 + bh - 1],
                   outline=RULE, width=1)
    hf = SANS_B(15)
    hlines = fit_headline(draw, story["headline"], hf, w - 16, 2)
    hy = y + 112
    for ln in hlines:
        draw.text((x + 8, hy), ln, font=hf, fill=INK)
        hy += 18
    bf = SANS(12)
    blines, used = fit_body(draw, story["body"], bf, w - 16, 4)
    by = hy + 6
    for ln in blines:
        draw.text((x + 8, by), ln, font=bf, fill=INK)
        by += 15
    sy = draw_source(draw, x + 8, y + h - 18, w - 16, story)
    gap = sy - by
    assert gap >= 4, "lead %s body too close to source: %d px" % (story["id"], gap)
    report.append("%s headline %d lines, body %d lines, gap %d px%s"
                  % (story["id"], len(hlines), len(blines), gap,
                     "" if used == story["body"] else " [SHORTENED]"))


def draw_small(draw, story, x, y, w, h, report):
    draw_card(draw, x, y, w, h)
    hf = SANS_B(12)
    hlines = fit_headline(draw, story["headline"], hf, w - 16, 2)
    hy = y + 8
    for ln in hlines:
        draw.text((x + 8, hy), ln, font=hf, fill=INK)
        hy += 15
    bf = SANS(10)
    blines, used = fit_body(draw, story["body"], bf, w - 16, 3)
    by = hy + 4
    for ln in blines:
        draw.text((x + 8, by), ln, font=bf, fill=INK)
        by += 13
    sy = draw_source(draw, x + 8, y + h - 15, w - 16, story)
    gap = sy - by
    assert gap >= 4, "small %s body too close to source: %d px" % (story["id"], gap)
    report.append("%s headline %d lines, body %d lines, gap %d px%s"
                  % (story["id"], len(hlines), len(blines), gap,
                     "" if used == story["body"] else " [SHORTENED]"))


def draw_also(draw, items):
    y0 = 694
    hf, rf = SANS_B(11), SANS(9)
    draw.text((MARGIN, y0), "ALSO ON THIS DAY", font=hf, fill=INK)
    right = "25 MORE STORIES"
    rw = draw.textlength(right, font=rf)
    draw.text((W - MARGIN - rw, y0 + 1), right, font=rf, fill=GRAY)
    draw.line([MARGIN, y0 + 18, W - MARGIN, y0 + 18], fill=RULE, width=1)
    f = SANS(10)
    col_w = (CONTENT_W - 32) / 2
    half = 13
    for col, chunk in enumerate((items[:half], items[half:])):
        x = MARGIN + col * (col_w + 32)
        yy = y0 + 26
        for it in chunk:
            lines = wrap(draw, it["headline"], f, col_w)
            assert len(lines) == 1, "also item wraps: %r" % it["headline"]
            draw.text((x, yy), lines[0], font=f, fill=INK)
            yy += 13.5
    return y0 + 26 + 13 * 13.5


def draw_utc(draw, strip):
    y0 = 898
    hf = SANS_B(10)
    draw.text((MARGIN, y0), "THE DAY IN UTC", font=hf, fill=INK)
    draw.line([MARGIN, y0 + 16, W - MARGIN, y0 + 16], fill=RULE, width=1)
    tf, bf = SANS_B(9.5), SANS(9.5)
    col_w = (CONTENT_W - 32) / 2
    for col, chunk in enumerate((strip[:4], strip[4:])):
        x = MARGIN + col * (col_w + 32)
        yy = y0 + 22
        for when, what in chunk:
            draw.text((x, yy), when, font=tf, fill=RED)
            tw = draw.textlength(when, font=tf)
            draw.text((x + tw + 8, yy), what, font=bf, fill=INK)
            yy += 13.5


def draw_footer(draw):
    f = SANS(9)
    text = ("Sources: Reuters  •  AP  •  CNN  •  UKMTO  •  Bank of Korea  •  ESA  •  The Edge"
            "   —   Rendered deterministically by main.py  •  Thursday 26 November 2026")
    tw = draw.textlength(text, font=f)
    draw.text(((W - tw) / 2, 980), text, font=f, fill=GRAY)


def main():
    with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    leads, small, also = data["lead"], data["small"], data["also"]
    assert len(leads) == 3 and len(small) == 10 and len(also) == 25
    assert len(leads) + len(small) + len(also) == 38
    tags = [s["tag"] for s in leads + small + also]
    assert "FORECAST" not in tags, "no FORECAST tags allowed"
    assert tags.count("CONFIRMED") == 27, tags.count("CONFIRMED")
    assert tags.count("OFFICIAL") == 4, tags.count("OFFICIAL")
    assert tags.count("REPORTED") == 7, tags.count("REPORTED")

    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    report = []

    draw_masthead(draw)
    draw_numbers(draw, data["numbers"])

    lw = (CONTENT_W - 2 * 20) // 3
    for i, story in enumerate(leads):
        draw_lead(draw, img, story, MARGIN + i * (lw + 20), 150, lw, 240, report)

    sw = (CONTENT_W - 4 * 12) // 5
    for row in range(2):
        for col in range(5):
            story = small[row * 5 + col]
            draw_small(draw, story, MARGIN + col * (sw + 12),
                       398 + row * 148, sw, 140, report)

    draw_also(draw, also)
    draw_utc(draw, data["utc_strip"])
    draw_footer(draw)

    out = os.path.join(HERE, "entry.png")
    img.save(out, format="PNG")
    with open(out, "rb") as fh:
        digest = hashlib.sha256(fh.read()).hexdigest()
    size = os.path.getsize(out)
    assert size <= 1024 * 1024, "entry.png over 1 MiB: %d" % size
    print("entry.png %d bytes sha256 %s" % (size, digest))
    for line in report:
        print("  " + line)


if __name__ == "__main__":
    main()
