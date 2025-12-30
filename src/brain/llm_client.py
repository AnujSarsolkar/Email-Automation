from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv

load_dotenv()

class Brain:
    def __init__(self):
        self.base_url = os.getenv("LLM_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("LLM_MODEL", "llama3")
        
        self.llm = ChatOllama(
            base_url=self.base_url,
            model=self.model,
            temperature=0  # Deterministic for classification
        )

    def analyze_intent(self, email_body: str) -> str:
        """
        Classifies the email intent into: Claim, Renewal, Complaint, or Inquiry.
        """
        system_prompt = """
        You are an expert email classifier for an insurance company (LIC).
        Analyze the following email body and classify the intent into EXACTLY ONE of these categories:
        - Claim
        - Renewal
        - Complaint
        - Inquiry

        Output only the category name.
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "{email_body}")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            return chain.invoke({"email_body": email_body}).strip()
        except Exception as e:
            print(f"Error in intent analysis: {e}")
            return "Inquiry" # Default fallback

    def analyze_sentiment(self, email_body: str) -> str:
        """
        Analyzes the sentiment of the email: Positive, Neutral, or Negative.
        """
        system_prompt = """
        Analyze the sentiment of the following email.
        Output EXACTLY ONE of these:
        - Positive
        - Neutral
        - Negative

        If the user seems frustrated or angry, classify as Negative.
        Output only the sentiment label.
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "{email_body}")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            return chain.invoke({"email_body": email_body}).strip()
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return "Neutral"

if __name__ == "__main__":
    # Test
    brain = Brain()
    sample_text = "I am very angry that my claim hasn't been processed yet! It's been 3 weeks."
    print(f"Intent: {brain.analyze_intent(sample_text)}")
    print(f"Sentiment: {brain.analyze_sentiment(sample_text)}")
