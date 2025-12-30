import json
import csv
import re
from typing import List, Dict
import os

class DataLoader:
    def load_emails(self, file_path: str) -> List[Dict]:
        """
        Loads emails from a file based on its extension (.json, .csv, .txt).
        Returns a list of dictionaries with keys: 'id', 'subject', 'body'.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()

        if ext == '.json':
            return self._parse_json(file_path)
        elif ext == '.csv':
            return self._parse_csv(file_path)
        elif ext == '.txt':
            return self._parse_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def _parse_json(self, file_path: str) -> List[Dict]:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _parse_csv(self, file_path: str) -> List[Dict]:
        emails = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                emails.append({
                    "id": row.get("id", f"csv_{i}"),
                    "subject": row.get("subject", "No Subject"),
                    "body": row.get("body", "")
                })
        return emails

    def _parse_txt(self, file_path: str) -> List[Dict]:
        """
        Parses custom text format where emails are separated by '---'
        and headers are like '**Subject:** ...'
        """
        emails = []
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split by separator line
        blocks = content.split('---')

        for i, block in enumerate(blocks):
            if not block.strip():
                continue
            
            email_data = {"id": f"txt_{i+1}", "subject": "No Subject", "body": ""}
            
            # Extract Subject
            subject_match = re.search(r'\*\*Subject:\*\*\s*(.*)', block)
            if subject_match:
                email_data["subject"] = subject_match.group(1).strip()

            # Extract Body (for simplicity, we treat everything after headers as body)
            # Find the start of the body (e.g., "Dear ...")
            body_start = re.search(r'(Dear|Hi|Hello).*', block, re.DOTALL)
            if body_start:
                email_data["body"] = body_start.group(0).strip()
            else:
                 # Fallback: take content after Subject line
                 if subject_match:
                     email_data["body"] = block.split(subject_match.group(0))[1].strip()
                 else:
                     email_data["body"] = block.strip() # All content

            emails.append(email_data)
            
        return emails

if __name__ == "__main__":
    # Test
    loader = DataLoader()
    print("DataLoader initialized.")
