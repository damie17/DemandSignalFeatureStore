"""
Synthetic data generation for ERP shipment records and supplier notes.
"""

import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

SUPPLIERS = [
    {"id": "SUP-001", "name": "Apex Components", "region": "Asia-Pacific", "reliability": 0.85},
    {"id": "SUP-002", "name": "Nordic Metals", "region": "Europe", "reliability": 0.92},
    {"id": "SUP-003", "name": "Delta Plastics", "region": "North America", "reliability": 0.78},
    {"id": "SUP-004", "name": "Precision Parts Co", "region": "Europe", "reliability": 0.95},
    {"id": "SUP-005", "name": "ShenZhen Electronics", "region": "Asia-Pacific", "reliability": 0.70},
    {"id": "SUP-006", "name": "Great Lakes Materials", "region": "North America", "reliability": 0.88},
    {"id": "SUP-007", "name": "Rajasthan Textiles", "region": "Asia-Pacific", "reliability": 0.75},
    {"id": "SUP-008", "name": "Bavaria Engineering", "region": "Europe", "reliability": 0.93},
]

PRODUCTS = [
    {"sku": "SKU-1001", "name": "Aluminum Housing", "category": "Structural"},
    {"sku": "SKU-1002", "name": "PCB Module A", "category": "Electronics"},
    {"sku": "SKU-1003", "name": "Rubber Gasket Set", "category": "Sealing"},
    {"sku": "SKU-1004", "name": "Steel Bracket", "category": "Structural"},
    {"sku": "SKU-1005", "name": "Connector Cable 2m", "category": "Electronics"},
    {"sku": "SKU-1006", "name": "Thermal Pad Kit", "category": "Thermal"},
]

NOTE_TEMPLATES_NORMAL = [
    "Shipment from {supplier} arrived on schedule. Quality inspection passed. No issues noted.",
    "Regular delivery from {supplier}. All {qty} units of {product} received in good condition.",
    "{supplier} confirmed next shipment on track. Lead time stable at {lead_time} days.",
    "Routine check-in with {supplier}. Production running smoothly, capacity is adequate for current demand.",
    "Received confirmation from {supplier} — order #{order_id} will ship as planned. No delays expected.",
    "{supplier} quarterly review: strong performance, consistent delivery windows, no quality flags.",
]

NOTE_TEMPLATES_RISK = [
    "{supplier} warned of potential {delay_days}-day delay due to raw material shortage. Monitoring closely.",
    "Lead time from {supplier} has increased from {lead_time} to {lead_time_new} days. They cite port congestion in {region}.",
    "Quality issue flagged on last batch from {supplier}. {reject_pct}% rejection rate on {product}. Rework needed.",
    "{supplier} reports factory running at {capacity_pct}% capacity — labor shortage impacting output. May need to split order.",
    "Urgent: {supplier} notified us of a {delay_days}-day production halt due to equipment failure. Backup sourcing initiated.",
    "{supplier} is experiencing logistics disruption in {region}. Expect {delay_days}-day delay on {product} orders.",
    "Account manager at {supplier} flagged rising input costs — may request price adjustment. Also seeing {delay_days}-day lead time creep.",
    "{supplier} capacity constrained — they can only fulfill {capacity_pct}% of our order volume this month. Critical situation.",
    "Received notice from {supplier}: typhoon disruption in {region} affecting shipping routes. Estimated {delay_days}-day impact.",
    "{supplier} missed delivery window by {delay_days} days. Root cause: sub-tier supplier failure. Escalated to management.",
]


def generate_erp_data(n_records: int = 2000, start_date: str = "2024-01-01",
                      end_date: str = "2025-06-30", seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    random.seed(seed)

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    date_range = (end - start).days

    records = []
    for i in range(n_records):
        supplier = random.choice(SUPPLIERS)
        product = random.choice(PRODUCTS)
        order_date = start + timedelta(days=rng.integers(0, date_range))
        base_lead_time = rng.integers(5, 30)

        is_delayed = rng.random() < (1 - supplier["reliability"])
        delay_days = int(rng.integers(1, 21)) if is_delayed else 0
        actual_lead_time = base_lead_time + delay_days

        qty_ordered = int(rng.integers(50, 5000))
        qty_received = qty_ordered if not is_delayed else int(qty_ordered * rng.uniform(0.7, 1.0))

        delivery_date = order_date + timedelta(days=int(actual_lead_time))

        records.append({
            "order_id": f"ORD-{10000 + i}",
            "supplier_id": supplier["id"],
            "supplier_name": supplier["name"],
            "supplier_region": supplier["region"],
            "sku": product["sku"],
            "product_name": product["name"],
            "product_category": product["category"],
            "order_date": order_date.strftime("%Y-%m-%d"),
            "expected_delivery_date": (order_date + timedelta(days=int(base_lead_time))).strftime("%Y-%m-%d"),
            "actual_delivery_date": delivery_date.strftime("%Y-%m-%d"),
            "planned_lead_time_days": int(base_lead_time),
            "actual_lead_time_days": int(actual_lead_time),
            "delay_days": delay_days,
            "qty_ordered": qty_ordered,
            "qty_received": qty_received,
            "unit_cost": round(float(rng.uniform(5, 500)), 2),
            "on_time_delivery": delay_days == 0,
        })

    df = pd.DataFrame(records)
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["expected_delivery_date"] = pd.to_datetime(df["expected_delivery_date"])
    df["actual_delivery_date"] = pd.to_datetime(df["actual_delivery_date"])
    df["year_month"] = df["order_date"].dt.to_period("M").astype(str)
    return df


def generate_supplier_notes(erp_df: pd.DataFrame, notes_per_month: int = 3,
                            seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    random.seed(seed)

    year_months = erp_df["year_month"].unique()
    supplier_ids = erp_df["supplier_id"].unique()

    notes = []
    note_id = 0
    for ym in sorted(year_months):
        for sid in supplier_ids:
            subset = erp_df[(erp_df["year_month"] == ym) & (erp_df["supplier_id"] == sid)]
            if subset.empty:
                continue

            supplier = next(s for s in SUPPLIERS if s["id"] == sid)
            n_notes = rng.integers(1, notes_per_month + 1)

            for _ in range(n_notes):
                has_risk = rng.random() > supplier["reliability"]
                sample_row = subset.sample(1, random_state=int(rng.integers(0, 99999))).iloc[0]

                if has_risk:
                    template = random.choice(NOTE_TEMPLATES_RISK)
                    delay_days = int(rng.integers(2, 21))
                    note_text = template.format(
                        supplier=supplier["name"],
                        delay_days=delay_days,
                        lead_time=sample_row["planned_lead_time_days"],
                        lead_time_new=sample_row["planned_lead_time_days"] + delay_days,
                        region=supplier["region"],
                        product=sample_row["product_name"],
                        reject_pct=int(rng.integers(5, 25)),
                        capacity_pct=int(rng.integers(40, 80)),
                        order_id=sample_row["order_id"],
                        qty=sample_row["qty_ordered"],
                    )
                else:
                    template = random.choice(NOTE_TEMPLATES_NORMAL)
                    note_text = template.format(
                        supplier=supplier["name"],
                        lead_time=sample_row["planned_lead_time_days"],
                        product=sample_row["product_name"],
                        order_id=sample_row["order_id"],
                        qty=sample_row["qty_ordered"],
                    )

                note_date = pd.Timestamp(ym + "-01") + timedelta(days=int(rng.integers(0, 28)))
                notes.append({
                    "note_id": f"NOTE-{note_id:05d}",
                    "supplier_id": sid,
                    "supplier_name": supplier["name"],
                    "note_date": note_date.strftime("%Y-%m-%d"),
                    "note_text": note_text,
                    "author": random.choice(["procurement_team", "account_manager", "quality_inspector", "logistics_coord"]),
                    "has_risk_signal": has_risk,
                })
                note_id += 1

    df = pd.DataFrame(notes)
    df["note_date"] = pd.to_datetime(df["note_date"])
    return df
