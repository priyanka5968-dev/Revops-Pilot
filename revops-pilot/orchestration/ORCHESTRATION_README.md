Prefect orchestration for RevOps pilot

This folder contains a minimal Prefect flow that:
- runs `dbt run` in the project root
- runs the summarizer script to create and post the weekly summary

Quick start
1. Install requirements in your venv:

```powershell
pip install -r ..\requirements.txt
```

2. Run locally:

```powershell
python orchestrate.py
```

3. To run on a schedule, register the flow with Prefect Cloud/Server, or run this script via a cron/Task Scheduler that activates the environment.

Notes
- The flow uses subprocess calls to run dbt and the Python summarizer; for production replace with dbt Cloud API calls or direct dbt Python integration.
- Ensure environment variables (DATABASE_URL, OPENAI_API_KEY, SLACK_WEBHOOK) are set for the summarizer.
