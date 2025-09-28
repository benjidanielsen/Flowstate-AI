# Zapier – Comment→DM→CRM→Booking (Pseudo)
1. **Trigger:** Webhooks by Zapier (Catch Hook)
2. **Filter:** Only continue if `consent.messaging` = true
3. **Formatter:** Map payload → contact/deal/events
4. **Action:** Webhooks (Custom Request) → `POST https://YOUR_CRM/contacts/upsert`
5. **Action:** Webhooks (Custom Request) → `POST https://YOUR_SCHEDULER/links`
6. **Action:** Webhooks (Custom Request) → `POST https://YOUR_DM/messages`
7. **Action:** Webhooks (Custom Request) → `POST https://graph.facebook.com/vXX.X/{pixel}/events` (CAPI)
8. **Slack:** Send channel message with summary
