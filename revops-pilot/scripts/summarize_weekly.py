"""
summarize_weekly.py

Minimal script to:
- query the `canonical_pipeline` table for deltas between two dates
- build the JSON payload required by the LLM prompt
- call OpenAI's chat completions API (or placeholder for your LLM)
- print result (or optionally post to Slack via webhook)

Usage:
python summarize_weekly.py --start 2025-11-09 --end 2025-11-15 --client "Acme SaaS"

Note: set environment variables for DB connection and OPENAI_API_KEY and optional SLACK_WEBHOOK.
"""

import os
import argparse
import json
import datetime
import pprint

import sqlalchemy
import pandas as pd
import requests

# For OpenAI call; keep import optional to avoid hard dependency if using other LLM
try:
    import openai
except Exception:
    openai = None


def get_db_engine_from_env():
    # Expect DATABASE_URL env var e.g. postgresql://user:pass@host:5432/dbname
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        raise RuntimeError('DATABASE_URL environment variable not set')
    return sqlalchemy.create_engine(db_url)


def fetch_pipeline_deltas(engine, start_date, end_date, client_name=None):
    # Replace with appropriate schema/dataset if needed
    query = f"""
    select deal_id, name, owner_id, amount, canonical_stage, close_date, last_modified
    from canonical_pipeline
    where last_modified between '{start_date}' and '{end_date}'
    order by amount desc
    """
    df = pd.read_sql(query, engine)
    # naive classification into new_won/lost/risk based on stage
    if df.empty:
        new_won = []
        lost = []
        top_risks = []
        weighted_now = 0
    else:
        # ensure datetime parsing
        df['last_modified'] = pd.to_datetime(df['last_modified'], errors='coerce')
        # compute days in stage relative to end_date
        ref_date = pd.to_datetime(end_date)
        df['days_in_stage'] = (ref_date - df['last_modified']).dt.days.fillna(0).astype(int)

        new_won = df[df['canonical_stage'] == 'closed_won'].to_dict(orient='records')
        lost = df[df['canonical_stage'] == 'closed_lost'].to_dict(orient='records')

        # risks: deals in proposal/evaluation with days_in_stage > 30
        risks = df[df['canonical_stage'].isin(['proposal', 'evaluation']) & (df['days_in_stage'] > 30)]
        top_risks = risks.sort_values('days_in_stage', ascending=False).head(5).to_dict(orient='records')

        weighted_now = int(df['amount'].sum())

    # pipeline_change: placeholder numbers (you should compute weighted pipeline change over time)
    pipeline_change = {
        'weighted_pipeline_prev': 0,
        'weighted_pipeline_now': weighted_now
    }

    payload = {
        'client_name': client_name,
        'period_start': start_date,
        'period_end': end_date,
        'new_won': new_won,
        'lost': lost,
        'top_risks': top_risks,
        'pipeline_change': pipeline_change,
        'notes': []
    }
    return payload


def call_openai_summary(prompt_template, payload):
    if openai is None:
        raise RuntimeError('openai package not installed')
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise RuntimeError('OPENAI_API_KEY env var not set')
    openai.api_key = api_key

    system_prompt = prompt_template
    user_content = json.dumps(payload)

    resp = openai.ChatCompletion.create(
        model='gpt-4o-mini',
        messages=[
            {'role':'system','content': system_prompt},
            {'role':'user','content': user_content}
        ],
        max_tokens=500,
        temperature=0.2
    )
    return resp['choices'][0]['message']['content']


def post_to_slack(webhook_url, text):
    if not webhook_url:
        raise RuntimeError('SLACK_WEBHOOK not set')
    payload = {'text': text}
    r = requests.post(webhook_url, json=payload)
    r.raise_for_status()
    return r.text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', required=True)
    parser.add_argument('--end', required=True)
    parser.add_argument('--client', required=True)
    parser.add_argument('--slack', action='store_true', help='post to Slack using SLACK_WEBHOOK env var')
    args = parser.parse_args()

    start = args.start
    end = args.end
    client = args.client

    engine = get_db_engine_from_env()
    payload = fetch_pipeline_deltas(engine, start, end, client)

    # Load prompt template from file
    base_dir = os.path.dirname(os.path.dirname(__file__))
    prompt_file = os.path.join(base_dir, 'prompts', 'weekly_summary_prompt.txt')
    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompt_template = f.read()

    try:
        summary = call_openai_summary(prompt_template, payload)
    except Exception as e:
        print('OpenAI call failed:', e)
        summary = None

    print('--- PAYLOAD ---')
    pprint.pprint(payload)
    print('\n--- SUMMARY ---')
    print(summary)

    if args.slack:
        webhook = os.environ.get('SLACK_WEBHOOK')
        if not webhook:
            print('SLACK_WEBHOOK not set; skipping Slack post')
        else:
            post_to_slack(webhook, summary if summary else 'Summary generation failed')


if __name__ == '__main__':
    main()
