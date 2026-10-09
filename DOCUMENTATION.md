# Demand Signal Feature Store — Technical Documentation

## 1. Project Overview

**Objective:** Demonstrate that adding LLM-extracted supplier delay signals to structured ERP data improves next-day demand (sales) forecasting accuracy, measured by MAPE.

**Business Problem:** Demand forecasts run on structured ERP data (shipments, orders, inventory) and miss early warnings buried in unstructured supplier notes. By the time a delay shows up in the ERP, the forecast has already been wrong for days.

**Solution:** A feature pipeline that:
1. Extracts delay signals from supplier notes using GPT-4o
2. Merges them with ERP features in a feature store with lineage tracking
3. Proves the enhanced forecast has lower error than the ERP-only baseline

## 2. Data Description

### Company Profile
- Retail/wholesale company selling 5 physical products (SKUs)
- 4 suppliers with varying reliability (35%-55%)
- 18 months of daily data (540 days, Jan 2024 — Jun 2025)

### Data Tables

| Table | Rows | Description |
|-------|------|-------------|
| Daily Sales & Inventory | 2,700 | One row per SKU per day — sales, inventory, stockout flag |
| Purchase Orders | 92 | Each PO with order, promised, actual, and ERP update dates |
| Supplier Notes | 58 | Natural language delay warnings and routine check-ins |

### Products (SKUs)

| SKU ID | Name | Supplier | Base Demand/Day |
|--------|------|----------|-----------------|
| SKU01 | Widget Alpha | SUP01 (Apex Components) | 45 |
| SKU02 | Widget Beta | SUP02 (Nordic Metals) | 30 |
| SKU03 | Gadget Pro | SUP03 (Delta Plastics) | 55 |
| SKU04 | Gadget Lite | SUP04 (Precision Parts) | 20 |
| SKU05 | Component Z | SUP01 (Apex Components) | 38 |

### Key Temporal Relationship

For a delayed PO, events happen in this order:

```
order_date → note_date → erp_update_date → promised_date → actual_date
```

The gap between `note_date` and `erp_update_date` (5-12 days) is where the note provides early warning that the ERP does not yet have. This is the core value proposition.

## 3. LLM Extraction Pipeline

### Architecture
- **Model:** GPT-4o via OpenRouter (OpenAI-compatible API)
- **Input:** Supplier note text (natural language)
- **Output:** Structured JSON with schema-constrained fields

### Extraction Schema

| Field | Type | Description |
|-------|------|-------------|
| early_delay_flag | int (0/1) | 1 if note warns of delay |
| expected_delay_days | int | Estimated delay in days |
| delay_reason | string | Brief reason for delay |

### Lineage Metadata (per extraction)

| Field | Description |
|-------|-------------|
| extraction_timestamp | When the note was processed |
| model_version | Which LLM was used (openai/gpt-4o) |
| source | "llm_extraction" or "ground_truth" |

### Extraction Results
- 58 notes processed
- 48 delay warnings detected
- 10 routine notes correctly classified as no-delay

## 4. Feature Engineering

### ERP Features (15)

| Feature | Source | Description |
|---------|--------|-------------|
| sales_lag_1 | ERP | Sales 1 day ago |
| sales_lag_7 | ERP | Sales 7 days ago |
| sales_lag_28 | ERP | Sales 28 days ago |
| rolling_avg_7 | ERP | 7-day rolling average sales |
| rolling_avg_28 | ERP | 28-day rolling average sales |
| on_hand_inventory | ERP | Current warehouse stock level |
| available_inventory | ERP | On-hand inventory + open PO qty |
| stockout_flag | ERP | 1 if inventory was zero |
| inventory_cover | ERP | Days of inventory remaining (on_hand / rolling_avg_7) |
| open_po_qty | ERP | Units in open purchase orders |
| days_until_expected_delivery | ERP | Days until next PO is expected |
| historical_avg_supplier_delay | ERP | Running average of past delays for this supplier |
| day_of_week | Calendar | 0=Monday, 6=Sunday |
| month | Calendar | Month (1-12) |
| holiday | Calendar | 1 if US holiday |

### Note-Derived Features (2 used in model)

| Feature | Source | Description |
|---------|--------|-------------|
| early_delay_flag | Supplier Note (LLM) | 1 if note warns of delay — BEFORE ERP knows |
| expected_delay_days | Supplier Note (LLM) | Delay days from note — BEFORE ERP knows |

Note: `delay_reason` is extracted and stored in the feature store for lineage/traceability but excluded from the model due to variability in LLM text output.

### Leakage Prevention
- All lag features shifted (no same-day data)
- Rolling averages shifted by 1 day
- Note signals only active after note_date and before PO arrival
- Historical supplier delay uses only past completed POs (merge_asof)
- Chronological train/test split (no random shuffle)

### Target Variable
- `target_next_day_sales` — next-day observed sales (demand proxy)
- Observed sales = true demand when inventory is sufficient
- During stockouts, observed sales underestimates true demand

## 5. Feature Store

### Storage
- **Format:** CSV (universal, human-readable)
- **Location:** `data/feature_store.csv`
- **Lineage:** `data/feature_lineage.csv`

### Lineage Metadata (per feature)

| Field | Description |
|-------|-------------|
| feature_name | Feature identifier |
| source | Origin: erp, calendar, or supplier_note |
| description | Plain English explanation |
| source_timestamp | When underlying data was last updated |
| created_timestamp | When feature was computed |
| freshness_status | fresh or stale |

### Freshness SLA
- Threshold: 24 hours
- Features older than 24 hours are flagged stale
- In production, stale features trigger alerts before predictions run

## 6. Model Training & Evaluation

### Model
- **Algorithm:** XGBoost Regressor
- **Hyperparameters:** n_estimators=200, max_depth=5, learning_rate=0.1, random_state=42
- **Same parameters for both models** to ensure fair comparison

### Data Split
- **Method:** Chronological (time-series aware, no shuffling)
- **Training:** First 80% of dates (~14 months)
- **Testing:** Last 20% of dates (~4 months)

### Results

| Metric | Baseline (ERP only) | Enhanced (ERP + Notes) | Change |
|--------|---------------------|------------------------|--------|
| MAPE | 25.01% | 23.36% | -6.6% (improved) |
| MAE | 5.03 units | 4.55 units | -9.5% (improved) |
| RMSE | 6.80 units | 6.35 units | -6.6% (improved) |

All three metrics improved with the addition of supplier note signals.

### Feature Importance
The `early_delay_flag` is among the top features in the enhanced model, validating the hypothesis that note-derived signals provide genuine predictive power that ERP features alone cannot capture.

## 7. Drift Detection

### Method
- **PSI (Population Stability Index)** — compares feature distributions between training and test periods
- **Thresholds:** <0.1 stable, 0.1-0.2 moderate drift, >=0.2 significant drift

### Results

| Feature | PSI | Status |
|---------|-----|--------|
| sales_lag_1 | 0.03 | Stable |
| on_hand_inventory | 0.01 | Stable |
| early_delay_flag | 0.07 | Stable |
| inventory_cover | 0.12 | Moderate drift |
| rolling_avg_7 | 0.24 | Significant drift |
| expected_delay_days | 0.63 | Significant drift |
| historical_avg_supplier_delay | 0.78 | Significant drift |
| delay_reason_encoded | 1.06 | Significant drift |

### Interpretation
- `early_delay_flag` is stable — the key note feature is consistent
- `delay_reason_encoded` shows highest drift — confirms the decision to exclude it from the model
- `historical_avg_supplier_delay` drifts because it is cumulative and stabilizes over time
- In production, features crossing PSI > 0.2 would trigger model retraining alerts

## 8. Technology Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.12 |
| Notebook | Jupyter (VS Code) |
| ML Model | XGBoost |
| LLM | GPT-4o via OpenRouter |
| Feature Store | CSV |
| Drift Detection | PSI/CSI (scipy) |
| Data Processing | pandas, numpy |
| Visualization | matplotlib, seaborn |
| Version Control | Git/GitHub |

## 9. Project Structure

```
DemandSignalFeatureStore/
├── notebooks/
│   └── main.ipynb          # Single end-to-end notebook
├── src/
│   ├── data_generator.py   # Synthetic data simulation
│   ├── llm_extractor.py    # LLM extraction via OpenRouter
│   └── drift.py            # PSI/CSI drift detection
├── config/
│   └── settings.py         # API keys, model config, SLA
├── data/                   # Generated at runtime
├── .env.example            # Template for API key
├── requirements.txt        # Python dependencies
├── README.md               # Setup instructions
└── DOCUMENTATION.md        # This file
```

## 10. How to Run

```bash
git clone https://github.com/damie17/DemandSignalFeatureStore.git
cd DemandSignalFeatureStore
pip install ipykernel
cp .env.example .env
# Edit .env with your OpenRouter API key
```

Open `notebooks/main.ipynb` in VS Code and click Run All.

## 11. Future Improvements

- **Hyperparameter tuning** using GridSearchCV or Optuna
- **Weekly/monthly aggregation** for lower MAPE at higher granularity
- **Real-time extraction** with streaming LLM calls as notes arrive
- **Multi-supplier overlap** handling for SKUs with multiple suppliers
- **Automated retraining** triggered by PSI drift alerts
- **Cloud deployment** with Azure Blob Storage for the feature store
