# GDPR‑vakter (eksempel)
- **Samtykke før markedsføring:** lagre `consent` per kanal (email/sms/messaging) + `terms_version`.
- **Dataminimering:** lagre bare nødvendige felter; hash ved aktivering til annonseplattformer.
- **Rett til innsyn/sletting:** hold `external_id` + audit‑logg pr. event.
- **CAPI gating:** ikke send Purchase/Lead uten gyldig grunnlag.
