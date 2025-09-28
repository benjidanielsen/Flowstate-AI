/**
 * Vendor-agnostic example (Pipedream).
 * Trigger: HTTP Source
 */
export default defineComponent({
  async run({ steps, $ }) {
    const payload = steps.trigger.event;
    const contact = mapToContact(payload);
    await $.fetch("https://YOUR_CRM/contacts/upsert",{ method:"POST", body: JSON.stringify(contact)});
    const link = await $.fetch("https://YOUR_SCHEDULER/links",{ method:"POST", body: JSON.stringify({ contact_external_id:contact.external_id })}).then(r=>r.json());
    await $.fetch("https://YOUR_DM/messages",{ method:"POST", body: JSON.stringify({ to: payload.user_id, text: `Book her: ${link.url}` })});
    await $.fetch("https://graph.facebook.com/vXX.X/YOUR_PIXEL/events",{ method:"POST", body: JSON.stringify(buildCapi(payload))});
    return { ok: true };
  }
})
