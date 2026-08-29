"""
Technical Documentation PDF Generator for Marico SalesIQ
Compiles Architecture, Data Processing Logic, and Model Assumptions into an executive-ready PDF.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, letter[1] - 36, "MARICO SALESIQ — ARCHITECTURE, DATA PROCESSING & ASSUMPTIONS")
            self.drawRightString(letter[0] - 54, letter[1] - 36, "TECHNICAL SPECIFICATION")
            self.setStrokeColor(colors.HexColor("#CBD5E0"))
            self.setLineWidth(0.5)
            self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)

        # Footer (all pages)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 30, page_text)
        self.drawString(54, 30, "Marico Sales Intelligence System Specification | Official Documentation")
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(54, 42, letter[0] - 54, 42)
        self.restoreState()

def create_documentation_pdf(output_filename="Marico_SalesIQ_Technical_Documentation.pdf"):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    primary_color = colors.HexColor("#0F2942")   # Marico Navy
    accent_color = colors.HexColor("#008080")    # Deep Teal
    warning_color = colors.HexColor("#C53030")   # Red
    dark_text = colors.HexColor("#2D3748")
    light_bg = colors.HexColor("#F7FAFC")
    border_color = colors.HexColor("#E2E8F0")

    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=primary_color,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        textColor=accent_color,
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=primary_color,
        spaceBefore=11,
        spaceAfter=5,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13,
        textColor=accent_color,
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=dark_text,
        spaceAfter=5
    )

    body_bold = ParagraphStyle(
        "Body_Bold",
        parent=body_style,
        fontName="Helvetica-Bold"
    )

    callout_style = ParagraphStyle(
        "Callout_Text",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor("#1A202C")
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=1 # Center
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10,
        textColor=dark_text
    )

    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=table_cell_style,
        fontName="Helvetica-Bold"
    )

    story = []

    # HEADER / TITLE BLOCK
    story.append(Paragraph("MARICO SALESIQ — SYSTEM DOCUMENTATION", title_style))
    story.append(Paragraph("Technical Specification: Architecture, Data Processing Logic & Model Assumptions", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceAfter=8))

    # Metadata Table
    meta_data = [
        [
            Paragraph("<b>System:</b> Marico SalesIQ Intelligence Platform", table_cell_style),
            Paragraph("<b>Target Market:</b> KSA Modern Trade (8 Retailers)", table_cell_style),
            Paragraph("<b>Classification:</b> Technical Specification", table_cell_style)
        ],
        [
            Paragraph("<b>Data Scope:</b> 14,416 Records (12 Months)", table_cell_style),
            Paragraph("<b>Categories:</b> Hair Oils, Creams, Shampoo", table_cell_style),
            Paragraph("<b>Brands:</b> Marico, Parachute (+9 Competitors)", table_cell_style)
        ]
    ]
    t_meta = Table(meta_data, colWidths=[2.3*inch, 2.4*inch, 2.5*inch])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), light_bg),
        ('BOX', (0,0), (-1,-1), 1, border_color),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 8))

    # SECTION 1: ARCHITECTURE
    story.append(Paragraph("1. System Architecture & Modular Design", h1_style))
    story.append(Paragraph(
        "Marico SalesIQ follows a <b>modular, decoupled multi-tier architecture</b> that isolates data ingestion, econometric modeling, cognitive agent reasoning, and presentation layers:",
        body_style
    ))

    arch_data = [
        [Paragraph("Architectural Layer", table_header_style), Paragraph("Component / File", table_header_style), Paragraph("Core Functional Capabilities", table_header_style)],
        [
            Paragraph("<b>1. Ingestion & Pipeline Layer</b>", table_cell_bold),
            Paragraph("<code>sales_agent/data_pipeline.py</code><br/><code>SalesDataPipeline</code>", table_cell_style),
            Paragraph("Sanitizes Excel inputs, derives per-unit sell-in/sell-out pricing, calculates macro/micro non-promo baselines, and constructs the unified <code>df_merged</code> master dataset (14,416 rows).", table_cell_style)
        ],
        [
            Paragraph("<b>2. Econometric Analytics Layer</b>", table_cell_bold),
            Paragraph("<code>sales_agent/</code><br/>• <code>forecaster.py</code><br/>• <code>rpi_engine.py</code><br/>• <code>activation_optimizer.py</code><br/>• <code>promotion_roi.py</code><br/>• <code>distribution_engine.py</code>", table_cell_style),
            Paragraph("Five specialized mathematical engines executing ARDL Ridge forecasting, log-log price elasticity regressions, CDI/BDI/FSI fair share opportunity matrices, BTL trade spend ROI models, and ACV weighted distribution elasticity models.", table_cell_style)
        ],
        [
            Paragraph("<b>3. AI Intelligence & Orchestration</b>", table_cell_bold),
            Paragraph("<code>sales_agent/agent.py</code><br/><code>SalesIntelligenceAgent</code>", table_cell_style),
            Paragraph("Central natural language query router and decision engine that maps executive questions to underlying econometric models and synthesizes prescriptive textual and tabular answers.", table_cell_style)
        ],
        [
            Paragraph("<b>4. Presentation & Delivery Layer</b>", table_cell_bold),
            Paragraph("• <code>app.py</code> (Streamlit Web App)<br/>• <code>run_analysis.py</code> (CLI Batch)<br/>• <code>generate_pdf_report.py</code>", table_cell_style),
            Paragraph("Interactive 8-tab executive cockpit featuring Plotly dark visualizations, scenario sliders, chat assistant, and one-click PDF generation.", table_cell_style)
        ],
    ]
    t_arch = Table(arch_data, colWidths=[1.8*inch, 2.0*inch, 3.4*inch])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 8))

    # SECTION 2: DATA PROCESSING LOGIC
    story.append(Paragraph("2. Data Processing Logic & Mathematical Formulations", h1_style))
    story.append(Paragraph(
        "The ingestion and feature engineering pipeline processes raw commercial feeds through a strict 6-stage lifecycle:",
        body_style
    ))

    logic_points = [
        "<b>1. Data Sanitization:</b> Corrects vendor naming inconsistencies (e.g. standardizes <code>TRESemm</code> to <code>TRESemme</code>) and trims string whitespace across categorical columns.",
        "<b>2. Unit Price Derivation:</b> Derives real transaction unit price before merging: <code>Sell_in_Price = Sell-in Value / Sell-in Units</code> and <code>Sell_out_Price = Sell-out Value / Sell-out Units</code>.",
        "<b>3. Multi-Key Harmonization:</b> Merges Sell-In and EPOS Sell-Out using composite key <code>[Month, Chain, Category, Brand, SKU]</code> across 14,416 rows with 100% record retention.",
        "<b>4. Pipeline Inventory Dynamics:</b> Computes monthly channel stock shifts via <code>Inventory_Delta = Sell_in_Units - Sell_out_Units</code> and evaluates cumulative stock cover days.",
        "<b>5. Non-Promotional Baseline Decomposition:</b> For each SKU-Chain, average volume during <code>Scheme == 'No Promotion'</code> forms baseline volume. Fallback hierarchical macro-baselines prevent zero division. Incremental volume is computed as: <code>Incremental_Units = max(0, Sell_out_Units - Baseline_Units)</code>.",
        "<b>6. Relative Price Index (RPI):</b> Benchmarks brand price against the chain-category average price: <code>RPI = (Brand_Price / Category_Avg_Price) * 100</code>."
    ]
    for lp in logic_points:
        story.append(Paragraph(f"• {lp}", body_style))

    story.append(Spacer(1, 4))

    # Formulations Table
    form_data = [
        [Paragraph("Analytical Metric", table_header_style), Paragraph("Mathematical Formulation", table_header_style), Paragraph("Commercial Purpose", table_header_style)],
        [
            Paragraph("<b>Fair Share Index (FSI)</b>", table_cell_bold),
            Paragraph("<code>FSI = (Chain_Market_Share / Benchmark_Share) * 100</code>", table_cell_style),
            Paragraph("Identifies under-indexed accounts (&lt;98 FSI) requiring ATL marketing and Endcap visibility.", table_cell_style)
        ],
        [
            Paragraph("<b>Opportunity Gap (SAR)</b>", table_cell_bold),
            Paragraph("<code>Gap = max(0, Benchmark_Share - Chain_Share) * Chain_Cat_Turnover</code>", table_cell_style),
            Paragraph("Quantifies uncaptured revenue in SAR if the brand achieves fair-share portfolio share.", table_cell_style)
        ],
        [
            Paragraph("<b>Price Elasticity (PED)</b>", table_cell_bold),
            Paragraph("<code>ln(Units) = α + β * ln(Price) + ε  (PED = β)</code>", table_cell_style),
            Paragraph("Determines if category demand is Inelastic (Hair Oils: -0.75) or Elastic (Shampoo: -1.10).", table_cell_style)
        ],
        [
            Paragraph("<b>Trade Spend ROI (%)</b>", table_cell_bold),
            Paragraph("<code>ROI = [(Incremental_Rev * 45% - Trade_Discount) / Trade_Discount] * 100</code>", table_cell_style),
            Paragraph("Evaluates net gross profit return per SAR of BTL promotional discount spend.", table_cell_style)
        ],
        [
            Paragraph("<b>Weighted Distribution (WD) Elasticity</b>", table_cell_bold),
            Paragraph("<code>ΔMarket_Share = 0.085 * ΔWD%</code>", table_cell_style),
            Paragraph("Rule of thumb: Every +1.0% increase in Weighted Distribution yields +0.085% gain in market share.", table_cell_style)
        ],
    ]
    t_form = Table(form_data, colWidths=[1.8*inch, 3.2*inch, 2.2*inch])
    t_form.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), accent_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_form)
    story.append(Spacer(1, 8))

    # SECTION 3: ASSUMPTIONS
    story.append(Paragraph("3. Key Model Assumptions & Commercial Hypotheses", h1_style))
    story.append(Paragraph(
        "To ensure statistical validity and commercial realism, the models incorporate the following standard parameters:",
        body_style
    ))

    assump_data = [
        [Paragraph("Parameter / Domain", table_header_style), Paragraph("Standard Value / Assumption", table_header_style), Paragraph("Commercial Rationale & Industry Alignment", table_header_style)],
        [
            Paragraph("<b>Gross Margin Benchmark</b>", table_cell_bold),
            Paragraph("<b>45.0%</b> of Incremental Revenue", table_cell_style),
            Paragraph("Standard FMCG personal care gross margin threshold after deducting COGS and variable costs.", table_cell_style)
        ],
        [
            Paragraph("<b>Replenishment Lead-Lag</b>", table_cell_bold),
            Paragraph("<b>0 to 1 Month</b> Pull-Through (r = 0.84 – 0.99)", table_cell_style),
            Paragraph("Verified via cross-correlation; distributor sell-in synchronizes with retail EPOS offtakes within 0–30 days.", table_cell_style)
        ],
        [
            Paragraph("<b>Price Elasticity Kink</b>", table_cell_bold),
            Paragraph("Asymmetric demand penalty when RPI &gt; 100", table_cell_style),
            Paragraph("FMCG consumers exhibit sharp drop-off when pricing exceeds benchmark competitor levels.", table_cell_style)
        ],
        [
            Paragraph("<b>Trade Scheme Discount Mechanics</b>", table_cell_bold),
            Paragraph("• 15% Price Off: 15% discount<br/>• BOGO: 50% discount<br/>• Flat 2 SAR: 2.0 SAR/unit<br/>• 25% Extra Vol: 20% effective cost", table_cell_style),
            Paragraph("Models true brand and retailer funding requirements for BTL trade promotion schemes.", table_cell_style)
        ],
        [
            Paragraph("<b>Pipeline Health Thresholds</b>", table_cell_bold),
            Paragraph("• High Stockout Risk: &lt; 15 Days<br/>• Optimal Buffer: 15 – 90 Days<br/>• Excess Overhang: &gt; 90 Days", table_cell_style),
            Paragraph("Buffers distributor stock to support May–July summer demand surge without creating dead inventory.", table_cell_style)
        ],
        [
            Paragraph("<b>Portfolio Boundary</b>", table_cell_bold),
            Paragraph("Marico Portfolio = <code>Marico</code> & <code>Parachute</code>", table_cell_style),
            Paragraph("Harmonizes internal brand portfolio against 9 external multinational and regional competitors.", table_cell_style)
        ]
    ]
    t_assump = Table(assump_data, colWidths=[1.8*inch, 2.2*inch, 3.2*inch])
    t_assump.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_assump)
    story.append(Spacer(1, 8))

    # SECTION 4: HOW TO DELIVER
    story.append(Paragraph("4. How to Generate & Send as PDF Format", h1_style))
    
    delivery_box = [[
        Paragraph(
            "<b>Delivery Options for Evaluators / Stakeholders:</b><br/>"
            "1. <b>Direct Technical PDF:</b> Run <code>python generate_documentation_pdf.py</code> in the terminal to generate <code>Marico_SalesIQ_Technical_Documentation.pdf</code>.<br/>"
            "2. <b>Commercial Strategy PDF:</b> Run <code>python generate_pdf_report.py</code> to generate <code>Marico_Sales_Intelligence_Final_Report.pdf</code>.<br/>"
            "3. <b>Interactive Web App Export:</b> Run <code>streamlit run app.py</code>, open <b>Tab 8 (Final Executive Report)</b>, and click <b>Download Official Report (PDF)</b>.<br/>"
            "4. <b>Distribution:</b> Both generated PDF files are self-contained, publication-ready vector documents that can be attached directly to email or uploaded to your submission portal.",
            callout_style
        )
    ]]
    t_del = Table(delivery_box, colWidths=[7.2*inch])
    t_del.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EBF8FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#3182CE")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_del)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated documentation PDF: {output_filename}")

if __name__ == "__main__":
    create_documentation_pdf()
