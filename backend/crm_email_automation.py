"""
CRM Email Automation Service for Flowstate-AI
Handles automated email sequences and campaigns for CRM contacts.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
from openai import OpenAI

class CRMEmailAutomation:
    """Service for managing automated email sequences."""
    
    # Email templates for different lifecycle stages
    EMAIL_TEMPLATES = {
        "welcome_lead": {
            "subject": "Welcome to Flowstate-AI - Let's Transform Your Business",
            "template": """
            Hi {name},
            
            Thank you for your interest in Flowstate-AI! We're excited to help you leverage the power of autonomous AI agents to transform your business operations.
            
            Flowstate-AI offers:
            - Autonomous AI agents for various business functions
            - Intelligent CRM automation
            - Real-time analytics and insights
            - Seamless integration with your existing systems
            
            I'd love to schedule a quick call to understand your specific needs and show you how Flowstate-AI can help.
            
            Are you available for a 15-minute call this week?
            
            Best regards,
            The Flowstate-AI Team
            """
        },
        "nurture_mql": {
            "subject": "How Flowstate-AI Can Solve Your {pain_point}",
            "template": """
            Hi {name},
            
            I wanted to follow up on our previous conversation about Flowstate-AI.
            
            Many businesses like yours struggle with {pain_point}. Our autonomous AI agents are specifically designed to address this challenge by:
            
            1. Automating repetitive tasks
            2. Providing intelligent insights
            3. Scaling operations without increasing headcount
            
            I've attached a case study showing how a similar company achieved {result}.
            
            Would you be interested in a personalized demo?
            
            Best regards,
            The Flowstate-AI Team
            """
        },
        "proposal_sql": {
            "subject": "Your Personalized Flowstate-AI Proposal",
            "template": """
            Hi {name},
            
            Based on our discussion, I've prepared a personalized proposal for implementing Flowstate-AI in your organization.
            
            Key highlights:
            - Estimated ROI: {roi}
            - Implementation timeline: {timeline}
            - Dedicated support and training
            
            The proposal includes:
            1. Detailed implementation plan
            2. Pricing and payment options
            3. Success metrics and KPIs
            
            I'm available to discuss any questions you might have.
            
            Looking forward to partnering with you!
            
            Best regards,
            The Flowstate-AI Team
            """
        },
        "follow_up_booked": {
            "subject": "Looking Forward to Our Meeting",
            "template": """
            Hi {name},
            
            Just a quick reminder about our meeting scheduled for {meeting_time}.
            
            To make the most of our time together, please consider:
            - What are your top 3 business challenges?
            - What would success look like for your organization?
            - Who else should be involved in the decision-making process?
            
            If you need to reschedule, please let me know.
            
            See you soon!
            
            Best regards,
            The Flowstate-AI Team
            """
        },
        "onboarding_won": {
            "subject": "Welcome to Flowstate-AI - Let's Get Started!",
            "template": """
            Hi {name},
            
            Congratulations on joining Flowstate-AI! We're thrilled to have you as a customer.
            
            Your onboarding process will include:
            1. Initial setup and configuration (Week 1)
            2. Team training sessions (Week 2)
            3. Go-live and optimization (Week 3-4)
            
            Your dedicated account manager, {account_manager}, will be reaching out shortly to schedule your kickoff call.
            
            In the meantime, here are some resources to get you started:
            - Quick Start Guide: {guide_url}
            - Video Tutorials: {video_url}
            - Support Portal: {support_url}
            
            Welcome aboard!
            
            Best regards,
            The Flowstate-AI Team
            """
        },
        "retention_customer": {
            "subject": "How Can We Serve You Better?",
            "template": """
            Hi {name},
            
            It's been {days_since_onboarding} days since you started with Flowstate-AI, and we want to ensure you're getting the most value from our platform.
            
            Quick check-in:
            - Are you achieving your expected outcomes?
            - Is there anything we can help you with?
            - Any features you'd like to see added?
            
            Your feedback is invaluable to us. Would you be open to a brief 10-minute call?
            
            We're here to support your success!
            
            Best regards,
            The Flowstate-AI Team
            """
        }
    }
    
    def __init__(self):
        """Initialize the email automation service."""
        try:
            self.client = OpenAI()
        except Exception:
            # OpenAI client optional for testing
            self.client = None
        self.log_file = Path(__file__).parent.parent / "logs" / "email_automation.log"
        
    def log(self, message: str):
        """Log email automation activity."""
        timestamp = datetime.utcnow().isoformat()
        log_entry = f"[{timestamp}] Email Automation: {message}\n"
        print(log_entry.strip())
        
        try:
            with open(self.log_file, "a") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Warning: Could not write to log file: {e}")
    
    def generate_personalized_email(self, template_key: str, contact: Dict, 
                                   additional_vars: Optional[Dict] = None) -> Dict:
        """
        Generate a personalized email using AI.
        
        Args:
            template_key: Key for the email template
            contact: Contact information
            additional_vars: Additional variables for template customization
            
        Returns:
            Dictionary with subject and body
        """
        if template_key not in self.EMAIL_TEMPLATES:
            raise ValueError(f"Unknown template key: {template_key}")
        
        template = self.EMAIL_TEMPLATES[template_key]
        
        # Prepare variables for template
        variables = {
            "name": contact.get("name", "there"),
            "email": contact.get("email", ""),
            "country": contact.get("country", ""),
        }
        
        if additional_vars:
            variables.update(additional_vars)
        
        # Use AI to personalize the email further
        try:
            if self.client is None:
                # Fallback to template with simple variable substitution
                subject = template['subject'].format(**variables)
                body = template['template'].format(**variables)
                return {"subject": subject, "body": body}
            
            prompt = f"""
            Personalize the following email template for a contact with these details:
            - Name: {variables['name']}
            - Country: {variables['country']}
            - Lifecycle Stage: {contact.get('lifecycle_stage', 'lead')}
            
            Template:
            Subject: {template['subject']}
            Body: {template['template']}
            
            Make the email more engaging and personalized while keeping the core message. 
            Fill in any placeholder variables with appropriate content.
            Return the email in JSON format with 'subject' and 'body' fields.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "You are an expert email copywriter specializing in B2B sales and marketing."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            email_content = json.loads(response.choices[0].message.content)
            self.log(f"Generated personalized email for {contact.get('email')}")
            return email_content
        except Exception as e:
            self.log(f"Error generating personalized email: {e}")
            # Fallback to template with simple variable substitution
            subject = template['subject'].format(**variables)
            body = template['template'].format(**variables)
            return {"subject": subject, "body": body}
    
    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """
        Send an email (placeholder for actual email sending).
        
        In production, this would integrate with an email service like SendGrid, Mailgun, etc.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body
            
        Returns:
            True if successful, False otherwise
        """
        # Placeholder implementation - log the email instead of sending
        self.log(f"[SIMULATED] Sending email to {to_email}")
        self.log(f"Subject: {subject}")
        self.log(f"Body preview: {body[:100]}...")
        
        # In production, implement actual email sending here
        # Example with SendGrid:
        # from sendgrid import SendGridAPIClient
        # from sendgrid.helpers.mail import Mail
        # 
        # message = Mail(
        #     from_email='noreply@flowstate-ai.com',
        #     to_emails=to_email,
        #     subject=subject,
        #     html_content=body
        # )
        # sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        # response = sg.send(message)
        # return response.status_code == 202
        
        return True
    
    def create_email_sequence(self, contact: Dict, sequence_type: str) -> List[Dict]:
        """
        Create an email sequence for a contact based on their lifecycle stage.
        
        Args:
            contact: Contact information
            sequence_type: Type of sequence (e.g., 'lead_nurture', 'onboarding')
            
        Returns:
            List of email schedules with timing and content
        """
        sequence = []
        
        if sequence_type == "lead_nurture":
            # Day 0: Welcome email
            sequence.append({
                "delay_days": 0,
                "template_key": "welcome_lead",
                "additional_vars": {}
            })
            
            # Day 3: Nurture email
            sequence.append({
                "delay_days": 3,
                "template_key": "nurture_mql",
                "additional_vars": {
                    "pain_point": "inefficient operations",
                    "result": "40% cost reduction"
                }
            })
            
            # Day 7: Follow-up
            sequence.append({
                "delay_days": 7,
                "template_key": "nurture_mql",
                "additional_vars": {
                    "pain_point": "scaling challenges",
                    "result": "3x productivity increase"
                }
            })
        
        elif sequence_type == "sql_proposal":
            # Immediate: Proposal email
            sequence.append({
                "delay_days": 0,
                "template_key": "proposal_sql",
                "additional_vars": {
                    "roi": "250% in first year",
                    "timeline": "4-6 weeks"
                }
            })
            
            # Day 2: Follow-up
            sequence.append({
                "delay_days": 2,
                "template_key": "follow_up_booked",
                "additional_vars": {
                    "meeting_time": "TBD"
                }
            })
        
        elif sequence_type == "onboarding":
            # Day 0: Welcome and onboarding
            sequence.append({
                "delay_days": 0,
                "template_key": "onboarding_won",
                "additional_vars": {
                    "account_manager": "Sarah Johnson",
                    "guide_url": "https://docs.flowstate-ai.com/quickstart",
                    "video_url": "https://videos.flowstate-ai.com/tutorials",
                    "support_url": "https://support.flowstate-ai.com"
                }
            })
        
        elif sequence_type == "retention":
            # Day 30, 60, 90: Check-in emails
            for days in [30, 60, 90]:
                sequence.append({
                    "delay_days": days,
                    "template_key": "retention_customer",
                    "additional_vars": {
                        "days_since_onboarding": str(days)
                    }
                })
        
        self.log(f"Created {sequence_type} sequence with {len(sequence)} emails for {contact.get('email')}")
        return sequence
    
    def execute_sequence(self, contact: Dict, sequence: List[Dict]):
        """
        Execute an email sequence for a contact.
        
        Args:
            contact: Contact information
            sequence: List of email schedules
        """
        for email_schedule in sequence:
            # Generate personalized email
            email = self.generate_personalized_email(
                template_key=email_schedule["template_key"],
                contact=contact,
                additional_vars=email_schedule.get("additional_vars", {})
            )
            
            # In production, schedule the email based on delay_days
            # For now, just log it
            delay_days = email_schedule["delay_days"]
            send_date = datetime.utcnow() + timedelta(days=delay_days)
            
            self.log(f"Scheduled email for {contact.get('email')} on {send_date.isoformat()}")
            self.log(f"Subject: {email['subject']}")
            
            # Simulate sending (in production, this would be scheduled)
            if delay_days == 0:
                self.send_email(contact.get("email"), email["subject"], email["body"])

def main():
    """Test the email automation service."""
    automation = CRMEmailAutomation()
    
    # Test contact
    test_contact = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "country": "USA",
        "lifecycle_stage": "lead"
    }
    
    # Create and execute a lead nurture sequence
    sequence = automation.create_email_sequence(test_contact, "lead_nurture")
    automation.execute_sequence(test_contact, sequence)

if __name__ == "__main__":
    main()
