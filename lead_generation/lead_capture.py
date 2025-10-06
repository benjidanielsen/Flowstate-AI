import re
import json
import requests
from typing import Dict, Optional

class LeadCapture:
    """Automated lead capture with form validation and multi-source integration."""

    EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
    PHONE_REGEX = re.compile(r"^\+?\d{7,15}$")

    def __init__(self, sources_config: Dict[str, Dict]):
        """
        Initialize with sources configuration.

        sources_config example:
        {
            "crm_api": {
                "url": "https://crm.example.com/api/leads",
                "api_key": "your_api_key_here"
            },
            "email_marketing": {
                "url": "https://emailmarketing.example.com/api/subscribers",
                "token": "your_token_here"
            }
        }
        """
        self.sources_config = sources_config

    def validate_lead(self, lead_data: Dict[str, str]) -> Optional[str]:
        """
        Validate lead data.
        Required fields: name, email
        Optional validation: phone

        Returns None if valid, else error message string.
        """
        if 'name' not in lead_data or not lead_data['name'].strip():
            return "Name is required."

        email = lead_data.get('email', '').strip()
        if not email:
            return "Email is required."
        if not self.EMAIL_REGEX.match(email):
            return "Invalid email format."

        phone = lead_data.get('phone', '').strip()
        if phone and not self.PHONE_REGEX.match(phone):
            return "Invalid phone number format."

        return None

    def capture_lead(self, lead_data: Dict[str, str]) -> Dict[str, str]:
        """
        Validates and submits lead data to all configured sources.

        Returns dict with keys:
          - success: bool
          - errors: List[str]
        """
        errors = []

        validation_error = self.validate_lead(lead_data)
        if validation_error:
            return {"success": False, "errors": [validation_error]}

        for source, config in self.sources_config.items():
            try:
                if source == 'crm_api':
                    self._submit_to_crm(lead_data, config)
                elif source == 'email_marketing':
                    self._submit_to_email_marketing(lead_data, config)
                else:
                    errors.append(f"Unknown source: {source}")
            except Exception as e:
                errors.append(f"Failed to submit to {source}: {str(e)}")

        success = len(errors) == 0
        return {"success": success, "errors": errors}

    def _submit_to_crm(self, lead_data: Dict[str, str], config: Dict):
        headers = {
            'Authorization': f"Bearer {config.get('api_key')}",
            'Content-Type': 'application/json'
        }
        payload = {
            'name': lead_data['name'],
            'email': lead_data['email'],
            'phone': lead_data.get('phone', '')
        }
        response = requests.post(config['url'], headers=headers, data=json.dumps(payload), timeout=10)
        if response.status_code != 201:
            raise Exception(f"CRM API returned status {response.status_code}")

    def _submit_to_email_marketing(self, lead_data: Dict[str, str], config: Dict):
        headers = {
            'Authorization': f"Token {config.get('token')}",
            'Content-Type': 'application/json'
        }
        payload = {
            'email': lead_data['email'],
            'name': lead_data['name']
        }
        response = requests.post(config['url'], headers=headers, data=json.dumps(payload), timeout=10)
        if response.status_code != 200 and response.status_code != 201:
            raise Exception(f"Email marketing API returned status {response.status_code}")


# Example usage:
# sources = {
#     'crm_api': {
#         'url': 'https://crm.example.com/api/leads',
#         'api_key': 'secret_api_key'
#     },
#     'email_marketing': {
#         'url': 'https://emailmarketing.example.com/api/subscribers',
#         'token': 'secret_token'
#     }
# }
# lead_capture = LeadCapture(sources)
# result = lead_capture.capture_lead({"name": "John Doe", "email": "john@example.com", "phone": "+1234567890"})
# print(result)
