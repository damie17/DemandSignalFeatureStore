import os
from dotenv import load_dotenv

load_dotenv()

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
AZURE_STORAGE_CONTAINER = os.getenv("AZURE_STORAGE_CONTAINER", "demand-signal-store")

EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "risk_mentioned": {
            "type": "boolean",
            "description": "Whether the note mentions any supply risk"
        },
        "delay_days": {
            "type": "integer",
            "description": "Estimated delay in days mentioned or implied (0 if none)"
        },
        "capacity_flag": {
            "type": "string",
            "enum": ["normal", "constrained", "critical"],
            "description": "Supplier capacity status"
        },
        "sentiment_score": {
            "type": "number",
            "description": "Overall sentiment from -1.0 (negative) to 1.0 (positive)"
        },
        "key_phrases": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Key risk or delay phrases extracted from the note"
        }
    },
    "required": ["risk_mentioned", "delay_days", "capacity_flag", "sentiment_score", "key_phrases"]
}

FRESHNESS_SLA_HOURS = 24
