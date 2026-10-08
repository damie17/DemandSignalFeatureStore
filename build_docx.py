"""Build the capstone documentation as a formatted Word document."""

from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml

doc = Document()

# ── Page setup ──
section = doc.sections[0]
section.page_width = Cm(21)
section.page_height = Cm(29.7)
section.top_margin = Cm(2.5)
section.bottom_margin = Cm(2.5)
section.left_margin = Cm(2.5)
section.right_margin = Cm(2.5)

# ── EXL Colors ──
EXL_ORANGE = RGBColor(0xFB, 0x4D, 0x0A)
EXL_SLATE  = RGBColor(0x2E, 0x36, 0x43)
EXL_BLUE   = RGBColor(0x00, 0x50, 0x71)
EXL_GRAY   = RGBColor(0x6D, 0x72, 0x7B)
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
BLACK      = RGBColor(0x00, 0x00, 0x00)
DARK_GRAY  = RGBColor(0x33, 0x33, 0x33)

# ── Style customization ──
style = doc.styles['Normal']
style.font.name = 'Calibri'
style.font.size = Pt(11)
style.font.color.rgb = DARK_GRAY
style.paragraph_format.space_after = Pt(6)
style.paragraph_format.line_spacing = 1.15

for level in range(1, 4):
    h_style = doc.styles[f'Heading {level}']
    h_style.font.name = 'Calibri'
    if level == 1:
        h_style.font.size = Pt(22)
        h_style.font.color.rgb = EXL_ORANGE
        h_style.font.bold = True
        h_style.paragraph_format.space_before = Pt(24)
        h_style.paragraph_format.space_after = Pt(8)
    elif level == 2:
        h_style.font.size = Pt(16)
        h_style.font.color.rgb = EXL_BLUE
        h_style.font.bold = True
        h_style.paragraph_format.space_before = Pt(18)
        h_style.paragraph_format.space_after = Pt(6)
    elif level == 3:
        h_style.font.size = Pt(13)
        h_style.font.color.rgb = EXL_SLATE
        h_style.font.bold = True
        h_style.paragraph_format.space_before = Pt(12)
        h_style.paragraph_format.space_after = Pt(4)


def add_para(text, bold=False, italic=False, size=None, color=None, align=None, space_after=None):
    p = doc.add_paragraph()
    run = p.add_run(text)
    if bold:
        run.bold = True
    if italic:
        run.italic = True
    if size:
        run.font.size = Pt(size)
    if color:
        run.font.color.rgb = color
    if align:
        p.alignment = align
    if space_after is not None:
        p.paragraph_format.space_after = Pt(space_after)
    return p


def add_rich_para(parts, space_after=None):
    """parts = [(text, bold, italic, color, size), ...]"""
    p = doc.add_paragraph()
    for text, bold, italic, color, size in parts:
        run = p.add_run(text)
        run.bold = bold
        run.italic = italic
        if color:
            run.font.color.rgb = color
        if size:
            run.font.size = Pt(size)
    if space_after is not None:
        p.paragraph_format.space_after = Pt(space_after)
    return p


def add_bullet(text, bold_prefix=None, level=0):
    p = doc.add_paragraph(style='List Bullet')
    if bold_prefix:
        run = p.add_run(bold_prefix)
        run.bold = True
        run.font.color.rgb = EXL_SLATE
        run = p.add_run(text)
    else:
        p.text = text
    p.paragraph_format.left_indent = Cm(1.2 + level * 0.8)
    return p


def add_table(headers, rows, col_widths=None):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = 'Table Grid'

    # Header row
    hdr = table.rows[0]
    for i, h in enumerate(headers):
        cell = hdr.cells[i]
        cell.text = h
        p = cell.paragraphs[0]
        p.runs[0].bold = True
        p.runs[0].font.color.rgb = WHITE
        p.runs[0].font.size = Pt(10)
        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="005071"/>')
        cell._element.get_or_add_tcPr().append(shading)

    # Data rows
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = table.rows[r + 1].cells[c]
            cell.text = str(val)
            p = cell.paragraphs[0]
            p.runs[0].font.size = Pt(10)
            bg = "F5F5F5" if r % 2 == 0 else "FFFFFF"
            shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{bg}"/>')
            cell._element.get_or_add_tcPr().append(shading)

    if col_widths:
        for i, w in enumerate(col_widths):
            for row in table.rows:
                row.cells[i].width = Cm(w)

    doc.add_paragraph()
    return table


def add_callout(text, bg_color="E6F6FB"):
    p = doc.add_paragraph()
    pPr = p._element.get_or_add_pPr()
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{bg_color}"/>')
    pPr.append(shading)
    p.paragraph_format.left_indent = Cm(0.5)
    p.paragraph_format.right_indent = Cm(0.5)
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(8)
    run = p.add_run(text)
    run.font.size = Pt(11)
    run.font.color.rgb = EXL_BLUE
    run.italic = True
    return p


# ════════════════════════════════════════════════════════════════
# COVER PAGE
# ════════════════════════════════════════════════════════════════

doc.add_paragraph()
doc.add_paragraph()
doc.add_paragraph()

add_para("Demand Signal Feature Store", bold=True, size=32, color=EXL_ORANGE,
         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12)
add_para("Technical Documentation", bold=True, size=20, color=EXL_SLATE,
         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=24)

doc.add_paragraph()

add_para("Supply Chain — Demand Signal Feature Store", size=14, color=EXL_BLUE,
         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)
add_para("Capstone Project  |  AI Engineer Program", size=12, color=EXL_GRAY,
         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)
add_para("September 2026", size=12, color=EXL_GRAY,
         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=24)

doc.add_paragraph()
doc.add_paragraph()

add_callout(
    "This document provides a comprehensive technical walkthrough of the Demand Signal Feature Store project — "
    "covering the business problem, data generation, LLM extraction pipeline, feature engineering, "
    "model training, evaluation results, drift detection, and production-readiness considerations.",
    bg_color="FFF3E0"
)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════
# TABLE OF CONTENTS
# ════════════════════════════════════════════════════════════════

doc.add_heading("Table of Contents", level=1)
toc_items = [
    "1. Executive Summary",
    "2. Business Problem & Motivation",
    "3. Data Description",
    "    3.1 Company Profile",
    "    3.2 Data Tables",
    "    3.3 Products & Suppliers",
    "    3.4 Key Temporal Relationship",
    "4. Solution Architecture",
    "5. LLM Extraction Pipeline",
    "    5.1 Architecture & Model",
    "    5.2 Extraction Schema",
    "    5.3 Extraction Results & Lineage",
    "6. Feature Engineering",
    "    6.1 ERP Features",
    "    6.2 Note-Derived Features",
    "    6.3 Target Variable",
    "    6.4 Data Leakage Prevention",
    "7. Feature Store",
    "    7.1 Storage Format",
    "    7.2 Lineage Metadata",
    "    7.3 Freshness SLA",
    "8. Model Training & Evaluation",
    "    8.1 Model Selection",
    "    8.2 Data Splitting Strategy",
    "    8.3 Results",
    "    8.4 Feature Importance Analysis",
    "9. Drift Detection & Monitoring",
    "    9.1 Population Stability Index (PSI)",
    "    9.2 Characteristic Stability Index (CSI)",
    "    9.3 Drift Results & Interpretation",
    "10. Technology Stack",
    "11. Project Structure & How to Run",
    "12. Key Decisions & Trade-offs",
    "13. Future Improvements",
]
for item in toc_items:
    p = doc.add_paragraph()
    indent = item.startswith("    ")
    run = p.add_run(item.strip())
    run.font.size = Pt(11 if indent else 12)
    run.font.color.rgb = EXL_GRAY if indent else EXL_SLATE
    run.bold = not indent
    if indent:
        p.paragraph_format.left_indent = Cm(1.5)
    p.paragraph_format.space_after = Pt(2)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════
# 1. EXECUTIVE SUMMARY
# ════════════════════════════════════════════════════════════════

doc.add_heading("1. Executive Summary", level=1)

doc.add_paragraph(
    "This project demonstrates that adding LLM-extracted supplier delay signals to structured ERP data "
    "measurably improves next-day demand (sales) forecasting accuracy. The improvement is quantified "
    "using Mean Absolute Percentage Error (MAPE) — the industry-standard metric for forecast accuracy."
)

doc.add_paragraph(
    "In supply chain management, demand forecasting drives critical decisions: how much inventory to hold, "
    "when to reorder, and how to allocate resources. Traditional forecasting relies on structured data from "
    "ERP systems — historical sales, inventory levels, open purchase orders. However, a significant source "
    "of early intelligence is often overlooked: unstructured supplier communications."
)

doc.add_paragraph(
    "When a supplier sends a note warning of a shipment delay, that information exists in free text "
    "days before the ERP system is formally updated. This project builds a pipeline that extracts "
    "structured signals from these notes using a Large Language Model (GPT-4o), stores them in a "
    "feature store with full lineage tracking, and proves they improve forecast accuracy."
)

add_callout(
    "Key Result: Baseline MAPE 25.01% → Enhanced MAPE 23.36% — a 6.6% improvement. "
    "The LLM-extracted early_delay_flag became the #1 most important feature in the enhanced model."
)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════
# 2. BUSINESS PROBLEM
# ════════════════════════════════════════════════════════════════

doc.add_heading("2. Business Problem & Motivation", level=1)

doc.add_paragraph(
    "Enterprise Resource Planning (ERP) systems are the backbone of supply chain operations. They track "
    "every purchase order, shipment, inventory movement, and delivery date in structured, queryable records. "
    "Demand forecasting models built on this data can predict future sales with reasonable accuracy."
)

doc.add_paragraph(
    "However, ERP data has a fundamental blind spot: it only reflects what has been formally recorded. "
    "When a supplier experiences a disruption — port congestion, raw material shortage, factory maintenance — "
    "the delay often shows up first in an informal communication: an email, a phone call logged as a note, "
    "or a message in a procurement platform. This note arrives days before the ERP system is updated with "
    "the revised delivery date."
)

doc.add_heading("The Information Gap", level=2)

doc.add_paragraph(
    "Consider this timeline for a delayed purchase order:"
)

add_table(
    ["Event", "When It Happens", "Who Knows"],
    [
        ["Order placed", "Day 0", "ERP system"],
        ["Supplier sends delay warning (note)", "Day 3–5", "Only the note recipient"],
        ["ERP system updated with delay", "Day 10–15", "ERP system + everyone"],
        ["Original promised delivery", "Day 14", "ERP system"],
        ["Actual delivery (delayed)", "Day 20+", "ERP system"],
    ],
    col_widths=[5, 4, 5]
)

doc.add_paragraph(
    "During the gap between the note arrival (Day 3–5) and the ERP update (Day 10–15), "
    "the demand forecast is blind to the incoming delay. It continues predicting based on the assumption "
    "that inventory will arrive on time. In reality, inventory will run lower than expected, potentially "
    "causing stockouts, and demand patterns shift as the delay impacts product availability."
)

doc.add_paragraph(
    "In our simulation, this gap is 5–12 days — a period where the note contains actionable intelligence "
    "that the ERP does not yet have. This is the core value proposition of this project: extracting that "
    "intelligence and feeding it into the forecast."
)

doc.add_heading("Why LLMs?", level=2)

doc.add_paragraph(
    "Supplier notes are unstructured text with no consistent format. One supplier might write "
    "\"shipment delayed 8 days due to port congestion\" while another writes \"expect late arrival, "
    "equipment maintenance at our facility.\" Extracting structured fields — Is there a delay? How long? "
    "What caused it? — from this variability requires natural language understanding."
)

doc.add_paragraph(
    "Large Language Models like GPT-4o excel at this extraction task. Given a supplier note, the model "
    "returns a structured JSON object with three fields: a binary delay flag, the estimated delay in days, "
    "and the reason for the delay. This turns unstructured text into model-ready features."
)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════
# 3. DATA DESCRIPTION
# ════════════════════════════════════════════════════════════════

doc.add_heading("3. Data Description", level=1)

doc.add_paragraph(
    "All data in this project is synthetically generated to simulate a realistic supply chain scenario. "
    "This approach was chosen deliberately: it allows full control over the data-generating process, "
    "ensures no sensitive business data is exposed, and makes the project fully reproducible."
)

doc.add_heading("3.1 Company Profile", level=2)

doc.add_paragraph(
    "The simulated company is a mid-size retail/wholesale business with the following characteristics:"
)

add_bullet("Sells 5 physical products (SKUs) across different demand profiles")
add_bullet("Sources from 4 suppliers with varying reliability (35%–55% on-time delivery)")
add_bullet("Operates over 18 months of daily transactions (540 days, January 2024 — June 2025)")
add_bullet("Uses a reorder-point inventory system: when stock drops below a threshold, a new purchase order is placed")
add_bullet("Experiences seasonal demand patterns (higher in Q4, lower in Q1), day-of-week effects, and holiday impacts")

doc.add_heading("3.2 Data Tables", level=2)

doc.add_paragraph(
    "The data generator (src/data_generator.py) produces three internally consistent tables:"
)

add_table(
    ["Table", "Records", "Granularity", "Description"],
    [
        ["Daily Sales & Inventory", "2,700", "1 row per SKU per day",
         "Observed sales, on-hand inventory, stockout flag, open PO quantity, days until delivery"],
        ["Purchase Orders", "92", "1 row per PO",
         "Order date, promised date, actual date, ERP update date, quantity, delay flag and days"],
        ["Supplier Notes", "58", "1 row per note",
         "Free-text note from supplier, associated PO, note type (delay_warning or routine)"],
    ],
    col_widths=[3.5, 1.5, 3, 6]
)

doc.add_paragraph(
    "These tables are linked: each purchase order references a supplier and SKU, each supplier note "
    "references a specific PO, and the daily sales table reflects the impact of PO arrivals (inventory "
    "replenishment) and delays (demand decay, stockouts)."
)

doc.add_heading("3.3 Products & Suppliers", level=2)

add_table(
    ["SKU ID", "Product Name", "Supplier", "Base Demand/Day", "Base Lead Time (days)"],
    [
        ["SKU01", "Widget Alpha", "SUP01 (Apex Components)", "45 units", "10"],
        ["SKU02", "Widget Beta", "SUP02 (Nordic Metals)", "30 units", "14"],
        ["SKU03", "Gadget Pro", "SUP03 (Delta Plastics)", "55 units", "7"],
        ["SKU04", "Gadget Lite", "SUP04 (Precision Parts)", "20 units", "18"],
        ["SKU05", "Component Z", "SUP01 (Apex Components)", "38 units", "12"],
    ],
    col_widths=[1.8, 2.5, 4, 2.5, 2.5]
)

doc.add_paragraph(
    "Supplier reliability determines how often purchase orders are delayed. Lower reliability means more "
    "delays, which generates more supplier warning notes and more opportunities for the LLM extraction "
    "to add value:"
)

add_table(
    ["Supplier ID", "Supplier Name", "Reliability", "Interpretation"],
    [
        ["SUP01", "Apex Components", "45%", "55% of POs are delayed"],
        ["SUP02", "Nordic Metals", "35%", "65% of POs are delayed (least reliable)"],
        ["SUP03", "Delta Plastics", "55%", "45% of POs are delayed (most reliable)"],
        ["SUP04", "Precision Parts", "40%", "60% of POs are delayed"],
    ],
    col_widths=[2, 3, 2, 6]
)

doc.add_heading("3.4 Key Temporal Relationship", level=2)

doc.add_paragraph(
    "For every delayed purchase order, the following events occur in strict chronological order:"
)

add_rich_para([
    ("order_date", True, False, EXL_BLUE, 11),
    (" → ", False, False, None, 11),
    ("note_date", True, False, RGBColor(0x27,0xAE,0x60), 11),
    (" → ", False, False, None, 11),
    ("erp_update_date", True, False, EXL_ORANGE, 11),
    (" → ", False, False, None, 11),
    ("promised_date", True, False, EXL_GRAY, 11),
    (" → ", False, False, None, 11),
    ("actual_date", True, False, EXL_SLATE, 11),
], space_after=6)

doc.add_paragraph(
    "The note arrives shortly after the order (between 1/3 and 1/2 of the lead time after order_date). "
    "The ERP system is updated 5–12 days after the note. This gap is where the note provides "
    "intelligence that the ERP does not yet have."
)

doc.add_paragraph(
    "This temporal structure is critical because it means the features derived from supplier notes "
    "(early_delay_flag, expected_delay_days) contain genuinely forward-looking information. They are not "
    "redundant with ERP features — they provide a signal that does not exist anywhere in the structured data "
    "during the note-to-ERP-update window."
)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════
# 4. SOLUTION ARCHITECTURE
# ════════════════════════════════════════════════════════════════

doc.add_heading("4. Solution Architecture", level=1)

doc.add_paragraph(
    "The solution follows a modular pipeline architecture with four stages:"
)

add_rich_para([
    ("Stage 1 — Data Generation: ", True, False, EXL_ORANGE, 11),
    ("The data generator (src/data_generator.py) simulates 18 months of internally consistent "
     "supply chain data: daily sales/inventory, purchase orders, and supplier notes. All tables are "
     "linked through shared SKU and PO identifiers.", False, False, None, 11),
])

add_rich_para([
    ("Stage 2 — LLM Extraction: ", True, False, EXL_ORANGE, 11),
    ("The extraction module (src/llm_extractor.py) sends each supplier note to GPT-4o via the "
     "OpenRouter API. The model extracts three structured fields: early_delay_flag (binary), "
     "expected_delay_days (integer), and delay_reason (text). Each extraction is tagged with "
     "a timestamp and model version for lineage.", False, False, None, 11),
])

add_rich_para([
    ("Stage 3 — Feature Store: ", True, False, EXL_ORANGE, 11),
    ("ERP features (15) and note-derived features (2 used in model, 1 tracked) are merged into a "
     "unified feature store. The store is saved as Apache Parquet with a companion CSV file tracking "
     "lineage metadata (source, timestamps, freshness status) for every feature.", False, False, None, 11),
])

add_rich_para([
    ("Stage 4 — Model Training & Evaluation: ", True, False, EXL_ORANGE, 11),
    ("Two XGBoost regression models are trained with identical hyperparameters on a chronological "
     "80/20 split. The baseline model uses only ERP features. The enhanced model uses ERP + note features. "
     "The difference in MAPE quantifies the value of the LLM-extracted signals.", False, False, None, 11),
])

doc.add_paragraph(
    "All four stages run sequentially in a single Jupyter notebook (notebooks/main.ipynb). "
    "The notebook can be executed end-to-end with Run All — no manual intervention is required between stages."
)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════
# 5. LLM EXTRACTION PIPELINE
# ════════════════════════════════════════════════════════════════

doc.add_heading("5. LLM Extraction Pipeline", level=1)

doc.add_heading("5.1 Architecture & Model", level=2)

doc.add_paragraph(
    "The extraction pipeline uses GPT-4o (accessed via the OpenRouter API, which provides an "
    "OpenAI-compatible interface). OpenRouter was chosen because it allows access to multiple LLM "
    "providers through a single API, making it easy to switch models if needed."
)

doc.add_paragraph(
    "The API configuration is managed in config/settings.py, which reads the API key from a .env file. "
    "This separation ensures sensitive credentials are never committed to version control."
)

doc.add_paragraph(
    "The extraction function (src/llm_extractor.py) processes notes in batch. For each note, it sends "
    "a system prompt instructing the model to extract structured fields, along with the note text as "
    "the user message. The model is instructed to return a JSON object matching the extraction schema."
)

doc.add_heading("5.2 Extraction Schema", level=2)

doc.add_paragraph(
    "Each note is processed to extract three fields:"
)

add_table(
    ["Field", "Type", "Range", "Description"],
    [
        ["early_delay_flag", "Integer", "0 or 1",
         "Binary indicator: 1 if the note warns of an upcoming delay, 0 if the note is routine or positive"],
        ["expected_delay_days", "Integer", "0–30",
         "The number of days the supplier expects the shipment to be delayed. 0 if no delay."],
        ["delay_reason", "String", "Free text",
         "A brief description of the cause of the delay (e.g., 'port congestion', 'raw material shortage'). "
         "Empty string if no delay."],
    ],
    col_widths=[3, 1.5, 1.5, 7.5]
)

doc.add_paragraph(
    "The extraction schema is defined in config/settings.py as EXTRACTION_SCHEMA. The LLM is given this "
    "schema in its system prompt so it knows exactly what format to return."
)

doc.add_heading("5.3 Extraction Results & Lineage", level=2)

doc.add_paragraph(
    "When running with USE_LLM = True, the pipeline processed all 58 supplier notes:"
)

add_bullet("48 notes correctly identified as delay warnings (early_delay_flag = 1)")
add_bullet("10 notes correctly identified as routine check-ins (early_delay_flag = 0)")
add_bullet("The expected_delay_days values closely matched the actual delay days in the purchase orders")

doc.add_paragraph(
    "Every extraction is tagged with lineage metadata to ensure traceability:"
)

add_table(
    ["Metadata Field", "Value", "Purpose"],
    [
        ["extraction_timestamp", "ISO 8601 datetime", "When the extraction was performed — for freshness tracking"],
        ["model_version", "openai/gpt-4o", "Which LLM produced this extraction — for reproducibility"],
        ["source", "llm_extraction", "Distinguishes LLM results from ground-truth fallback"],
    ],
    col_widths=[3.5, 3, 7]
)

doc.add_paragraph(
    "This lineage is critical for production systems. If a model degrades, the lineage allows "
    "engineers to trace back to which LLM version produced the features, when they were extracted, "
    "and whether the extraction pipeline needs updating."
)

doc.add_heading("5.4 Error Handling & Fallback", level=2)

doc.add_paragraph(
    "If the LLM API is unavailable (network issue, invalid key, rate limiting), the extraction function "
    "defaults to safe values: early_delay_flag = 0, expected_delay_days = 0, delay_reason = empty string. "
    "This ensures the pipeline never crashes due to an LLM failure — it gracefully degrades to ERP-only features."
)

doc.add_paragraph(
    "A ground-truth extraction function (generate_ground_truth_extractions) is also available as a "
    "development fallback. When USE_LLM = False, this function creates extraction results directly from "
    "the known PO delay data, allowing the entire notebook to run without an API key."
)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════
# 6. FEATURE ENGINEERING
# ════════════════════════════════════════════════════════════════

doc.add_heading("6. Feature Engineering", level=1)

doc.add_paragraph(
    "Feature engineering transforms raw data into model-ready inputs. The project uses 18 features total "
    "(15 ERP + 3 note-derived), of which 17 are used in the model. Each feature is carefully designed to "
    "avoid data leakage — no feature uses information that would not be available at prediction time."
)

doc.add_heading("6.1 ERP Features (15)", level=2)

doc.add_paragraph("These features come from the structured ERP data and are available for both the baseline and enhanced models:")

add_rich_para([("Demand History (5 features)", True, False, EXL_BLUE, 12)])

add_table(
    ["Feature", "Calculation", "Why It Matters"],
    [
        ["sales_lag_1", "Sales from 1 day ago", "Most recent demand signal; captures day-to-day trends"],
        ["sales_lag_7", "Sales from 7 days ago", "Same-weekday comparison; captures weekly patterns"],
        ["sales_lag_28", "Sales from 28 days ago", "Same-weekday-of-month; captures monthly patterns"],
        ["rolling_avg_7", "7-day rolling average (shifted 1 day)", "Smoothed short-term demand trend"],
        ["rolling_avg_28", "28-day rolling average (shifted 1 day)", "Smoothed long-term demand baseline"],
    ],
    col_widths=[2.5, 4.5, 6.5]
)

doc.add_paragraph(
    "All lag features are shifted to prevent leakage. For example, sales_lag_1 uses yesterday's sales, "
    "not today's. Rolling averages are shifted by 1 day so they only include data available before "
    "the prediction point."
)

add_rich_para([("Inventory & Supply (5 features)", True, False, EXL_BLUE, 12)])

add_table(
    ["Feature", "Calculation", "Why It Matters"],
    [
        ["on_hand_inventory", "Current physical stock in warehouse",
         "Direct constraint on sales — can't sell what you don't have"],
        ["available_inventory", "on_hand_inventory + open_po_qty",
         "Total supply picture including incoming orders"],
        ["stockout_flag", "1 if inventory = 0, else 0",
         "Binary signal that demand is being suppressed by lack of stock"],
        ["inventory_cover", "on_hand_inventory / rolling_avg_7",
         "Days of stock remaining at current demand rate — measures urgency"],
        ["open_po_qty", "Quantity in open (not yet received) POs",
         "Incoming supply that will replenish inventory"],
    ],
    col_widths=[2.5, 4.5, 6.5]
)

add_rich_para([("Supply Chain Timing (3 features)", True, False, EXL_BLUE, 12)])

add_table(
    ["Feature", "Calculation", "Why It Matters"],
    [
        ["days_until_expected_delivery", "Promised date minus current date",
         "How soon inventory replenishment is expected"],
        ["historical_avg_supplier_delay", "Running average of past delay days for this supplier (merge_asof)",
         "Supplier track record — a supplier that is usually late will likely be late again"],
        ["open_po_qty", "(Also listed above)", "Bridges supply and timing"],
    ],
    col_widths=[3.5, 5, 5]
)

doc.add_paragraph(
    "The historical_avg_supplier_delay is computed using merge_asof, which ensures that for each date, "
    "only past completed POs are used. This prevents future information from leaking into the feature."
)

add_rich_para([("Calendar Features (3 features)", True, False, EXL_BLUE, 12)])

add_table(
    ["Feature", "Values", "Why It Matters"],
    [
        ["day_of_week", "0 (Monday) to 6 (Sunday)", "Demand varies by weekday — weekends are typically lower"],
        ["month", "1 to 12", "Captures seasonal patterns — Q4 demand spike, Q1 slowdown"],
        ["holiday", "0 or 1", "US public holidays have sharply reduced demand (0.3x multiplier)"],
    ],
    col_widths=[2.5, 4, 7]
)

doc.add_heading("6.2 Note-Derived Features", level=2)

doc.add_paragraph(
    "These features come from the LLM extraction of supplier notes. They are the key differentiator "
    "between the baseline and enhanced models."
)

add_table(
    ["Feature", "Source", "Active Window", "Used in Model?"],
    [
        ["early_delay_flag", "LLM extraction from supplier note",
         "Between note_date and PO actual_date", "Yes — most important feature"],
        ["expected_delay_days", "LLM extraction from supplier note",
         "Between note_date and PO actual_date", "Yes"],
        ["delay_reason", "LLM extraction from supplier note",
         "Between note_date and PO actual_date",
         "No — excluded due to high variability"],
    ],
    col_widths=[3, 3.5, 3.5, 3.5]
)

add_rich_para([
    ("Why early_delay_flag is powerful: ", True, False, EXL_ORANGE, 11),
    ("This feature flips to 1 the moment a supplier note warns of a delay — days before the ERP system "
     "is updated. During this window, it is the only signal in the entire feature set that knows a delay "
     "is coming. The model learns to associate this flag with the demand decay that follows supplier delays "
     "(customers find alternatives, internal allocation changes). This is why it became the #1 most "
     "important feature.", False, False, None, 11),
])

add_rich_para([
    ("Why delay_reason was excluded: ", True, False, EXL_ORANGE, 11),
    ("The delay_reason field is a free-text string produced by the LLM. While semantically meaningful, "
     "its exact wording varies across extraction runs — the LLM might say 'port congestion' in one run "
     "and 'congestion at port' in another. When label-encoded, this creates unstable numeric values that "
     "add noise rather than signal. The PSI drift analysis confirmed this with a score of 1.06 "
     "(extreme drift), validating the decision to exclude it.", False, False, None, 11),
])

doc.add_heading("6.3 Target Variable", level=2)

doc.add_paragraph(
    "The prediction target is target_next_day_sales — the observed sales on the following day. "
    "This is computed by shifting the sales column by -1 (i.e., tomorrow's sales become today's target)."
)

doc.add_paragraph(
    "It is important to note that observed sales is a proxy for demand, not true demand itself. When "
    "inventory is sufficient, observed sales equals true demand. During stockouts, observed sales "
    "underestimates true demand because customers who wanted to buy could not. This is a known limitation "
    "and is common in real-world demand forecasting."
)

doc.add_heading("6.4 Data Leakage Prevention", level=2)

doc.add_paragraph(
    "Data leakage occurs when a model has access to information during training that would not be available "
    "at prediction time. This is a critical concern in time-series forecasting. The project implements "
    "five safeguards:"
)

add_table(
    ["Leakage Risk", "Safeguard", "Implementation"],
    [
        ["Using future sales data", "Feature lag shifting",
         "All lag features use past data only (1, 7, 28 days ago). Rolling averages are shifted by 1 additional day."],
        ["Test set contamination", "Chronological split",
         "The data is split by date — first 80% of dates for training, last 20% for testing. No random shuffling."],
        ["Note signals before they exist", "Temporal windowing",
         "Note-derived features (early_delay_flag, expected_delay_days) are only active between note_date and PO arrival. Before the note date, these features are 0."],
        ["ERP delay before formal update", "Date gating",
         "The erp_expected_delay_days field is only populated after erp_update_date. Before that date, it reads 0."],
        ["Future supplier performance", "merge_asof",
         "historical_avg_supplier_delay uses only completed POs with actual_date before the current date. It never looks ahead."],
    ],
    col_widths=[2.5, 2.5, 8.5]
)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════
# 7. FEATURE STORE
# ════════════════════════════════════════════════════════════════

doc.add_heading("7. Feature Store", level=1)

doc.add_paragraph(
    "A feature store is a centralized repository for storing, managing, and serving features for "
    "machine learning models. It bridges the gap between data engineering and model training by providing "
    "a single source of truth for features with metadata, versioning, and freshness tracking."
)

doc.add_heading("7.1 Storage Format", level=2)

doc.add_paragraph(
    "The feature store uses Apache Parquet as its storage format:"
)

add_bullet("Columnar format — reads only the columns needed, not entire rows")
add_bullet("Compressed — significantly smaller than CSV for numeric data")
add_bullet("Type-preserving — integers stay integers, dates stay dates (unlike CSV where everything is text)")
add_bullet("Widely supported — pandas, Spark, Polars, and cloud services all read Parquet natively")

doc.add_paragraph(
    "The feature store is saved to data/feature_store.parquet. It contains one row per SKU per date "
    "with all 18 features and the target variable."
)

doc.add_heading("7.2 Lineage Metadata", level=2)

doc.add_paragraph(
    "Every feature in the store is documented with lineage metadata, saved to data/feature_lineage.csv. "
    "This tracks the provenance and freshness of each feature:"
)

add_table(
    ["Metadata Field", "Example Value", "Purpose"],
    [
        ["feature_name", "early_delay_flag", "Unique identifier for the feature"],
        ["source", "supplier_note", "Origin category: erp, calendar, or supplier_note"],
        ["description", "Binary flag from LLM extraction...", "Human-readable explanation of what the feature represents"],
        ["source_timestamp", "2025-06-24T10:30:00", "When the underlying data was last updated"],
        ["created_timestamp", "2025-06-24T10:30:05", "When the feature was computed from the source data"],
        ["freshness_status", "fresh", "Whether the feature is within SLA (fresh) or overdue (stale)"],
    ],
    col_widths=[3, 3.5, 7]
)

doc.add_paragraph(
    "Lineage is essential for debugging and auditing. If a model's predictions suddenly degrade, "
    "the lineage allows engineers to check: Which features changed? When were they last updated? "
    "Were any features stale when the prediction was made?"
)

doc.add_heading("7.3 Freshness SLA", level=2)

doc.add_paragraph(
    "The freshness Service Level Agreement (SLA) is set to 24 hours (configured in config/settings.py "
    "as FRESHNESS_SLA_HOURS = 24). This means:"
)

add_bullet("A feature is considered fresh if its source_timestamp is within the last 24 hours")
add_bullet("A feature is stale if its source_timestamp is older than 24 hours")
add_bullet("In production, stale features would trigger an alert before any predictions are served")

doc.add_paragraph(
    "The 24-hour threshold was chosen because the forecast runs daily (predicting next-day sales). "
    "Features older than 24 hours mean the model is making predictions with outdated information."
)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════
# 8. MODEL TRAINING & EVALUATION
# ════════════════════════════════════════════════════════════════

doc.add_heading("8. Model Training & Evaluation", level=1)

doc.add_heading("8.1 Model Selection — XGBoost", level=2)

doc.add_paragraph(
    "XGBoost (eXtreme Gradient Boosting) is a gradient-boosted decision tree algorithm widely used in "
    "tabular data competitions and production ML systems. It was chosen for this project for several reasons:"
)

add_bullet("Handles mixed feature types (continuous, binary, categorical) without preprocessing")
add_bullet("Captures non-linear relationships and feature interactions automatically")
add_bullet("Provides built-in feature importance scores for interpretability")
add_bullet("Fast training on tabular data — well suited for iterative experimentation")

doc.add_paragraph("The model hyperparameters were kept identical for both models to ensure a fair comparison:")

add_table(
    ["Hyperparameter", "Value", "Meaning"],
    [
        ["n_estimators", "200", "Number of boosting rounds (trees)"],
        ["max_depth", "5", "Maximum depth of each tree — controls complexity"],
        ["learning_rate", "0.1", "Step size for each boosting round — lower = more conservative"],
        ["random_state", "42", "Seed for reproducibility"],
    ],
    col_widths=[3, 2, 8.5]
)

doc.add_paragraph(
    "No hyperparameter tuning (e.g., GridSearchCV, Optuna) was performed. This was a deliberate decision: "
    "the goal is to measure the marginal value of adding note features, not to achieve the lowest possible "
    "MAPE. Using the same hyperparameters for both models ensures that any difference in accuracy comes "
    "purely from the additional features, not from tuning differences."
)

doc.add_heading("8.2 Data Splitting Strategy", level=2)

doc.add_paragraph(
    "The data is split chronologically — the first 80% of dates form the training set (~14 months), "
    "and the last 20% form the test set (~4 months). This is critical for time-series data:"
)

add_bullet("Random splitting would leak future patterns into training — a model trained on December data "
           "should not be tested on October data")
add_bullet("Chronological splitting simulates real deployment: the model is always predicting the future "
           "based on the past")
add_bullet("It also tests whether the model generalizes to a time period it has never seen, which is "
           "a harder and more realistic evaluation")

doc.add_heading("8.3 Results", level=2)

add_table(
    ["Metric", "Baseline (ERP only)", "Enhanced (ERP + Notes)", "Change"],
    [
        ["MAPE", "25.01%", "23.36%", "-6.6% (improved)"],
        ["MAE", "5.03 units", "4.55 units", "-9.5% (improved)"],
        ["RMSE", "6.80 units", "6.35 units", "-6.6% (improved)"],
    ],
    col_widths=[2.5, 3.5, 3.5, 3.5]
)

add_rich_para([
    ("MAPE (Mean Absolute Percentage Error) ", True, False, EXL_BLUE, 11),
    ("measures the average percentage by which predictions deviate from actuals. A MAPE of 25% means "
     "the baseline model's predictions are off by about 25% on average. The enhanced model reduces this "
     "to 23.36%.", False, False, None, 11),
])

add_rich_para([
    ("MAE (Mean Absolute Error) ", True, False, EXL_BLUE, 11),
    ("measures the average absolute difference in units. The enhanced model is off by 4.55 units on "
     "average, compared to 5.03 units for the baseline — a 9.5% improvement.", False, False, None, 11),
])

add_rich_para([
    ("RMSE (Root Mean Squared Error) ", True, False, EXL_BLUE, 11),
    ("penalizes large errors more heavily than MAE. The improvement here (6.80 → 6.35) indicates that "
     "the enhanced model not only has lower average error but also fewer extreme mispredictions.", False, False, None, 11),
])

add_callout(
    "All three metrics improve consistently, confirming the hypothesis: LLM-extracted supplier delay "
    "signals provide genuine predictive value that ERP features alone cannot capture.",
    bg_color="E8F5E9"
)

doc.add_heading("8.4 Feature Importance Analysis", level=2)

doc.add_paragraph(
    "XGBoost provides feature importance scores based on how frequently and effectively each feature is "
    "used across all trees. The top 5 features in the enhanced model:"
)

add_table(
    ["Rank", "Feature", "Source", "Interpretation"],
    [
        ["1", "early_delay_flag", "Supplier Note (LLM)",
         "The most impactful signal — binary indicator of an incoming delay, available before the ERP knows"],
        ["2", "sales_lag_1", "ERP",
         "Yesterday's sales — strongest short-term demand predictor"],
        ["3", "rolling_avg_7", "ERP",
         "Smoothed 7-day demand trend — captures recent demand momentum"],
        ["4", "on_hand_inventory", "ERP",
         "Current stock level — directly constrains achievable sales"],
        ["5", "inventory_cover", "ERP",
         "Days of stock remaining — urgency metric combining inventory and demand"],
    ],
    col_widths=[1, 3, 3, 6.5]
)

doc.add_paragraph(
    "The fact that early_delay_flag — a feature derived entirely from unstructured supplier notes via "
    "LLM extraction — ranks as the single most important feature is the strongest possible validation of "
    "the project's hypothesis. The model is not just marginally using the note signals; it relies on them "
    "more than any other feature."
)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════
# 9. DRIFT DETECTION
# ════════════════════════════════════════════════════════════════

doc.add_heading("9. Drift Detection & Monitoring", level=1)

doc.add_paragraph(
    "In production ML systems, the statistical properties of features can change over time — a phenomenon "
    "called feature drift. If the distribution of a feature in production diverges significantly from what "
    "the model saw during training, the model's predictions may degrade. Drift detection provides an early "
    "warning system."
)

doc.add_heading("9.1 Population Stability Index (PSI)", level=2)

doc.add_paragraph(
    "PSI measures how much a feature's distribution has shifted between two time periods (typically "
    "training vs. production/test). It is calculated by:"
)

add_bullet("Dividing the feature values into bins (typically 10 equal-width bins)")
add_bullet("Computing the proportion of values in each bin for both the training and test periods")
add_bullet("Summing the divergence across bins using the formula: PSI = Σ (Actual% - Expected%) × ln(Actual% / Expected%)")

doc.add_paragraph("The industry-standard thresholds for interpreting PSI are:")

add_table(
    ["PSI Range", "Interpretation", "Action"],
    [
        ["< 0.1", "Stable — no significant drift", "No action needed"],
        ["0.1 – 0.2", "Moderate drift — monitor closely", "Investigate if performance degrades"],
        ["≥ 0.2", "Significant drift — distribution has shifted materially", "Consider retraining the model"],
    ],
    col_widths=[2, 5, 6.5]
)

doc.add_heading("9.2 Characteristic Stability Index (CSI)", level=2)

doc.add_paragraph(
    "CSI is the per-bin breakdown of PSI. While PSI gives a single number summarizing overall drift, "
    "CSI shows which specific regions of the distribution have shifted. For example, a feature might "
    "have stable behavior in its normal range but show drift in its extreme values. CSI reveals this "
    "granularity."
)

doc.add_paragraph(
    "The implementation (src/drift.py) provides both calculate_psi_for_features() for the summary "
    "score and calculate_csi() for the per-bin breakdown."
)

doc.add_heading("9.3 Drift Results & Interpretation", level=2)

add_table(
    ["Feature", "PSI Score", "Status", "Interpretation"],
    [
        ["sales_lag_1", "0.03", "Stable",
         "Recent sales patterns are consistent between train and test periods"],
        ["on_hand_inventory", "0.01", "Stable",
         "Inventory levels have similar distribution across time"],
        ["early_delay_flag", "0.07", "Stable",
         "The key note feature is consistent — important for model reliability"],
        ["inventory_cover", "0.12", "Moderate",
         "Slight shift in how many days of stock are typically on hand"],
        ["rolling_avg_7", "0.24", "Significant",
         "7-day demand trend has shifted — seasonal effects between periods"],
        ["expected_delay_days", "0.63", "Significant",
         "Delay durations differ between early and late periods"],
        ["historical_avg_supplier_delay", "0.78", "Significant",
         "Cumulative average stabilizes over time — expected drift"],
        ["delay_reason_encoded", "1.06", "Significant",
         "Extreme drift — confirms decision to exclude from model"],
    ],
    col_widths=[3.5, 1.5, 2, 6.5]
)

doc.add_paragraph("Key takeaways from the drift analysis:")

add_bullet("early_delay_flag (PSI = 0.07) — The most important feature is also the most stable. "
           "This gives confidence that the enhanced model will perform consistently over time.", "Positive: ")
add_bullet("delay_reason_encoded (PSI = 1.06) — Extreme drift confirms the decision to exclude this "
           "feature from the model. The LLM produces different text descriptions across runs, making "
           "label-encoded values unreliable.", "Validated: ")
add_bullet("historical_avg_supplier_delay (PSI = 0.78) — This drifts because it is a cumulative "
           "running average. In the early training period, the average is volatile (few data points). "
           "By the test period, it stabilizes. This is expected behavior, not a problem.", "Expected: ")
add_bullet("In a production deployment, any feature crossing PSI > 0.2 would trigger an automated "
           "alert, prompting the team to investigate and potentially retrain the model.", "Production: ")

doc.add_page_break()

# ════════════════════════════════════════════════════════════════
# 10. TECHNOLOGY STACK
# ════════════════════════════════════════════════════════════════

doc.add_heading("10. Technology Stack", level=1)

add_table(
    ["Component", "Technology", "Role in Project"],
    [
        ["Programming Language", "Python 3.12", "All data processing, modeling, and analysis"],
        ["Notebook", "Jupyter (VS Code)", "Single end-to-end executable notebook"],
        ["ML Framework", "XGBoost", "Gradient-boosted regression for demand forecasting"],
        ["LLM", "GPT-4o via OpenRouter", "Extracting structured signals from unstructured notes"],
        ["Feature Store", "Apache Parquet", "Columnar storage for feature data with type preservation"],
        ["Drift Detection", "PSI/CSI (scipy)", "Monitoring feature distribution stability"],
        ["Data Processing", "pandas, numpy", "Data manipulation, feature engineering, aggregation"],
        ["Visualization", "matplotlib, seaborn", "Charts for feature importance, drift, and comparisons"],
        ["Version Control", "Git / GitHub", "Code versioning and collaboration"],
    ],
    col_widths=[3, 3, 7.5]
)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════
# 11. PROJECT STRUCTURE & HOW TO RUN
# ════════════════════════════════════════════════════════════════

doc.add_heading("11. Project Structure & How to Run", level=1)

doc.add_heading("11.1 Repository Structure", level=2)

p = doc.add_paragraph()
run = p.add_run(
    "DemandSignalFeatureStore/\n"
    "├── notebooks/\n"
    "│   └── main.ipynb            # Single end-to-end notebook\n"
    "├── src/\n"
    "│   ├── data_generator.py     # Synthetic data simulation\n"
    "│   ├── llm_extractor.py      # LLM extraction via OpenRouter\n"
    "│   └── drift.py              # PSI/CSI drift detection\n"
    "├── config/\n"
    "│   └── settings.py           # API keys, model config, SLA\n"
    "├── data/                     # Generated at runtime (not in git)\n"
    "├── .env.example              # Template for API key\n"
    "├── requirements.txt          # Python dependencies\n"
    "├── README.md                 # Setup instructions\n"
    "└── DOCUMENTATION.md          # Technical documentation (markdown)"
)
run.font.name = "Consolas"
run.font.size = Pt(10)
run.font.color.rgb = EXL_SLATE

doc.add_heading("11.2 How to Run", level=2)

doc.add_paragraph("Follow these steps to run the project from scratch:")

add_rich_para([("Step 1: Clone the repository", True, False, EXL_ORANGE, 11)])
p = doc.add_paragraph()
run = p.add_run("git clone https://github.com/damie17/DemandSignalFeatureStore.git\ncd DemandSignalFeatureStore")
run.font.name = "Consolas"
run.font.size = Pt(10)

add_rich_para([("Step 2: Install Jupyter kernel (if not already available)", True, False, EXL_ORANGE, 11)])
p = doc.add_paragraph()
run = p.add_run("pip install ipykernel")
run.font.name = "Consolas"
run.font.size = Pt(10)

add_rich_para([("Step 3: Configure the API key", True, False, EXL_ORANGE, 11)])
p = doc.add_paragraph()
run = p.add_run("cp .env.example .env\n# Edit .env and replace the placeholder with your OpenRouter API key")
run.font.name = "Consolas"
run.font.size = Pt(10)

add_rich_para([("Step 4: Open and run the notebook", True, False, EXL_ORANGE, 11)])
doc.add_paragraph(
    "Open notebooks/main.ipynb in VS Code and click Run All. The first cell installs all dependencies "
    "from requirements.txt and creates the data/ directory automatically."
)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════
# 12. KEY DECISIONS
# ════════════════════════════════════════════════════════════════

doc.add_heading("12. Key Decisions & Trade-offs", level=1)

add_table(
    ["Decision", "Rationale", "Trade-off"],
    [
        ["Excluded delay_reason from model",
         "LLM text output is too variable across runs — PSI = 1.06 confirmed extreme drift in the encoded values",
         "We lose the semantic richness of the reason but gain model stability"],
        ["XGBoost over linear regression",
         "Supply chain data has non-linear relationships and feature interactions that linear models cannot capture",
         "Less interpretable than linear regression, but feature importance partially compensates"],
        ["No hyperparameter tuning",
         "The goal is to measure the marginal value of note features, not to minimize MAPE. Same params ensure fair comparison",
         "MAPE could likely be improved further with tuning — this is listed as a future improvement"],
        ["Synthetic data only",
         "Demonstrates the full pipeline without exposing sensitive business data. Makes the project fully reproducible",
         "Results may differ on real-world data with more complex supplier patterns"],
        ["24-hour freshness SLA",
         "Matches the daily forecast cadence — features older than 1 day are outdated for next-day prediction",
         "Higher-frequency forecasts would need a tighter SLA (e.g., 1 hour)"],
        ["Chronological split over cross-validation",
         "Time-series data must be split in order to prevent future leakage. K-fold would mix time periods",
         "Only one train/test split rather than K, but it is the correct methodology for time-series"],
    ],
    col_widths=[3, 5, 5.5]
)

doc.add_page_break()

# ════════════════════════════════════════════════════════════════
# 13. FUTURE IMPROVEMENTS
# ════════════════════════════════════════════════════════════════

doc.add_heading("13. Future Improvements", level=1)

doc.add_paragraph(
    "While the project successfully demonstrates the value of LLM-extracted features, several "
    "enhancements could be made for a production deployment:"
)

add_rich_para([("Hyperparameter Tuning", True, False, EXL_ORANGE, 12)])
doc.add_paragraph(
    "Using GridSearchCV or Optuna to optimize XGBoost's hyperparameters (n_estimators, max_depth, "
    "learning_rate, min_child_weight, subsample) could reduce MAPE further. This was intentionally "
    "skipped to keep the comparison fair, but would be essential in production."
)

add_rich_para([("Weekly/Monthly Aggregation", True, False, EXL_ORANGE, 12)])
doc.add_paragraph(
    "Predicting daily sales is inherently noisy. Aggregating to weekly or monthly granularity "
    "smooths out day-to-day variance and typically yields lower MAPE. Many business decisions "
    "(inventory planning, purchasing) operate at weekly or monthly cadence."
)

add_rich_para([("Real-Time Extraction", True, False, EXL_ORANGE, 12)])
doc.add_paragraph(
    "Currently, extraction runs in batch within the notebook. A production system would use streaming "
    "extraction — processing supplier notes as they arrive in real time and updating the feature store "
    "immediately."
)

add_rich_para([("Automated Retraining", True, False, EXL_ORANGE, 12)])
doc.add_paragraph(
    "The PSI drift detection currently runs as a diagnostic. In production, features crossing the "
    "PSI > 0.2 threshold would automatically trigger a model retraining pipeline, ensuring the model "
    "adapts to changing data distributions."
)

add_rich_para([("Cloud Deployment", True, False, EXL_ORANGE, 12)])
doc.add_paragraph(
    "The feature store could be deployed on Azure Blob Storage with Azure ML serving the model. "
    "This would enable scheduled daily forecasts, API-based predictions, and integration with "
    "existing ERP/procurement systems."
)

add_rich_para([("Multi-Supplier Handling", True, False, EXL_ORANGE, 12)])
doc.add_paragraph(
    "The current simulation assigns one supplier per SKU. In reality, companies often have multiple "
    "suppliers for the same product. Handling overlapping supplier delays and choosing the best "
    "supplier signal would add complexity but improve real-world applicability."
)

# ── Save ──
out_path = r"C:\Users\LKDJ\Documents\DemandSignalFeatureStore\DOCUMENTATION.docx"
doc.save(out_path)
print(f"Saved: {out_path}")
