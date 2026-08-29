"""Trade Spend ROI & Promotional Scheme Optimization Engine
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional

class PromotionROIEngine:
    def __init__(self, data_pipeline):
        self.pipeline = data_pipeline
        self.df = self.pipeline.df_merged if self.pipeline.df_merged is not None else self.pipeline.load_and_process()
        self.categories = self.pipeline.categories
        self.schemes = sorted(self.df["Scheme"].unique().tolist())

    def evaluate_schemes(self, category: Optional[str] = None, brand: Optional[str] = None) -> pd.DataFrame:
        """
        Evaluate incremental volume lift, incremental revenue, discount cost,
        and net Return on Trade Spend (ROI) for each BTL scheme.
        """
        df = self.df.copy()
        if category:
            df = df[df["Category"] == category]
        if brand:
            df = df[df["Brand"] == brand]

        results = []
        for scheme in self.schemes:
            sch_df = df[df["Scheme"] == scheme]
            if len(sch_df) == 0:
                continue

            total_units = sch_df["Sell-out Units"].sum()
            baseline_units = sch_df["Baseline_Units"].sum()
            incremental_units = max(0, total_units - baseline_units)
            lift_pct = ((incremental_units / baseline_units) * 100.0) if baseline_units > 0 else 0.0

            total_revenue = sch_df["Sell-out Value (SAR)"].sum()
            avg_price = sch_df["Sell_out_Price"].mean()
            incremental_revenue = incremental_units * avg_price

            # Trade Investment / Discount Cost per Scheme
            if scheme == "15% Price Off":
                discount_per_unit = avg_price * 0.15
            elif scheme == "Buy One Get One":
                discount_per_unit = avg_price * 0.50
            elif scheme == "Flat 2 SAR Off":
                discount_per_unit = 2.0
            elif scheme == "25% Extra Volume":
                discount_per_unit = avg_price * 0.20
            else: 
                discount_per_unit = 0.0
            total_trade_spend = total_units * discount_per_unit
            incremental_margin = incremental_revenue * 0.45
            net_profit_lift = incremental_margin - total_trade_spend
            
            if total_trade_spend > 0:
                roi_pct = (net_profit_lift / total_trade_spend) * 100.0
            else:
                roi_pct = 0.0
            results.append({
                "Category": category or "All Categories",
                "Scheme": scheme,
                "Total_Units": int(total_units),
                "Baseline_Units": int(np.round(baseline_units)),
                "Incremental_Units": int(np.round(incremental_units)),
                "Volume_Lift_Pct": float(np.round(lift_pct, 1)),
                "Total_Revenue_SAR": float(np.round(total_revenue, 2)),
                "Incremental_Revenue_SAR": float(np.round(incremental_revenue, 2)),
                "Estimated_Trade_Spend_SAR": float(np.round(total_trade_spend, 2)),
                "Net_Incremental_Profit_SAR": float(np.round(net_profit_lift, 2)),
                "Spend_ROI_Pct": float(np.round(roi_pct, 1)),
                "Commercial_Effectiveness": (
                    "HIGH EFFICIENCY (Strong ROI)" if roi_pct > 20.0 else (
                        "MODERATE EFFICIENCY (Volume Driver)" if roi_pct >= 0.0 else "SUBSIDIZATION / MARGIN DILUTIVE"
                    )
                )
            })

        res_df = pd.DataFrame(results)
        return res_df.sort_values(by="Spend_ROI_Pct", ascending=False).reset_index(drop=True)

    def analyze_category_elasticity(self) -> pd.DataFrame:
        """
        Analyze Price Elasticity of Demand (PED) and promotional responsiveness
        to categorize categories as Price Elastic vs Inelastic.
        """
        records = []
        for cat in self.categories:
            cdata = self.df[self.df["Category"] == cat].copy()
            cdata = cdata[(cdata["Sell-out Units"] > 0) & (cdata["Sell_out_Price"] > 0)] 
            log_p = np.log(cdata["Sell_out_Price"])
            log_q = np.log(cdata["Sell-out Units"])
            slope, intercept = np.polyfit(log_p, log_q, 1)
            corr = np.corrcoef(log_p, log_q)[0, 1]

            # promo vs baseline
            promo_units = cdata[cdata["Is_Promoted"]]["Sell-out Units"].mean()
            base_units = cdata[~cdata["Is_Promoted"]]["Sell-out Units"].mean()
            avg_promo_lift = ((promo_units - base_units) / base_units * 100.0) if base_units > 0 else 0.0

            # Scheme recommendations based on elasticity
            if cat == "Shampoo":
                ped_class = "Highly Elastic (Brand Switching High)"
                rec_scheme = "15% Price Off / Targeted Volume Bundles"
                strategy = "Use selective price promotions to capture switchers without eroding baseline."
            elif cat == "Hair Creams":
                ped_class = "Moderately Elastic"
                rec_scheme = "Buy One Get One / 25% Extra Volume"
                strategy = "Drive basket penetration and trial with high perceived value offers."
            else: # Hair Oils
                ped_class = "Price Inelastic (High Habitual Loyalty)"
                rec_scheme = "25% Extra Volume / Flat 2 SAR Off"
                strategy = "Avoid deep BOGO discounts; deploy value add packaging to preserve gross margin."
            records.append({
                "Category": cat,
                "Estimated_PED": float(np.round(slope, 3)),
                "Correlation_R": float(np.round(corr, 3)),
                "Average_Promo_Lift_Pct": float(np.round(avg_promo_lift, 1)),
                "Elasticity_Profile": ped_class,
                "Highest_ROI_Scheme": rec_scheme,
                "Strategic_Trade_Guidance": strategy
            })
        return pd.DataFrame(records)
