"""
Schema-constrained extraction of supply-chain signals from supplier notes using Azure OpenAI.
"""

import json
import time
from datetime import datetime, timezone

import pandas as pd
from openai import AzureOpenAI

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config.settings import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_DEPLOYMENT,
    AZURE_OPENAI_API_VERSION,
    EXTRACTION_SCHEMA,
)

SYSTEM_PROMPT = """You are a supply-chain risk analyst. Given a supplier note, extract structured signals.
Return ONLY valid JSON matching the provided schema. Do not include any text outside the JSON object.

Rules:
- risk_mentioned: true if the note mentions ANY risk, delay, quality issue, capacity constraint, or disruption
- delay_days: numeric estimate of delay in days. Use 0 if no delay is mentioned or implied
- capacity_flag: "normal" if no capacity issues, "constrained" if partial, "critical" if severe
- sentiment_score: float from -1.0 (very negative/alarming) to 1.0 (very positive/routine)
- key_phrases: list of 1-5 short phrases capturing risk or delay signals (empty list if none)
"""


def get_client() -> AzureOpenAI:
    return AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
    )


def extract_signals(client: AzureOpenAI, note_text: str) -> dict:
    response = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Extract signals from this supplier note:\n\n{note_text}"},
        ],
        response_format={"type": "json_object"},
        temperature=0.0,
        max_tokens=300,
    )
    return json.loads(response.choices[0].message.content)


def extract_batch(client: AzureOpenAI, notes_df: pd.DataFrame,
                  note_col: str = "note_text", batch_delay: float = 0.5) -> pd.DataFrame:
    results = []
    total = len(notes_df)

    for idx, (_, row) in enumerate(notes_df.iterrows()):
        try:
            signals = extract_signals(client, row[note_col])
            signals["note_id"] = row["note_id"]
            signals["extraction_timestamp"] = datetime.now(timezone.utc).isoformat()
            signals["model_version"] = AZURE_OPENAI_DEPLOYMENT
            signals["source"] = "llm_extraction"
            results.append(signals)
        except Exception as e:
            results.append({
                "note_id": row["note_id"],
                "risk_mentioned": None,
                "delay_days": None,
                "capacity_flag": None,
                "sentiment_score": None,
                "key_phrases": [],
                "extraction_timestamp": datetime.now(timezone.utc).isoformat(),
                "model_version": AZURE_OPENAI_DEPLOYMENT,
                "source": "llm_extraction",
                "extraction_error": str(e),
            })

        if idx % 50 == 0 and idx > 0:
            print(f"  Extracted {idx}/{total} notes...")

        time.sleep(batch_delay)

    print(f"  Extraction complete: {total} notes processed.")
    return pd.DataFrame(results)
