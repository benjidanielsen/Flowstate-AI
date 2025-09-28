# Generiske CRM‑felter (map til hvilket som helst CRM)
Contact:
- external_id, name, email, phone, handle_ig, country, language
- lifecycle_stage (subscriber|lead|mql|sql|customer|partner)
- consent: email/sms/messaging, terms_version
- utm: source/medium/campaign/content/term

Deal:
- pipeline (Recruiting|Sales), stage, amount, currency
- contact_external_id, owner_id, product
- booking_time, booking_status

Team:
- owner_id, role (upline|coach|rep), territory, calendars[]
