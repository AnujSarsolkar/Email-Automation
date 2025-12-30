import os
import smtplib
from email.message import EmailMessage
from imap_tools import MailBox, AND
from typing import List, Dict, Optional
from datetime import datetime

class EmailConnector:
    def __init__(self, imap_server: str, imap_user: str, imap_pass: str, 
                 smtp_server: str, smtp_port: int, smtp_user: str, smtp_pass: str):
        self.imap_server = imap_server
        self.imap_user = imap_user
        self.imap_pass = imap_pass
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_pass = smtp_pass

    def fetch_emails(self, folder="INBOX", limit=10, mark_seen=False) -> List[Dict]:
        """
        Fetches unread emails from the specified folder.
        """
        results = []
        try:
            with MailBox(self.imap_server).login(self.imap_user, self.imap_pass, initial_folder=folder) as mailbox:
                # Fetch UNSEEN messages
                criteria = AND(seen=False)
                for msg in mailbox.fetch(criteria, limit=limit, mark_seen=mark_seen):
                    email_data = {
                        "uid": msg.uid,
                        "subject": msg.subject,
                        "sender": msg.from_,
                        "date": msg.date.isoformat(),
                        "body_text": msg.text,
                        "body_html": msg.html,
                        "headers": msg.headers
                    }
                    results.append(email_data)
        except Exception as e:
            print(f"Error fetching emails: {e}")
        
        return results

    def send_response(self, to_email: str, subject: str, body: str):
        """
        Sends an email response via SMTP.
        """
        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = self.smtp_user
        msg["To"] = to_email

        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
            print(f"Email sent to {to_email}")
        except Exception as e:
            print(f"Error sending email: {e}")

if __name__ == "__main__":
    # Test execution
    ec = EmailConnector(
        imap_server="imap.gmail.com", imap_user="test@example.com", imap_pass="pass",
        smtp_server="smtp.gmail.com", smtp_port=465, smtp_user="test@example.com", smtp_pass="pass"
    )
    print("EmailConnector initialized.")
