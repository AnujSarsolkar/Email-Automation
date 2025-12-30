from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from typing import List, Dict

class PrivacyFilter:
    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        self._add_custom_recognizers()

    def _add_custom_recognizers(self):
        # PAN Card (Permanent Account Number)
        # Format: 5 letters, 4 digits, 1 letter (e.g., ABCDE1234F)
        pan_pattern = Pattern(name="pan_pattern", regex=r"[A-Z]{5}[0-9]{4}[A-Z]{1}", score=0.85)
        pan_recognizer = PatternRecognizer(supported_entity="IN_PAN", patterns=[pan_pattern])
        self.analyzer.registry.add_recognizer(pan_recognizer)

        # Aadhaar Card
        # Format: 12 digits, can be spaced XXXX XXXX XXXX
        aadhaar_pattern = Pattern(name="aadhaar_pattern", regex=r"\b\d{4}\s?\d{4}\s?\d{4}\b", score=0.85)
        aadhaar_recognizer = PatternRecognizer(supported_entity="IN_AADHAAR", patterns=[aadhaar_pattern])
        self.analyzer.registry.add_recognizer(aadhaar_recognizer)

    def redact(self, text: str) -> str:
        """
        Scans and redacts PII from the given text.
        Returns the redacted text.
        """
        if not text:
            return ""

        # Analyze
        results = self.analyzer.analyze(text=text, entities=[], language='en')

        # Anonymize
        # Define operators for custom entities if needed, generic 'replace' is default
        operators = {
            "IN_PAN": OperatorConfig("replace", {"new_value": "<REDACTED_PAN>"}),
            "IN_AADHAAR": OperatorConfig("replace", {"new_value": "<REDACTED_AADHAAR>"}),
            "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "<REDACTED_PHONE>"}),
            "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<REDACTED_EMAIL>"}),
            "PERSON": OperatorConfig("replace", {"new_value": "<REDACTED_PERSON>"}),
        }
        
        anonymized_result = self.anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators=operators
        )
        
        return anonymized_result.text

if __name__ == "__main__":
    # Test
    pf = PrivacyFilter()
    sample_text = "My name is Amit. My PAN is ABCDE1234F and my Aadhaar is 1234 5678 9012. Call me at 9876543210."
    print(f"Original: {sample_text}")
    print(f"Redacted: {pf.redact(sample_text)}")
