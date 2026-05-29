# Scout — Conversational Web App

A local web interface for the published Scout agent. Type a tactical question
in plain language (English or Slovak); Scout queries the verified BigQuery
marts and the app renders the answer on a football pitch.

This is the "interface layer" for a non-technical user. The thinking happens
in the agent; the football-native visuals happen here.

## Why local-only

The Conversational Analytics API bills the calling project per query. Running
locally with your own gcloud credentials means YOU pay for YOUR own usage,
and nobody else can ring up charges against you. This mirrors how internal
analytics tools at real clubs are deployed — on the analyst's machine,
against the team's GCP project, authenticated with their normal identity.
The same architecture would deploy to an internal Cloud Run instance for
the analyst staff.

## Run

```bash
pip install -r requirements.txt
gcloud auth application-default login   # one-time
streamlit run app.py
```

Then open http://localhost:8501.

## What it does

- **Chat input** in plain language; English or Slovak (sidebar toggle).
- **Calls the published Scout agent** via the Conversational Analytics API.
- **Renders the answer on a pitch:** zone heatmap, pass network, or shot map,
  chosen automatically from the shape of the data the agent returns.
- **Shows the SQL** the agent ran (collapsible).

## Cost

Each question = one Gemini call + one small BigQuery query against the marts.
Effectively pennies per question. Keep your GCP budget alert active.
