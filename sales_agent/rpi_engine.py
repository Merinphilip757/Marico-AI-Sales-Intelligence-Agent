"""Relative Price Index (RPI) & Pricing Optimization Engine
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional

class RPIEngine:
    def __init__(self, data_pipeline):
        self.pipeline = data_pipeline
        self.df = self.pipeline.df_merged if self.pipeline.df_merged is not None else self.pipeline.load_and_process()
        self.categories = self.pipeline.categories
        self.brands = self.pipeline.brands

    def calculate_rpi_summary(self) -> pd.DataFrame:
        """Compute brand-level RPI, average unit prices, and market share by category."""
        summary = self.df.groupby(["Category", "Brand"]).agg(
            Avg_Sell_out_Price=("Sell_out_Price", "mean"),
            Avg_RPI=("RPI", "mean"),
            Total_Volume_Units=("Sell-out Units", "sum"),
            Total_Revenue_SAR=("Sell-out Value (SAR)", "sum"),
            Avg_Category_Market_Share=("Category Market Share (%)", "mean"),
            Avg_Chain_Market_Share=("Chain Market Share (%)", "mean")
        ).reset_index()
        summary["Is_Marico_Portfolio"] = summary["Brand"].isin(self.pipeline.marico_brands)
        summary["RPI_Position"] = np.where(
            summary["Avg_RPI"] > 103.0, "Premium Index (>103)",
            np.where(summary["Avg_RPI"] < 97.0, "Discount Index (<97)", "Parity Index (97-103)")
        )
        return summary.sort_values(by=["Category", "Total_Revenue_SAR"], ascending=[True, False]).reset_index(drop=True)

    def calculate_price_elasticity(self, category: Optional[str] = None, brand: Optional[str] = None) -> Dict[str, Any]:
        """
        Estimate Own-Price Elasticity of Demand (PED) and RPI Share Elasticity
        using log-log econometric regression.
        """
        df = self.df.copy()
        if category:
            df = df[df["Category"] == category]
        if brand:
            df = df[df["Brand"] == brand]

        valid = df[(df["Sell-out Units"] > 0) & (df["Sell_out_Price"] > 0) & (df["RPI"] > 0)].copy()
        if len(valid) < 10:
            return {"error": "Insufficient data points for regression"}

        log_p = np.log(valid["Sell_out_Price"])
        log_q = np.log(valid["Sell-out Units"])
        log_rpi = np.log(valid["RPI"])
        log_ms = np.log(valid["Category Market Share (%)"] + 1e-4)

        # 1. Own-price elasticity 
        slope_p, intercept_p = np.polyfit(log_p, log_q, 1)
        r2_p = float(np.corrcoef(log_p, log_q)[0, 1] ** 2)

        # 2. RPI elasticity to market 
        slope_rpi, intercept_rpi = np.polyfit(log_rpi, log_ms, 1)
        r2_rpi = float(np.corrcoef(log_rpi, log_ms)[0, 1] ** 2)

        ped_value = float(np.round(slope_p, 3))
        rpi_elasticity = float(np.round(slope_rpi, 3))

        # classification
        if abs(ped_value) > 1.2:
            elasticity_class = "Highly Price Elastic (|PED| > 1.2)"
        elif abs(ped_value) >= 0.8:
            elasticity_class = "Unit / Moderately Elastic (0.8 <= |PED| <= 1.2)"
        else:
            elasticity_class = "Price Inelastic (|PED| < 0.8)"
        return {
            "Category": category or "All Categories",
            "Brand": brand or "All Brands",
            "Own_Price_Elasticity_PED": ped_value,
            "PED_R_Squared": float(np.round(r2_p, 4)),
            "Elasticity_Classification": elasticity_class,
            "RPI_to_MarketShare_Elasticity": rpi_elasticity,
            "RPI_R_Squared": float(np.round(r2_rpi, 4)),
            "Commercial_Interpretation": (
                f"A 10% reduction in relative price index (RPI) is associated with a "
                f"{abs(rpi_elasticity * 10):.1f}% change in category market share."
            )
        }

    def discover_optimal_rpi_corridor(self, category: str, brand: str = "Parachute") -> Dict[str, Any]:
        """
        Simulate demand and revenue curve across RPI continuum (75 to 130)
        to identify volume maximizing, revenue maximizing, and margin balanced pricing sweet spots.
        Uses realistic FMCG kinked demand response beyond price parity.
        """
        cat_df = self.df[self.df["Category"] == category].copy()
        brand_df = cat_df[cat_df["Brand"] == brand].copy()
        if len(brand_df) == 0:
            brand_df = cat_df[cat_df["Is_Marico_Portfolio"]].copy()
            brand = "Marico Portfolio"

        current_rpi = float(np.round(brand_df["RPI"].mean(), 1))
        current_price = float(np.round(brand_df["Sell_out_Price"].mean(), 2))
        cat_benchmark_price = float(np.round(cat_df["Sell_out_Price"].mean(), 2))
        current_share = float(np.round(brand_df["Category Market Share (%)"].mean(), 2))
        base_volume = float(brand_df["Sell-out Units"].sum() / 12.0)
        rpi_range = np.arange(75, 131, 1)
        sim_data = []

        for rpi in rpi_range:
            sim_price = (rpi / 100.0) * cat_benchmark_price
            price_ratio = sim_price / (current_price + 1e-4)
            
            # higher elasticity when pricing above benchmark
            if rpi <= 100:
                eff_ped = -0.75 if category == "Hair Oils" else (-0.90 if category == "Hair Creams" else -1.10)
            else:
                penalty = 1.0 + ((rpi - 100) / 10.0) * 0.8
                eff_ped = (-0.75 * penalty) if category == "Hair Oils" else (-1.10 * penalty)

            sim_vol = base_volume * ((price_ratio) ** eff_ped)
            sim_rev = sim_vol * sim_price
            sim_share = current_share * ((100.0 / rpi) ** 0.85)
            sim_data.append({
                "RPI": int(rpi),
                "Simulated_Price_SAR": float(np.round(sim_price, 2)),
                "Simulated_Monthly_Volume_Units": float(np.round(sim_vol, 1)),
                "Simulated_Monthly_Revenue_SAR": float(np.round(sim_rev, 2)),
                "Simulated_Market_Share_Pct": float(np.round(max(0.05, sim_share), 2))
            })
        sim_df = pd.DataFrame(sim_data)
        vol_max_idx = sim_df["Simulated_Monthly_Volume_Units"].idxmax()
        rev_max_idx = sim_df["Simulated_Monthly_Revenue_SAR"].idxmax()
        vol_max_rpi = int(sim_df.loc[vol_max_idx, "RPI"])
        rev_max_rpi = int(sim_df.loc[rev_max_idx, "RPI"])

        # balanced RPI corridor: 90-106 (or +/- 4 points around revenue maximizing RPI)
        corridor_min = max(90, rev_max_rpi - 4)
        corridor_max = min(106, rev_max_rpi + 4)
        if current_rpi > corridor_max:
            action = f"Over-indexed against competition (RPI {current_rpi}). Rationalize price or run targeted promotion to bring RPI to {corridor_max}."
        elif current_rpi < corridor_min:
            action = f"Under-indexed (RPI {current_rpi}). Headroom exists for +2-4% price realization without sacrificing volume share."
        else:
            action = f"Optimal positioning (RPI {current_rpi} within corridor {corridor_min}-{corridor_max}). Defend current price architecture."
        return {
            "Category": category,
            "Brand": brand,
            "Current_RPI": current_rpi,
            "Current_Avg_Price_SAR": current_price,
            "Category_Benchmark_Price_SAR": cat_benchmark_price,
            "Current_Category_Market_Share_Pct": current_share,
            "Volume_Maximizing_RPI": vol_max_rpi,
            "Revenue_Maximizing_RPI": rev_max_rpi,
            "Optimal_RPI_Corridor": f"{corridor_min} - {corridor_max}",
            "Recommended_Commercial_Action": action,
            "Simulation_Curve": sim_df
        }
