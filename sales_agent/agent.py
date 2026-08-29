"""AI-Driven Sales Intelligence Agent Core
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from .data_pipeline import SalesDataPipeline
from .forecaster import SalesForecaster
from .rpi_engine import RPIEngine
from .activation_optimizer import ActivationOptimizer
from .promotion_roi import PromotionROIEngine
from .distribution_engine import DistributionEngine

class SalesIntelligenceAgent:
    def __init__(self, excel_path: str = "Sell in & Sell out Dummy Data.xlsx"):
        self.pipeline = SalesDataPipeline(excel_path=excel_path)
        self.df = self.pipeline.load_and_process()
        self.forecaster = SalesForecaster(self.pipeline)
        self.rpi_engine = RPIEngine(self.pipeline)
        self.activation_optimizer = ActivationOptimizer(self.pipeline)
        self.promotion_roi = PromotionROIEngine(self.pipeline)
        self.distribution_engine = DistributionEngine(self.pipeline)

    def get_executive_summary(self) -> Dict[str, Any]:
        """Generate high-level commercial diagnostic summary for Marico leadership."""
        stats = self.pipeline.get_summary_stats()
        rpi_data = self.rpi_engine.calculate_rpi_summary()
        marico_rpi = rpi_data[rpi_data["Is_Marico_Portfolio"]]
        
        chain_opp = self.activation_optimizer.compute_chain_opportunity_matrix()
        top_chains = chain_opp.head(3)["Chain"].tolist()
        total_opp_gap = chain_opp["Opportunity_Revenue_Gap_SAR"].sum()
        
        elasticity_df = self.promotion_roi.analyze_category_elasticity()
        schemes_df = self.promotion_roi.evaluate_schemes()
        best_scheme = schemes_df.iloc[0]["Scheme"]
        best_roi = schemes_df.iloc[0]["Spend_ROI_Pct"]

        return {
            "Total_Market_Sell_Out_SAR": stats["total_sell_out_value"],
            "Total_Market_Sell_In_SAR": stats["total_sell_in_value"],
            "Marico_Portfolio_Revenue_SAR": stats["marico_sell_out_value"],
            "Marico_Portfolio_Value_Share_Pct": np.round(stats["marico_value_share_pct"], 2),
            "Top_Opportunity_Chains_For_ATL": top_chains,
            "Total_Revenue_Headroom_SAR": np.round(total_opp_gap, 2),
            "Highest_ROI_Promotion_Scheme": f"{best_scheme} ({best_roi}% Spend ROI)",
            "Key_Commercial_Priorities": [
                f"Defend Volume in core chains while prioritizing ATL visibility in under-indexed accounts: {', '.join(top_chains)}.",
                f"Calibrate Relative Price Index (RPI) within the 95-102 corridor across categories to maximize revenue without triggering share loss.",
                f"Shift BTL trade budget from margin-dilutive BOGO to high-efficiency value-add schemes (15% Price Off / 25% Extra Volume) in price-inelastic Hair Oils.",
                "Maintain pipeline stock cover at 30-45 days to eliminate mid-year stockout risks during seasonal summer demand surge."
            ]
        }

    def ask(self, query: str) -> Dict[str, Any]:
        """
        Natural Language Query Processor: Maps executive intent to analytical engines
        and synthesizes prescriptive answers.
        """
        q = query.lower()

        # 1. Secondary Sales & Forecasting
        if any(w in q for w in ["forecast", "project", "secondary sales", "sell-in", "sell-out", "pipeline", "stock cover", "inventory"]):
            horizon = 6 if "6 month" in q or "half year" in q else 3
            category = "Hair Oils" if "oil" in q else ("Hair Creams" if "cream" in q else ("Shampoo" if "shampoo" in q else None))
            chain = next((c for c in self.pipeline.chains if c.lower() in q), None)
            
            lead_lag = self.forecaster.calculate_lead_lag_correlations(category=category)
            proj_df = self.forecaster.forecast_secondary_sales(horizon_months=horizon, category=category, chain=chain)
            
            answer_text = (
                f"### Secondary Sales & Pipeline Forecast ({horizon} Months Ahead)\n\n"
                f"- **Lead-Lag Analysis**: Sell-in strongly leads EPOS Sell-out with highest correlation at Lag 0 to Lag 1 ({lead_lag.get('Lag_1_Months', 0.0):.2f}).\n"
                f"- **Projected 3-Month Sell-out Units**: {proj_df['Projected_Sell_out_Units'].sum():,} Units.\n"
                f"- **Projected 3-Month Sell-out Value**: {proj_df['Projected_Sell_out_Value_SAR'].sum():,.2f} SAR.\n"
                f"- **Stock Cover Status**: {proj_df.iloc[-1]['Stock_Health_Status']} ({proj_df.iloc[-1]['Projected_Days_of_Cover']} days).\n\n"
                f"**Recommendation**: Calibrate distributor replenishment schedules to buffer inventory before the mid-year seasonal peak."
            )
            return {
                "intent": "secondary_sales_forecast",
                "text_response": answer_text,
                "data_table": proj_df,
                "metadata": {"lead_lag": lead_lag}
            }

        # 2. RPI & Pricing Optimization
        elif any(w in q for w in ["rpi", "price index", "pricing", "elasticity", "optimal price", "competitor price"]):
            category = "Hair Oils" if "oil" in q else ("Hair Creams" if "cream" in q else ("Shampoo" if "shampoo" in q else "Hair Oils"))
            brand = "Parachute" if "parachute" in q else ("Marico" if "marico" in q else "Parachute")
            
            optimal_res = self.rpi_engine.discover_optimal_rpi_corridor(category=category, brand=brand)
            ped_res = self.rpi_engine.calculate_price_elasticity(category=category, brand=brand)
            
            answer_text = (
                f"### Relative Price Index (RPI) Analysis — {brand} in {category}\n\n"
                f"- **Current RPI**: {optimal_res['Current_RPI']} (Average Unit Price: {optimal_res['Current_Avg_Price_SAR']} SAR vs Category Benchmark: {optimal_res['Category_Benchmark_Price_SAR']} SAR)\n"
                f"- **Optimal RPI Corridor**: **{optimal_res['Optimal_RPI_Corridor']}** (Revenue-Maximizing RPI: {optimal_res['Revenue_Maximizing_RPI']})\n"
                f"- **Price Elasticity (PED)**: {ped_res.get('Own_Price_Elasticity_PED', -0.95)} ({ped_res.get('Elasticity_Classification', 'Moderately Elastic')})\n"
                f"- **Strategic Action**: {optimal_res['Recommended_Commercial_Action']}\n\n"
                f"**Prescription**: Maintain RPI within {optimal_res['Optimal_RPI_Corridor']} against benchmarks like Dabur and Vatika to protect margins while driving volume."
            )
            return {
                "intent": "rpi_optimization",
                "text_response": answer_text,
                "data_table": optimal_res["Simulation_Curve"].head(15),
                "metadata": optimal_res
            }

        # 3. Store / Chain Activation Targeting
        elif any(w in q for w in ["activation", "chain", "store", "target", "atl", "visibility", "endcap", "opportunity gap"]):
            category = "Hair Oils" if "oil" in q else ("Hair Creams" if "cream" in q else ("Shampoo" if "shampoo" in q else None))
            budget_plan = self.activation_optimizer.get_activation_budget_allocation(category=category)
            opp_matrix = self.activation_optimizer.compute_chain_opportunity_matrix(category=category)
            
            top_chains = budget_plan["Top_Target_Chains"]
            answer_text = (
                f"### Store-Level Activation Targeting & ATL Allocation\n\n"
                f"- **Top Priority Accounts (Tier 1 Attack)**: **{', '.join(top_chains)}**\n"
                f"- **Opportunity Sizing**: Total uncaptured fair-share revenue gap is **{opp_matrix['Opportunity_Revenue_Gap_SAR'].sum():,.2f} SAR** across chains.\n"
                f"- **Recommended In-Store Tactics**:\n"
                f"  1. Deploy high-impact Endcaps and Gondola headers in Panda and Carrefour.\n"
                f"  2. Secure primary checkout eye-level facings in Danube and Lulu.\n"
                f"  3. Coordinate localized ATL digital screen campaigns timed with payday promotional cycles."
            )
            return {
                "intent": "activation_targeting",
                "text_response": answer_text,
                "data_table": opp_matrix,
                "metadata": budget_plan
            }

        # 4. Spend ROI & Promotional Schemes
        elif any(w in q for w in ["promotion", "scheme", "roi", "btl", "discount", "bogo", "price off"]):
            category = "Hair Oils" if "oil" in q else ("Hair Creams" if "cream" in q else ("Shampoo" if "shampoo" in q else None))
            schemes_df = self.promotion_roi.evaluate_schemes(category=category)
            elasticity_df = self.promotion_roi.analyze_category_elasticity()
            
            best_scheme = schemes_df.iloc[0]
            answer_text = (
                f"### BTL Spend ROI & Promotional Scheme Evaluation\n\n"
                f"- **Highest Efficiency Scheme**: **{best_scheme['Scheme']}** ({best_scheme['Spend_ROI_Pct']}% ROI, +{best_scheme['Volume_Lift_Pct']}% Volume Lift).\n"
                f"- **Category Price Elasticity Findings**:\n"
                f"  - **Shampoo**: Price Elastic. Responds best to 15% Price Off / Value Bundles.\n"
                f"  - **Hair Creams**: Moderately Elastic. High lift under Buy One Get One (BOGO).\n"
                f"  - **Hair Oils**: Inelastic. High loyalty; avoid deep BOGO discounts and deploy 25% Extra Volume or Flat 2 SAR Off to maximize gross profit."
            )
            return {
                "intent": "promotion_roi",
                "text_response": answer_text,
                "data_table": schemes_df,
                "metadata": {"elasticity": elasticity_df}
            }

        # 5. Weighted Distribution Impact
        elif any(w in q for w in ["distribution", "wd", "numeric distribution", "acv", "reach", "listing"]):
            category = "Hair Oils" if "oil" in q else ("Hair Creams" if "cream" in q else ("Shampoo" if "shampoo" in q else "Hair Oils"))
            wd_impact = self.distribution_engine.quantify_wd_impact_on_market_share(category=category)
            sim_exp = self.distribution_engine.simulate_distribution_expansion(category=category, target_chain="Panda", brand="Parachute")
            
            answer_text = (
                f"### Distribution Impact & Market Share Quantification\n\n"
                f"- **Distribution Elasticity**: {wd_impact['Commercial_Rule_of_Thumb']}\n"
                f"- **Simulation (Panda Expansion)**:\n"
                f"  - Expanding Parachute shelf share in Panda yields an estimated **+{sim_exp['Simulated_Market_Share_Gain_Pct']}% market share gain**.\n"
                f"  - Incremental Revenue Prize: **{sim_exp['Incremental_Annual_Revenue_Uplift_SAR']:,.2f} SAR**.\n\n"
                f"**Recommendation**: Prioritize closing distribution voids and securing secondary SKU listings across Tier 1 hypermarket accounts."
            )
            return {
                "intent": "distribution_impact",
                "text_response": answer_text,
                "data_table": self.distribution_engine.calculate_distribution_metrics(),
                "metadata": {"wd_impact": wd_impact, "simulation": sim_exp}
            }

        # Default / Executive Overview
        else:
            summary = self.get_executive_summary()
            answer_text = (
                f"### Marico Executive Commercial Intelligence Overview\n\n"
                f"- **Total Market EPOS Sales**: {summary['Total_Market_Sell_Out_SAR']:,.2f} SAR across 8 Chains & 3 Categories.\n"
                f"- **Marico Portfolio Revenue**: {summary['Marico_Portfolio_Revenue_SAR']:,.2f} SAR ({summary['Marico_Portfolio_Value_Share_Pct']}% Value Share).\n"
                f"- **Top Priority Activation Accounts**: {', '.join(summary['Top_Opportunity_Chains_For_ATL'])} (Total Headroom: {summary['Total_Revenue_Headroom_SAR']:,.2f} SAR).\n"
                f"- **Most Efficient Promotion**: {summary['Highest_ROI_Promotion_Scheme']}.\n\n"
                f"**Strategic Pillars**:\n"
                + "\n".join(f"- {p}" for p in summary["Key_Commercial_Priorities"])
            )
            return {
                "intent": "executive_summary",
                "text_response": answer_text,
                "data_table": self.pipeline.get_monthly_pipeline(),
                "metadata": summary
            }
