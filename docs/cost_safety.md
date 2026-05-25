# Cost & Credential Safety

## Credentials: there are NONE in this repo (by design)
- Notebooks use auth.authenticate_user() -> browser login, no key file.
- CLI uses `gcloud auth login` -> browser login, no key file.
- The Data Agent uses your logged-in cloud identity.
- DO NOT ever create a service-account JSON key for this project. You don't need one.
- A project ID is NOT a secret (it appears in every GCP URL). Safe to publish.

## Cost protection (three layers)
1. Budget alert: Billing -> Budgets -> $10 cap, alerts at 50/90/100%.
2. The agent only queries MARTS (small), never raw JSON (the only big thing).
3. BigQuery gives 1 TiB free query processing/month. This dataset stays well under.

## Hard guard — cap bytes per query (paste in BigQuery before exploring)
Run any risky query with a billing cap so a mistake cannot run away:

    -- caps this query at ~1 GB; fails instead of charging if it would exceed
    SET @@maximum_bytes_billed = 1000000000;

In Dataform, add to workflow_settings.yaml if you want a global cap.
In the Data Agent console, set "maximum bytes billed" in query settings if available.
