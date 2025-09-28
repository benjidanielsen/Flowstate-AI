-- dim_contacts.sql (eksempel)
select
  external_id as contact_id,
  first_name, last_name, email, phone, country, language,
  lifecycle_stage
from raw.contacts;
