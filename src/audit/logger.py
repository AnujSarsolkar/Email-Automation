import json
import logging
import os
from datetime import datetime

class ReasoningLog:
    def __init__(self, log_dir="logs"):
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        self.log_file = os.path.join(log_dir, f"audit_{datetime.now().strftime('%Y%m%d')}.jsonl")
        
        # Configure logging
        logging.basicConfig(
            filename=os.path.join(log_dir, "system.log"),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def log_event(self, event_type: str, details: dict):
        """
        Logs a structured event with reasoning.
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        }
        
        # Append to JSONL file
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
            
        logging.info(f"Event: {event_type} - {details.get('summary', '')}")

if __name__ == "__main__":
    logger = ReasoningLog()
    logger.log_event("TEST_EVENT", {"summary": "This is a test", "reasoning": "checking if log works"})
