"""
Feature drift detection using Population Stability Index (PSI) and
Characteristic Stability Index (CSI).
"""

import numpy as np
import pandas as pd


def _calculate_psi(expected: np.ndarray, actual: np.ndarray, bins: int = 10) -> float:
    """Calculate PSI between two distributions."""
    breakpoints = np.linspace(
        min(expected.min(), actual.min()) - 1e-6,
        max(expected.max(), actual.max()) + 1e-6,
        bins + 1,
    )

    expected_counts = np.histogram(expected, bins=breakpoints)[0]
    actual_counts = np.histogram(actual, bins=breakpoints)[0]

    expected_pct = (expected_counts + 1) / (expected_counts.sum() + bins)
    actual_pct = (actual_counts + 1) / (actual_counts.sum() + bins)

    psi = np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct))
    return float(psi)


def calculate_psi_for_features(reference_df: pd.DataFrame, current_df: pd.DataFrame,
                                feature_cols: list[str], bins: int = 10) -> pd.DataFrame:
    """Calculate PSI for each feature between reference and current periods."""
    results = []
    for col in feature_cols:
        ref_vals = reference_df[col].dropna().values
        cur_vals = current_df[col].dropna().values

        if len(ref_vals) < bins or len(cur_vals) < bins:
            results.append({"feature": col, "psi": None, "status": "insufficient_data"})
            continue

        psi = _calculate_psi(ref_vals, cur_vals, bins)
        if psi < 0.1:
            status = "stable"
        elif psi < 0.2:
            status = "moderate_drift"
        else:
            status = "significant_drift"

        results.append({"feature": col, "psi": round(psi, 4), "status": status})

    return pd.DataFrame(results)


def calculate_csi(reference_df: pd.DataFrame, current_df: pd.DataFrame,
                  feature_col: str, bins: int = 10) -> pd.DataFrame:
    """Calculate CSI — bin-level breakdown showing where drift originates."""
    ref_vals = reference_df[feature_col].dropna().values
    cur_vals = current_df[feature_col].dropna().values

    breakpoints = np.linspace(
        min(ref_vals.min(), cur_vals.min()) - 1e-6,
        max(ref_vals.max(), cur_vals.max()) + 1e-6,
        bins + 1,
    )

    ref_counts = np.histogram(ref_vals, bins=breakpoints)[0]
    cur_counts = np.histogram(cur_vals, bins=breakpoints)[0]

    ref_pct = (ref_counts + 1) / (ref_counts.sum() + bins)
    cur_pct = (cur_counts + 1) / (cur_counts.sum() + bins)

    csi_per_bin = (cur_pct - ref_pct) * np.log(cur_pct / ref_pct)

    bin_labels = [f"({breakpoints[i]:.2f}, {breakpoints[i+1]:.2f}]" for i in range(bins)]

    return pd.DataFrame({
        "bin": bin_labels,
        "reference_pct": np.round(ref_pct, 4),
        "current_pct": np.round(cur_pct, 4),
        "csi_contribution": np.round(csi_per_bin, 4),
    })
