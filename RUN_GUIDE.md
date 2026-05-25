# RUN_GUIDE — every command, in order

Prerequisites: a Google account, a Google Cloud project with billing enabled,
and the `gcloud` CLI installed (https://cloud.google.com/sdk/docs/install).
You can run all CLI parts from Cloud Shell in the browser (no local install) —
open https://console.cloud.google.com and click the terminal icon top-right.

Throughout, replace statsbomb-football-iq with your real project id.

================================================================================
PART 0 — GCLOUD SETUP  (run in Cloud Shell or local terminal)
================================================================================

# Log in and pick your project
gcloud auth login
gcloud config set project statsbomb-football-iq

# Turn on the APIs we need
gcloud services enable \
  bigquery.googleapis.com \
  storage.googleapis.com \
  dataform.googleapis.com \
  geminidataanalytics.googleapis.com \
  aiplatform.googleapis.com

# Create a Cloud Storage bucket for the raw JSON archive
# (bucket names are globally unique — add your initials/number)
gsutil mb -l europe-west1 gs://statsbomb-football-iq-raw

# Set a budget alert so a runaway query can never surprise you.
# Console route: Billing -> Budgets & alerts -> Create budget -> $10, alert at 50/90/100%.
# (Budgets are easiest in the console; the CLI form is verbose.)

echo "Part 0 done. APIs on, bucket created."

================================================================================
PART 1 & 2 — INGEST + VALIDATE   (in Google Colab, NOT the CLI)
================================================================================
# 1. Go to https://colab.research.google.com
# 2. File -> Upload notebook -> pick notebooks/01_ingest.ipynb
# 3. Edit the CONFIG cell (project id, bucket name), then Runtime -> Run all.
# 4. Repeat with notebooks/02_validate.ipynb
# These load all 51 matches into Cloud Storage AND BigQuery (statsbomb_raw).

================================================================================
PART 3 — CREATE BIGQUERY DATASETS   (bq CLI)
================================================================================
bq --location=europe-west1 mk --dataset statsbomb-football-iq:statsbomb_raw
bq --location=europe-west1 mk --dataset statsbomb-football-iq:statsbomb_core
bq --location=europe-west1 mk --dataset statsbomb-football-iq:statsbomb_marts
bq --location=europe-west1 mk --dataset statsbomb-football-iq:agent_eval
# (statsbomb_raw may already exist from Colab — that's fine, it'll just warn.)

================================================================================
PART 4 — DATAFORM: BUILD CORE + MARTS   (the SQL brain)
================================================================================
# EASIEST ROUTE — Dataform web UI (recommended first time):
#  a) Console -> BigQuery -> Dataform -> Create repository "scout"
#  b) Create a development workspace.
#  c) Upload every file from this repo's dataform/ folder, same structure.
#  d) Edit dataform/workflow_settings.yaml -> set defaultDatabase: statsbomb-football-iq
#  e) Click "Start execution" -> "Execute all actions". Watch the DAG turn green.
#
# CLI ROUTE (if you prefer terminal) — requires the dataform CLI:
npm i -g @dataform/cli
cd dataform
dataform install
# edit workflow_settings.yaml: defaultDatabase: statsbomb-football-iq
dataform compile          # checks all SQL compiles
dataform run              # builds core tables, marts, runs assertions
# A failed assertion = a real data bug. Fix before continuing.

================================================================================
PART 5 & 6 — xT GRID + VISUALS   (Colab again)
================================================================================
# Upload notebooks/03_xt_grid.ipynb and 04_visuals.ipynb to Colab, Run all.
# 03 builds the expected-threat grid into statsbomb_marts.
# 04 reads the marts and draws pass networks, shot maps, radar charts.

================================================================================
PART 7 — CREATE THE DATA AGENT   (Conversational Analytics)
================================================================================
# Console route (recommended):
#  a) Console -> BigQuery -> Gemini Data Analytics / "Data agents" -> Create.
#  b) Name: "Scout Euro 2024 Analyst".
#  c) Data sources: ADD ONLY the statsbomb_marts.* tables + agent_eval tables.
#     DO NOT add statsbomb_raw (cost + the agent must use verified marts only).
#  d) System instructions: paste the entire contents of agent/scout_instructions.md
#  e) Save. Test with the questions in eval/question_tests.csv.

================================================================================
PART 8 — RUN EVALUATION
================================================================================
# Load the gold-standard facts so you can verify the agent against reality:
bq load --autodetect --source_format=CSV \
  statsbomb-football-iq:agent_eval.gold_standard_checks \
  eval/gold_standard_checks.csv

# Then ask the agent each question in eval/question_tests.csv and score it.
# A question is PASS only if: right mart used + right filter + numbers match
# the gold-standard reality + caveat present where required.

echo "If all gold-standard checks reproduce and the example questions pass, Scout works."
