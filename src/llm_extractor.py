"""
Schema-constrained extraction of supplier delay signals from notes using OpenRouter.
"""

import json
import time
from datetime import datetime, timezone

import pandas as pd
from openai import OpenAI

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config.settings import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, LLM_MODEL

SYSTEM_PROMPT = """You are a supply-chain analyst. Given a supplier note, extract delay information.
Return ONLY valid JSON matching this schema:

{
  "supplier_id": "the supplier ID mentioned",
  "po_id": "the purchase order ID mentioned",
  "early_delay_flag": 1 if the note warns of an upcoming delay (0 otherwise),
  "expected_delay_days": estimated delay in days as integer (0 if no delay),
  "delay_reason": "brief reason for delay (empty string if no delay)"
}
"""


def get_client():
    return OpenAI(base_url=OPENROUTER_BASE_URL, api_key=OPENROUTER_API_KEY)


def extract_signals(client, note_text):
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Extract delay signals from this note:\n\n{note_text}"},
        ],
        response_format={"type": "json_object"},
        temperature=0.0,
        max_tokens=200,
    )
    return json.loads(response.choices[0].message.content)


def extract_batch(client, notes_df, note_col="note_text", batch_delay=0.5):
    results = []
    total = len(notes_df)

    for idx, (_, row) in enumerate(notes_df.iterrows()):
        try:
            signals = extract_signals(client, row[note_col])
            signals["note_id"] = row["note_id"]
            signals["extraction_timestamp"] = datetime.now(timezone.utc).isoformat()
            signals["model_version"] = LLM_MODEL
            signals["source"] = "llm_extraction"
            results.append(signals)
        except Exception as e:
            results.append({
                "note_id": row["note_id"],
                "supplier_id": row.get("supplier_id", ""),
                "po_id": row.get("po_id", ""),
                "early_delay_flag": 0,
                "expected_delay_days": 0,
                "delay_reason": "",
                "extraction_timestamp": datetime.now(timezone.utc).isoformat(),
                "model_version": LLM_MODEL,
                "source": "llm_extraction",
                "extraction_error": str(e),
            })

        if (idx + 1) % 20 == 0:
            print(f"  Extracted {idx + 1}/{total} notes...")

        time.sleep(batch_delay)

    print(f"  Extraction complete: {total} notes processed.")
    return pd.DataFrame(results)
