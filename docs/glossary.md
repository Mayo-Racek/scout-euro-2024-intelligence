# Scout Glossary — every term defined measurably

These are the definitions the agent uses. They live in ONE place (and in
constants.js) so they never drift. This is what lets Scout stay accurate.

**Forward pass** — a pass whose end point is more than 5m closer to the
opponent goal than its start (x increases by > 5 on the 120-long pitch).

**Backward pass** — end point more than 5m further from goal (x decreases by > 5).

**Progressive pass** — a completed pass ending at least 25% closer to the
opponent goal than where it started.

**Final-third entry** — a pass/carry ending at x >= 80.

**Box entry** — a pass/carry ending inside the penalty area (x >= 102, y 18-62).

**Opening phase** — first 15 minutes of a match unless another phase is asked.

**xG** — StatsBomb's shipped per-shot expected goals. Aggregated, never re-modelled.

**Non-penalty xG (npxG)** — xG excluding penalties.

**PPDA** — opponent passes in their build-up area divided by our defensive
actions high up the pitch. A PROXY for pressing intensity. Lower = more intense.

**xT (expected threat)** — a PROJECT-BUILT 16x12 grid model valuing pitch
locations. This is NOT StatsBomb's OBV / possession value. Always labelled as such.

**Style label** (e.g. "controlled_build_up") — a rule-based bucket defined by
visible thresholds over real metrics. NOT a black-box 0-1 score. Every label
is auditable from its components.

**Defensive structure** — inferred from event + 360 data. A PROXY, not
tracking-based team shape.

**Sample-size flag** — < 180 min = low; 180-360 = medium; 360+ = stronger.
Used to suppress overconfident finishing/skill claims.

## Zone model (added)
**18-zone grid** — pitch split into 3 thirds (Def/Mid/Att, lengthwise) x 6
channels (LW, LHS, LC, RC, RHS, RW, widthwise). A recognized analytics framework.
Each zone is ~40 x 13.3 on the 120x80 pitch. Labels are from the attacking
team's perspective.

**Zone control (zone_xg_control)** — own xG created in a zone minus opponent xG
conceded in that same zone. Positive = team wins that zone; negative = vulnerable.

**Net ball battle** — recoveries minus ball losses in a zone. Measures "where a
team is winning/losing battles" spatially.

**Half-space (LHS/RHS)** — the channels between centre and wing; tactically
important attacking zones.
