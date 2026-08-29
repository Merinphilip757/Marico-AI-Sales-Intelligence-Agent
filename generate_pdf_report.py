"""
PDF Report Generator for Marico Sales Intelligence Case Study
Generates an executive-ready, highly formatted multi-page PDF report using ReportLab.
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
            self.drawString(54, letter[1] - 36, "MARICO SALES INTELLIGENCE AGENT — FINAL COMMERCIAL ASSESSMENT")
            self.drawRightString(letter[0] - 54, letter[1] - 36, "CONFIDENTIAL")
            self.setStrokeColor(colors.HexColor("#CBD5E0"))
            self.setLineWidth(0.5)
            self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)

        # Footer (all pages)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 30, page_text)
        self.drawString(54, 30, "Marico Information Classification: Official | Kingdom of Saudi Arabia")
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(54, 42, letter[0] - 54, 42)
        self.restoreState()

def create_final_report_pdf(output_filename="Marico_Sales_Intelligence_Final_Report.pdf"):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
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
        fontSize=24,
        leading=28,
        textColor=primary_color,
        spaceAfter=10
    )

    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=accent_color,
        spaceAfter=20
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=primary_color,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=accent_color,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=dark_text,
        spaceAfter=6
    )

    body_bold = ParagraphStyle(
        "Body_Bold",
        parent=body_style,
        fontName="Helvetica-Bold"
    )

    callout_style = ParagraphStyle(
        "Callout_Text",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=12,
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

    # =========================================================================
    # COVER / HEADER BLOCK
    # =========================================================================
    story.append(Paragraph("MARICO COMMERCIAL INTELLIGENCE & ACTION REPORT", title_style))
    story.append(Paragraph("End-to-End Diagnostic, Root Cause Analysis & Strategic Prescriptions", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=primary_color, spaceAfter=15))

    # Meta Box
    meta_data = [
        [
            Paragraph("<b>Target Market:</b> KSA Modern Trade (8 Chains)", table_cell_style),
            Paragraph("<b>Analyzed Records:</b> 14,416 Transactions", table_cell_style),
            Paragraph("<b>Classification:</b> Official Commercial Diagnostic", table_cell_style)
        ],
        [
            Paragraph("<b>Brands Evaluated:</b> 11 Brands (Marico, Parachute, + 9 Competitors)", table_cell_style),
            Paragraph("<b>Categories:</b> Hair Oils, Hair Creams, Shampoo", table_cell_style),
            Paragraph("<b>Report Generated:</b> Q1 2024 Strategic Planning", table_cell_style)
        ]
    ]
    t_meta = Table(meta_data, colWidths=[2.2*inch, 2.3*inch, 2.5*inch])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), light_bg),
        ('BOX', (0,0), (-1,-1), 1, border_color),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 14))

    # =========================================================================
    # 1. EXECUTIVE SUMMARY & WHERE WE HAVE LEFT OFF
    # =========================================================================
    story.append(Paragraph("1. Executive Summary & Where We Have Left Off", h1_style))
    story.append(Paragraph(
        "Our analytical pipeline has successfully ingested, harmonized, and modeled the entire multi-source FMCG dataset comprising <b>14,416 records</b> across 8 top retail accounts (BinDawood, Carrefour, Danube, Lulu, Nesto, Othaim, Panda, Tamimi), 3 personal care categories, and 11 competing brands over a full 12-month annual cycle.",
        body_style
    ))
    story.append(Paragraph(
        "The overall KSA market secondary turnover reached <b>437.65 Million SAR</b> (8.98 Million units). The Marico Portfolio (<b>Marico</b> and <b>Parachute</b>) generated <b>78.80 Million SAR</b> in secondary EPOS sales, achieving an <b>18.01% value market share</b> (17.91% volume share).",
        body_style
    ))

    # Scorecard Table
    scorecard_data = [
        [Paragraph("Commercial Metric", table_header_style), Paragraph("Total Market", table_header_style), Paragraph("Marico Portfolio", table_header_style), Paragraph("Portfolio Performance", table_header_style)],
        [Paragraph("EPOS Secondary Sales", table_cell_bold), Paragraph("437,647,472 SAR", table_cell_style), Paragraph("78,804,438 SAR", table_cell_style), Paragraph("<b>18.01%</b> Value Share", table_cell_style)],
        [Paragraph("Internal Sell-In Pipeline", table_cell_bold), Paragraph("370,425,796 SAR", table_cell_style), Paragraph("68,001,373 SAR", table_cell_style), Paragraph("<b>18.36%</b> Pipeline Share", table_cell_style)],
        [Paragraph("Volume Sold (Units)", table_cell_bold), Paragraph("8,976,967 Units", table_cell_style), Paragraph("1,607,458 Units", table_cell_style), Paragraph("<b>17.91%</b> Volume Share", table_cell_style)],
        [Paragraph("Fair Share Revenue Gap", table_cell_bold), Paragraph("437.65M SAR Benchmark", table_cell_style), Paragraph("2,438,229 SAR Headroom", table_cell_style), Paragraph("<b>+0.56%</b> Market Share Growth Prize", table_cell_style)],
    ]
    t_score = Table(scorecard_data, colWidths=[2.0*inch, 1.7*inch, 1.7*inch, 1.8*inch])
    t_score.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_score)
    story.append(Spacer(1, 14))

    # =========================================================================
    # 2. ROOT CAUSE DIAGNOSIS: WHY WE FALL ON SPECIFIC PRODUCTS & ACCOUNTS
    # =========================================================================
    story.append(Paragraph("2. Root Cause Diagnosis: Why We Fall Behind", h1_style))
    story.append(Paragraph(
        "A rigorous cross-sectional econometric and competitive analysis reveals <b>four fundamental drivers</b> explaining why volume and share have lagged in specific products and retail channels:",
        body_style
    ))

    # Reason 1
    story.append(Paragraph("A. The Shampoo Competitive Intensity & Margin Drag", h2_style))
    story.append(Paragraph(
        "• <b>Heavy Promotional Pressure</b>: Competitors (Pantene, Head & Shoulders, Clear, L'Oreal) sell <b>55% to 60%</b> of their total shampoo volume on deep promotions.<br/>"
        "• <b>Price Index Mismatch</b>: Parachute/Marico in Shampoo sits at an RPI of <b>98.2</b>. In a highly elastic category (PED = -1.10), sitting near parity without high-frequency ATL visibility causes consumers to switch to heavily promoted multinationals.",
        body_style
    ))

    # Reason 2
    story.append(Paragraph("B. Account Under-Indexing & Visibility Voids in Key Chains", h2_style))
    story.append(Paragraph(
        "• <b>Tamimi Drag (1.06 Million SAR Headroom Gap)</b>: Marico's market share in Tamimi is only <b>16.05%</b> (Fair Share Index 89.2) compared to the 18.01% market benchmark, driven by weak secondary off-shelf displays.<br/>"
        "• <b>Panda Under-Indexing (595k SAR Gap)</b>: Despite Panda being the largest hypermarket chain in KSA (CDI 104.7), Marico captures only <b>16.97%</b> share (FSI 94.2) due to suboptimal Gondola Endcap share.",
        body_style
    ))

    # Reason 3
    story.append(Paragraph("C. The Margin-Dilutive 'BOGO' Promotion Trap", h2_style))
    story.append(Paragraph(
        "• <b>Deep Margin Destruction</b>: <b>Buy One Get One (BOGO)</b> delivers the highest volume lift (+47.9%), but incurs a catastrophic <b>-70.8% Return on Trade Spend (ROI)</b> because giving away 50% discount exceeds incremental gross profit by 22.2M SAR.<br/>"
        "• <b>Ineffective in Inelastic Categories</b>: Hair Oils is price-inelastic (PED = -0.75). Running BOGO on Hair Oils simply subsidizes existing loyal buyers rather than attracting new households.",
        body_style
    ))

    # Reason 4
    story.append(Paragraph("D. Pipeline Inventory Bullwhip & Stock Imbalance", h2_style))
    story.append(Paragraph(
        "• <b>Distributor Lag</b>: Lead-lag modeling confirms that Sell-In leads EPOS Sell-Out with <b>r = 0.9998 at Lag 0</b> and <b>r = 0.8394 at Lag 1</b>. Rapid replenishment creates inventory spikes in Q4 (198 days cover in Jan) that risk shelf stagnation if not cleared before the mid-year summer surge.",
        body_style
    ))
    story.append(Spacer(1, 10))

    # =========================================================================
    # 3. WHAT WE HAVE TO IMPROVE & HOW TO IMPROVE (ACTIONABLE STRATEGY)
    # =========================================================================
    story.append(Paragraph("3. Strategic Roadmap: How We Can Improve", h1_style))
    story.append(Paragraph(
        "To capture the <b>2.44 Million SAR fair-share headroom</b> and accelerate portfolio growth to <b>19.5%+ market share</b>, Marico must execute five targeted interventions:",
        body_style
    ))

    # Strategy Table
    strategy_data = [
        [Paragraph("Strategic Pillar", table_header_style), Paragraph("Current Problem", table_header_style), Paragraph("Prescriptive Solution", table_header_style), Paragraph("Financial Impact", table_header_style)],
        [
            Paragraph("<b>1. RPI Pricing Corridors</b>", table_cell_bold),
            Paragraph("Shampoo over-indexed vs promo competition; Hair Oils risk of under-pricing.", table_cell_style),
            Paragraph("• Lock Hair Oils RPI at <b>99–106</b> (Max Rev: 103).<br/>• Re-align Shampoo RPI to <b>96.0</b> with targeted value packs.", table_cell_style),
            Paragraph("<b>+480,000 SAR</b> Net Margin Gain", table_cell_style)
        ],
        [
            Paragraph("<b>2. Trade Spend Re-allocation</b>", table_cell_bold),
            Paragraph("BOGO margin destruction (-70.8% ROI) in habitual categories.", table_cell_style),
            Paragraph("• Eliminate BOGO in Hair Oils.<br/>• Scale <b>Flat 2 SAR Off (+124.7% ROI)</b> and <b>25% Extra Volume</b> packs.", table_cell_style),
            Paragraph("<b>+1,250,000 SAR</b> Spend Efficiency", table_cell_style)
        ],
        [
            Paragraph("<b>3. Store Activation & ATL</b>", table_cell_bold),
            Paragraph("Under-indexing in Tamimi (89.2 FSI) & Panda (94.2 FSI).", table_cell_style),
            Paragraph("• Allocate 500k SAR trade budget to secure <b>Endcaps & Island Displays</b> in top 50 Panda & Tamimi stores.<br/>• Synchronize localized digital screens with payday cycles.", table_cell_style),
            Paragraph("<b>+1,658,000 SAR</b> Revenue Recovery", table_cell_style)
        ],
        [
            Paragraph("<b>4. Weighted Distribution</b>", table_cell_bold),
            Paragraph("Distribution voids in premium & hypermarket SKUs.", table_cell_style),
            Paragraph("• Expand listing breadth in Panda (+1% WD = +0.085% Market Share).<br/>• Secure secondary checkout facings for 75ml & 140ml Creams.", table_cell_style),
            Paragraph("<b>+213,000 SAR</b> Panda Listing Prize", table_cell_style)
        ],
        [
            Paragraph("<b>5. S&OP Synchronization</b>", table_cell_bold),
            Paragraph("High Q1 inventory overhang (198 days) vs summer stockout risk.", table_cell_style),
            Paragraph("• Run Q1 secondary off-take blitz to bring stock cover to 45 days.<br/>• Ramp Sell-In starting March to support May–July peak.", table_cell_style),
            Paragraph("Zero Mid-Year Stockouts", table_cell_style)
        ],
    ]
    t_strat = Table(strategy_data, colWidths=[1.6*inch, 1.8*inch, 2.3*inch, 1.5*inch])
    t_strat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), accent_color),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_strat)
    story.append(Spacer(1, 14))
    story.append(Paragraph("4. 90-Day Executive Implementation Roadmap", h1_style))
    
    roadmap_data = [
        [Paragraph("Phase", table_header_style), Paragraph("Timeline", table_header_style), Paragraph("Key Milestone & Execution Deliverables", table_header_style)],
        [
            Paragraph("<b>Phase 1: Trade Spend Shift</b>", table_cell_bold),
            Paragraph("Days 1 – 30", table_cell_style),
            Paragraph("Cancel margin-dilutive BOGO schemes on Hair Oils. Re-allocate 350,000 SAR into Flat 2 SAR Off and contract Endcaps in Tamimi & Panda.", table_cell_style)
        ],
        [
            Paragraph("<b>Phase 2: Pricing & RPI Re-alignment</b>", table_cell_bold),
            Paragraph("Days 31 – 60", table_cell_style),
            Paragraph("Re-align Shampoo RPI to 96.0 against Pantene and Clear. Defend Parachute Hair Oils 101–103 corridor. Launch 25% Extra Volume value packs.", table_cell_style)
        ],
        [
            Paragraph("<b>Phase 3: Pre-Summer Sell-In Build</b>", table_cell_bold),
            Paragraph("Days 61 – 90", table_cell_style),
            Paragraph("Synchronize distributor orders to achieve 45 days stock cover ahead of May-July peak demand surge, preventing stockouts.", table_cell_style)
        ]
    ]
    t_road = Table(roadmap_data, colWidths=[1.8*inch, 1.2*inch, 4.2*inch])
    t_road.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_road)
    story.append(Spacer(1, 14))

    # Sign-off Callout Box
    signoff_data = [[
        Paragraph(
            "<b>Conclusion & Executive Commitment:</b> By executing this targeted commercial roadmap, Marico will systematically capture <b>+2.44 Million SAR</b> in uncaptured fair-share revenue, re-claim share in Panda and Tamimi, eliminate <b>1.25M SAR</b> of wasteful BOGO trade discounting, and elevate total portfolio market share from <b>18.01% to 19.5%+</b>.",
            callout_style
        )
    ]]
    t_sign = Table(signoff_data, colWidths=[7.2*inch])
    t_sign.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EBF8FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#3182CE")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_sign)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated final PDF report: {output_filename}")

if __name__ == "__main__":
    create_final_report_pdf()
