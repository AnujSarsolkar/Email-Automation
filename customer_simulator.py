#!/usr/bin/env python3
"""
Customer Email Simulator for LIC Testing Environment
Generates realistic email traffic from various policyholder personas
"""

import json
import os
import time
import random
from pathlib import Path
from email.mime.text import MIMEText
import base64

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from langchain_community.llms import Ollama

# Gmail API Scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Test email recipient
TEST_EMAIL = "anujsarsolkar15@gmail.com"

# Indian names database for realistic personas
FIRST_NAMES = [
    "Rajesh", "Priya", "Amit", "Sunita", "Vikram", "Anjali", "Suresh", "Deepa",
    "Ramesh", "Kavita", "Anil", "Pooja", "Mahesh", "Sneha", "Vijay", "Rekha",
    "Satish", "Meera", "Ashok", "Nisha", "Ravi", "Divya", "Mohan", "Geeta",
    "Sanjay", "Lalita", "Prakash", "Usha", "Dinesh", "Swati", "Kiran", "Vandana"
]

LAST_NAMES = [
    "Sharma", "Patel", "Kumar", "Singh", "Reddy", "Desai", "Mehta", "Gupta",
    "Nair", "Rao", "Iyer", "Joshi", "Verma", "Pillai", "Shah", "Agarwal",
    "Malhotra", "Chopra", "Kulkarni", "Shetty", "Menon", "Bhat", "Das", "Pandey"
]

INDIAN_CITIES = [
    {"name": "Mumbai", "state": "Maharashtra", "pincode_start": "400"},
    {"name": "Delhi", "state": "Delhi", "pincode_start": "110"},
    {"name": "Bangalore", "state": "Karnataka", "pincode_start": "560"},
    {"name": "Chennai", "state": "Tamil Nadu", "pincode_start": "600"},
    {"name": "Kolkata", "state": "West Bengal", "pincode_start": "700"},
    {"name": "Pune", "state": "Maharashtra", "pincode_start": "411"},
    {"name": "Hyderabad", "state": "Telangana", "pincode_start": "500"},
    {"name": "Ahmedabad", "state": "Gujarat", "pincode_start": "380"},
    {"name": "Jaipur", "state": "Rajasthan", "pincode_start": "302"},
    {"name": "Lucknow", "state": "Uttar Pradesh", "pincode_start": "226"}
]

STREET_TYPES = ["Road", "Street", "Avenue", "Lane", "Nagar", "Colony", "Park", "Enclave"]
AREA_NAMES = ["MG", "Gandhi", "Nehru", "Sarojini", "Rajendra", "Sardar Patel", "Laxmi", "Krishna"]

# Customer personas with different tones and characteristics
PERSONAS = [
    {
        "name": "Angry Claimant",
        "tone": "angry, frustrated, demanding immediate action",
        "background": "claim denied or delayed, feeling unfairly treated"
    },
    {
        "name": "Confused Senior",
        "tone": "confused, polite but repetitive, asking basic questions",
        "background": "elderly policyholder struggling with policy terms"
    },
    {
        "name": "Anxious New Customer",
        "tone": "worried, uncertain, seeking reassurance",
        "background": "recently purchased policy, concerned about coverage"
    },
    {
        "name": "Impatient Professional",
        "tone": "curt, business-like, time-pressed",
        "background": "busy professional wanting quick answers"
    },
    {
        "name": "Grateful Beneficiary",
        "tone": "thankful, emotional, appreciative",
        "background": "recently received claim payout"
    },
    {
        "name": "Skeptical Investigator",
        "tone": "questioning, suspicious, demanding documentation",
        "background": "doubting policy terms or claim process"
    },
    {
        "name": "Overwhelmed Parent",
        "tone": "stressed, multitasking, somewhat disorganized",
        "background": "managing family policies, juggling responsibilities"
    },
    {
        "name": "Tech-Savvy Millennial",
        "tone": "casual, expects digital solutions, uses modern language",
        "background": "prefers online interactions, impatient with slow processes"
    }
]

# Common LIC-related topics
TOPICS = [
    "Premium Payment Overdue - Need Extension",
    "Claim Status Inquiry - Policy Matured",
    "Policy Document Not Received",
    "Nominee Details Update Required",
    "Surrender Value Calculation Query",
    "Loan Against Policy Request",
    "Premium Receipt Missing",
    "Maturity Benefit Delay",
    "Death Claim Documentation",
    "Policy Revival After Lapse",
    "Bonus Information Request",
    "Address Change Confirmation",
    "Duplicate Policy Bond Request",
    "Premium Payment Mode Change",
    "Tax Certificate Not Received"
]


def generate_customer_details():
    """
    Generate realistic Indian customer personal details
    """
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    
    # Generate policy number (LIC format: 8-9 digits)
    policy_number = f"{random.randint(100000000, 999999999)}"
    
    # Generate phone number (Indian format: +91-XXXXXXXXXX)
    phone = f"+91-{random.randint(7000000000, 9999999999)}"
    
    # Generate address
    city_info = random.choice(INDIAN_CITIES)
    street_num = random.randint(1, 999)
    area_name = random.choice(AREA_NAMES)
    street_type = random.choice(STREET_TYPES)
    pincode = f"{city_info['pincode_start']}{random.randint(100, 999):03d}"
    
    address = f"{street_num}, {area_name} {street_type}, {city_info['name']}, {city_info['state']} - {pincode}"
    
    # Generate email (derived from name)
    email_domain = random.choice(["gmail.com", "yahoo.com", "outlook.com", "rediffmail.com"])
    email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@{email_domain}"
    
    # Generate age (typical LIC policyholder range)
    age = random.randint(25, 70)
    
    # Policy start year (realistic range)
    policy_year = random.randint(2010, 2024)
    
    return {
        "full_name": f"{first_name} {last_name}",
        "policy_number": policy_number,
        "phone": phone,
        "email": email,
        "address": address,
        "city": city_info['name'],
        "state": city_info['state'],
        "pincode": pincode,
        "age": age,
        "policy_year": policy_year
    }


def generate_email_content(llm, persona, topic):
    """
    Authenticate with Gmail API using OAuth 2.0
    Handles token creation and refresh automatically
    """
    creds = None
    token_path = Path('token.json')
    creds_path = Path('credentials.json')
    
    # Check if credentials.json exists
    if not creds_path.exists():
        raise FileNotFoundError(
            "credentials.json not found. Please download it from Google Cloud Console."
        )
    
    # Load existing token if available
    if token_path.exists():
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # Refresh or create new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing access token...")
            creds.refresh(Request())
        else:
            print("🔐 Starting OAuth flow (browser will open)...")
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES
            )
            # Try multiple ports if needed
            for port in [0, 8081, 8082, 9090, 5000]:
                try:
                    creds = flow.run_local_server(port=port, open_browser=True)
                    break
                except OSError as e:
                    if port == 5000:  # Last port to try
                        raise
                    print(f"⚠️  Port {port} in use, trying next...")
        
        # Save credentials for future runs
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        print("✅ Authentication successful! Token saved.")
    
    return creds


def generate_email_content(llm, persona, topic, customer_details):
    """
    Generate realistic email content using Ollama LLM with customer details
    Returns dict with 'subject' and 'body'
    """
    prompt = f"""You are {customer_details['full_name']}, a {persona['name']} who is an LIC (Life Insurance Corporation) policyholder.

Your Personal Details:
- Name: {customer_details['full_name']}
- Policy Number: {customer_details['policy_number']}
- Phone: {customer_details['phone']}
- Email: {customer_details['email']}
- Address: {customer_details['address']}
- Age: {customer_details['age']}
- Policy Since: {customer_details['policy_year']}

Persona Details:
- Tone: {persona['tone']}
- Background: {persona['background']}

Topic: {topic}

Write a realistic email about this topic. Include your personal details naturally in the email (policy number is MUST, and 1-2 other details like phone or address as appropriate). The email should sound authentic to the persona and naturally incorporate the relevant details.

IMPORTANT: Respond ONLY with valid JSON in this exact format (no markdown, no extra text):
{{"subject": "Email subject line here", "body": "Full email body text here with signature"}}

Make the subject concise (under 80 characters). The body should be 4-6 sentences that:
1. State the issue/query clearly
2. Include policy number and 1-2 other relevant personal details
3. Match the persona's tone
4. End with a proper signature including name and contact details"""

    try:
        response = llm.invoke(prompt)
        
        # Clean response - remove markdown code blocks if present
        cleaned = response.strip()
        if cleaned.startswith('```'):
            # Remove markdown fences
            lines = cleaned.split('\n')
            cleaned = '\n'.join([l for l in lines if not l.startswith('```')])
        
        cleaned = cleaned.strip()
        
        # Parse JSON
        email_data = json.loads(cleaned)
        
        # Validate structure
        if 'subject' not in email_data or 'body' not in email_data:
            raise ValueError("Missing subject or body in response")
        
        return email_data
    
    except json.JSONDecodeError as e:
        print(f"⚠️  JSON parsing error: {e}")
        print(f"Raw response: {response[:200]}...")
        # Fallback with customer details
        return {
            "subject": f"{topic} - Policy #{customer_details['policy_number']}",
            "body": f"""Dear Sir/Madam,

I am writing regarding {topic}.

My Policy Number: {customer_details['policy_number']}
Phone: {customer_details['phone']}

Please provide assistance at the earliest.

Regards,
{customer_details['full_name']}
{customer_details['address']}"""
        }
    except Exception as e:
        print(f"⚠️  Content generation error: {e}")
        return {
            "subject": f"{topic} - Policy #{customer_details['policy_number']}",
            "body": f"""Dear LIC Team,

I need help with {topic} for my policy {customer_details['policy_number']}.

Contact: {customer_details['phone']}

Thank you,
{customer_details['full_name']}"""
        }


def authenticate_gmail():
    """
    Authenticate with Gmail API using OAuth 2.0
    Handles token creation and refresh automatically
    """
    creds = None
    token_path = Path('token.json')
    creds_path = Path('credentials.json')
    
    # Check if credentials.json exists
    if not creds_path.exists():
        raise FileNotFoundError(
            "credentials.json not found. Please download it from Google Cloud Console."
        )
    
    # Load existing token if available
    if token_path.exists():
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # Refresh or create new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing access token...")
            creds.refresh(Request())
        else:
            print("🔐 Starting OAuth flow (browser will open)...")
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES
            )
            # Try multiple ports if needed
            for port in [0, 8081, 8082, 9090, 5000]:
                try:
                    creds = flow.run_local_server(port=port, open_browser=True)
                    break
                except OSError as e:
                    if port == 5000:  # Last port to try
                        raise
                    print(f"⚠️  Port {port} in use, trying next...")
        
        # Save credentials for future runs
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        print("✅ Authentication successful! Token saved.")
    
    return creds


def send_email(service, to_email, subject, body):
    """
    Send email via Gmail API
    """
    try:
        message = MIMEText(body)
        message['to'] = to_email
        message['subject'] = subject
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Send via API
        service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        return True
    
    except HttpError as error:
        print(f"❌ Gmail API error: {error}")
        return False
    except Exception as e:
        print(f"❌ Send error: {e}")
        return False


def main():
    """
    Main simulator loop
    """
    # CONFIGURATION: Set to None for infinite emails, or a number like 10, 50, 100
    MAX_EMAILS = None  # Change this to limit emails (e.g., MAX_EMAILS = 20)
    
    print("=" * 70)
    print("🎭 LIC Customer Email Simulator")
    print("=" * 70)
    print()
    
    # Initialize Ollama LLM
    print("🤖 Initializing Ollama LLM (llama3)...")
    try:
        llm = Ollama(model="llama3", temperature=0.8)
        # Test the connection
        llm.invoke("test")
        print("✅ Ollama connected successfully")
    except Exception as e:
        print(f"❌ Failed to connect to Ollama: {e}")
        print("Make sure Ollama is running: ollama serve")
        return
    
    # Authenticate Gmail
    print("\n📧 Authenticating Gmail API...")
    try:
        creds = authenticate_gmail()
        gmail_service = build('gmail', 'v1', credentials=creds)
        print("✅ Gmail API ready")
    except Exception as e:
        print(f"❌ Gmail authentication failed: {e}")
        return
    
    print("\n" + "=" * 70)
    print("🚀 Starting email simulation loop...")
    print(f"📬 Sending to: {TEST_EMAIL}")
    if MAX_EMAILS:
        print(f"🎯 Target: {MAX_EMAILS} emails")
    else:
        print("♾️  Mode: Infinite (press Ctrl+C to stop)")
    print("⏸️  Press Ctrl+C to stop")
    print("=" * 70)
    print()
    
    email_count = 0
    
    try:
        while True:
            # Check if we've reached the limit
            if MAX_EMAILS and email_count >= MAX_EMAILS:
                print(f"\n🎉 Target reached! Sent {email_count} emails.")
                break
            
            # Randomly select persona and topic
            persona = random.choice(PERSONAS)
            topic = random.choice(TOPICS)
            
            # Generate random customer details
            customer_details = generate_customer_details()
            
            print(f"\n[{time.strftime('%H:%M:%S')}] 👤 Customer: {customer_details['full_name']}")
            print(f"                  📋 Policy: {customer_details['policy_number']}")
            print(f"                  🎭 Persona: {persona['name']}")
            print(f"                  📝 Topic: {topic}")
            
            # Generate email content
            print("                  🔄 Generating content...")
            email_data = generate_email_content(llm, persona, topic, customer_details)
            
            subject = email_data['subject']
            body = email_data['body']
            
            # Send email
            print("                  📤 Sending email...")
            success = send_email(gmail_service, TEST_EMAIL, subject, body)
            
            if success:
                email_count += 1
                print(f"                  ✅ Email #{email_count} sent successfully!")
                print(f"                  📤 [Customer] Sent email: '{subject}'")
            else:
                print("                  ❌ Failed to send email")
            
            # Random delay between emails (10-40 seconds)
            delay = random.randint(10, 40)
            print(f"                  ⏳ Waiting {delay} seconds before next email...")
            time.sleep(delay)
    
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print(f"🛑 Simulation stopped by user")
        print(f"📊 Total emails sent: {email_count}")
        print("=" * 70)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print(f"📊 Total emails sent before error: {email_count}")


if __name__ == "__main__":
    main()