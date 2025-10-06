import os
from typing import Optional

# You can switch between SendGrid and Mailgun by setting EMAIL_PROVIDER env var to 'sendgrid' or 'mailgun'
EMAIL_PROVIDER = os.getenv('EMAIL_PROVIDER', 'sendgrid').lower()

# Common email sending interface
class EmailService:
    def send_email(self, to_email: str, subject: str, content: str, from_email: Optional[str] = None) -> bool:
        raise NotImplementedError("send_email method must be implemented")


# -------- SendGrid Implementation --------
if EMAIL_PROVIDER == 'sendgrid':
    import sendgrid
    from sendgrid.helpers.mail import Mail

    class SendGridEmailService(EmailService):
        def __init__(self):
            api_key = os.getenv('SENDGRID_API_KEY')
            if not api_key:
                raise ValueError('SENDGRID_API_KEY environment variable not set')
            self.sg = sendgrid.SendGridAPIClient(api_key=api_key)

        def send_email(self, to_email: str, subject: str, content: str, from_email: Optional[str] = None) -> bool:
            from_email = from_email or os.getenv('DEFAULT_FROM_EMAIL', 'no-reply@flowstate.ai')
            message = Mail(
                from_email=from_email,
                to_emails=to_email,
                subject=subject,
                plain_text_content=content
            )
            try:
                response = self.sg.send(message)
                return 200 <= response.status_code < 300
            except Exception as e:
                print(f"SendGrid send email error: {e}")
                return False

    EmailServiceImpl = SendGridEmailService

# -------- Mailgun Implementation --------
elif EMAIL_PROVIDER == 'mailgun':
    import requests

    class MailgunEmailService(EmailService):
        def __init__(self):
            self.api_key = os.getenv('MAILGUN_API_KEY')
            self.domain = os.getenv('MAILGUN_DOMAIN')
            if not self.api_key or not self.domain:
                raise ValueError('MAILGUN_API_KEY and MAILGUN_DOMAIN environment variables must be set')

        def send_email(self, to_email: str, subject: str, content: str, from_email: Optional[str] = None) -> bool:
            from_email = from_email or os.getenv('DEFAULT_FROM_EMAIL', f'no-reply@{self.domain}')
            url = f'https://api.mailgun.net/v3/{self.domain}/messages'
            data = {
                'from': from_email,
                'to': [to_email],
                'subject': subject,
                'text': content
            }
            try:
                response = requests.post(url, auth=('api', self.api_key), data=data)
                return 200 <= response.status_code < 300
            except Exception as e:
                print(f"Mailgun send email error: {e}")
                return False

    EmailServiceImpl = MailgunEmailService

else:
    raise ValueError(f"Unsupported EMAIL_PROVIDER: {EMAIL_PROVIDER}")


# Factory method to get email service instance

def get_email_service() -> EmailService:
    return EmailServiceImpl()
