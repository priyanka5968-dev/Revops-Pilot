"""
orchestrate.py
A simple Prefect flow that runs dbt (via subprocess) and then runs the summarize_weekly.py script.

This is designed for local testing or a small Prefect agent. For production, replace subprocess calls with API calls to dbt Cloud or your orchestration layer.
"""

import os
import subprocess
from datetime import datetime, timedelta

from prefect import flow, task


@task
def run_dbt():
    # Assumes dbt is installed in the environment and project root is the parent of this file
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    cmd = ['dbt', 'run']
    print('Running dbt run in', project_root)
    subprocess.check_call(cmd, cwd=project_root)
    return True


@task
def run_summarizer(start_date, end_date, client_name, post_slack=False):
    script = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), 'scripts', 'summarize_weekly.py')
    cmd = ['python', script, '--start', start_date, '--end', end_date, '--client', client_name]
    if post_slack:
        cmd.append('--slack')
    print('Running summarizer:', ' '.join(cmd))
    subprocess.check_call(cmd)
    return True


@flow
def daily_pipeline_flow(client_name='Acme SaaS', days_back=7, post_slack=False):
    # run dbt
    run_dbt()

    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days_back)

    run_summarizer(start_date.isoformat(), end_date.isoformat(), client_name, post_slack=post_slack)


if __name__ == '__main__':
    # simple CLI entry
    daily_pipeline_flow()