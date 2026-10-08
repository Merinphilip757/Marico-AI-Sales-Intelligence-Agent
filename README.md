# Marico-Inspired AI Sales Intelligence & Decision Support System 🚀

An enterprise-grade AI-driven **Sales Intelligence & Decision Support System** designed to process diverse FMCG commercial data streams (Internal Sell-In, EPOS Secondary Sell-Out, Category Market Shares, and Pricing/Scheme feeds) to deliver predictive, diagnostic, and prescriptive commercial intelligence.

---

## 🏗️ Architecture & Module Organization

```
salesiq -  marico/
├── Sell in & Sell out Dummy Data.xlsx    # Harmonized FMCG commercial dataset
├── sales_agent/                         # Core Python Analytics & AI Agent Package
│   ├── __init__.py                      # Package initialization & exports
│   ├── data_pipeline.py                 # Multi-source harmonization, price derivations, stock buffer
│   ├── forecaster.py                    # Secondary sales & offtake forecasting (ARDL Ridge, HHI)
│   ├── rpi_engine.py                    # Relative Price Index (RPI) & optimal corridor optimizer
│   ├── activation_optimizer.py          # EPOS store/chain activation targeting & budget allocation
│   ├── promotion_roi.py                 # BTL scheme evaluation, incremental lift & price elasticity
│   ├── distribution_engine.py           # Weighted Distribution (WD) quantification & listing simulator
│   └── agent.py                         # Natural language AI Sales Intelligence Agent core
├── app.py                               # Executive Streamlit Web App & What-If Scenario Simulator
├── test_agent.py                        # Automated Unit & Integration Test Suite (100% Pass)
├── run_analysis.py                      # Comprehensive CLI Batch Analyzer & Report Generator
├── marico_sales_intelligence_report.md  # Detailed Commercial & Econometric Strategy Report
└── README.md                            # Project Documentation & User Guide
```

---

## ⚡ Quick Start & Execution Guide

### 1. Run Automated Test Suite
To verify data pipeline integrity, econometric models, and AI agent responses:
```bash
python test_agent.py
```

### 2. Run Comprehensive CLI Analysis
To generate an end-to-end analytical breakdown of all 6 case study pillars in your terminal:
```bash
python run_analysis.py
```

### 3. Launch Interactive Executive Dashboard
To start the full-featured interactive Streamlit Web App & AI Assistant:
```bash
streamlit run app.py
```

---

## 📊 Analytical Scope & Mathematical Formulations

### 1. Secondary Sales Projection & Pipeline Dynamics
- **Transmission Equation**: $\text{Inventory}_{t} = \text{Inventory}_{t-1} + \text{SellIn}_{t} - \text{SellOut}_{t}$
- **Lead-Lag Cross-Correlation**: Sell-In leads EPOS Sell-Out with $r = 0.9998$ (Lag 0) and $r = 0.8394$ (Lag 1).
- **ARDL Ridge Model**: Projects 1 to 6 months forward secondary sales, cumulative inventory, and stock cover days to prevent stockouts during peak summer demand.

### 2. Offtakes & Market Share Projections Under Competitive Intensity
- **Market Concentration (HHI)**: $HHI = \sum (\text{MS}_i)^2 = 909.96$ (*Highly competitive market*).
- **Competitor Promotional Pressure**: Tracks the percentage of competitor volume sold on active promotions (55% to 60% across competitors).
- **Multi-Step Offtake Forecasting**: Decomposes baseline trend, seasonality, and promotional shocks to predict brand volume and value market shares.

### 3. Relative Price Index (RPI) Optimization
- **RPI Formulation**: $\text{RPI} = \left(\frac{\text{Brand Price}}{\text{Category Benchmark Price}}\right) \times 100$
- **Optimal Corridors Discovered**:
  - **Hair Oils**: Current RPI `101.2` | Optimal Revenue Corridor: `99 - 106` (Revenue max at `103`).
  - **Hair Creams**: Current RPI `99.3` | Optimal Revenue Corridor: `96 - 104` (Revenue max at `100`).
  - **Shampoo**: Current RPI `98.2` | Optimal Revenue Corridor: `90 - 100` (Revenue max at `96`).

### 4. Store / Chain-Level Activation Targeting (ATL & Visibility)
- **Fair Share Index (FSI)**: $\text{FSI} = \left(\frac{\text{Marico Share in Chain}}{\text{Marico Market Share}}\right) \times 100$
- **Opportunity Revenue Gap (SAR)**: $\text{Gap} = \max(0, \text{Benchmark Share} - \text{Current Share}) \times \text{Chain Category Size}$
- **Top Priority Accounts**:
  - **Tamimi**: 1.06M SAR Revenue Opportunity (FSI 89.2) -> *Deploy Endcaps & Gondola Headers*.
  - **Panda**: 595k SAR Revenue Opportunity (FSI 94.2) -> *Deploy Secondary Island Displays & Localized ATL Signage*.

### 5. Spend ROI & Promotional Schemes (BTL Optimization)
- **Financial Metric**: $\text{Trade ROI (\%)} = \left(\frac{\text{Incremental Gross Margin} - \text{Trade Discount Cost}}{\text{Trade Discount Cost}}\right) \times 100$
- **High-ROI Winner**: **Flat 2 SAR Off** delivers **+124.7% Spend ROI** with +25.8% volume lift.
- **Margin-Dilutive Trap**: **Buy One Get One (BOGO)** delivers **-70.8% ROI** due to excessive 50% discount depth.
- **Category Elasticity Guidance**: Hair Oils is Price Inelastic ($PED = -0.75$), requiring Value-Add promotions (25% Extra Volume) over deep discounts; Shampoo is Price Elastic ($PED = -1.10$).

### 6. Weighted Distribution (WD) Impact Quantification
- **Distribution Elasticity**: $\Delta \text{Market Share} = 0.085 \times \Delta \text{WD}$
- **Rule of Thumb**: Every +1.0% increase in Weighted Distribution generates an estimated **+0.085% gain in Category Market Share**.
- **Expansion Prize**: Expanding listing breadth and secondary placement in Panda yields an incremental **+213,062 SAR** in annual revenue.

---

## 🤖 AI Sales Intelligence Decision Assistant

The agent incorporates natural language intent understanding, enabling commercial executives to ask questions such as:
- *"What is our projected secondary sales next quarter?"*
- *"What is the optimal RPI for Parachute in Hair Oils against Dabur and Vatika?"*
- *"Which retail chains should we target for ATL and visibility activation?"*
- *"Which BTL promotional scheme gives the highest ROI in Shampoo?"*
- *"What is the market share impact if we increase weighted distribution in Panda?"*

---
*Created for Marico Sales Intelligence Case Study.*
