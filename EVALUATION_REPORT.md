# Evaluation Report — Demand Signal Feature Store

## Objective

Measure whether LLM-extracted supplier delay signals improve next-day demand forecasting accuracy compared to an ERP-only baseline.

## Experimental Setup

| Parameter | Value |
|-----------|-------|
| Algorithm | XGBoost Regressor |
| Hyperparameters | n_estimators=200, max_depth=5, learning_rate=0.1, random_state=42 |
| Train/Test Split | Chronological 80/20 (first ~14 months train, last ~4 months test) |
| Baseline Features | 15 ERP features (sales lags, inventory, PO timing, calendar) |
| Enhanced Features | 15 ERP + 2 note-derived (early_delay_flag, expected_delay_days) |
| Target Variable | target_next_day_sales |
| Data | Synthetic: 2,700 daily records, 5 SKUs, 4 suppliers, 540 days |

Both models use identical hyperparameters to isolate the value of the additional features.

## LLM Extraction Quality

The LLM (GPT-4o) extracts structured fields from 58 supplier notes. Ground truth comes from the data generator's `note_type` label.

| Metric | Score |
|--------|-------|
| **Precision** | 100% |
| **Recall** | 100% |
| **F1 Score** | 100% |
| **Accuracy** | 100% |
| **Delay Days MAE** | ~1.5 days |

- **Precision:** Of the notes flagged as delays, all were actual delays
- **Recall:** All actual delay notes were correctly identified
- **F1 Score:** Harmonic mean of precision and recall
- **Delay Days MAE:** Average error in predicted delay duration vs. actual

Note: Scores are near-perfect on synthetic data. Real-world supplier notes with more variability would likely produce lower scores.

## Forecast Results

| Metric | Baseline (ERP only) | Enhanced (ERP + Notes) | Change |
|--------|---------------------|------------------------|--------|
| **MAPE** | 25.01% | 23.36% | **-6.6%** (improved) |
| **MAE** | 5.03 units | 4.55 units | **-9.5%** (improved) |
| **RMSE** | 6.80 units | 6.35 units | **-6.6%** (improved) |

### Metric Definitions

- **MAPE (Mean Absolute Percentage Error):** Average percentage deviation of predictions from actuals. Lower is better. Industry-standard metric for demand forecasting.
- **MAE (Mean Absolute Error):** Average absolute difference between predicted and actual values in units. Lower is better.
- **RMSE (Root Mean Squared Error):** Square root of the average squared error. Penalizes large errors more heavily than MAE. Lower is better.

## Feature Importance (Enhanced Model — Top 5)

| Rank | Feature | Source | Role |
|------|---------|--------|------|
| 1 | early_delay_flag | Supplier Note (LLM) | Binary delay warning — available before ERP update |
| 2 | sales_lag_1 | ERP | Previous day's sales |
| 3 | rolling_avg_7 | ERP | 7-day smoothed demand trend |
| 4 | on_hand_inventory | ERP | Current warehouse stock |
| 5 | inventory_cover | ERP | Days of stock remaining |

The LLM-extracted `early_delay_flag` is the single most important feature, validating the hypothesis that unstructured supplier signals carry unique predictive value.

## Drift Detection (PSI)

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

**PSI thresholds:** <0.1 stable, 0.1–0.2 moderate, ≥0.2 significant.

Key finding: `early_delay_flag` (PSI = 0.07) is stable — the most important feature is also the most reliable. `delay_reason_encoded` (PSI = 1.06) confirms the decision to exclude it from the model.

## Leakage Prevention

| Risk | Safeguard |
|------|-----------|
| Future sales in features | All lags use past data only; rolling averages shifted by 1 day |
| Test set contamination | Chronological split — no random shuffling |
| Notes before they exist | Note features active only between note_date and PO arrival |
| Future supplier performance | historical_avg_supplier_delay uses only past completed POs (merge_asof) |

## Conclusion

Adding two LLM-extracted features (early_delay_flag, expected_delay_days) to 15 ERP features improves all three evaluation metrics. The improvement is driven by the early warning signal that supplier notes provide 5–12 days before the ERP system is updated. The key note feature is stable (PSI = 0.07), supporting production deployment confidence.

### Limitations

- Synthetic data — real supplier notes may have more variability
- No hyperparameter tuning — MAPE could be further reduced with optimization
- Single supplier per SKU — no multi-supplier overlap handling
- Observed sales underestimates true demand during stockouts
