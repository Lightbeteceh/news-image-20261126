# The World in One Day — 26 November 2026

[![make.fun](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/Lightbeteceh/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/Lightbeteceh/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126)

A program that renders one deterministic image summing up the world news
of Thursday 26 November 2026 — a newspaper front page with three
illustrated lead stories, ten small cards, 25 more headlines, a numbers
strip and a UTC timeline. Full-day edition: every figure was re-checked
against the evening's developments before rendering.

## The day

Three tankers hit mines in the Strait of Hormuz, the Houthis hit the Ras
Tanura refinery, and Washington proposed new tariffs on 14 trading
partners. Brent settled at $96.57. EU leaders left Brussels with no deal
on a €45bn Ukraine loan. Drones killed two Italians in Kuwait and one
worker at the Jazan refinery. Asia's markets rebounded; the 100th Macy's
parade was postponed to Saturday.

## Files

- `main.py` — the renderer (Python 3, Pillow only). Reads `stories.json`,
  draws the 1024×1024 front page, writes `entry.png`.
- `stories.json` — the 38 stories: 3 leads, 10 small cards, 25 also-on
  headlines, plus the numbers strip and the UTC timeline. Every story is
  tagged CONFIRMED, OFFICIAL or REPORTED — no forecasts.
- `entry.png` — the rendered image (1024×1024, under 1 MiB).
- `fonts/` — DejaVu fonts used by the renderer.

## Run it

```sh
python3 main.py
```

The render is deterministic: running it twice produces byte-identical
`entry.png` files. The script prints the image hash and, for every card,
how many lines its headline and body took and how far the body sits above
its source line.

## Entry

Built for the [make.fun news-image-20261126 bounty](https://make.fun/bounty/news-image-20261126)
— "Sum up 26 November's world news in one image". MIT licensed.
