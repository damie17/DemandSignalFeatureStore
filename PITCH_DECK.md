# Demand Signal Feature Store — Pitch Deck
## 20-Minute Capstone Presentation

---

### SLIDE 1: Title

**Supply Chain — Demand Signal Feature Store**

*Can LLM-extracted supplier signals improve demand forecasting?*

Capstone Project | AI Engineer Program

---

### SLIDE 2: The Problem

**Demand forecasts miss early warnings hidden in unstructured data**

- ERP systems track structured data: orders, inventory, shipments
- Supplier delay warnings arrive as free-text notes days before ERP updates
- That 5-12 day blind spot causes inaccurate forecasts and poor inventory decisions

**Visual:** Timeline showing order_date → note_date → [GAP] → erp_update_date → promised_date

---

### SLIDE 3: The Hypothesis

> Adding LLM-extracted supplier delay signals to structured ERP features will reduce demand forecasting error (MAPE)

**How we test it:**
- Train two identical XGBoost models
- Baseline: ERP features only (15 features)
- Enhanced: ERP features + note-derived features (17 features)
- Same hyperparameters, same chronological train/test split

---

### SLIDE 4: Solution Architecture

```
Supplier Notes (text)          ERP System (structured)
        │                              │
   GPT-4o Extraction              Feature Engineering
   (early_delay_flag,             (15 lag, inventory,
    expected_delay_days,           calendar features)
    delay_reason)                      │
        │                              │
        └──────── Feature Store ───────┘
                  (Parquet + Lineage)
                       │
              XGBoost Regression
                       │
              Next-Day Sales Forecast
```

---

### SLIDE 5: Data Overview

| Dataset | Records | Description |
|---------|---------|-------------|
| Daily Sales | 2,700 | 5 SKUs × 540 days |
| Purchase Orders | 92 | 4 suppliers, 35-55% reliability |
| Supplier Notes | 58 | 48 delay warnings + 10 routine |

- **Synthetic data** — simulates a retail/wholesale company
- **18 months** of daily operations (Jan 2024 — Jun 2025)
- **Internally consistent**: inventory, sales, POs, and notes all linked

---

### SLIDE 6: LLM Extraction

**Input** (unstructured note):
> "Apex Components (SUP01) reports PO0012 may arrive 8 days late. Cause: port congestion."

**Output** (structured JSON via GPT-4o):
```json
{
  "early_delay_flag": 1,
  "expected_delay_days": 8,
  "delay_reason": "port congestion"
}
```

- 58 notes processed → 48 delays correctly identified
- Extraction includes lineage: timestamp, model version, source

---

### SLIDE 7: Feature Store Design

**18 features tracked** with full lineage metadata:

| Category | Count | Examples |
|----------|-------|---------|
| ERP — Demand | 5 | sales_lag_1, rolling_avg_7 |
| ERP — Inventory | 5 | on_hand_inventory, stockout_flag |
| ERP — Supply | 3 | open_po_qty, historical_avg_supplier_delay |
| Calendar | 3 | day_of_week, month, holiday |
| Note-Derived | 2* | early_delay_flag, expected_delay_days |

*delay_reason extracted but excluded from model (LLM text too variable)

**Storage:** Apache Parquet — columnar, compressed, type-preserving
**Freshness SLA:** 24-hour check — stale features flagged before inference

---

### SLIDE 8: Data Leakage Prevention

| Risk | Mitigation |
|------|-----------|
| Future data in features | All lags shifted by 1+ days |
| Future data in test set | Chronological 80/20 split (no shuffle) |
| Note signals before note arrives | Features only active between note_date and PO arrival |
| ERP delay before it's known | erp_expected_delay only populated after erp_update_date |
| Future supplier performance | merge_asof — only past completed POs |

---

### SLIDE 9: Results

| Metric | Baseline (ERP only) | Enhanced (ERP + Notes) | Change |
|--------|---------------------|------------------------|--------|
| **MAPE** | **25.01%** | **23.36%** | **-6.6%** |
| MAE | 5.03 units | 4.55 units | -9.5% |
| RMSE | 6.80 units | 6.35 units | -6.6% |

**All three metrics improved** with the addition of supplier note signals.

*Hypothesis confirmed: LLM-extracted features reduce forecast error.*

---

### SLIDE 10: Feature Importance

**Top 5 features in the enhanced model:**

1. early_delay_flag ← **Note-derived (LLM)**
2. sales_lag_1
3. rolling_avg_7
4. on_hand_inventory
5. inventory_cover

The LLM-extracted `early_delay_flag` is the #1 most important feature — the model genuinely relies on the note signal, not just the ERP data.

---

### SLIDE 11: Drift Detection

**PSI (Population Stability Index)** monitors feature stability between train and test periods:

| Status | Features |
|--------|----------|
| Stable (<0.1) | sales_lag_1, on_hand_inventory, early_delay_flag |
| Moderate (0.1-0.2) | inventory_cover |
| Significant (>0.2) | rolling_avg_7, expected_delay_days, historical_avg_supplier_delay |

**Key insight:** `early_delay_flag` (the top feature) is stable — the most impactful signal is also the most reliable.

**In production:** PSI > 0.2 would trigger automated model retraining.

---

### SLIDE 12: Technology Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.12, Jupyter Notebook |
| ML | XGBoost |
| LLM | GPT-4o via OpenRouter |
| Feature Store | Apache Parquet + CSV lineage |
| Monitoring | PSI/CSI (scipy) |
| Data | pandas, numpy |
| Visualization | matplotlib, seaborn |
| Code | Git/GitHub |

Single notebook — fully reproducible with Run All.

---

### SLIDE 13: Key Decisions & Trade-offs

| Decision | Rationale |
|----------|-----------|
| Excluded delay_reason from model | LLM text output too variable — PSI confirmed drift |
| XGBoost over linear regression | Handles non-linear feature interactions |
| No hyperparameter tuning | Fair comparison; same params for both models |
| Synthetic data | Demonstrates pipeline without sensitive real data |
| 24-hour freshness SLA | Matches daily forecast cadence |

---

### SLIDE 14: Future Improvements

- **Hyperparameter tuning** — GridSearchCV / Optuna for better MAPE
- **Weekly aggregation** — smoother predictions at higher granularity
- **Real-time extraction** — streaming LLM as notes arrive
- **Automated retraining** — triggered by PSI drift alerts
- **Cloud deployment** — Azure Blob for feature store, Azure ML for inference
- **Multi-supplier handling** — SKUs with overlapping supplier relationships

---

### SLIDE 15: Summary

1. **Problem:** ERP-only forecasts miss early supplier delay signals
2. **Solution:** Feature store + LLM extraction pipeline
3. **Result:** 6.6% MAPE improvement; early_delay_flag is the top feature
4. **Monitoring:** PSI drift detection + freshness SLA ensure production readiness
5. **Takeaway:** Unstructured supplier data has measurable, demonstrable predictive value

---

## Speaker Notes

### Slide 2 — The Problem
"When a supplier emails saying 'our shipment will be 8 days late due to port congestion', that information sits in a text note. The ERP system doesn't know about it for another 5 to 12 days. During that gap, our forecast is blind to the delay."

### Slide 6 — LLM Extraction
"We use GPT-4o to extract three structured fields from each note. The key one is early_delay_flag — a binary 0 or 1 that tells the model a delay is coming before the ERP knows."

### Slide 9 — Results
"The enhanced model reduces MAPE from 25% to 23.4% — a 6.6% improvement. All three error metrics improve. This is with the exact same model and hyperparameters, so the improvement comes purely from the note-derived features."

### Slide 10 — Feature Importance
"What's compelling is that early_delay_flag isn't just helping a little — it's the single most important feature. The model is genuinely learning from the supplier notes."

### Slide 11 — Drift
"We also monitor feature drift using PSI. Our top feature, early_delay_flag, has a PSI of 0.07 — well within the stable range. This gives us confidence it will perform consistently in production."

### Slide 13 — Decisions
"We deliberately excluded delay_reason from the model. The PSI of 1.06 confirms it drifts heavily — the LLM describes the same delay differently each time. Keeping it in the feature store for traceability but out of the model was the right call."
