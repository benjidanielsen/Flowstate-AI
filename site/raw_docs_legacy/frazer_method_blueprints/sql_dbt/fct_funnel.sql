-- fct_funnel.sql (eksempel)
with e as (select * from {{ ref('stg_events') }})
select
  user_id,
  min(case when event_name='DM_STARTED' then ts end) as dm_ts,
  min(case when event_name='LEAD_QUALIFIED' then ts end) as qualified_ts,
  min(case when event_name='MEETING_BOOKED' then ts end) as booked_ts,
  min(case when event_name='MEETING_HELD' then ts end) as held_ts,
  min(case when event_name in ('PURCHASED','JOINED_TEAM') then ts end) as success_ts
from e
group by 1;
