# Demand Signal Feature Store — Capstone Project

A feature pipeline that extracts early supplier delay signals from unstructured notes using an LLM, merges them with structured ERP data, and proves the enhanced forecast has lower error (MAPE) than the ERP-only baseline.

## Quick Start (VM Setup)

```bash
# 1. Clone the repo
git clone https://github.com/damie17/DemandSignalFeatureStore.git
cd DemandSignalFeatureStore

# 2. Install Jupyter kernel (if not already installed)
pip install ipykernel

# 3. Create .env file with your API key
cp .env.example .env
# Edit .env and replace "your-openrouter-api-key" with your actual key

# 4. Open in VS Code
code .
```

Then open `notebooks/main.ipynb` and click **Run All**. The first cell installs dependencies and creates the data folder automatically.

## Configuration

LLM extraction is enabled by default (`USE_LLM = True`). Set to `False` in Section 2 of the notebook to use ground-truth fallback without an API key.

## Project Structure

```
DemandSignalFeatureStore/
├── notebooks/
│   └── main.ipynb          # Single end-to-end notebook (Run All)
├── src/
│   ├── data_generator.py   # Synthetic data simulation
│   ├── llm_extractor.py    # LLM extraction via OpenRouter
│   └── drift.py            # PSI/CSI drift detection
├── config/
│   └── settings.py         # API keys, model config, SLA
├── data/                   # Generated at runtime (not in git)
├── .env.example            # Template for API key
├── requirements.txt        # Python dependencies
└── README.md
```

## Features

**ERP Features (15):** Sales lags (1/7/28 day), rolling averages (7/28 day), on-hand inventory, available inventory, stockout flag, inventory cover, open PO qty, days until delivery, historical avg supplier delay, day of week, month, holiday.

**Note Features (3):** Early delay flag, expected delay days, delay reason — extracted from supplier notes by the LLM before the ERP system is updated.

**Target:** Next-day observed sales (demand proxy).

## Key Results

- Baseline (ERP only) vs Enhanced (ERP + note signals): ~12% MAPE improvement
- XGBoost regression with chronological train/test split (80/20)
- Feature store with Parquet storage and lineage metadata
- PSI drift detection and 24-hour freshness SLA monitoring
