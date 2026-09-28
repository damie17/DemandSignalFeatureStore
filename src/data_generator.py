"""
Synthetic data generation for demand forecasting with supplier delay signals.
Generates internally consistent: daily sales/inventory, purchase orders, supplier notes.
"""

import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


SKUS = [
    {"sku_id": "SKU01", "name": "Widget Alpha", "base_demand": 45, "supplier_id": "SUP01", "base_lead_time": 10},
    {"sku_id": "SKU02", "name": "Widget Beta",  "base_demand": 30, "supplier_id": "SUP02", "base_lead_time": 14},
    {"sku_id": "SKU03", "name": "Gadget Pro",   "base_demand": 55, "supplier_id": "SUP03", "base_lead_time": 7},
    {"sku_id": "SKU04", "name": "Gadget Lite",  "base_demand": 20, "supplier_id": "SUP04", "base_lead_time": 18},
    {"sku_id": "SKU05", "name": "Component Z",  "base_demand": 38, "supplier_id": "SUP01", "base_lead_time": 12},
]

SUPPLIERS = [
    {"supplier_id": "SUP01", "name": "Apex Components", "reliability": 0.75},
    {"supplier_id": "SUP02", "name": "Nordic Metals",   "reliability": 0.65},
    {"supplier_id": "SUP03", "name": "Delta Plastics",  "reliability": 0.85},
    {"supplier_id": "SUP04", "name": "Precision Parts",  "reliability": 0.70},
]

DELAY_REASONS = [
    "port congestion", "raw material shortage", "transportation disruption",
    "factory equipment maintenance", "labor shortage", "customs clearance delay",
    "severe weather conditions", "sub-tier supplier failure",
]

NOTE_TEMPLATES_DELAY = [
    "Supplier {supplier_id} ({supplier}) informed us that shipment {po_id} will be delayed by approximately {delay} days due to {reason}.",
    "{supplier} ({supplier_id}) reports {po_id} may arrive {delay} days late. Cause: {reason}.",
    "Update from {supplier}: shipment {po_id}, originally due {promised_date}, now expected around {new_date}. Reason: {reason}.",
    "Urgent notice from {supplier_id}: {po_id} facing a {delay}-day delay due to {reason}.",
    "{supplier} notified us of a {delay}-day delay for {po_id}. {reason} impacting their operations.",
]

NOTE_TEMPLATES_NORMAL = [
    "Routine check-in with {supplier} ({supplier_id}). Shipment {po_id} on track for {promised_date}.",
    "{supplier_id} confirmed {po_id} will arrive as scheduled on {promised_date}. No issues.",
    "No issues reported by {supplier}. Shipment {po_id} on schedule for {promised_date}.",
    "Weekly update from {supplier}: operations normal, {po_id} on track.",
]

US_HOLIDAYS = [
    "2024-01-01", "2024-01-15", "2024-02-19", "2024-05-27", "2024-07-04",
    "2024-09-02", "2024-10-14", "2024-11-28", "2024-11-29", "2024-12-25",
    "2025-01-01", "2025-01-20", "2025-02-17", "2025-05-26", "2025-07-04",
    "2025-09-01", "2025-10-13", "2025-11-27", "2025-11-28", "2025-12-25",
]
HOLIDAY_SET = {pd.Timestamp(d) for d in US_HOLIDAYS}


def _seasonal_demand(base_demand, date, rng):
    dow_mult = [1.1, 1.05, 1.0, 1.0, 1.15, 0.7, 0.6][date.weekday()]
    month_mult = {
        1: 0.85, 2: 0.85, 3: 0.90, 4: 0.95, 5: 1.0, 6: 1.0,
        7: 0.95, 8: 0.95, 9: 1.05, 10: 1.15, 11: 1.25, 12: 1.20,
    }[date.month]
    holiday_mult = 0.3 if pd.Timestamp(date) in HOLIDAY_SET else 1.0
    noise = max(0.5, rng.normal(1.0, 0.15))
    return max(1, int(base_demand * dow_mult * month_mult * holiday_mult * noise))


def _create_po(po_counter, sku, supplier, order_date, rng):
    lead_time = sku["base_lead_time"]
    promised_date = order_date + timedelta(days=lead_time)
    order_qty = sku["base_demand"] * (lead_time + 10)

    is_delayed = rng.random() > supplier["reliability"]
    if is_delayed:
        delay_days = int(rng.integers(3, 16))
        actual_date = promised_date + timedelta(days=delay_days)
        days_after_order = int(rng.integers(max(1, lead_time // 2), max(2, lead_time - 1)))
        note_date = order_date + timedelta(days=days_after_order)
        erp_update_days = int(rng.integers(1, 4))
        erp_update_date = note_date + timedelta(days=erp_update_days)
        if erp_update_date >= actual_date:
            erp_update_date = actual_date - timedelta(days=1)
    else:
        delay_days = 0
        actual_date = promised_date
        note_date = None
        erp_update_date = None

    return {
        "po_id": f"PO{po_counter:04d}",
        "sku_id": sku["sku_id"],
        "supplier_id": supplier["supplier_id"],
        "order_date": order_date,
        "promised_date": promised_date,
        "actual_date": actual_date,
        "erp_update_date": erp_update_date,
        "qty": order_qty,
        "delay_days": delay_days,
        "is_delayed": is_delayed,
        "note_date": note_date,
    }


def _create_delay_note(note_counter, po, supplier, rng):
    reason = random.choice(DELAY_REASONS)
    template = random.choice(NOTE_TEMPLATES_DELAY)
    note_text = template.format(
        supplier=supplier["name"],
        supplier_id=supplier["supplier_id"],
        po_id=po["po_id"],
        delay=po["delay_days"],
        reason=reason,
        new_date=po["actual_date"].strftime("%Y-%m-%d"),
        promised_date=po["promised_date"].strftime("%Y-%m-%d"),
    )
    return {
        "note_id": f"N{note_counter:04d}",
        "note_date": po["note_date"],
        "supplier_id": supplier["supplier_id"],
        "po_id": po["po_id"],
        "note_text": note_text,
        "note_type": "delay_warning",
    }


def _create_routine_note(note_counter, po, supplier, rng):
    template = random.choice(NOTE_TEMPLATES_NORMAL)
    note_text = template.format(
        supplier=supplier["name"],
        supplier_id=supplier["supplier_id"],
        po_id=po["po_id"],
        promised_date=po["promised_date"].strftime("%Y-%m-%d"),
    )
    days_after = int(rng.integers(1, max(2, (po["promised_date"] - po["order_date"]).days)))
    note_date = po["order_date"] + timedelta(days=days_after)
    return {
        "note_id": f"N{note_counter:04d}",
        "note_date": note_date,
        "supplier_id": supplier["supplier_id"],
        "po_id": po["po_id"],
        "note_text": note_text,
        "note_type": "routine",
    }


def generate_all_data(n_days=540, start_date="2024-01-01", seed=42):
    """
    Simulate internally consistent supply chain data.

    Returns:
        daily_df: Daily sales and inventory per SKU (one row per date per SKU)
        po_df: Purchase orders with promised/actual delivery dates
        notes_df: Supplier notes (delay warnings + routine check-ins)
    """
    rng = np.random.default_rng(seed)
    random.seed(seed)

    start = datetime.strptime(start_date, "%Y-%m-%d")
    dates = [start + timedelta(days=i) for i in range(n_days)]

    daily_records = []
    po_records = []
    note_records = []
    po_counter = 0
    note_counter = 0

    for sku in SKUS:
        supplier = next(s for s in SUPPLIERS if s["supplier_id"] == sku["supplier_id"])
        reorder_point = sku["base_demand"] * (sku["base_lead_time"] + 5)
        order_qty = sku["base_demand"] * (sku["base_lead_time"] + 10)

        inventory = order_qty
        open_po = None

        for date in dates:
            # 1. Check PO arrival
            arrived_qty = 0
            if open_po is not None and date >= open_po["actual_date"]:
                arrived_qty = open_po["qty"]
                inventory += arrived_qty
                open_po = None

            # 2. Demand and sales
            true_demand = _seasonal_demand(sku["base_demand"], date, rng)
            sales = min(true_demand, max(0, int(inventory)))
            stockout = int(inventory <= 0)
            inventory = max(0, inventory - sales)

            # 3. Check reorder
            if inventory < reorder_point and open_po is None:
                po_counter += 1
                open_po = _create_po(po_counter, sku, supplier, date, rng)
                po_records.append(open_po)

                if open_po["is_delayed"]:
                    note_counter += 1
                    note = _create_delay_note(note_counter, open_po, supplier, rng)
                    note_records.append(note)
                elif rng.random() < 0.3:
                    note_counter += 1
                    note = _create_routine_note(note_counter, open_po, supplier, rng)
                    note_records.append(note)

            # 4. Daily record
            open_po_qty = open_po["qty"] if open_po else 0
            days_until = (open_po["promised_date"] - date).days if open_po else None

            # ERP-known delay: only available after erp_update_date
            erp_expected_delay = 0
            if open_po and open_po["is_delayed"] and open_po["erp_update_date"]:
                if date >= open_po["erp_update_date"]:
                    erp_expected_delay = open_po["delay_days"]

            daily_records.append({
                "date": date.strftime("%Y-%m-%d"),
                "sku_id": sku["sku_id"],
                "sku_name": sku["name"],
                "supplier_id": sku["supplier_id"],
                "true_demand": true_demand,
                "sales": sales,
                "on_hand_inventory": int(inventory),
                "stockout_flag": stockout,
                "open_po_qty": open_po_qty,
                "days_until_expected_delivery": days_until,
                "erp_expected_delay_days": erp_expected_delay,
                "arrived_qty": arrived_qty,
            })

    daily_df = pd.DataFrame(daily_records)
    daily_df["date"] = pd.to_datetime(daily_df["date"])

    po_df = pd.DataFrame(po_records)
    if not po_df.empty:
        for col in ["order_date", "promised_date", "actual_date", "note_date", "erp_update_date"]:
            po_df[col] = pd.to_datetime(po_df[col])

    notes_df = pd.DataFrame(note_records)
    if not notes_df.empty:
        notes_df["note_date"] = pd.to_datetime(notes_df["note_date"])

    return daily_df, po_df, notes_df


def generate_ground_truth_extractions(notes_df, po_df):
    """
    Create extraction results from known ground truth.
    Fallback if LLM API is unavailable.
    """
    results = []
    for _, note in notes_df.iterrows():
        if note["note_type"] == "delay_warning":
            po = po_df[po_df["po_id"] == note["po_id"]]
            delay = int(po.iloc[0]["delay_days"]) if not po.empty else 0
            results.append({
                "note_id": note["note_id"],
                "supplier_id": note["supplier_id"],
                "po_id": note["po_id"],
                "early_delay_flag": 1,
                "expected_delay_days": delay,
                "delay_reason": "extracted from note",
            })
        else:
            results.append({
                "note_id": note["note_id"],
                "supplier_id": note["supplier_id"],
                "po_id": note["po_id"],
                "early_delay_flag": 0,
                "expected_delay_days": 0,
                "delay_reason": "",
            })

    df = pd.DataFrame(results)
    df["extraction_timestamp"] = datetime.now().isoformat()
    df["model_version"] = "ground_truth"
    df["source"] = "ground_truth"
    return df
