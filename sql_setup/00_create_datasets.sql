-- sql_setup/00_create_datasets.sql
-- Run with:  bq query --use_legacy_sql=false < this_file   (after editing project)
-- Or just run the bq mk commands in RUN_GUIDE Part 3 (simpler).

CREATE SCHEMA IF NOT EXISTS `statsbomb_raw`   OPTIONS(location="europe-west1");
CREATE SCHEMA IF NOT EXISTS `statsbomb_core`  OPTIONS(location="europe-west1");
CREATE SCHEMA IF NOT EXISTS `statsbomb_marts` OPTIONS(location="europe-west1");
CREATE SCHEMA IF NOT EXISTS `agent_eval`      OPTIONS(location="europe-west1");
