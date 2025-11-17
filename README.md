# Revops

This repo contains a RevOps pilot project using dbt, scripts to summarize data, and orchestration code.

## Quick start

1. Create and activate a Python virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. Run the setup script to create SQLite DB (if needed):

   ```powershell
   python scripts/setup_sqlite_db.py
   ```

3. Run weekly summary or other scripts:

   ```powershell
   python scripts/summarize_weekly.py
   ```

## I want to upload this project to GitHub

Follow the instructions in the repository root `.gitignore` and the developer docs to create a new GitHub repository and push your code — see `CONTRIBUTING.md` if you want to add contribution rules.

## Files of interest

- `dbt_project.yml` — dbt configuration
- `scripts/` — helper scripts for summarization
- `models/` — dbt models
