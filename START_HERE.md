# START HERE — Scout, with your real project (statsbomb-football-iq)

Everything below has your real project ID already in it. Copy-paste as-is.
Region used throughout: europe-west1. Don't mix regions.

================================================================================
 STEP 1 — CLOUD SHELL SETUP   (console top-right terminal icon >_)
================================================================================
Paste this whole block into Cloud Shell:

    gcloud config set project statsbomb-football-iq

    gcloud services enable \
      bigquery.googleapis.com \
      storage.googleapis.com \
      dataform.googleapis.com \
      geminidataanalytics.googleapis.com \
      aiplatform.googleapis.com

    gsutil mb -l europe-west1 gs://statsbomb-football-iq-raw

    bq --location=europe-west1 mk --dataset statsbomb-football-iq:statsbomb_raw
    bq --location=europe-west1 mk --dataset statsbomb-football-iq:statsbomb_core
    bq --location=europe-west1 mk --dataset statsbomb-football-iq:statsbomb_marts
    bq --location=europe-west1 mk --dataset statsbomb-football-iq:agent_eval

Then set a BUDGET ALERT (console): Billing -> Budgets & alerts -> Create budget
-> $10, alerts at 50/90/100%. This is your cost safety net.

================================================================================
 STEP 2 — INGEST  (colab.research.google.com)
================================================================================
Upload notebooks/01_ingest.ipynb -> Runtime -> Run all.
  (CONFIG cell is already set: PROJECT_ID=statsbomb-football-iq,
   BUCKET=statsbomb-football-iq-raw. Log in with the SAME google account.)
Then upload notebooks/02_validate.ipynb -> Run all.
  Expect: 51 matches, 24 teams, ~3,400 events/match, near-zero missing xG.
  If a column-not-found error appears, paste it to me — 2-line fix in fact_event.

================================================================================
 STEP 3 — DATAFORM  (console -> BigQuery -> Dataform)
================================================================================
  a) Create repository "scout" (region europe-west1).
  b) Create development workspace "dev".
  c) Recreate the dataform/ folder structure and paste each file in.
     workflow_settings.yaml is ALREADY set to defaultProject: statsbomb-football-iq.
  d) Start execution -> Execute all actions -> Start.
  e) Watch the DAG go green. Red on an assertion = real data bug, fix it.
  Result: statsbomb_core.* and statsbomb_marts.* tables now exist.

================================================================================
 STEP 4 — xT + VISUALS  (Colab)
================================================================================
Upload notebooks/03_xt_grid.ipynb -> Run all  (builds mart_xt_grid).
Upload notebooks/04_visuals.ipynb -> Run all  (pass networks, shot maps,
  style radar, the 18-zone heatmaps + vulnerability map). These are your screenshots.

================================================================================
 STEP 5 — CREATE THE AGENT  (console -> BigQuery -> Data agents)
================================================================================
  a) Create agent "Scout Euro 2024 Analyst".
  b) Data sources: add ONLY statsbomb_marts.* and agent_eval.* tables.
     NEVER add statsbomb_raw (cost + correctness guard).
  c) Paste ALL of agent/scout_instructions.md into system instructions.
  d) Test with the questions in eval/question_tests.csv.

================================================================================
 STEP 6 — PROVE IT + PUBLISH
================================================================================
    bq load --autodetect --source_format=CSV \
      statsbomb-football-iq:agent_eval.gold_standard_checks \
      eval/gold_standard_checks.csv

Verify Scout reproduces reality (51 matches, correct final, Spain's 7 games).
Then push to GitHub — .gitignore blocks credentials; no secrets exist in this repo.

    git init
    git add .
    git commit -m "Scout: governed Euro 2024 football intelligence agent"
    git branch -M main
    git remote add origin https://github.com/YOURNAME/scout-euro-2024-intelligence.git
    git push -u origin main
