import sqlite3
import pandas as pd
from datetime import datetime

def canonicalize_stage(stage):
    s = (stage or '').lower()
    if s in ('closed_won', 'won'):
        return 'closed_won'
    if s in ('closed_lost', 'lost'):
        return 'closed_lost'
    if s == 'proposal':
        return 'proposal'
    if s == 'evaluation':
        return 'evaluation'
    if s == 'qualification':
        return 'qualification'
    return 'unspecified'

def summarize_pipeline(db_path):
    conn = sqlite3.connect(db_path)
    # Read both tables
    hubspot = pd.read_sql_query("SELECT * FROM raw_hubspot_deals", conn)
    sheets = pd.read_sql_query("SELECT * FROM raw_sheets_pipeline_sheet", conn)
    # Standardize columns
    hubspot = hubspot.rename(columns={
        'deal_id': 'source_id',
        'name': 'dealname',
        'amount': 'amount',
        'stage': 'dealstage',
        'owner': 'owner_id',
        'last_modified': 'last_modified',
    })
    hubspot['source_system'] = 'hubspot'
    sheets = sheets.rename(columns={
        'pipeline_id': 'source_id',
        'deal_name': 'dealname',
        'deal_amount': 'amount',
        'current_stage': 'dealstage',
        'account_owner': 'owner_id',
        'updated_date': 'last_modified',
    })
    sheets['source_system'] = 'sheets'
    # Union
    df = pd.concat([hubspot, sheets], ignore_index=True)
    df['canonical_stage'] = df['dealstage'].apply(canonicalize_stage)
    # Summary
    summary = df.groupby('canonical_stage').agg(
        deals=('source_id', 'count'),
        total_amount=('amount', 'sum')
    ).reset_index()
    print('Canonical Pipeline Summary:')
    print(summary)
    print('\nSample Deals:')
    print(df[['source_id','dealname','amount','canonical_stage','owner_id','source_system']].head(10))
    conn.close()

if __name__ == "__main__":
    summarize_pipeline(r"C:/Users/Priyanka Shah/OneDrive/Desktop/Cognizant/revops_pilot.db")
