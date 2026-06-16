# Scout — A Governed Football Intelligence Agent on Google Cloud

> Ask *"How did Spain start their games?"* or *"Where was England most vulnerable?"* and get an answer grounded in verified data — with the metric, the filter, and an honest caveat. Built on StatsBomb's open Euro 2024 dataset, on BigQuery + Dataform, exposed through a governed conversational agent.

---

## The idea in one paragraph

Modern football generates enormous amounts of event data, but raw events are not insight. A coach doesn't want a table of 187,000 rows — they want to know *how their opponent builds up, where they're fragile, who drives their attack.* Scout turns the public StatsBomb Euro 2024 dataset into a governed tactical-intelligence layer that a non-technical person can query in plain language. Crucially, Scout does **not** improvise SQL or invent metrics. Every answer traces back to a verified, documented calculation — and when it labels a team's style, it shows you the numbers behind the label rather than a black-box score.

**The thesis:** an AI agent knows football not because it sounds fluent, but because the data model, glossary, verified metrics, and quality gates taught it what tactical concepts actually mean.

---

## About the data: StatsBomb / Hudl Open Data

[StatsBomb](https://statsbomb.com/) (now part of Hudl) is one of the leading providers of football data. Beyond their commercial product, they release a generous **open dataset** for research and education — and in 2024 they published the complete **UEFA Euro 2024** tournament: all **51 matches**, with **event data** (~3,400 events per match: every pass, shot, carry, pressure, duel, with pitch coordinates and, for shots, their expected-goals value) plus **360 freeze-frame data** capturing the positions of players around key events.

This is unusually rich. Most public football data is match-level (final scores, totals). StatsBomb's open data is **event-level with locations and an xG model included** — which is what makes genuine tactical analysis possible from a free source. This project uses that Euro 2024 release (competition 55, season 282). All credit for the underlying data belongs to StatsBomb/Hudl; see `ATTRIBUTION.md`.

**An honest boundary:** this is event + freeze-frame data, *not* continuous tracking. Scout can analyse on-ball actions, locations, and the visible frame around events. It deliberately refuses questions it cannot support — distance covered, sprint counts, fatigue, continuous defensive-line height — because event data cannot answer them. Knowing the limits of your data is part of doing this credibly.

---

## What Scout can answer

| Question | Mart it uses | What you get back |
|---|---|---|
| How did Spain start their games? | `mart_team_phase_profile` | Opening-phase profile + the numbers behind it |
| Compare Spain vs England's style | `mart_team_style_labels` | Transparent style components (radar) |
| Where did Slovakia lose the ball? | `mart_team_zone_activity` | 18-zone turnover heatmap |
| Where is England vulnerable? | `mart_team_zone_control` | Per-zone "created minus conceded" map |
| Which teams pressed highest? | `mart_team_pressure_profile` | PPDA ranking (from real pressure events) |
| Who drove a team's possession? | `mart_player_match_profile` | Progressive passers, with sample-size honesty |

**A real finding from the pipeline:** England's most exposed area at Euro 2024 was the **attacking-third left-centre** channel — they conceded considerably more expected threat there than they created — while their strongest zone was the **right-centre**. That's a defensible spatial read produced entirely from open event data.

---

## How it's built, and why each choice matters

Scout is a pipeline, not a single app. Each tool does one job:
