"""
Generate a professional, fully detailed Word document (.docx) for:
Internship Working & Progress Report
Student: Ashit Upadhyay
Institution: Vishveshwarya Group of Institutions
Host Organization: Zidio Development (Project FORESIGHT)
"""

import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    """Sets background color of a table cell."""
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Sets cell padding (in dxa)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_header_styled(doc, text, level=1):
    h = doc.add_heading(text, level=level)
    h.paragraph_format.keep_with_next = True
    h.paragraph_format.space_before = Pt(14)
    h.paragraph_format.space_after = Pt(6)
    for run in h.runs:
        run.font.name = 'Calibri'
        if level == 1:
            run.font.size = Pt(15)
            run.font.bold = True
            run.font.color.rgb = RGBColor(15, 23, 42) # slate-900
        elif level == 2:
            run.font.size = Pt(13)
            run.font.bold = True
            run.font.color.rgb = RGBColor(30, 58, 138) # blue-900
        elif level == 3:
            run.font.size = Pt(11.5)
            run.font.bold = True
            run.font.color.rgb = RGBColor(51, 65, 85) # slate-700
    return h

def add_callout(doc, title, text, bg_hex="F1F5F9", border_hex="2563EB"):
    """Adds a callout box with a colored left border and background."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.8)
    set_cell_background(cell, bg_hex)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    
    # Left border only
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:top w:val="none"/>
            <w:left w:val="single" w:sz="24" w:space="0" w:color="{border_hex}"/>
            <w:bottom w:val="none"/>
            <w:right w:val="none"/>
        </w:tcBorders>
    ''')
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    run_t = p.add_run(f"{title}\n")
    run_t.font.name = 'Calibri'
    run_t.font.size = Pt(10.5)
    run_t.font.bold = True
    run_t.font.color.rgb = RGBColor(15, 23, 42)
    
    run_b = p.add_run(text)
    run_b.font.name = 'Calibri'
    run_b.font.size = Pt(9.5)
    run_b.font.color.rgb = RGBColor(51, 65, 85)
    
    # Spacer
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(2)
    sp.paragraph_format.space_after = Pt(4)

def format_table(table, col_widths, headers, data, align_cols=None):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    # Header Row
    hdr_cells = table.rows[0].cells
    for i, header_text in enumerate(headers):
        hdr_cells[i].text = header_text
        set_cell_background(hdr_cells[i], "1E293B") # Dark slate
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=140, right=140)
        p = hdr_cells[i].paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        if align_cols and align_cols[i] == 'C':
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif align_cols and align_cols[i] == 'R':
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        else:
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for run in p.runs:
            run.font.name = 'Calibri'
            run.font.size = Pt(9.5)
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            
    # Data Rows
    for row_idx, row_data in enumerate(data):
        row_cells = table.rows[row_idx + 1].cells
        bg_color = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, cell_value in enumerate(row_data):
            row_cells[col_idx].text = str(cell_value)
            set_cell_background(row_cells[col_idx], bg_color)
            set_cell_margins(row_cells[col_idx], top=90, bottom=90, left=130, right=130)
            p = row_cells[col_idx].paragraphs[0]
            p.paragraph_format.space_before = Pt(1.5)
            p.paragraph_format.space_after = Pt(1.5)
            if align_cols and align_cols[col_idx] == 'C':
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            elif align_cols and align_cols[col_idx] == 'R':
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for run in p.runs:
                run.font.name = 'Calibri'
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(30, 41, 59)
                
    # Set Widths
    for row in table.rows:
        for idx, width in enumerate(col_widths):
            row.cells[idx].width = Inches(width)

def build_internship_report():
    doc = Document()
    
    # Page setup - Margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.85)
        section.right_margin = Inches(0.85)
        section.header_distance = Inches(0.4)
        section.footer_distance = Inches(0.4)
        
        # Header text
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("Vishveshwarya Group of Institutions | Internship Working Report — Ashit Upadhyay")
        hrun.font.name = 'Calibri'
        hrun.font.size = Pt(8)
        hrun.font.color.rgb = RGBColor(148, 163, 184)
        
        # Footer text
        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        frun = fp.add_run("Project FORESIGHT — Demand & Inventory Intelligence | Zidio Development Internship")
        frun.font.name = 'Calibri'
        frun.font.size = Pt(8)
        frun.font.color.rgb = RGBColor(148, 163, 184)

    # -------------------------------------------------------------
    # INSTITUTION & TITLE HEADER (Modeled exactly after Reference PDF)
    # -------------------------------------------------------------
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(0)
    p_inst.paragraph_format.space_after = Pt(2)
    r1 = p_inst.add_run("VISHVESHWARYA GROUP OF INSTITUTIONS\n")
    r1.font.name = 'Calibri'
    r1.font.size = Pt(16)
    r1.font.bold = True
    r1.font.color.rgb = RGBColor(30, 58, 138) # Navy Blue
    
    r2 = p_inst.add_run("Affiliated to AKTU, Lucknow (U.P) | CCS University, Meerut (U.P)\nTechnical Campus Approved by AICTE / UGC / PCI / BTE / BCI | Ministry of Education, Govt. of India\n")
    r2.font.name = 'Calibri'
    r2.font.size = Pt(8.5)
    r2.font.color.rgb = RGBColor(100, 116, 139)
    
    r3 = p_inst.add_run("UPCOMING VISHVESHWARYA UNIVERSITY\n")
    r3.font.name = 'Calibri'
    r3.font.size = Pt(9.5)
    r3.font.bold = True
    r3.font.color.rgb = RGBColor(71, 85, 105)

    p_line = doc.add_paragraph()
    p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_line.paragraph_format.space_before = Pt(2)
    p_line.paragraph_format.space_after = Pt(14)
    r_line = p_line.add_run("―" * 58)
    r_line.font.color.rgb = RGBColor(203, 213, 225)

    # DOCUMENT TITLE
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(4)
    p_title.paragraph_format.space_after = Pt(4)
    rt = p_title.add_run("INTERNSHIP WORKING & PROGRESS REPORT\n")
    rt.font.name = 'Calibri'
    rt.font.size = Pt(18)
    rt.font.bold = True
    rt.font.color.rgb = RGBColor(15, 23, 42)
    
    r_sub = p_title.add_run("Data Science & Analytics Engineering Track\nProject FORESIGHT — Demand & Inventory Intelligence Platform")
    r_sub.font.name = 'Calibri'
    r_sub.font.size = Pt(12)
    r_sub.font.bold = True
    r_sub.font.color.rgb = RGBColor(37, 99, 235)

    # METADATA BLOCK
    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_before = Pt(12)
    p_meta.paragraph_format.space_after = Pt(16)
    p_meta.paragraph_format.line_spacing = 1.25
    
    meta_items = [
        ("Host Organization:", " Zidio Development (Data Science & Analytics Engineering Team)"),
        ("Client Engagement:", " NorthBay Living — Direct-to-Consumer (D2C) Home & Lifestyle Brand"),
        ("Submitted by:", " Ashit Upadhyay"),
        ("Program / Branch:", " B.Tech — Computer Science & Engineering (AIML)"),
        ("Submitted to:", " Department of Computer Science & Engineering, Vishveshwarya Group of Institutions"),
        ("Internship Status:", " Currently Working / Ongoing Client Engagement Project"),
        ("Engagement Duration:", " 4-Week Intensive Industry Engagement (Phase 1 to Phase 8 Track)"),
        ("Current Submission Date:", " October 2026"),
        ("GitHub Repository:", " https://github.com/codexboy0417/demand-inventory-intelligence.git")
    ]
    for lbl, val in meta_items:
        r_lbl = p_meta.add_run(lbl)
        r_lbl.font.name = 'Calibri'
        r_lbl.font.size = Pt(10)
        r_lbl.font.bold = True
        r_lbl.font.color.rgb = RGBColor(15, 23, 42)
        
        r_val = p_meta.add_run(val + "\n")
        r_val.font.name = 'Calibri'
        r_val.font.size = Pt(10)
        r_val.font.color.rgb = RGBColor(51, 65, 85)

    # DECLARATION
    add_header_styled(doc, "Declaration", level=2)
    p_dec = doc.add_paragraph()
    p_dec.paragraph_format.space_before = Pt(2)
    p_dec.paragraph_format.space_after = Pt(8)
    p_dec.paragraph_format.line_spacing = 1.15
    r_dec = p_dec.add_run(
        "I, Ashit Upadhyay, hereby declare that this report is a true, authentic, and accurate record of the "
        "industrial internship I am actively pursuing at Zidio Development on the client account NorthBay Living. "
        "The project architecture, data engineering pipelines, forecasting models, inventory risk scoring engine, "
        "and interactive software artifacts described in this document represent my original work and active engineering contributions, "
        "developed under the mentorship and guidance of the technical leads at Zidio Development."
    )
    r_dec.font.name = 'Calibri'
    r_dec.font.size = Pt(10)
    r_dec.font.color.rgb = RGBColor(51, 65, 85)

    # Signatures
    p_sig = doc.add_paragraph()
    p_sig.paragraph_format.space_before = Pt(12)
    p_sig.paragraph_format.space_after = Pt(18)
    r_sig1 = p_sig.add_run("Signature: __________________________                    Date: __________________________\n")
    r_sig1.font.name = 'Calibri'
    r_sig1.font.size = Pt(10)
    r_sig1.font.bold = True
    r_sig2 = p_sig.add_run("Ashit Upadhyay (Student Intern)                           Vishveshwarya Group of Institutions")
    r_sig2.font.name = 'Calibri'
    r_sig2.font.size = Pt(9.5)
    r_sig2.font.color.rgb = RGBColor(100, 116, 139)

    # ACKNOWLEDGEMENT
    add_header_styled(doc, "Acknowledgement", level=2)
    p_ack = doc.add_paragraph()
    p_ack.paragraph_format.space_before = Pt(2)
    p_ack.paragraph_format.space_after = Pt(14)
    p_ack.paragraph_format.line_spacing = 1.15
    r_ack = p_ack.add_run(
        "I express my sincere gratitude to the Leadership and Technical Mentorship Team at Zidio Development "
        "for granting me the opportunity to work as a Data Scientist on a live client engagement for NorthBay Living. "
        "The professional mentorship, weekly technical checkpoints, and rigorous rubric-based code reviews have been invaluable "
        "in bridging the gap between academic theory and production-grade software delivery. "
        "I also extend my heartfelt thanks to the Head of Department, faculty members, and training coordinators at "
        "Vishveshwarya Group of Institutions for their continuous encouragement, academic support, and approval "
        "of this valuable internship experience."
    )
    r_ack.font.name = 'Calibri'
    r_ack.font.size = Pt(10)
    r_ack.font.color.rgb = RGBColor(51, 65, 85)

    # -------------------------------------------------------------
    # 1. EXECUTIVE SUMMARY
    # -------------------------------------------------------------
    add_header_styled(doc, "1. Executive Summary", level=1)
    p_ex = doc.add_paragraph()
    p_ex.paragraph_format.line_spacing = 1.15
    p_ex.paragraph_format.space_after = Pt(8)
    p_ex.add_run(
        "As part of my Data Science & Analytics internship at Zidio Development, I am placed on an active commercial client engagement: "
        "Project FORESIGHT (Demand & Inventory Intelligence). The client, NorthBay Living, is a fast-growing Direct-to-Consumer (D2C) "
        "home, decor, and lifestyle brand managing ~200 active SKUs shipped from a single fulfillment center. "
        "Historically, the brand planned inventory using gut feel and static spreadsheets. This created a dual failure mode: "
        "best-selling velocity items frequently stocked out (causing unrecoverable revenue loss and customer dissatisfaction), "
        "while slow-moving products piled up in warehouse racks (trapping crucial working capital and forcing margin-diluting markdowns)."
    )

    p_ex2 = doc.add_paragraph()
    p_ex2.paragraph_format.line_spacing = 1.15
    p_ex2.paragraph_format.space_after = Pt(8)
    p_ex2.add_run(
        "My work centers on building an end-to-end, production-ready analytics product that turns raw transactional extracts "
        "into weekly SKU-level demand forecasts and an automated risk-scoring early-warning system. "
        "The system has been designed across five core functional pillars:"
    )

    pillars = [
        ("1. Data Engineering & Star Schema Ingestion: ", "Processing over 1,067,371 raw transaction records across 2 full years (2009–2011) and 5,305 SKUs, constructing a clean 4-table Star Schema (sales_daily, sku_master, calendar, inventory_snapshots)."),
        ("2. Exploratory Data Analysis & Behavioral Mining: ", "Quantifying the 80/20 Pareto volume distribution (top 15% SKUs generate 68% of sales volume), identifying severe Q4 holiday seasonality surges (38% of annual revenue), and detecting dormant dead stock."),
        ("3. Machine Learning Demand Forecasting: ", "Engineering strictly shifted temporal lags and rolling statistics to prevent lookahead leakage, evaluating Seasonal-Naive, Random Forest, XGBoost, and LightGBM models via 4-fold Rolling-Origin Cross-Validation. LightGBM earned model selection with an out-of-sample WAPE of 72.9% (+34.9% error reduction over baseline)."),
        ("4. Inventory Risk Scoring & 2x2 Decision Matrix: ", "Decoupling probabilistic demand forecasts from warehouse inventory physics to build an explainable 2x2 Decision Grid (Reorder Now, Markdown / Clear, Watch / Volatile, Healthy) with exact rupee-level financial risk quantification."),
        ("5. Productization & Cloud Serving: ", "Packaging the intelligence stack into a 7-Page Streamlit Planning Dashboard and a live FastAPI REST scoring microservice with automated Swagger documentation.")
    ]
    for p_title, p_desc in pillars:
        p_item = doc.add_paragraph(style='List Bullet')
        p_item.paragraph_format.space_after = Pt(4)
        p_item.paragraph_format.line_spacing = 1.15
        r_pt = p_item.add_run(p_title)
        r_pt.font.name = 'Calibri'
        r_pt.font.bold = True
        r_pt.font.color.rgb = RGBColor(15, 23, 42)
        r_pd = p_item.add_run(p_desc)
        r_pd.font.name = 'Calibri'
        r_pd.font.color.rgb = RGBColor(51, 65, 85)

    add_callout(
        doc,
        "Headline Key Performance Indicators (KPIs) Achieved to Date:",
        "• Data Volume Processed: 1,067,371 raw transactions | 5,305 SKUs | 2 Full Operational Years\n"
        "• Machine Learning Forecast Accuracy: 72.9% Out-of-Sample WAPE (LightGBM) vs 107.8% (Seasonal-Naive Baseline)\n"
        "• Accuracy Lift Over Client Baseline: +34.9% WAPE Error Reduction\n"
        "• Financial Exposure Identified: ₹1,002,813.06 Total Financial Value at Stake\n"
        "• Working Capital Trapped in Overstock: ₹1,000,800.85 (45 SKUs flagged for immediate clearance discounting)\n"
        "• Revenue Protected from Stockouts: ₹2,012.21 (1 SKU flagged for immediate PO replenishment)\n"
        "• Software Deliverables: 7-Page Interactive Streamlit UI + FastAPI REST Service + Complete Jupyter Notebook",
        bg_hex="F0FDF4", border_hex="16A34A"
    )

    # -------------------------------------------------------------
    # 2. HOST ORGANIZATION & PROGRAM GOVERNANCE
    # -------------------------------------------------------------
    add_header_styled(doc, "2. Host Organization & Program Governance", level=1)
    p_org = doc.add_paragraph()
    p_org.paragraph_format.line_spacing = 1.15
    p_org.paragraph_format.space_after = Pt(8)
    p_org.add_run(
        "Zidio Development operates an experiential learning and engineering consultancy platform that deploys student data scientists "
        "onto real-world client engagements. Unlike academic coursework, interns are held to professional client standards: "
        "solving business-critical problems, working against acceptance criteria, ensuring reproducibility, and presenting to non-technical stakeholders."
    )

    # Stakeholders Table
    stk_headers = ["Role / Title", "Stakeholder & Entity", "Business Focus & Responsibility"]
    stk_data = [
        ["Primary Client", "Head of Operations (NorthBay Living)", "Wants reliable reorder/markdown guidance to prevent warehouse stockouts."],
        ["Merchandiser", "Merchandising Lead (NorthBay Living)", "Decides catalog promotions, discounts, and slow-moving item clearances."],
        ["Finance Lead", "Finance Lead (NorthBay Living)", "Focused on working capital protection, inventory holding costs, and ₹ margin impact."],
        ["Lead Data Scientist", "Ashit Upadhyay (Student Intern)", "Owns end-to-end data pipelines, ML modeling, risk engines, UI dashboards, and reporting."],
        ["Engagement Lead", "Technical Mentor (Zidio Development)", "Client proxy overseeing weekly checkpoints, code quality, and milestone rubrics."]
    ]
    stk_tbl = doc.add_table(rows=len(stk_data) + 1, cols=3)
    format_table(stk_tbl, [1.5, 2.0, 3.3], stk_headers, stk_data)

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(4)
    p_sp.paragraph_format.space_after = Pt(6)

    # Deliverables & Acceptance Criteria
    add_header_styled(doc, "Governed Deliverables & Acceptance Criteria (D1 to D7)", level=2)
    deliv_headers = ["Code", "Deliverable Name", "Specification & Client Definition of Done", "Status"]
    deliv_data = [
        ["D1", "Data Pipeline", "Reproducible ingestion & cleaning producing analysis-ready Star Schema.", "Completed"],
        ["D2", "EDA Insight Memo", "Comprehensive reporting on trends, Pareto rules, seasonality, and dead stock.", "Completed"],
        ["D3", "Demand Forecast Model", "Weekly SKU forecast evaluated via rolling CV beating seasonal-naive baseline.", "Completed"],
        ["D4", "Risk Scoring Engine", "Deterministic 2x2 decision grid with rupee-quantified sales & capital impact.", "Completed"],
        ["D5", "Planning Dashboard", "7-page interactive Streamlit dashboard with drill-downs and confidence bands.", "Completed"],
        ["D6", "Deployed Scoring Service", "FastAPI REST API serving single-SKU and batch predictions.", "Completed"],
        ["D7", "Executive Readout", "10-slide executive presentation deck & full formal project report.", "Completed"]
    ]
    deliv_tbl = doc.add_table(rows=len(deliv_data) + 1, cols=4)
    format_table(deliv_tbl, [0.6, 1.8, 3.5, 0.9], deliv_headers, deliv_data, align_cols=['C', 'L', 'L', 'C'])

    # -------------------------------------------------------------
    # 3. TECHNOLOGY STACK & LEARNING TRACKS
    # -------------------------------------------------------------
    add_header_styled(doc, "3. Technology Stack & Core Competencies", level=1)
    p_tech = doc.add_paragraph()
    p_tech.paragraph_format.line_spacing = 1.15
    p_tech.paragraph_format.space_after = Pt(8)
    p_tech.add_run(
        "The project combines modern Python data science frameworks, gradient-boosted tree algorithms, "
        "deterministic supply chain physics, and web application serving:"
    )

    tech_headers = ["Layer / Domain", "Libraries & Technologies", "Functional Purpose in Project FORESIGHT"]
    tech_data = [
        ["Core Language", "Python 3.11+ / 3.14", "Underlying runtime for data manipulation, modeling, and application serving."],
        ["Data Engineering", "pandas, numpy, openpyxl", "High-volume data wrangling, star schema building, aggregation, vector operations."],
        ["Machine Learning", "scikit-learn, LightGBM, XGBoost", "Supervised tree regression, gradient boosting, temporal feature extraction."],
        ["Time-Series Validation", "Rolling-Origin Cross-Validation", "4-fold temporal backtesting preventing future lookahead data leakage."],
        ["Interactive Visuals", "Plotly Express, Graph Objects", "Dynamic interactive scatter plots, confidence intervals, revenue trendlines."],
        ["Web Application", "Streamlit Multi-Page Framework", "7-page interactive planning dashboard for operations and merchandising."],
        ["REST API Serving", "FastAPI, Uvicorn, Pydantic", "Production microservice endpoint for ERP integration and batch SKU scoring."],
        ["Version Control", "Git, GitHub", "Collaborative development, change tracking, and public artifact hosting."]
    ]
    tech_tbl = doc.add_table(rows=len(tech_data) + 1, cols=3)
    format_table(tech_tbl, [1.6, 2.2, 3.0], tech_headers, tech_data)

    # -------------------------------------------------------------
    # 4. WEEKLY PROGRESS SUMMARY & EXECUTION TIMELINE
    # -------------------------------------------------------------
    add_header_styled(doc, "4. Chronological Progress Summary & Weekly Phases", level=1)
    p_prog = doc.add_paragraph()
    p_prog.paragraph_format.line_spacing = 1.15
    p_prog.paragraph_format.space_after = Pt(8)
    p_prog.add_run(
        "The project followed an agile four-week commercial consulting cadence with scheduled client checkpoints:"
    )

    weeks_summary = [
        ("Phase 1: Foundations, Ingestion & Data Wrangling (Week 1 / Milestone M1)", [
            "Project Kickoff: Analyzed client engagement brief, clarified objectives, established git repository and environment.",
            "Raw Ingestion: Downloaded and processed the Online Retail II dataset (1,067,371 rows across 2009–2011).",
            "Data Cleansing: Filtered out return orders (Quantity <= 0) and bad debt write-offs (Price <= 0).",
            "Star Schema Formulation: Built sales_daily (532k rows), sku_master (4,917 SKUs), calendar (739 days), and inventory_snapshots (200 SKUs).",
            "Checkpoint M1 Delivered: Approved reproducible pipeline script (src/pipeline.py) and data foundation."
        ]),
        ("Phase 2: Exploratory Data Analysis & Feature Engineering (Week 2 / Milestone M2)", [
            "EDA & Pattern Mining: Quantified Q4 holiday seasonality surge (38% of revenue), Pareto 80/20 volume skew, and identified 18% dormant catalog SKUs.",
            "Feature Engineering: Created shifted temporal lags (t-1w, t-2w, t-4w, t-52w), rolling moving averages (4w, 8w), rolling volatility, and discount ratios.",
            "Baseline Construction: Formulated the Seasonal-Naive baseline predictor (107.8% WAPE) to serve as the hurdle metric.",
            "Checkpoint M2 Delivered: Approved EDA Insight Memo (reports/eda_insight_memo.md) and feature matrix."
        ]),
        ("Phase 3: Multi-Model Demand Forecasting & Backtesting (Week 3 / Milestone M3)", [
            "Model Training: Fitted Random Forest, XGBoost, and LightGBM regressors on 198,412 weekly feature instances.",
            "Rolling Cross-Validation: Evaluated out-of-sample WAPE across 4 temporal folds with zero data leakage.",
            "Model Selection: LightGBM established clear victory with 72.9% WAPE, outperforming baseline by +34.9%.",
            "Checkpoint M3 Delivered: Validated backtest comparison script (src/forecast.py) and performance summary."
        ]),
        ("Phase 4: Inventory Risk Scoring Engine & Decision Matrix (Week 3-4 / Milestone M3)", [
            "Deterministic Mechanics: Built lead time demand projections vs warehouse available stock (on-hand + on-order).",
            "2x2 Matrix Implementation: Coded assign_quadrant() to categorize SKUs into Reorder Now, Markdown/Clear, Watch/Volatile, and Healthy.",
            "Financial Quantification: Calculated exact rupee metrics for Sales at Risk (₹2,012) and Capital Locked (₹1,000,800).",
            "Output Reporting: Automatically generated reports/inventory_risk_decision_matrix.csv."
        ]),
        ("Phase 5: Productization, Serving & Client Handover (Week 4 / Milestone M4)", [
            "Dashboard Engineering: Developed 7 distinct pages in Streamlit (Home, Sales Analytics, Forecast, Inventory, Risk, Product Details, Executive Summary).",
            "FastAPI REST Microservice: Built and tested service/api.py with /forecast/{sku_id} and /score-batch routes.",
            "Notebook Consolidation: Generated complete 15-cell standalone notebook (notebooks/project_foresight_complete_ml_pipeline.ipynb).",
            "Final Reporting: Authored 10-slide executive presentation, technical code review, and publication-ready PDF report."
        ])
    ]

    for ph_title, ph_tasks in weeks_summary:
        add_header_styled(doc, ph_title, level=2)
        for tsk in ph_tasks:
            p_t = doc.add_paragraph(style='List Bullet')
            p_t.paragraph_format.space_after = Pt(2.5)
            p_t.paragraph_format.line_spacing = 1.15
            r_t = p_t.add_run(tsk)
            r_t.font.name = 'Calibri'
            r_t.font.size = Pt(9.5)
            r_t.font.color.rgb = RGBColor(51, 65, 85)

    # -------------------------------------------------------------
    # 5. CORE PROJECT IMPLEMENTATION: PROJECT FORESIGHT
    # -------------------------------------------------------------
    add_header_styled(doc, "5. Core Project Implementation: Project FORESIGHT", level=1)
    p_impl = doc.add_paragraph()
    p_impl.paragraph_format.line_spacing = 1.15
    p_impl.paragraph_format.space_after = Pt(8)
    p_impl.add_run(
        "Project FORESIGHT is structured as an enterprise analytics stack. The technical core consists of three key mathematical "
        "and architectural components:"
    )

    # 5.1 System Architecture
    add_header_styled(doc, "5.1 System Architecture & Information Flow", level=2)
    p_arch = doc.add_paragraph()
    p_arch.paragraph_format.line_spacing = 1.15
    p_arch.paragraph_format.space_after = Pt(6)
    p_arch.add_run(
        "The architecture follows a strict one-way dependency graph to ensure modularity and ease of maintenance:\n"
        "Raw Transaction Dumps  -->  Data Cleaning & NLP Categorization  -->  Star Schema Fact & Dimensions  -->  "
        "Feature Engineering (Lags, Rolling Stats)  -->  LightGBM Demand Forecaster  -->  "
        "Deterministic Inventory Risk Engine  -->  Streamlit 7-Page Dashboard & FastAPI Service."
    )

    # 5.2 Mathematical Formulations
    add_header_styled(doc, "5.2 Mathematical Formulas for Forecasting & Risk Decisioning", level=2)
    p_math = doc.add_paragraph()
    p_math.paragraph_format.line_spacing = 1.2
    p_math.paragraph_format.space_after = Pt(8)
    
    math_text = (
        "1. Weighted Absolute Percentage Error (Primary Metric):\n"
        "   WAPE = Sum(|Actual_y - Predicted_y|) / Sum(Actual_y)\n\n"
        "2. Projected Demand Over Lead Time (D_LT):\n"
        "   D_LT = Weekly_Forecast * (Lead_Time_Days / 7.0)\n\n"
        "3. Total Available Stock (S_avail):\n"
        "   S_avail = On_Hand_Units + On_Order_Units\n\n"
        "4. Stockout Risk Score (0.0 to 1.0):\n"
        "   Stockout_Gap = max(0, D_LT - S_avail)\n"
        "   Stockout_Risk = clip( (D_LT - S_avail) / (D_LT + 1e-5), 0.0, 1.0 )\n\n"
        "5. Overstock Risk Score (0.0 to 1.0):\n"
        "   D_6W = Weekly_Forecast * 6.0\n"
        "   Overstock_Gap = max(0, On_Hand_Units - D_6W)\n"
        "   Overstock_Risk = clip( (On_Hand_Units - D_6W) / (On_Hand_Units + 1e-5), 0.0, 1.0 )\n\n"
        "6. Rupee Financial Quantifications:\n"
        "   Sales at Risk (INR) = Stockout_Gap * List_Price\n"
        "   Capital Locked (INR) = Overstock_Gap * Unit_Cost\n"
        "   Total at Stake (INR) = Sales_at_Risk + Capital_Locked"
    )
    r_m = p_math.add_run(math_text)
    r_m.font.name = 'Consolas'
    r_m.font.size = Pt(8.5)
    r_m.font.color.rgb = RGBColor(30, 41, 59)

    # 5.3 Core Code Implementation Snippet
    add_header_styled(doc, "5.3 Core Python Implementation (Risk Scoring & Quadrant Assignment)", level=2)
    p_code = doc.add_paragraph()
    p_code.paragraph_format.space_before = Pt(4)
    p_code.paragraph_format.space_after = Pt(8)
    
    code_snippet = (
        "def assign_quadrant(row):\n"
        "    is_stockout = row['stockout_risk'] > 0.25\n"
        "    is_overstock = row['overstock_risk'] > 0.35\n"
        "    \n"
        "    if is_stockout and not is_overstock:\n"
        "        return 'Reorder Now'\n"
        "    elif is_overstock and not is_stockout:\n"
        "        return 'Markdown / Clear'\n"
        "    elif is_stockout and is_overstock:\n"
        "        return 'Watch / Volatile'\n"
        "    else:\n"
        "        return 'Healthy'\n\n"
        "action_map = {\n"
        "    'Reorder Now': 'Raise replenishment order before stock runs out.',\n"
        "    'Markdown / Clear': 'Promote or discount to free up locked capital.',\n"
        "    'Watch / Volatile': 'Investigate erratic demand; review manually.',\n"
        "    'Healthy': 'No action needed; inventory level optimal.'\n"
        "}"
    )
    r_c = p_code.add_run(code_snippet)
    r_c.font.name = 'Consolas'
    r_c.font.size = Pt(8.5)
    r_c.font.color.rgb = RGBColor(15, 23, 42)

    # -------------------------------------------------------------
    # 6. RESULTS & BENCHMARKING
    # -------------------------------------------------------------
    add_header_styled(doc, "6. Results, Benchmarking & Model Evaluation", level=1)
    p_res = doc.add_paragraph()
    p_res.paragraph_format.line_spacing = 1.15
    p_res.paragraph_format.space_after = Pt(8)
    p_res.add_run(
        "The machine learning models were subjected to rigorous out-of-sample backtesting against the client's seasonal-naive baseline. "
        "The results across 4 rolling-origin temporal folds demonstrate clear machine learning superiority:"
    )

    # Backtest Table
    bt_headers = ["Fold #", "Cutoff Date", "Seasonal-Naive WAPE", "Random Forest WAPE", "XGBoost WAPE", "LightGBM WAPE (Winner)"]
    bt_data = [
        ["Fold 1", "2011-11-22", "141.4%", "83.4%", "88.4%", "78.4%"],
        ["Fold 2", "2011-11-27", "76.9%", "56.7%", "56.5%", "53.4%"],
        ["Fold 3", "2011-12-01", "105.0%", "61.5%", "59.9%", "59.8%"],
        ["Fold 4", "2011-12-06", "108.1%", "100.5%", "100.3%", "99.9%"],
        ["Average", "Mean Out-of-Sample", "107.8%", "75.5%", "76.3%", "72.9% (-34.9%)"]
    ]
    bt_tbl = doc.add_table(rows=len(bt_data) + 1, cols=6)
    format_table(bt_tbl, [0.8, 1.2, 1.2, 1.2, 1.1, 1.3], bt_headers, bt_data, align_cols=['C', 'C', 'R', 'R', 'R', 'R'])

    p_sp2 = doc.add_paragraph()
    p_sp2.paragraph_format.space_before = Pt(4)
    p_sp2.paragraph_format.space_after = Pt(6)

    # Quadrant Distribution Table
    add_header_styled(doc, "6.1 Inventory Risk Quadrant Distribution & Financial Impact", level=2)
    quad_headers = ["Decision Quadrant", "SKU Count", "Percentage", "Financial Value (INR)", "Primary Prescribed Operational Action"]
    quad_data = [
        ["Reorder Now", "1 SKU", "0.5%", "₹2,012.21 (Sales at Risk)", "Issue immediate replenishment PO before stock depresses."],
        ["Markdown / Clear", "45 SKUs", "22.5%", "₹1,000,800.85 (Locked Capital)", "Launch promotional clearance discounts to free cash."],
        ["Healthy", "154 SKUs", "77.0%", "₹0.00 (Optimal Balance)", "Inventory matches velocity; maintain standard cadence."],
        ["Watch / Volatile", "0 SKUs", "0.0%", "₹0.00", "Stable velocity; no erratic outlier behavior detected."],
        ["Total", "200 SKUs", "100.0%", "₹1,002,813.06 At Stake", "Combined operational financial optimization opportunity."]
    ]
    quad_tbl = doc.add_table(rows=len(quad_data) + 1, cols=5)
    format_table(quad_tbl, [1.4, 0.8, 0.9, 1.8, 1.9], quad_headers, quad_data, align_cols=['L', 'C', 'C', 'R', 'L'])

    # -------------------------------------------------------------
    # 7. TECHNICAL CHALLENGES & ENGINEERING SOLUTIONS
    # -------------------------------------------------------------
    add_header_styled(doc, "7. Technical Challenges & Engineering Solutions", level=1)
    
    challenges = [
        ("1. Temporal Data Leakage in Time-Series Features: ", 
         "Standard train/test splits or naive rolling means inadvertently allow future data to touch features, producing falsely optimistic evaluations. "
         "Solution: Strictly shifted all lag terms (t-1w, t-2w, etc.) and rolling windows by 1 period, and implemented Rolling-Origin Cross-Validation mimicking real-world weekly forecasting."),
        ("2. High-Entropy Unstructured Text in Catalog Master: ", 
         "Raw transaction records contained dirty, unstandardized product descriptions with no department categories. "
         "Solution: Engineered an automated NLP keyword parser that mapped text into 5 standard retail categories (Kitchen & Dining, Home Decor, Storage, Seasonal, Furnishings)."),
        ("3. The 'Black-Box' Trust Problem in Inventory Operations: ", 
         "Warehouse managers and finance directors reject purely algorithmic purchase order commands if they cannot understand the underlying logic. "
         "Solution: Decoupled ML demand prediction from deterministic inventory mechanics. The 2x2 matrix relies on transparent lead-time math and exact rupee calculations."),
        ("4. Streamlit Cloud Runtime & Dependency Deprecations: ", 
         "Encountered Pandas resampling deprecation errors (resample('M')) and missing XGBoost dependencies during cloud deployment. "
         "Solution: Refactored monthly aggregation to universal dt.to_period('M') period groupings and implemented safe try/except fallback wrappers in src/forecast.py.")
    ]
    for c_title, c_desc in challenges:
        p_c = doc.add_paragraph(style='List Bullet')
        p_c.paragraph_format.space_after = Pt(4)
        p_c.paragraph_format.line_spacing = 1.15
        r_ct = p_c.add_run(c_title)
        r_ct.font.name = 'Calibri'
        r_ct.font.bold = True
        r_ct.font.color.rgb = RGBColor(15, 23, 42)
        r_cd = p_c.add_run(c_desc)
        r_cd.font.name = 'Calibri'
        r_cd.font.color.rgb = RGBColor(51, 65, 85)

    # -------------------------------------------------------------
    # 8. SKILLS ACQUIRED & COMPETENCY DEVELOPMENT
    # -------------------------------------------------------------
    add_header_styled(doc, "8. Skills Acquired & Professional Competencies", level=1)
    skills = [
        "Production Data Engineering: Designing reproducible star schemas, automated data cleaning, and feature pipelines.",
        "Advanced Time-Series Machine Learning: Rolling-origin backtesting, feature engineering, LightGBM/XGBoost tuning, and WAPE/MAPE metrics.",
        "Supply Chain Analytics & Decision Science: Lead time modeling, safety stock gap computation, and working capital risk quantification.",
        "Full-Stack Analytics Productization: 7-page interactive Streamlit dashboard development, Plotly graphics, and FastAPI REST APIs.",
        "Consulting & Stakeholder Communication: Translating complex mathematical algorithms into rupee financial impacts and executive slide decks."
    ]
    for s in skills:
        p_s = doc.add_paragraph(style='List Bullet')
        p_s.paragraph_format.space_after = Pt(3)
        p_s.paragraph_format.line_spacing = 1.15
        r_s = p_s.add_run(s)
        r_s.font.name = 'Calibri'
        r_s.font.size = Pt(9.5)
        r_s.font.color.rgb = RGBColor(51, 65, 85)

    # -------------------------------------------------------------
    # 9. CURRENT PROGRESS & NEXT STEPS
    # -------------------------------------------------------------
    add_header_styled(doc, "9. Current Progress, Ongoing Work & Strategic Next Steps", level=1)
    p_cur = doc.add_paragraph()
    p_cur.paragraph_format.line_spacing = 1.15
    p_cur.paragraph_format.space_after = Pt(8)
    p_cur.add_run(
        "As this is an ongoing industrial internship, all core technical milestones (M1 to M4) have been fully developed, "
        "validated, and deployed. Current and upcoming focus areas include:"
    )

    next_steps = [
        ("Current Active Status: ", "The 7-page Streamlit dashboard and FastAPI service are operational and actively serving predictions."),
        ("Lead Time Sensitivity Control: ", "Implementing an interactive slider in the Streamlit UI allowing warehouse managers to simulate what-if supplier delays (+7 days, +14 days) and observe real-time risk quadrant shifts."),
        ("Automated Monthly Cron Pipeline: ", "Scheduling monthly batch executions of src/pipeline.py and src/risk.py as fresh inventory snapshot CSVs arrive from the warehouse."),
        ("Clearance Promotion Campaign: ", "Assisting NorthBay Living's merchandising lead in rolling out promotional discounts on the top 45 clearance candidate SKUs to liquidate the ₹1,000,800.85 in trapped working capital.")
    ]
    for ns_title, ns_desc in next_steps:
        p_ns = doc.add_paragraph(style='List Bullet')
        p_ns.paragraph_format.space_after = Pt(3)
        p_ns.paragraph_format.line_spacing = 1.15
        r_nst = p_ns.add_run(ns_title)
        r_nst.font.name = 'Calibri'
        r_nst.font.bold = True
        r_nst.font.color.rgb = RGBColor(15, 23, 42)
        r_nsd = p_ns.add_run(ns_desc)
        r_nsd.font.name = 'Calibri'
        r_nsd.font.color.rgb = RGBColor(51, 65, 85)

    # -------------------------------------------------------------
    # 10. VERIFICATION & ARTIFACT REGISTRY
    # -------------------------------------------------------------
    add_header_styled(doc, "10. Project Verification Record & Submission Artifacts", level=1)
    p_v = doc.add_paragraph()
    p_v.paragraph_format.line_spacing = 1.15
    p_v.paragraph_format.space_after = Pt(8)
    p_v.add_run(
        "The academic faculty, mentor review board, and stakeholders can independently audit and inspect all project deliverables "
        "at the official repository and hosted interfaces below:"
    )

    verif_headers = ["Item / Deliverable", "Location / Link", "Description"]
    verif_data = [
        ["Public Git Repository", "https://github.com/codexboy0417/demand-inventory-intelligence", "Complete production source code, notebooks, and reports."],
        ["Interactive Dashboard", "app/main.py (Streamlit Community Cloud)", "7-Page interactive UI with filters, charts, and action tables."],
        ["Scoring REST Service", "service/api.py (FastAPI / Swagger UI)", "Real-time single SKU and batch scoring endpoints."],
        ["Single Jupyter Notebook", "notebooks/project_foresight_complete_ml_pipeline.ipynb", "Complete 15-cell end-to-end reproducible pipeline."],
        ["Executive Presentation", "reports/executive_presentation.md", "10-slide executive readout deck for operations and finance."],
        ["Data Quality & EDA Memo", "reports/eda_insight_memo.md", "Detailed data quality findings, demand patterns, and Pareto rules."],
        ["Decision Matrix Output", "reports/inventory_risk_decision_matrix.csv", "Full 200 SKU risk scoring results with rupee values."],
        ["Terminal Execution Guide", "steps.txt", "Step-by-step reproduction commands from installation to launch."]
    ]
    verif_tbl = doc.add_table(rows=len(verif_data) + 1, cols=3)
    format_table(verif_tbl, [1.6, 2.7, 2.5], verif_headers, verif_data)

    p_end = doc.add_paragraph()
    p_end.paragraph_format.space_before = Pt(16)
    p_end.paragraph_format.space_after = Pt(0)
    p_end.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_end = p_end.add_run("― End of Internship Working Report ―")
    r_end.font.name = 'Calibri'
    r_end.font.size = Pt(9.5)
    r_end.font.italic = True
    r_end.font.color.rgb = RGBColor(148, 163, 184)

    # Save documents
    os.makedirs('reports', exist_ok=True)
    docx_path1 = os.path.join('reports', 'Internship_Working_Report_Ashit_Upadhyay.docx')
    docx_path2 = 'Internship_Working_Report_Ashit_Upadhyay.docx'
    
    doc.save(docx_path1)
    doc.save(docx_path2)
    
    print(f"Successfully generated Word document at: {docx_path1}")
    print(f"Successfully generated Word document at: {docx_path2}")
    return docx_path1

if __name__ == '__main__':
    build_internship_report()
