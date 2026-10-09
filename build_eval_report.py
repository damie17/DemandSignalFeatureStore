"""Build the Evaluation Report as a formatted Word document."""

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml

doc = Document()

section = doc.sections[0]
section.page_width = Cm(21)
section.page_height = Cm(29.7)
section.top_margin = Cm(2.5)
section.bottom_margin = Cm(2.5)
section.left_margin = Cm(2.5)
section.right_margin = Cm(2.5)

EXL_ORANGE = RGBColor(0xFB, 0x4D, 0x0A)
EXL_SLATE  = RGBColor(0x2E, 0x36, 0x43)
EXL_BLUE   = RGBColor(0x00, 0x50, 0x71)
EXL_GRAY   = RGBColor(0x6D, 0x72, 0x7B)
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
DARK_GRAY  = RGBColor(0x33, 0x33, 0x33)
GREEN      = RGBColor(0x27, 0xAE, 0x60)

style = doc.styles['Normal']
style.font.name = 'Calibri'
style.font.size = Pt(11)
style.font.color.rgb = DARK_GRAY
style.paragraph_format.space_after = Pt(6)
style.paragraph_format.line_spacing = 1.15

for level in range(1, 4):
    h = doc.styles[f'Heading {level}']
    h.font.name = 'Calibri'
    if level == 1:
        h.font.size = Pt(22)
        h.font.color.rgb = EXL_ORANGE
        h.font.bold = True
        h.paragraph_format.space_before = Pt(24)
        h.paragraph_format.space_after = Pt(8)
    elif level == 2:
        h.font.size = Pt(16)
        h.font.color.rgb = EXL_BLUE
        h.font.bold = True
        h.paragraph_format.space_before = Pt(18)
        h.paragraph_format.space_after = Pt(6)
    elif level == 3:
        h.font.size = Pt(13)
        h.font.color.rgb = EXL_SLATE
        h.font.bold = True
        h.paragraph_format.space_before = Pt(12)
        h.paragraph_format.space_after = Pt(4)


def add_para(text, bold=False, italic=False, size=None, color=None, align=None, space_after=None):
    p = doc.add_paragraph()
    run = p.add_run(text)
    if bold: run.bold = True
    if italic: run.italic = True
    if size: run.font.size = Pt(size)
    if color: run.font.color.rgb = color
    if align: p.alignment = align
    if space_after is not None: p.paragraph_format.space_after = Pt(space_after)
    return p


def add_rich_para(parts, space_after=None):
    p = doc.add_paragraph()
    for text, bold, italic, color, size in parts:
        run = p.add_run(text)
        run.bold = bold
        run.italic = italic
        if color: run.font.color.rgb = color
        if size: run.font.size = Pt(size)
    if space_after is not None: p.paragraph_format.space_after = Pt(space_after)
    return p


def add_bullet(text, bold_prefix=None):
    p = doc.add_paragraph(style='List Bullet')
    if bold_prefix:
        run = p.add_run(bold_prefix)
        run.bold = True
        run.font.color.rgb = EXL_SLATE
        p.add_run(text)
    else:
        p.text = text
    p.paragraph_format.left_indent = Cm(1.2)
    return p


def add_table(headers, rows, col_widths=None):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = 'Table Grid'
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


# ── COVER ──
doc.add_paragraph()
doc.add_paragraph()
doc.add_paragraph()

add_para("Evaluation Report", bold=True, size=32, color=EXL_ORANGE,
         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12)
add_para("Demand Signal Feature Store", bold=True, size=20, color=EXL_SLATE,
         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=24)

doc.add_paragraph()

add_para("Supply Chain — Demand Signal Feature Store", size=14, color=EXL_BLUE,
         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)
add_para("Capstone Project  |  AI Engineer Program  |  Track 1", size=12, color=EXL_GRAY,
         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)
add_para("Damini Thandele  |  October 2026", size=12, color=EXL_GRAY,
         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=24)

doc.add_paragraph()

add_callout(
    "This report evaluates whether LLM-extracted supplier delay signals improve next-day "
    "demand forecasting accuracy compared to an ERP-only baseline. The primary metric is "
    "MAPE (Mean Absolute Percentage Error).",
    bg_color="FFF3E0"
)

doc.add_page_break()

# ── 1. OBJECTIVE ──
doc.add_heading("1. Objective", level=1)

doc.add_paragraph(
    "Measure whether adding LLM-extracted supplier delay signals to structured ERP data "
    "improves next-day demand (sales) forecasting accuracy. The hypothesis is that supplier "
    "notes contain early warning signals — available 5–12 days before the ERP system is updated — "
    "that reduce forecast error."
)

doc.add_paragraph(
    "The primary evaluation metric is MAPE (Mean Absolute Percentage Error), the industry-standard "
    "metric for demand forecasting. Two secondary metrics (MAE, RMSE) provide additional perspectives "
    "on error magnitude."
)

# ── 2. EXPERIMENTAL SETUP ──
doc.add_heading("2. Experimental Setup", level=1)

add_table(
    ["Parameter", "Value"],
    [
        ["Algorithm", "XGBoost Regressor"],
        ["Hyperparameters", "n_estimators=200, max_depth=5, learning_rate=0.1, random_state=42"],
        ["Train/Test Split", "Chronological 80/20 (first ~14 months train, last ~4 months test)"],
        ["Baseline Features", "15 ERP features (sales lags, inventory, PO timing, calendar)"],
        ["Enhanced Features", "15 ERP + 2 note-derived (early_delay_flag, expected_delay_days)"],
        ["Target Variable", "target_next_day_sales"],
        ["Data", "Synthetic: 2,700 daily records, 5 SKUs, 4 suppliers, 540 days"],
    ],
    col_widths=[4, 12]
)

doc.add_paragraph(
    "Both models use identical hyperparameters to ensure a fair comparison. Any difference in "
    "accuracy comes purely from the additional note-derived features, not from tuning differences."
)

doc.add_heading("Why Chronological Split?", level=2)

doc.add_paragraph(
    "Time-series data must be split in chronological order to prevent data leakage. A random "
    "train/test split would allow the model to learn from future patterns during training, "
    "producing misleadingly good results. The chronological split ensures the model is always "
    "predicting the future based on the past — the same condition as a real deployment."
)

doc.add_page_break()

# ── 3. RESULTS ──
doc.add_heading("3. Results", level=1)

add_table(
    ["Metric", "Baseline (ERP only)", "Enhanced (ERP + Notes)", "Change"],
    [
        ["MAPE", "25.01%", "23.36%", "-6.6% (improved)"],
        ["MAE", "5.03 units", "4.55 units", "-9.5% (improved)"],
        ["RMSE", "6.80 units", "6.35 units", "-6.6% (improved)"],
    ],
    col_widths=[3, 3.5, 3.5, 3.5]
)

add_callout(
    "Key Result: MAPE improved from 25.01% to 23.36% — a 6.6% reduction. "
    "All three metrics improved consistently, confirming the hypothesis.",
    bg_color="E8F5E9"
)

doc.add_heading("3.1 Metric Definitions", level=2)

add_rich_para([
    ("MAPE (Mean Absolute Percentage Error): ", True, False, EXL_BLUE, 11),
    ("Average percentage deviation of predictions from actuals. Lower is better. "
     "A MAPE of 25% means the baseline model's predictions are off by about 25% on average. "
     "This is the primary metric for this evaluation.", False, False, None, 11),
])

add_rich_para([
    ("MAE (Mean Absolute Error): ", True, False, EXL_BLUE, 11),
    ("Average absolute difference between predicted and actual values, measured in units. "
     "The enhanced model is off by 4.55 units on average vs. 5.03 for baseline — a 9.5% improvement.",
     False, False, None, 11),
])

add_rich_para([
    ("RMSE (Root Mean Squared Error): ", True, False, EXL_BLUE, 11),
    ("Square root of the average squared error. Penalizes large errors more heavily than MAE. "
     "The improvement (6.80 → 6.35) indicates fewer extreme mispredictions in the enhanced model.",
     False, False, None, 11),
])

doc.add_heading("3.2 How MAPE Improvement Is Calculated", level=2)

doc.add_paragraph(
    "The percentage change in MAPE is calculated as:"
)

add_para("(New MAPE − Old MAPE) / Old MAPE × 100 = (23.36 − 25.01) / 25.01 × 100 = −6.6%",
         bold=True, size=11, color=EXL_SLATE)

doc.add_paragraph(
    "The negative sign indicates improvement (lower error). This means the enhanced model's "
    "forecast error is 6.6% smaller than the baseline's."
)

doc.add_page_break()

# ── 4. FEATURE IMPORTANCE ──
doc.add_heading("4. Feature Importance Analysis", level=1)

doc.add_paragraph(
    "XGBoost provides feature importance scores based on how frequently and effectively each "
    "feature is used in splitting decisions across all 200 trees. The top 5 features in the "
    "enhanced model:"
)

add_table(
    ["Rank", "Feature", "Source", "Role"],
    [
        ["1", "early_delay_flag", "Supplier Note (LLM)",
         "Binary delay warning — available before ERP update"],
        ["2", "sales_lag_1", "ERP", "Previous day's sales"],
        ["3", "rolling_avg_7", "ERP", "7-day smoothed demand trend"],
        ["4", "on_hand_inventory", "ERP", "Current warehouse stock"],
        ["5", "inventory_cover", "ERP", "Days of stock remaining"],
    ],
    col_widths=[1.2, 3.5, 3, 5.8]
)

add_callout(
    "The LLM-extracted early_delay_flag is the #1 most important feature — the model relies on it "
    "more than any ERP feature. This is the strongest possible validation of the project hypothesis.",
    bg_color="E8F5E9"
)

doc.add_paragraph(
    "Why early_delay_flag is so powerful: this feature flips to 1 the moment a supplier note warns "
    "of a delay — days before the ERP system is updated. During this window, it is the only signal "
    "in the entire feature set that knows a delay is coming. The model learns to associate this flag "
    "with the demand decay that follows supplier delays."
)

doc.add_page_break()

# ── 5. DRIFT DETECTION ──
doc.add_heading("5. Drift Detection (PSI)", level=1)

doc.add_paragraph(
    "Population Stability Index (PSI) measures how much a feature's distribution has shifted "
    "between the training and test periods. This is critical for production confidence — a feature "
    "that drifts significantly may cause model degradation over time."
)

add_table(
    ["PSI Range", "Interpretation", "Action"],
    [
        ["< 0.1", "Stable — no significant drift", "No action needed"],
        ["0.1 – 0.2", "Moderate drift — monitor closely", "Investigate if performance degrades"],
        ["≥ 0.2", "Significant drift — distribution has shifted", "Consider retraining the model"],
    ],
    col_widths=[2, 5, 6.5]
)

doc.add_heading("5.1 Drift Results", level=2)

add_table(
    ["Feature", "PSI Score", "Status", "Interpretation"],
    [
        ["sales_lag_1", "0.03", "Stable", "Recent sales patterns consistent across periods"],
        ["on_hand_inventory", "0.01", "Stable", "Inventory levels have similar distribution"],
        ["early_delay_flag", "0.07", "Stable", "Key note feature is consistent — reliable for production"],
        ["inventory_cover", "0.12", "Moderate", "Slight shift in days-of-stock distribution"],
        ["rolling_avg_7", "0.24", "Significant", "7-day demand trend shifted — seasonal effect"],
        ["expected_delay_days", "0.63", "Significant", "Delay durations differ between periods"],
        ["historical_avg_supplier_delay", "0.78", "Significant", "Cumulative average stabilizes over time — expected"],
        ["delay_reason_encoded", "1.06", "Significant", "Extreme drift — confirms exclusion from model"],
    ],
    col_widths=[3.5, 1.5, 2, 6.5]
)

doc.add_paragraph("Key takeaways:")

add_bullet("early_delay_flag (PSI = 0.07) is stable — the most important feature is also the most reliable", "Positive: ")
add_bullet("delay_reason_encoded (PSI = 1.06) shows extreme drift — validates excluding it from the model", "Validated: ")
add_bullet("In production, features crossing PSI > 0.2 would trigger automated retraining alerts", "Production: ")

doc.add_page_break()

# ── 6. LEAKAGE PREVENTION ──
doc.add_heading("6. Data Leakage Prevention", level=1)

doc.add_paragraph(
    "Data leakage occurs when a model has access to information during training that would not be "
    "available at prediction time. This is a critical concern in time-series forecasting. The project "
    "implements four safeguards:"
)

add_table(
    ["Leakage Risk", "Safeguard"],
    [
        ["Future sales in features",
         "All lag features use past data only (1, 7, 28 days ago). Rolling averages shifted by 1 day."],
        ["Test set contamination",
         "Chronological split — first 80% of dates for training, last 20% for testing. No random shuffling."],
        ["Note signals before they exist",
         "Note features (early_delay_flag, expected_delay_days) active only between note_date and PO arrival."],
        ["Future supplier performance",
         "historical_avg_supplier_delay uses only past completed POs via merge_asof — never looks ahead."],
    ],
    col_widths=[3.5, 10]
)

# ── 7. CONCLUSION ──
doc.add_heading("7. Conclusion", level=1)

doc.add_paragraph(
    "Adding two LLM-extracted features (early_delay_flag, expected_delay_days) to 15 ERP features "
    "improves all three evaluation metrics. The primary metric, MAPE, improved from 25.01% to 23.36% "
    "— a 6.6% reduction in forecast error."
)

doc.add_paragraph(
    "The improvement is driven by the early warning signal that supplier notes provide 5–12 days "
    "before the ERP system is updated. The key note feature (early_delay_flag) is both the most "
    "important feature in the model and the most stable (PSI = 0.07), supporting confidence in "
    "production deployment."
)

doc.add_heading("Limitations", level=2)

add_bullet("Synthetic data — real supplier notes may have more variability")
add_bullet("No hyperparameter tuning — MAPE could be further reduced with optimization")
add_bullet("Single supplier per SKU — no multi-supplier overlap handling")
add_bullet("Observed sales underestimates true demand during stockouts")

doc.add_heading("Next Steps", level=2)

add_bullet("Hyperparameter tuning (Optuna/GridSearchCV) for further MAPE reduction")
add_bullet("Real-time streaming extraction as supplier notes arrive")
add_bullet("Automated model retraining triggered by PSI drift alerts")
add_bullet("Multi-supplier overlap handling for SKUs with multiple sources")

# ── Save ──
out_path = r"C:\Users\LKDJ\Documents\DemandSignalFeatureStore\EVALUATION_REPORT.docx"
doc.save(out_path)
print(f"Saved: {out_path}")
