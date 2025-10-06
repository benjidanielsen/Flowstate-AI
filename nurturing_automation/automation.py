import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any
import time
import threading
import requests

# Configuration for email and SMS gateways
EMAIL_HOST = 'smtp.example.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'no-reply@flowstate-ai.com'
EMAIL_HOST_PASSWORD = 'your-email-password'
SMS_API_URL = 'https://smsprovider.example.com/api/send'
SMS_API_KEY = 'your-sms-api-key'

class EmailSender:
    def __init__(self, host=EMAIL_HOST, port=EMAIL_PORT, user=EMAIL_HOST_USER, password=EMAIL_HOST_PASSWORD):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None):
        msg = MIMEMultipart('alternative')
        msg['From'] = self.user
        msg['To'] = to_email
        msg['Subject'] = subject

        if text_content is None:
            # fallback text
            text_content = 'This email contains HTML content. Please use an email client that supports HTML.'

        part1 = MIMEText(text_content, 'plain')
        part2 = MIMEText(html_content, 'html')

        msg.attach(part1)
        msg.attach(part2)

        with smtplib.SMTP(self.host, self.port) as server:
            server.starttls()
            server.login(self.user, self.password)
            server.sendmail(self.user, to_email, msg.as_string())

class SMSSender:
    def __init__(self, api_url=SMS_API_URL, api_key=SMS_API_KEY):
        self.api_url = api_url
        self.api_key = api_key

    def send_sms(self, phone_number: str, message: str) -> bool:
        payload = {
            'api_key': self.api_key,
            'to': phone_number,
            'message': message
        }
        response = requests.post(self.api_url, json=payload)
        return response.status_code == 200

class NurturingAutomation:
    def __init__(self, email_sender: EmailSender, sms_sender: SMSSender):
        self.email_sender = email_sender
        self.sms_sender = sms_sender

    def send_email_sequence(self, user_email: str, sequence: List[Dict[str, Any]]):
        """
        sequence: list of dicts with keys: 'subject', 'html_content', 'text_content'(optional), 'delay_seconds'
        """
        def run_sequence():
            for step in sequence:
                self.email_sender.send_email(
                    user_email,
                    step['subject'],
                    step['html_content'],
                    step.get('text_content')
                )
                time.sleep(step.get('delay_seconds', 0))

        threading.Thread(target=run_sequence).start()

    def send_sms_campaign(self, phone_numbers: List[str], message: str):
        def send_to_all():
            for number in phone_numbers:
                self.sms_sender.send_sms(number, message)
                time.sleep(1)  # throttle to avoid rate limits

        threading.Thread(target=send_to_all).start()

    def deliver_personalized_content(self, user_contact: Dict[str, Any], content: Dict[str, Any]):
        """
        user_contact: dict with keys like 'email', 'phone', 'name', etc.
        content: dict with personalized 'subject', 'html_content', 'text_content', 'sms_message'
        """
        if 'email' in user_contact:
            self.email_sender.send_email(
                user_contact['email'],
                content.get('subject', 'Hello from Flowstate-AI'),
                content.get('html_content', ''),
                content.get('text_content')
            )
        if 'phone' in user_contact and content.get('sms_message'):
            self.sms_sender.send_sms(user_contact['phone'], content['sms_message'])
