# Demand Signal Feature Store

LLM-extracted supplier delay signals improve demand forecasting by 6.6% (MAPE: 25.01% → 23.36%).

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Synthetic ERP  │     │  Supplier Notes  │     │    GPT-4o via   │
│  Data Generator │     │   (58 texts)     │────▶│   OpenRouter    │
│  (2,700 rows)   │     └─────────────────┘     │  (extraction)   │
└────────┬────────┘                              └────────┬────────┘
         │                                                │
         │  15 ERP features                               │  3 note features
         │  (sales lags, inventory,                       │  (early_delay_flag,
         │   PO timing, calendar)                         │   expected_delay_days,
         │                                                │   delay_reason)
         ▼                                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Feature Store (CSV)                           │
│  18 features + target  │  Lineage metadata  │  24h freshness SLA│
└────────────────────────────────┬────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
          ┌─────────────────┐       ┌─────────────────┐
          │    Baseline     │       │    Enhanced      │
          │  XGBoost Model  │       │  XGBoost Model   │
          │  (15 ERP only)  │       │  (15 ERP + 2     │
          │  MAPE: 25.01%   │       │   note features) │
          └─────────────────┘       │  MAPE: 23.36%    │
                                    └─────────────────┘
                                             │
                                    ┌────────┴────────┐
                                    │  PSI/CSI Drift  │
                                    │   Monitoring    │
                                    └─────────────────┘
```

## Setup & Run

```bash
# 1. Clone the repo
git clone https://github.com/damie17/DemandSignalFeatureStore.git
cd DemandSignalFeatureStore

# 2. Install Jupyter kernel
pip install ipykernel

# 3. Create .env file with your API key
cp .env.example .env
# Edit .env and replace "your-openrouter-api-key" with your actual key

# 4. Open in VS Code
code .
```

Open `notebooks/main.ipynb` and click **Run All**. The first cell installs all dependencies automatically.

## Notes

- LLM extraction is enabled by default (`USE_LLM = True` in Section 2 of the notebook)
- Set `USE_LLM = False` to run without an API key (uses ground-truth fallback)
- All data is synthetic and generated at runtime
