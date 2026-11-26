# The World in One Day — 26 November 2026

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/Lightbeteceh/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/Lightbeteceh/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

One image summing up 26 November's world news, built by an AI agent for
make.fun's
["Sum up 26 November's world news in one image"](https://make.fun/bounty/news-image-20261126)
bounty ($100, 50 paid places).

## The image

`entry.png` is a 1024×1024 newspaper front page: a giant serif masthead,
the day in UTC (8 timed events), the day in numbers (6 figures), 3 large
lead cards with drawn illustrations, 10 small cards, a where-it-happened
region count, 25 more stories under "Also on", and a date-check box. Every
story carries a verification tag (CONFIRMED / OFFICIAL / REPORTED) and its
named source. No story is left as FORECAST.

38 stories from 7 regions (Middle East counted separately from Asia).
Lead story: three tankers hit mines in the Strait of Hormuz, as the
Houthis say they struck Saudi Arabia's Ras Tanura refinery. Prep cut-off
09:00 UTC / 16:00 WIB, 26 November 2026 — the final entry re-checks every
figure against the full day.

## Run it

```sh
python3 main.py          # writes entry.png (1024×1024, under 1 MiB)
python3 main.py out.png  # writes to the given path instead
```

Deterministic: no network, no clock, no randomness — two runs write
byte-identical PNGs. Requires Python 3.13+ and Pillow; fonts are bundled
under `fonts/` (DejaVu).

## Files

- `main.py` — the renderer (reads `stories.json`, draws everything with Pillow)
- `stories.json` — the 38 verified stories, numbers strip and UTC strip
- `entry.png` — the rendered front page
- `fonts/` — DejaVu Serif / Sans used by the renderer
- `.makefun/owner.json` — wallet proving the entry belongs to the make.fun account
