from twilio.rest import Client
import os

class TwilioService:
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.from_phone = os.getenv('TWILIO_PHONE_NUMBER')
        if not all([self.account_sid, self.auth_token, self.from_phone]):
            raise EnvironmentError('Twilio environment variables TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER must be set')
        self.client = Client(self.account_sid, self.auth_token)

    def send_sms(self, to_phone: str, message: str) -> str:
        """Send a single SMS message."""
        try:
            message_response = self.client.messages.create(
                body=message,
                from_=self.from_phone,
                to=to_phone
            )
            return message_response.sid
        except Exception as e:
            raise RuntimeError(f'Failed to send SMS: {e}')

    def send_bulk_sms(self, phone_numbers: list, message: str) -> dict:
        """Send SMS message to multiple recipients.

        Returns a dict mapping phone number to message SID or error string.
        """
        results = {}
        for number in phone_numbers:
            try:
                sid = self.send_sms(number, message)
                results[number] = sid
            except Exception as e:
                results[number] = str(e)
        return results
