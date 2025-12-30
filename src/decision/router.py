from src.audit.logger import ReasoningLog
from typing import Dict

class Router:
    def __init__(self):
        self.logger = ReasoningLog()

    def route(self, email_id: str, intent: str, sentiment: str, entities: Dict) -> Dict:
        """
        Decides the priority and routing queue for the email.
        """
        reasoning = []
        priority = "Normal"
        queue = "General"

        # Rule 1: Claims are always high priority
        if intent == "Claim":
            priority = "High"
            queue = "Claims Dept"
            reasoning.append("Intent is Claim (Critical Business Function).")
        
        # Rule 2: Negative sentiment upgrades priority
        if sentiment == "Negative":
            if priority == "Normal":
                priority = "High"
                reasoning.append("Customer sentiment is Negative (Risk of Churn).")
            else:
                priority = "Critical"
                reasoning.append("Negative sentiment escalates High priority to Critical.")
                
        # Rule 3: Routing based on intent
        if intent == "Renewal":
            queue = "Policy Servicing"
        elif intent == "Complaint":
            queue = "Grievance Redressal"
            if sentiment == "Negative":
                priority = "Critical" # Angry complaints are critical
                
        decision = {
            "email_id": email_id,
            "priority": priority,
            "queue": queue,
            "intent": intent,
            "sentiment": sentiment,
            "reasoning": " | ".join(reasoning)
        }
        
        # Audit the decision
        self.logger.log_event("ROUTING_DECISION", decision)
        
        return decision

if __name__ == "__main__":
    router = Router()
    print(router.route("email_123", "Complaint", "Negative", {}))
