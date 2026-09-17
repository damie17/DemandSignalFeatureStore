"""
Feature store that merges ERP tabular features with LLM-extracted signals.
Tracks lineage, freshness SLA, and serves both feature families.
"""

from datetime import datetime, timezone

import pandas as pd

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config.settings import FRESHNESS_SLA_HOURS


def build_erp_features(erp_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate ERP data into monthly supplier-level features."""
    features = erp_df.groupby(["supplier_id", "year_month"]).agg(
        total_orders=("order_id", "count"),
        avg_lead_time=("actual_lead_time_days", "mean"),
        avg_delay=("delay_days", "mean"),
        max_delay=("delay_days", "max"),
        on_time_rate=("on_time_delivery", "mean"),
        total_qty_ordered=("qty_ordered", "sum"),
        total_qty_received=("qty_received", "sum"),
        avg_unit_cost=("unit_cost", "mean"),
    ).reset_index()

    features["fulfillment_rate"] = features["total_qty_received"] / features["total_qty_ordered"]
    features["source"] = "erp"
    features["lineage_timestamp"] = datetime.now(timezone.utc).isoformat()
    return features


def build_llm_features(notes_df: pd.DataFrame, extracted_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate LLM-extracted signals into monthly supplier-level features."""
    merged = notes_df.merge(extracted_df, on="note_id", how="left")
    merged["year_month"] = merged["note_date"].dt.to_period("M").astype(str)

    features = merged.groupby(["supplier_id", "year_month"]).agg(
        note_count=("note_id", "count"),
        risk_mention_rate=("risk_mentioned", "mean"),
        avg_delay_signal=("delay_days", "mean"),
        max_delay_signal=("delay_days", "max"),
        avg_sentiment=("sentiment_score", "mean"),
        min_sentiment=("sentiment_score", "min"),
    ).reset_index()

    capacity_mode = merged.groupby(["supplier_id", "year_month"])["capacity_flag"].agg(
        lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else "normal"
    ).reset_index()
    capacity_mode.columns = ["supplier_id", "year_month", "capacity_mode"]

    features = features.merge(capacity_mode, on=["supplier_id", "year_month"], how="left")
    features["capacity_is_constrained"] = features["capacity_mode"].isin(["constrained", "critical"]).astype(int)

    features["source"] = "llm_extraction"
    features["lineage_timestamp"] = merged["extraction_timestamp"].max()
    features["model_version"] = merged["model_version"].iloc[0] if "model_version" in merged.columns else "unknown"
    return features


def build_combined_feature_store(erp_features: pd.DataFrame,
                                  llm_features: pd.DataFrame) -> pd.DataFrame:
    """Merge ERP and LLM feature families into a single feature store."""
    store = erp_features.merge(
        llm_features.drop(columns=["source", "lineage_timestamp"], errors="ignore"),
        on=["supplier_id", "year_month"],
        how="left",
        suffixes=("_erp", "_llm"),
    )

    store["lineage"] = store.apply(
        lambda r: {
            "erp_source": "erp_shipment_data",
            "llm_source": "supplier_notes_extraction",
            "erp_timestamp": r.get("lineage_timestamp", ""),
            "llm_model": r.get("model_version", ""),
        },
        axis=1,
    )

    store["feature_store_updated_at"] = datetime.now(timezone.utc).isoformat()
    return store


def check_freshness_sla(feature_store: pd.DataFrame) -> pd.DataFrame:
    """Check which records violate the freshness SLA."""
    now = datetime.now(timezone.utc)
    store = feature_store.copy()

    if "lineage_timestamp" in store.columns:
        store["lineage_ts_parsed"] = pd.to_datetime(store["lineage_timestamp"], errors="coerce", utc=True)
        store["hours_since_update"] = (now - store["lineage_ts_parsed"]).dt.total_seconds() / 3600
        store["freshness_sla_met"] = store["hours_since_update"] <= FRESHNESS_SLA_HOURS
    else:
        store["freshness_sla_met"] = True

    return store


def get_lineage_report(feature_store: pd.DataFrame) -> pd.DataFrame:
    """Generate a lineage summary for auditing."""
    report = feature_store[["supplier_id", "year_month", "source", "lineage_timestamp"]].copy()
    report["has_erp_features"] = True
    report["has_llm_features"] = feature_store["risk_mention_rate"].notna()
    return report
