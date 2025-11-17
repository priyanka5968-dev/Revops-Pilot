RevOps Pilot - Quick Start

Purpose
This folder contains a minimal dbt canonical pipeline model and LLM prompt/templates to run a pilot for Perfect Ventures.

Contents
- models/canonical_pipeline.sql — a dbt model that unions HubSpot & Sheets sources into a canonical pipeline table.
- models/schema.yml — simple dbt tests for the canonical model.
- prompts/weekly_summary_prompt.txt — LLM prompt for generating an executive weekly summary.
- templates/weekly_summary_template.md — markdown template for the weekly summary report.

Getting started (assumes dbt and a data warehouse configured)
1. Add source definitions in your dbt project `models` or `sources`:
   - `hubspot_raw.deals` should point to the replicated HubSpot deals table.
   - `sheets_raw.pipeline_sheet` should point to the sheet/table used for manual pipeline entries.

2. Copy this folder into your dbt project or add as a subfolder and reference models in `dbt_project.yml`.

3. Run dbt model and tests:

```powershell
# from your dbt project root (Windows PowerShell)
dbt deps; dbt run --select revops-pilot.models.canonical_pipeline; dbt test --select revops-pilot.models.canonical_pipeline
```

4. Configure an orchestration (Prefect/cron/dbt Cloud) to run hourly/daily.

5. Hook up the summarization step: pass the canonical deltas as JSON to your LLM and use `prompts/weekly_summary_prompt.txt` as the system instruction.

Recommendations
- Extend `schema.yml` with more tests (unique, relationships) before production.
- Add incremental configuration and snapshots if table size grows.
- Add a small review UI (Notion or internal app) for flagged deals before sending summaries.

If you want, I can:
- Generate a sample dbt `sources.yml` file for HubSpot and Sheets.
- Create the exact LLM input generator script (Python) that pulls top deltas and calls the OpenAI API.
- Add a Prefect flow that runs the transforms and generates + posts the summary to Slack.
