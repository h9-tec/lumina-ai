"""
Email Service - Send meeting minutes via email
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import List, Optional


class EmailService:
    """Send emails via SMTP or Gmail API"""

    def __init__(self, use_gmail_api: bool = False):
        """
        Initialize email service

        Args:
            use_gmail_api: Use Gmail API instead of SMTP (requires setup)
        """
        self.use_gmail_api = use_gmail_api

        if use_gmail_api:
            self._init_gmail_api()
        else:
            self._init_smtp()

    def _init_smtp(self):
        """Initialize SMTP settings from environment"""
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')

        if not self.smtp_user or not self.smtp_password:
            print("⚠️  SMTP credentials not configured in .env")
            print("   Set SMTP_USER and SMTP_PASSWORD to send emails")

    def _init_gmail_api(self):
        """Initialize Gmail API (if credentials exist)"""
        try:
            from googleapiclient.discovery import build
            from google.oauth2.credentials import Credentials

            # Use existing token from calendar service
            token_path = Path(__file__).parent / 'token.pickle'
            if token_path.exists():
                import pickle
                with open(token_path, 'rb') as token:
                    creds = pickle.load(token)

                self.gmail_service = build('gmail', 'v1', credentials=creds)
                print("✅ Gmail API initialized")
            else:
                print("⚠️  Gmail API token not found, falling back to SMTP")
                self.use_gmail_api = False
                self._init_smtp()

        except Exception as e:
            print(f"⚠️  Gmail API initialization failed: {e}")
            print("   Falling back to SMTP")
            self.use_gmail_api = False
            self._init_smtp()

    def send_meeting_minutes(
        self,
        to_emails: List[str],
        subject: str,
        minutes_markdown: str,
        minutes_file_path: Optional[str] = None,
        from_email: Optional[str] = None
    ) -> bool:
        """
        Send meeting minutes via email

        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            minutes_markdown: Meeting minutes in markdown format
            minutes_file_path: Optional path to attach minutes file
            from_email: Optional from email (defaults to SMTP_USER)

        Returns:
            True if sent successfully
        """
        if not to_emails:
            print("❌ No recipients specified")
            return False

        try:
            if self.use_gmail_api:
                return self._send_via_gmail_api(to_emails, subject, minutes_markdown, minutes_file_path)
            else:
                return self._send_via_smtp(to_emails, subject, minutes_markdown, minutes_file_path, from_email)

        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False

    def _send_via_smtp(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        attachment_path: Optional[str] = None,
        from_email: Optional[str] = None
    ) -> bool:
        """Send email via SMTP"""

        if not self.smtp_user or not self.smtp_password:
            print("❌ SMTP credentials not configured")
            return False

        from_email = from_email or self.smtp_user

        # Create message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = ', '.join(to_emails)
        msg['Subject'] = subject

        # Convert markdown to HTML (basic)
        html_body = self._markdown_to_html(body)
        msg.attach(MIMEText(html_body, 'html'))

        # Attach file if provided
        if attachment_path and Path(attachment_path).exists():
            with open(attachment_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {Path(attachment_path).name}'
                )
                msg.attach(part)

        # Send email
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            print(f"✅ Email sent successfully to {len(to_emails)} recipient(s)")
            return True

        except Exception as e:
            print(f"❌ SMTP error: {e}")
            return False

    def _send_via_gmail_api(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        attachment_path: Optional[str] = None
    ) -> bool:
        """Send email via Gmail API"""

        try:
            from email.mime.text import MIMEText
            import base64

            html_body = self._markdown_to_html(body)

            message = MIMEText(html_body, 'html')
            message['to'] = ', '.join(to_emails)
            message['subject'] = subject

            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            # Send via API
            send_message = {'raw': raw_message}
            self.gmail_service.users().messages().send(
                userId='me', body=send_message
            ).execute()

            print(f"✅ Email sent via Gmail API to {len(to_emails)} recipient(s)")
            return True

        except Exception as e:
            print(f"❌ Gmail API error: {e}")
            return False

    def _markdown_to_html(self, markdown_text: str) -> str:
        """Convert markdown to basic HTML"""

        html = markdown_text

        # Headers
        html = html.replace('# ', '<h1>').replace('\n', '</h1>\n', 1)
        html = html.replace('## ', '<h2>').replace('\n', '</h2>\n')
        html = html.replace('### ', '<h3>').replace('\n', '</h3>\n')

        # Bold
        import re
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)

        # Lists
        lines = html.split('\n')
        in_list = False
        new_lines = []

        for line in lines:
            if line.strip().startswith('- '):
                if not in_list:
                    new_lines.append('<ul>')
                    in_list = True
                new_lines.append(f'<li>{line.strip()[2:]}</li>')
            else:
                if in_list:
                    new_lines.append('</ul>')
                    in_list = False
                new_lines.append(line)

        if in_list:
            new_lines.append('</ul>')

        html = '\n'.join(new_lines)

        # Wrap in HTML structure
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                h2 {{ color: #34495e; margin-top: 20px; }}
                ul {{ padding-left: 20px; }}
                li {{ margin: 5px 0; }}
                hr {{ border: none; border-top: 1px solid #ddd; margin: 20px 0; }}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """

        return html


# Test function
if __name__ == "__main__":
    print("Testing Email Service...")

    # Sample minutes
    sample_minutes = """# Team Meeting - November 14, 2025

**Date:** 2025-11-14

---

## Summary

Discussed Q4 roadmap and decided to prioritize mobile app launch for November 15th. Budget of $50k approved for marketing campaign.

---

## Key Points & Decisions

- Mobile app launch prioritized for Q4
- Target date: November 15th for beta release
- Marketing budget: $50k approved

---

## Action Items

- [ ] Backend API updates (Owner: Mike) - Due: Nov 1st
- [ ] UI coordination with design team (Owner: Sarah)
- [ ] Technical spec preparation (Owner: Mike) - Due: Friday

---

_Generated by Lumina_
"""

    # Initialize service
    email_service = EmailService(use_gmail_api=False)

    print("\nNote: Configure SMTP_USER and SMTP_PASSWORD in .env to send emails")
    print("Example .env entries:")
    print("SMTP_SERVER=smtp.gmail.com")
    print("SMTP_PORT=587")
    print("SMTP_USER=your-email@gmail.com")
    print("SMTP_PASSWORD=your-app-password")

    print("\nTest complete!")
