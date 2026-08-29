"""
Sales Data Pipeline Module
Harmonizes and enriches Sell-in, Sell-out (EPOS), and Market Share data streams.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List

class SalesDataPipeline:
    def __init__(self, excel_path: str = "Sell in & Sell out Dummy Data.xlsx"):
        self.excel_path = excel_path
        self.df_sell_in: Optional[pd.DataFrame] = None
        self.df_sell_out: Optional[pd.DataFrame] = None
        self.df_merged: Optional[pd.DataFrame] = None
        self.categories: List[str] = []
        self.chains: List[str] = []
        self.brands: List[str] = []
        self.skus: List[str] = []
        self.months: List[str] = []
        self.marico_brands = ["Marico", "Parachute"]

    def load_and_process(self) -> pd.DataFrame:
        """Load raw sheets from Excel, sanitize, harmonize, and engineer commercial features."""
        xls = pd.ExcelFile(self.excel_path)
        self.df_sell_in = pd.read_excel(xls, "SELL IN Data")
        self.df_sell_out = pd.read_excel(xls, "Sell OUT & Market Share")

        # 1. Clean brand strings and categorical columns
        for df in [self.df_sell_in, self.df_sell_out]:
            df["Brand"] = df["Brand"].apply(lambda x: "TRESemme" if "TRESemm" in str(x) else str(x).strip())
            df["Category"] = df["Category"].astype(str).str.strip()
            df["Chain"] = df["Chain"].astype(str).str.strip()
            df["SKU"] = df["SKU"].astype(str).str.strip()
            df["Month"] = df["Month"].astype(str).str.strip()

        # 2. Derive unit prices before merge
        self.df_sell_in["Sell_in_Price"] = np.where(
            self.df_sell_in["Sell-in Units"] > 0,
            self.df_sell_in["Sell-in Value (SAR)"] / self.df_sell_in["Sell-in Units"],
            0.0
        )

        self.df_sell_out["Sell_out_Price"] = np.where(
            self.df_sell_out["Sell-out Units"] > 0,
            self.df_sell_out["Sell-out Value (SAR)"] / self.df_sell_out["Sell-out Units"],
            0.0
        )

        # 3. Merge datasets
        merge_keys = ["Month", "Chain", "Category", "Brand", "SKU"]
        merged = pd.merge(
            self.df_sell_in,
            self.df_sell_out,
            on=merge_keys,
            how="inner"
        )

        # 4. Feature Engineering
        merged["Is_Marico_Portfolio"] = merged["Brand"].isin(self.marico_brands)
        merged["Inventory_Delta_Units"] = merged["Sell-in Units"] - merged["Sell-out Units"]
        merged["Inventory_Delta_Value"] = merged["Sell-in Value (SAR)"] - merged["Sell-out Value (SAR)"]
        
        # Trade promotion handling
        merged["Scheme"] = merged["Scheme"].fillna("No Promotion").astype(str).str.strip()
        merged["Is_Promoted"] = merged["Scheme"] != "No Promotion"

        # Category Benchmark Prices 
        cat_chain_avg = merged.groupby(["Month", "Chain", "Category"])["Sell_out_Price"].transform("mean")
        merged["Category_Chain_Avg_Price"] = cat_chain_avg
        merged["RPI"] = np.where(
            merged["Category_Chain_Avg_Price"] > 0,
            (merged["Sell_out_Price"] / merged["Category_Chain_Avg_Price"]) * 100.0,
            100.0
        )

        # Calculate Non-Promotional
        base_df = merged[merged["Scheme"] == "No Promotion"].groupby(
            ["Chain", "Category", "Brand", "SKU"]
        )["Sell-out Units"].mean().reset_index().rename(columns={"Sell-out Units": "Baseline_Units"})
        
        macro_base = merged[merged["Scheme"] == "No Promotion"].groupby(
            ["Category", "Brand", "SKU"]
        )["Sell-out Units"].mean().reset_index().rename(columns={"Sell-out Units": "Macro_Baseline_Units"})
        
        merged = pd.merge(merged, base_df, on=["Chain", "Category", "Brand", "SKU"], how="left")
        merged = pd.merge(merged, macro_base, on=["Category", "Brand", "SKU"], how="left")
        merged["Baseline_Units"] = merged["Baseline_Units"].fillna(merged["Macro_Baseline_Units"])
        merged["Baseline_Units"] = merged["Baseline_Units"].fillna(merged["Sell-out Units"])
        merged.drop(columns=["Macro_Baseline_Units"], inplace=True, errors="ignore")

        merged["Incremental_Units"] = np.maximum(0, merged["Sell-out Units"] - merged["Baseline_Units"])
        merged["Promo_Lift_Pct"] = np.where(
            merged["Baseline_Units"] > 0,
            ((merged["Sell-out Units"] - merged["Baseline_Units"]) / merged["Baseline_Units"]) * 100.0,
            0.0
        )
        merged = merged.sort_values(by=["Category", "Brand", "SKU", "Chain", "Month"]).reset_index(drop=True)
        self.df_merged = merged
        self.categories = sorted(merged["Category"].unique().tolist())
        self.chains = sorted(merged["Chain"].unique().tolist())
        self.brands = sorted(merged["Brand"].unique().tolist())
        self.skus = sorted(merged["SKU"].unique().tolist())
        self.months = sorted(merged["Month"].unique().tolist())
        return self.df_merged

    def get_summary_stats(self) -> Dict[str, Any]:
        """Compute high-level dataset metrics."""
        if self.df_merged is None:
            self.load_and_process()
        df = self.df_merged
        total_sell_out_val = float(df["Sell-out Value (SAR)"].sum())
        marico_sell_out_val = float(df[df["Is_Marico_Portfolio"]]["Sell-out Value (SAR)"].sum())
        return {
            "total_rows": len(df),
            "months_count": len(self.months),
            "months_range": f"{self.months[0]} to {self.months[-1]}",
            "chains_count": len(self.chains),
            "categories_count": len(self.categories),
            "brands_count": len(self.brands),
            "skus_count": len(self.skus),
            "total_sell_in_value": float(df["Sell-in Value (SAR)"].sum()),
            "total_sell_out_value": total_sell_out_val,
            "total_sell_in_units": int(df["Sell-in Units"].sum()),
            "total_sell_out_units": int(df["Sell-out Units"].sum()),
            "marico_sell_out_value": marico_sell_out_val,
            "marico_value_share_pct": (marico_sell_out_val / total_sell_out_val * 100.0) if total_sell_out_val > 0 else 0.0
        }

    def get_monthly_pipeline(self) -> pd.DataFrame:
        """Aggregate monthly sell-in vs sell-out and compute stock cover and inventory deltas."""
        if self.df_merged is None:
            self.load_and_process()
        df = self.df_merged
        monthly = df.groupby("Month").agg(
            Sell_in_Units=("Sell-in Units", "sum"),
            Sell_in_Value=("Sell-in Value (SAR)", "sum"),
            Sell_out_Units=("Sell-out Units", "sum"),
            Sell_out_Value=("Sell-out Value (SAR)", "sum")
        ).reset_index()
        
        # Calculate Marico monthly sell-out
        marico_monthly = df[df["Is_Marico_Portfolio"]].groupby("Month").agg(
            Marico_Sell_out_Units=("Sell-out Units", "sum"),
            Marico_Sell_out_Value=("Sell-out Value (SAR)", "sum")
        ).reset_index()
        
        monthly = pd.merge(monthly, marico_monthly, on="Month", how="left")
        monthly["Inventory_Delta_Units"] = monthly["Sell_in_Units"] - monthly["Sell_out_Units"]
        monthly["Cumulative_Pipeline_Units"] = monthly["Inventory_Delta_Units"].cumsum()
        monthly["Days_of_Cover"] = np.where(
            monthly["Sell_out_Units"] > 0,
            (monthly["Cumulative_Pipeline_Units"] / (monthly["Sell_out_Units"] / 30.0)),
            0.0
        )
        return monthly
