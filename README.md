# Scout — Euro 2024 Football Intelligence Agent

A governed football-analytics agent on Google Cloud, built on StatsBomb/Hudl
Euro 2024 open data. The agent answers tactical questions from a verified
metric layer — it does not improvise SQL.

Data: StatsBomb / Hudl Open Data, used for research/education with attribution.

## Why the layout looks like this
Dataform requires its config (workflow_settings.yaml), definitions/, and
includes/ to live at the REPOSITORY ROOT — so they are here at the top level,
not inside a subfolder. Everything else sits in clearly-named folders.

    /  (repo root = Dataform project root)
    workflow_settings.yaml   <- Dataform reads this here (must be at root)
    package.json             <- Dataform core dependency
    definitions/             <- the SQL: sources, core bricks, marts, assertions
      sources/
      core/                  <- fact_event, fact_pass, fact_shot, ...
      marts/                 <- the verified tables the agent reads
      assertions/            <- data-quality gates
    includes/                <- constants.js, zones.js (shared definitions)
    notebooks/               <- Colab: ingest + validate + xT + visuals
    agent/                   <- Data Agent system instructions + verified queries
    eval/                    <- gold-standard reality checks + question tests
    docs/                    <- glossary, boundaries, metric library, cost/safety
    START_HERE.md            <- full step-by-step run guide

## How to run
See START_HERE.md. Short version:
1. Cloud Shell: enable APIs, make bucket + 4 BigQuery datasets, set budget alert.
2. Colab: run notebooks/01_ingest.ipynb then 02_validate.ipynb.
3. Dataform: connect this GitHub repo, pull, Execute all actions.
4. Colab: 03_xt_grid.ipynb, 04_visuals.ipynb.
5. Create the Data Agent on the marts; paste agent/scout_instructions.md.
6. Run eval/ checks; you're live.

## Safety
No credentials anywhere — all auth is browser login. .gitignore blocks any
key file. Safe to keep public.
