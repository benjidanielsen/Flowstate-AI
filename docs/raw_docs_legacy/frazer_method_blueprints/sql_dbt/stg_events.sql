-- stg_events.sql (eksempel)
select
  event_id,
  event_name,
  user_id,
  account_id,
  parse_datetime(timestamp) as ts,
  properties,
  consent,
  utm
from raw.events;
