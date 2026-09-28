import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-4o")

EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "supplier_id": {"type": "string", "description": "Supplier ID mentioned in the note"},
        "po_id": {"type": "string", "description": "Purchase order ID mentioned in the note"},
        "early_delay_flag": {"type": "integer", "enum": [0, 1], "description": "1 if note warns of delay, 0 otherwise"},
        "expected_delay_days": {"type": "integer", "description": "Estimated delay in days (0 if none)"},
        "delay_reason": {"type": "string", "description": "Brief reason for delay (empty if none)"},
    },
    "required": ["supplier_id", "po_id", "early_delay_flag", "expected_delay_days", "delay_reason"],
}

FRESHNESS_SLA_HOURS = 24
