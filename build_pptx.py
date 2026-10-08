"""Build the capstone pitch deck using the EXL 2023 template."""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

TEMPLATE = r"C:\Users\LKDJ\Downloads\EXL's Response to Niagara RFP_Strawman.pptx"

prs = Presentation(TEMPLATE)

# Delete all existing slides (keep only layouts/master)
while len(prs.slides) > 0:
    rId = prs.slides._sldIdLst[0].get(
        '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
    prs.part.drop_rel(rId)
    prs.slides._sldIdLst.remove(prs.slides._sldIdLst[0])

# ── EXL 2023 Palette ──
EXL_ORANGE    = RGBColor(0xFB, 0x4D, 0x0A)   # dk2 - primary brand
EXL_SLATE     = RGBColor(0x2E, 0x36, 0x43)   # accent1 - dark headers
EXL_GRAY      = RGBColor(0x6D, 0x72, 0x7B)   # accent2
EXL_BLUE      = RGBColor(0x00, 0x50, 0x71)   # accent3 - teal blue
EXL_MID_BLUE  = RGBColor(0x4D, 0x84, 0x9B)   # accent4
EXL_LIGHT_BG  = RGBColor(0xDC, 0xF3, 0xFA)   # accent5
EXL_PALE_BG   = RGBColor(0xE6, 0xF6, 0xFB)   # accent6
WHITE         = RGBColor(0xFF, 0xFF, 0xFF)
BLACK         = RGBColor(0x00, 0x00, 0x00)
DARK_GRAY     = RGBColor(0x33, 0x33, 0x33)
LIGHT_GRAY    = RGBColor(0xA0, 0xA0, 0xA0)
GREEN_OK      = RGBColor(0x27, 0xAE, 0x60)
RED_WARN      = RGBColor(0xE7, 0x4C, 0x3C)
YELLOW_MOD    = RGBColor(0xF3, 0x9C, 0x12)

# Layout indices
LY_COVER_ORANGE = 2     # "Cover title orange" - title + subtitle
LY_HEADER1      = 13    # "Header1" - content slides with title bar
LY_ONE_COL      = 16    # "One column layout" - title + body
LY_DIVIDER_BLUE = 7     # "Divider slate blue bkgrd"


def add_text(slide, left, top, width, height, text, size=18, bold=False,
             color=BLACK, alignment=PP_ALIGN.LEFT, font_name="Calibri"):
    txBox = slide.shapes.add_textbox(Inches(left), Inches(top),
                                      Inches(width), Inches(height))
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.font.name = font_name
    p.alignment = alignment
    return tf


def add_multiline(slide, left, top, width, height, lines, size=16,
                  color=BLACK, bold=False, spacing=Pt(4), font_name="Calibri"):
    txBox = slide.shapes.add_textbox(Inches(left), Inches(top),
                                      Inches(width), Inches(height))
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, (txt, bld, clr, sz) in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = txt
        p.font.size = Pt(sz) if sz else Pt(size)
        p.font.bold = bld if bld is not None else bold
        p.font.color.rgb = clr if clr else color
        p.font.name = font_name
        p.space_after = spacing
    return tf


def add_bullet_list(slide, left, top, width, height, items, size=16,
                    color=DARK_GRAY, spacing=Pt(4), bullet_color=None):
    txBox = slide.shapes.add_textbox(Inches(left), Inches(top),
                                      Inches(width), Inches(height))
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        if isinstance(item, tuple):
            txt, bld, clr = item
        else:
            txt, bld, clr = item, False, color
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = txt
        p.font.size = Pt(size)
        p.font.bold = bld
        p.font.color.rgb = clr
        p.font.name = "Calibri"
        p.space_after = spacing
        p.level = 0
    return tf


def add_table(slide, left, top, width, rows_data, col_widths=None,
              header_bg=EXL_SLATE, row1_bg=WHITE, row2_bg=EXL_PALE_BG,
              header_font_color=WHITE, body_font_color=BLACK):
    n_rows = len(rows_data)
    n_cols = len(rows_data[0])
    tbl_shape = slide.shapes.add_table(n_rows, n_cols,
                                        Inches(left), Inches(top),
                                        Inches(width), Inches(0.42 * n_rows))
    tbl = tbl_shape.table

    if col_widths:
        for i, w in enumerate(col_widths):
            tbl.columns[i].width = Inches(w)

    for r, row in enumerate(rows_data):
        for c, val in enumerate(row):
            cell = tbl.cell(r, c)
            cell.text = str(val)
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(13)
            p.font.name = "Calibri"
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            if r == 0:
                p.font.bold = True
                p.font.color.rgb = header_font_color
                cell.fill.solid()
                cell.fill.fore_color.rgb = header_bg
            else:
                p.font.color.rgb = body_font_color
                cell.fill.solid()
                cell.fill.fore_color.rgb = row1_bg if r % 2 == 1 else row2_bg
    return tbl_shape


def add_rounded_box(slide, left, top, width, height, text, fill_color,
                    font_color=WHITE, font_size=14, bold=True):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                    Inches(left), Inches(top),
                                    Inches(width), Inches(height))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    shape.line.fill.background()
    tf = shape.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = font_color
    p.font.name = "Calibri"
    p.alignment = PP_ALIGN.CENTER
    return shape


def make_content_slide(title_text, subtitle_text=None):
    sl = prs.slides.add_slide(prs.slide_layouts[LY_ONE_COL])
    # Set the title placeholder
    for ph in sl.placeholders:
        if ph.placeholder_format.idx == 0:
            ph.text = title_text
            for p in ph.text_frame.paragraphs:
                p.font.size = Pt(28)
                p.font.bold = True
                p.font.color.rgb = EXL_SLATE
                p.font.name = "Calibri"
        elif ph.placeholder_format.idx == 14:
            if subtitle_text:
                ph.text = subtitle_text
                for p in ph.text_frame.paragraphs:
                    p.font.size = Pt(14)
                    p.font.color.rgb = EXL_GRAY
                    p.font.name = "Calibri"
            else:
                ph.text = ""
    return sl


# ════════════════════════════════════════
# SLIDE 1 — Title (EXL Cover)
# ════════════════════════════════════════
sl = prs.slides.add_slide(prs.slide_layouts[LY_COVER_ORANGE])
for ph in sl.placeholders:
    if ph.placeholder_format.idx == 0:
        ph.text = "Demand Signal Feature Store"
        for p in ph.text_frame.paragraphs:
            p.font.size = Pt(40)
            p.font.bold = True
            p.font.name = "Calibri"
    elif ph.placeholder_format.idx == 1:
        ph.text = "Can LLM-extracted supplier signals improve demand forecasting?\nCapstone Project  |  AI Engineer Program"
        for p in ph.text_frame.paragraphs:
            p.font.size = Pt(20)
            p.font.name = "Calibri"

# ════════════════════════════════════════
# SLIDE 2 — The Problem
# ════════════════════════════════════════
sl = make_content_slide("The Problem")

add_bullet_list(sl, 0.6, 1.5, 11.5, 1.8, [
    ("ERP systems track structured data: orders, inventory, shipments", False, DARK_GRAY),
    ("Supplier delay warnings arrive as free-text notes — days before ERP is updated", True, EXL_ORANGE),
    ("That 5–12 day blind spot causes inaccurate forecasts and poor inventory decisions", False, DARK_GRAY),
], size=18, spacing=Pt(8))

add_text(sl, 2.0, 3.6, 9, 0.5, "The Timeline Gap — Where Value Is Hidden",
         size=18, bold=True, color=EXL_BLUE, alignment=PP_ALIGN.CENTER)

labels = [("Order Date", EXL_GRAY), ("Note Date", GREEN_OK),
          ("5–12 day GAP", EXL_ORANGE), ("ERP Update", RED_WARN),
          ("Promised Date", EXL_GRAY)]
for i, (lbl, clr) in enumerate(labels):
    x = 1.2 + i * 2.3
    add_rounded_box(sl, x, 4.3, 2.1, 0.6, lbl, clr,
                    font_color=WHITE, font_size=12)

add_text(sl, 1.5, 5.2, 10, 0.4,
         "The note knows about the delay BEFORE the ERP does — this is the core value proposition",
         size=14, bold=True, color=EXL_ORANGE, alignment=PP_ALIGN.CENTER)

# ════════════════════════════════════════
# SLIDE 3 — Hypothesis
# ════════════════════════════════════════
sl = make_content_slide("The Hypothesis")

add_rounded_box(sl, 1.0, 1.5, 11, 1.0,
                "Adding LLM-extracted supplier delay signals to structured ERP features\nwill reduce demand forecasting error (MAPE)",
                EXL_BLUE, WHITE, font_size=20, bold=True)

add_text(sl, 0.6, 3.0, 11, 0.5, "How we test it:", size=20, bold=True, color=EXL_SLATE)
add_bullet_list(sl, 0.6, 3.6, 11.5, 2.5, [
    ("Train two identical XGBoost models with the same hyperparameters", False, DARK_GRAY),
    ("Baseline: ERP features only (15 features)", True, EXL_GRAY),
    ("Enhanced: ERP + note-derived features (17 features)", True, EXL_ORANGE),
    ("Chronological train/test split (80/20) — no data leakage", False, DARK_GRAY),
], size=18, spacing=Pt(8))

# ════════════════════════════════════════
# SLIDE 4 — Architecture
# ════════════════════════════════════════
sl = make_content_slide("Solution Architecture")

# Left box - Notes
add_rounded_box(sl, 0.8, 1.6, 5.0, 1.1,
                "Supplier Notes (text)\nLLM Extraction via GPT-4o",
                EXL_ORANGE, WHITE, font_size=16)
# Right box - ERP
add_rounded_box(sl, 7.0, 1.6, 5.0, 1.1,
                "ERP System (structured)\nFeature Engineering",
                EXL_BLUE, WHITE, font_size=16)
# Center - Feature Store
add_rounded_box(sl, 3.0, 3.4, 7.0, 1.0,
                "Feature Store — Parquet + Lineage Metadata",
                EXL_SLATE, WHITE, font_size=16)
# Bottom - Model
add_rounded_box(sl, 3.0, 5.0, 7.0, 1.0,
                "XGBoost Regression → Next-Day Sales Forecast",
                EXL_MID_BLUE, WHITE, font_size=16)

# Arrows (simple text)
add_text(sl, 2.8, 2.8, 1, 0.5, "↓", size=28, color=EXL_GRAY, alignment=PP_ALIGN.CENTER)
add_text(sl, 9.0, 2.8, 1, 0.5, "↓", size=28, color=EXL_GRAY, alignment=PP_ALIGN.CENTER)
add_text(sl, 6.0, 4.4, 1, 0.5, "↓", size=28, color=EXL_GRAY, alignment=PP_ALIGN.CENTER)

# ════════════════════════════════════════
# SLIDE 5 — Data Overview
# ════════════════════════════════════════
sl = make_content_slide("Data Overview")

add_table(sl, 0.8, 1.4, 11.5, [
    ["Dataset", "Records", "Description"],
    ["Daily Sales & Inventory", "2,700", "5 SKUs × 540 days (18 months)"],
    ["Purchase Orders", "92", "4 suppliers, 35–55% reliability"],
    ["Supplier Notes", "58", "48 delay warnings + 10 routine check-ins"],
], col_widths=[3.5, 1.5, 6.5], header_bg=EXL_BLUE)

add_bullet_list(sl, 0.8, 3.6, 11.5, 2.5, [
    ("Synthetic data — simulates a retail/wholesale company", False, DARK_GRAY),
    ("5 products (SKUs) sourced from 4 suppliers", False, DARK_GRAY),
    ("Internally consistent: inventory, sales, POs, and notes all linked", False, DARK_GRAY),
    ("Time period: Jan 2024 — Jun 2025 (540 days)", False, DARK_GRAY),
], size=16, spacing=Pt(6))

# ════════════════════════════════════════
# SLIDE 6 — LLM Extraction
# ════════════════════════════════════════
sl = make_content_slide("LLM Extraction Pipeline")

add_text(sl, 0.6, 1.3, 5.5, 0.4, "Input (unstructured note):", size=16, bold=True, color=EXL_GRAY)
add_rounded_box(sl, 0.6, 1.8, 5.8, 1.2,
                '"Apex Components (SUP01) reports\nPO0012 may arrive 8 days late.\nCause: port congestion."',
                EXL_PALE_BG, DARK_GRAY, font_size=14, bold=False)

add_text(sl, 6.8, 1.3, 5.5, 0.4, "Output (structured JSON):", size=16, bold=True, color=EXL_ORANGE)
add_rounded_box(sl, 6.8, 1.8, 5.8, 1.2,
                'early_delay_flag: 1\nexpected_delay_days: 8\ndelay_reason: "port congestion"',
                EXL_SLATE, RGBColor(0x7F, 0xDB, 0xFF), font_size=14, bold=False)

add_text(sl, 5.8, 2.2, 1.2, 0.5, "→", size=36, bold=True, color=EXL_ORANGE, alignment=PP_ALIGN.CENTER)

add_text(sl, 0.6, 3.4, 11, 0.4, "Extraction Results", size=18, bold=True, color=EXL_SLATE)
add_bullet_list(sl, 0.6, 3.9, 11.5, 2.5, [
    ("Model: GPT-4o via OpenRouter (OpenAI-compatible API)", False, DARK_GRAY),
    ("58 notes processed → 48 delays correctly identified", True, EXL_BLUE),
    ("Each extraction includes lineage: timestamp, model version, source", False, DARK_GRAY),
    ("delay_reason extracted but excluded from model (too variable across LLM runs)", False, EXL_GRAY),
], size=16, spacing=Pt(6))

# ════════════════════════════════════════
# SLIDE 7 — Feature Store Design
# ════════════════════════════════════════
sl = make_content_slide("Feature Store Design")

add_table(sl, 0.6, 1.4, 8.5, [
    ["Category", "Count", "Examples"],
    ["ERP — Demand", "5", "sales_lag_1, rolling_avg_7, rolling_avg_28"],
    ["ERP — Inventory", "5", "on_hand_inventory, stockout_flag, inventory_cover"],
    ["ERP — Supply", "3", "open_po_qty, historical_avg_supplier_delay"],
    ["Calendar", "3", "day_of_week, month, holiday"],
    ["Note-Derived", "2*", "early_delay_flag, expected_delay_days"],
], col_widths=[2.5, 1.0, 5.0], header_bg=EXL_BLUE)

add_text(sl, 0.6, 4.3, 8.5, 0.3,
         "* delay_reason extracted & stored but excluded from model (LLM text too variable)",
         size=12, color=EXL_GRAY)

# Right side info boxes
add_rounded_box(sl, 9.5, 1.5, 3.2, 0.7, "Storage: Parquet", EXL_SLATE, WHITE, font_size=14)
add_rounded_box(sl, 9.5, 2.4, 3.2, 0.7, "Lineage: CSV metadata", EXL_BLUE, WHITE, font_size=14)
add_rounded_box(sl, 9.5, 3.3, 3.2, 0.7, "Freshness SLA: 24h", EXL_ORANGE, WHITE, font_size=14)
add_rounded_box(sl, 9.5, 4.2, 3.2, 0.7, "17 features in model", EXL_MID_BLUE, WHITE, font_size=14)

# ════════════════════════════════════════
# SLIDE 8 — Leakage Prevention
# ════════════════════════════════════════
sl = make_content_slide("Data Leakage Prevention")

add_table(sl, 0.6, 1.4, 12, [
    ["Risk", "Mitigation"],
    ["Future data in features", "All lag features shifted by 1+ days"],
    ["Future data in test set", "Chronological 80/20 split (no random shuffle)"],
    ["Note signals before note arrives", "Features only active between note_date and PO arrival"],
    ["ERP delay before it's known", "erp_expected_delay only populated after erp_update_date"],
    ["Future supplier performance", "merge_asof — only past completed POs used"],
], col_widths=[4.5, 7.5], header_bg=EXL_SLATE)

# ════════════════════════════════════════
# SLIDE 9 — Results (KEY SLIDE)
# ════════════════════════════════════════
sl = make_content_slide("Results")

add_table(sl, 1.5, 1.4, 10, [
    ["Metric", "Baseline (ERP only)", "Enhanced (ERP + Notes)", "Change"],
    ["MAPE", "25.01%", "23.36%", "-6.6%  ↓"],
    ["MAE", "5.03 units", "4.55 units", "-9.5%  ↓"],
    ["RMSE", "6.80 units", "6.35 units", "-6.6%  ↓"],
], col_widths=[2.0, 3.0, 3.0, 2.0], header_bg=EXL_ORANGE)

add_rounded_box(sl, 2.0, 3.6, 9.0, 0.9,
                "Hypothesis confirmed: LLM-extracted features reduce forecast error",
                GREEN_OK, WHITE, font_size=20, bold=True)

add_text(sl, 1.5, 4.8, 10, 0.5,
         "All three metrics improved with the same model & hyperparameters —\nimprovement comes purely from note-derived features",
         size=14, color=EXL_GRAY, alignment=PP_ALIGN.CENTER)

# ════════════════════════════════════════
# SLIDE 10 — Feature Importance
# ════════════════════════════════════════
sl = make_content_slide("Feature Importance — Enhanced Model")

add_text(sl, 0.6, 1.3, 10, 0.4, "Top 5 Features (sorted by importance)",
         size=18, bold=True, color=EXL_SLATE)

features_top5 = [
    ("1.  early_delay_flag", True, 10.0),
    ("2.  sales_lag_1", False, 7.5),
    ("3.  rolling_avg_7", False, 6.2),
    ("4.  on_hand_inventory", False, 5.0),
    ("5.  inventory_cover", False, 4.0),
]

for i, (feat, is_note, bw) in enumerate(features_top5):
    y = 2.0 + i * 0.75
    clr = EXL_ORANGE if is_note else EXL_SLATE
    label_clr = EXL_ORANGE if is_note else DARK_GRAY
    add_text(sl, 0.6, y, 3.5, 0.5, feat, size=16, bold=True, color=label_clr)
    bar = sl.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                               Inches(4.5), Inches(y + 0.05), Inches(bw * 0.78), Inches(0.4))
    bar.fill.solid()
    bar.fill.fore_color.rgb = clr
    bar.line.fill.background()

    if is_note:
        add_text(sl, 4.5 + bw * 0.78 + 0.2, y, 3, 0.5,
                 "← LLM-extracted", size=13, bold=True, color=EXL_ORANGE)

add_text(sl, 0.6, 5.8, 12, 0.5,
         "The LLM-extracted early_delay_flag is the #1 most important feature — "
         "the model genuinely learns from supplier notes",
         size=14, bold=True, color=EXL_BLUE)

# ════════════════════════════════════════
# SLIDE 11 — Drift Detection
# ════════════════════════════════════════
sl = make_content_slide("Drift Detection — PSI")

add_text(sl, 0.6, 1.2, 12, 0.4,
         "Population Stability Index compares feature distributions between train and test periods",
         size=14, color=EXL_GRAY)

add_table(sl, 0.6, 1.8, 12, [
    ["Status", "PSI Range", "Features"],
    ["Stable", "< 0.1", "sales_lag_1, on_hand_inventory, early_delay_flag"],
    ["Moderate Drift", "0.1 – 0.2", "inventory_cover"],
    ["Significant Drift", "> 0.2", "rolling_avg_7, expected_delay_days, historical_avg_supplier_delay"],
], col_widths=[2.5, 2.0, 7.5], header_bg=EXL_BLUE)

# Color-coded boxes for key insights
add_rounded_box(sl, 0.6, 4.0, 5.8, 0.6,
                "early_delay_flag (top feature) PSI = 0.07 — Stable",
                GREEN_OK, WHITE, font_size=14)
add_rounded_box(sl, 6.8, 4.0, 5.8, 0.6,
                "delay_reason_encoded PSI = 1.06 — Excluded from model",
                RED_WARN, WHITE, font_size=14)

add_bullet_list(sl, 0.6, 5.0, 12, 1.5, [
    ("The most impactful signal is also the most reliable across time periods", True, EXL_BLUE),
    ("In production: PSI > 0.2 triggers automated model retraining alerts", False, DARK_GRAY),
], size=16, spacing=Pt(6))

# ════════════════════════════════════════
# SLIDE 12 — Technology Stack
# ════════════════════════════════════════
sl = make_content_slide("Technology Stack")

add_table(sl, 2.0, 1.4, 9, [
    ["Layer", "Technology"],
    ["Language", "Python 3.12, Jupyter Notebook"],
    ["ML Model", "XGBoost Regressor"],
    ["LLM", "GPT-4o via OpenRouter"],
    ["Feature Store", "Apache Parquet + CSV lineage"],
    ["Drift Monitoring", "PSI / CSI (scipy)"],
    ["Data Processing", "pandas, numpy"],
    ["Visualization", "matplotlib, seaborn"],
    ["Version Control", "Git / GitHub"],
], col_widths=[3.0, 6.0], header_bg=EXL_SLATE)

add_rounded_box(sl, 3.0, 5.5, 7.0, 0.6,
                "Single Jupyter notebook — fully reproducible with Run All",
                EXL_BLUE, WHITE, font_size=16)

# ════════════════════════════════════════
# SLIDE 13 — Key Decisions
# ════════════════════════════════════════
sl = make_content_slide("Key Decisions & Trade-offs")

add_table(sl, 0.6, 1.4, 12, [
    ["Decision", "Rationale"],
    ["Excluded delay_reason from model", "LLM text output too variable — PSI = 1.06 confirmed drift"],
    ["XGBoost over linear regression", "Handles non-linear feature interactions in supply chain data"],
    ["No hyperparameter tuning", "Fair comparison: identical parameters for both models"],
    ["Synthetic data", "Demonstrates pipeline without sensitive real data"],
    ["24-hour freshness SLA", "Matches daily forecast cadence"],
], col_widths=[4.5, 7.5], header_bg=EXL_ORANGE)

# ════════════════════════════════════════
# SLIDE 14 — Future Improvements
# ════════════════════════════════════════
sl = make_content_slide("Future Improvements")

improvements = [
    ("Hyperparameter Tuning", "GridSearchCV / Optuna for better MAPE", EXL_SLATE),
    ("Weekly Aggregation", "Smoother predictions at higher granularity", EXL_BLUE),
    ("Real-time Extraction", "Streaming LLM calls as notes arrive", EXL_ORANGE),
    ("Automated Retraining", "Triggered by PSI drift alerts", EXL_MID_BLUE),
    ("Cloud Deployment", "Azure Blob for feature store, Azure ML for inference", EXL_GRAY),
    ("Multi-supplier", "SKUs with overlapping supplier relationships", EXL_SLATE),
]
for i, (title, desc, clr) in enumerate(improvements):
    row = i // 2
    col = i % 2
    x = 0.6 + col * 6.2
    y = 1.5 + row * 1.6
    add_rounded_box(sl, x, y, 5.8, 0.6, title, clr, WHITE, font_size=16)
    add_text(sl, x + 0.2, y + 0.7, 5.4, 0.5, desc, size=14, color=DARK_GRAY)

# ════════════════════════════════════════
# SLIDE 15 — Summary
# ════════════════════════════════════════
sl = make_content_slide("Summary")

summary_items = [
    ("Problem", "ERP-only forecasts miss early supplier delay signals", EXL_ORANGE),
    ("Solution", "Feature store + LLM extraction pipeline (GPT-4o)", EXL_BLUE),
    ("Result", "6.6% MAPE improvement; early_delay_flag is the #1 feature", GREEN_OK),
    ("Monitoring", "PSI drift detection + 24-hour freshness SLA", EXL_MID_BLUE),
    ("Takeaway", "Unstructured supplier data has measurable predictive value", EXL_SLATE),
]
for i, (label, desc, clr) in enumerate(summary_items):
    y = 1.4 + i * 0.95
    add_rounded_box(sl, 0.6, y, 2.5, 0.65, label, clr, WHITE, font_size=18)
    add_text(sl, 3.4, y + 0.1, 9, 0.5, desc, size=18, color=DARK_GRAY)

add_text(sl, 2.0, 6.2, 9, 0.5, "Thank you — Questions?",
         size=28, bold=True, color=EXL_ORANGE, alignment=PP_ALIGN.CENTER)

# ── Save ──
out_path = r"C:\Users\LKDJ\Documents\DemandSignalFeatureStore\PITCH_DECK.pptx"
prs.save(out_path)
print(f"Saved: {out_path}")
