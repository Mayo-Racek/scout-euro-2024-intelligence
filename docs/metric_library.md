# Canonical Metric Library

Each metric = ONE definition the agent calls. Never improvised. Source of the
flags is dataform/includes/constants.js + the fact tables.

| Metric | Definition | Source brick |
|---|---|---|
| xG | sum of StatsBomb per-shot xg | fact_shot.xg |
| npxG | xG excluding penalties | fact_shot (is_penalty) |
| forward/backward pass | end_x - start_x vs +/-5m | fact_pass.pass_direction |
| progressive pass | ends >=25% closer to goal | fact_pass.is_progressive |
| final-third entry | end_x >= 80 | fact_pass.into_final_third |
| box entry | end inside penalty area | fact_pass.into_box |
| pass completion under pressure | completed / total where under_pressure | mart_team_match_profile |
| PPDA | opp build-up passes / our high def actions | mart_team_pressure_profile |
| xT added | grid xT(end) - grid xT(start) | mart_xt_grid (notebook 03) |
| style label | rule over components (no 0-1 score) | mart_team_style_labels |
