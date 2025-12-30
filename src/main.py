import os
import time
from src.ingestion.email_connector import EmailConnector
from src.ingestion.loader import DataLoader
from src.privacy.privacy_filter import PrivacyFilter
from src.brain.llm_client import Brain
from src.memory.vector_store import ContextRetriever
from src.decision.router import Router
from dotenv import load_dotenv

load_dotenv()

class LicEmailProcessor:
    def __init__(self):
        print("Initializing LIC Email Processor...")
        # Initialize components
        self.privacy = PrivacyFilter()
        self.brain = Brain()
        self.memory = ContextRetriever()
        self.router = Router()
        
        # Load some policies into memory (Simulation)
        self._load_policies()

    def _load_policies(self):
        print("Loading policies into memory...")
        self.memory.add_policy_document(
            doc_id="pol_claim_01",
            text="Maturity claims require Policy Bond, Discharge Voucher, and NEFT details.",
            metadata={"category": "Claim"}
        )
        self.memory.add_policy_document(
            doc_id="pol_renewal_01",
            text="Grace period is 30 days for quarterly, half-yearly and yearly modes.",
            metadata={"category": "Renewal"}
        )

    def process_email(self, email_id: str, subject: str, body: str):
        print(f"\n--- Processing Email: {subject} ({email_id}) ---")
        
        # Step 1: PII Redaction
        print("Step 1: PII Redaction...")
        redacted_body = self.privacy.redact(body)
        print(f"Redacted Body: {redacted_body[:100]}...") # Print preview

        # Step 2: Intent & Sentiment
        print("Step 2: Brain Analysis...")
        intent = self.brain.analyze_intent(redacted_body)
        sentiment = self.brain.analyze_sentiment(redacted_body)
        print(f"Intent: {intent} | Sentiment: {sentiment}")

        # Step 3: Context Retrieval
        print("Step 3: RAG Retrieval...")
        context = self.memory.retrieve_context(f"{intent} {redacted_body}")
        print(f"Context Found: {len(context)} documents")

        # Step 4: Decision & Routing
        print("Step 4: Decisioning...")
        decision = self.router.route(email_id, intent, sentiment, {"context_count": len(context)})
        
        print(f"Final Decision: {decision}")
        return decision

if __name__ == "__main__":
    import json
    import sys

    app = LicEmailProcessor()
    
    # Check if a file path is provided, otherwise default to sample data
    input_file = "data/LIC_mail_templates.txt"
    if len(sys.argv) > 1:
        input_file = sys.argv[1]

    if os.path.exists(input_file):
        print(f"\n[+] Loading emails from {input_file}...")
        try:
            loader = DataLoader()
            emails = loader.load_emails(input_file)
            print(f"[+] Loaded {len(emails)} emails.\n")
            
            for email in emails:
                app.process_email(email.get("id", "unknown"), email.get("subject", "No Subject"), email.get("body", ""))
                print("-" * 50)
        except Exception as e:
            print(f"[-] Error loading file: {e}")
    else:
        print(f"File {input_file} not found. Running single dummy test.")
        # Simulate an incoming email
        dummy_email = {
            "id": "msg_999",
            "subject": "Delay in Claim Settlement",
            "body": "Hi, I am frustrated. My Policy number is 123456789 and PAN is ABCDE1234F. I submitted the claim 40 days ago. Why is it delayed?"
        }
        app.process_email(dummy_email["id"], dummy_email["subject"], dummy_email["body"])
