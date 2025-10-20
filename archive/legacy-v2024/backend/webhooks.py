import json
import threading
import requests
from typing import List, Dict, Any

# In-memory storage for registered webhooks
# In production, consider a persistent DB
registered_webhooks: List[Dict[str, Any]] = []

class WebhookManager:
    @staticmethod
    def register_webhook(url: str, events: List[str]) -> Dict[str, Any]:
        # Basic validation
        if not url.startswith(('http://', 'https://')):
            raise ValueError('Invalid URL')
        webhook = {
            'url': url,
            'events': events
        }
        registered_webhooks.append(webhook)
        return webhook

    @staticmethod
    def unregister_webhook(url: str) -> bool:
        global registered_webhooks
        before_count = len(registered_webhooks)
        registered_webhooks = [w for w in registered_webhooks if w['url'] != url]
        return len(registered_webhooks) < before_count

    @staticmethod
    def dispatch_event(event_name: str, payload: Dict[str, Any]) -> None:
        # Dispatch event asynchronously to all webhooks subscribed to event_name
        for webhook in registered_webhooks:
            if event_name in webhook['events']:
                threading.Thread(target=WebhookManager._post_event, args=(webhook['url'], event_name, payload)).start()

    @staticmethod
    def _post_event(url: str, event_name: str, payload: Dict[str, Any]) -> None:
        headers = {
            'Content-Type': 'application/json',
            'X-FlowstateAI-Event': event_name
        }
        try:
            requests.post(url, headers=headers, data=json.dumps(payload), timeout=5)
        except requests.RequestException as e:
            # In production, log failure or retry
            print(f'Failed to send webhook to {url}: {e}')
