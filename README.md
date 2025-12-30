# LIC Email Processor

An intelligent, automated email processing system designed for insurance use cases (specifically LIC). This system ingests emails, protects privacy by redacting PII, understands intent and sentiment using LLMs, retrieves relevant policy context via RAG, and routes the email to the appropriate department.

## 🚀 Technologies & Libraries

This project leverages a modern AI stack:

### Core & AI
*   **Python**: Primary programming language.
*   **Ollama**: Local LLM backend running `llama3` for intent classification and sentiment analysis.
*   **LangChain**: Framework for orchestrating LLM workflows and chains.
*   **ChromaDB**: Vector database for storing and retrieving policy documents (RAG).

### Security & Privacy
*   **Microsoft Presidio**: Industrial-grade PII (Personally Identifiable Information) recognition and anonymization.
    *   `presidio-analyzer`
    *   `presidio-anonymizer`

### Utilities
*   **imap-tools**: For fetching emails from mail servers (IMAP).
*   **secure-smtplib**: For secure SMTP connections.
*   **Pydantic**: Data validation and setting management.
*   **Tenacity**: Retries for robust network operations.
*   **Python-dotenv**: Environment variable management.

## ✨ Features

1.  **PII Redaction**: Automatically removes sensitive info (Aadhaar, PAN, Phone numbers) before processing.
2.  **Intent Analysis**: Classifies emails into categories like *Claim*, *Renewal*, *Complaint*, or *Inquiry*.
3.  **Sentiment Analysis**: Detects user emotion (*Positive*, *Neutral*, *Negative*) to prioritize urgent cases.
4.  **RAG (Retrieval-Augmented Generation)**: Fetches relevant policy guidelines based on the email context to aid decision-making.
5.  **Smart Routing**: Decides the final action/department based on intent, sentiment, and policy context.

## 🛠️ Prerequisites

1.  **Python 3.10+**
2.  **Ollama**: You must have [Ollama](https://ollama.com/) installed and running.
    *   Pull the model: `ollama pull llama3`

## 📦 Installation

1.  Clone the repository.
2.  Create a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Download the spaCy model for Presidio (if not already installed):
    ```bash
    python -m spacy download en_core_web_lg
    ```

## ⚙️ Configuration

Create a `.env` file in the root directory:

```env
# LLM Configuration
LLM_BASE_URL=http://localhost:11434
LLM_MODEL=llama3

# Email Configuration (Optional for local testing)
EMAIL_USER=your_email@example.com
EMAIL_PASS=your_password
EMAIL_IMAP_SERVER=imap.example.com
```

## ▶️ Usage

To run the processor with the sample data provided:

```bash
python src/main.py
```

To run with a custom input file:

```bash
python src/main.py data/your_emails.txt
```

### How it works
The `main.py` script initializes the **Brain** (LLM), **Memory** (Vector DB), and **Privacy Filter**. It then processes emails sequentially through the pipeline: `Redact -> Analyze -> Retrieve Context -> Decide`.
