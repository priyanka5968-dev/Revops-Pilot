-- canonical_pipeline.sql
-- Minimal dbt model to canonicalize pipeline data from HubSpot and Sheets
{{ config(materialized='incremental', unique_key='deal_id') }}

with hubspot as (
  select
    deal_id as source_id,
    'hubspot' as source_system,
    owner as owner_id,
    name as dealname,
    amount,
    stage as dealstage,
    null as close_date,
    last_modified,
    null as dealurl
  from {{ source('hubspot_raw', 'raw_hubspot_deals') }}
),

sheets as (
  select
    pipeline_id as source_id,
    'sheets' as source_system,
    account_owner as owner_id,
    deal_name as dealname,
    deal_amount as amount,
    current_stage as dealstage,
    null as close_date,
    updated_date as last_modified,
    null as dealurl
  from {{ source('sheets_raw', 'raw_sheets_pipeline_sheet') }}
),

raw_union as (
  select * from hubspot
  union all
  select * from sheets
),

-- canonical mapping for stages
stage_map as (
  select *,
    case
      when lower(dealstage) in ('closed_won', 'won') then 'closed_won'
      when lower(dealstage) in ('closed_lost', 'lost') then 'closed_lost'
      when lower(dealstage) in ('proposal') then 'proposal'
      when lower(dealstage) in ('evaluation') then 'evaluation'
      when lower(dealstage) in ('qualification') then 'qualification'
      else 'unspecified'
    end as canonical_stage
  from raw_union
)

select
  source_system,
  source_id as deal_id,
  dealname as name,
  owner_id,
  amount,
  canonical_stage,
  close_date,
  last_modified,
  dealurl,
  current_timestamp as loaded_at
from stage_map
where amount is not null
  {% if is_incremental() %}
    and last_modified > (select coalesce(max(loaded_at), '1970-01-01') from {{ this }})
  {% endif %}
;