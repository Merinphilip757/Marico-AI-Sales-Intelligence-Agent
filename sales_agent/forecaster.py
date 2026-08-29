"""Sales Forecasting & Offtake Dynamics Engine
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from sklearn.linear_model import Ridge

class SalesForecaster:
    def __init__(self, data_pipeline):
        self.pipeline = data_pipeline
        self.df = self.pipeline.df_merged if self.pipeline.df_merged is not None else self.pipeline.load_and_process()
        self.months = self.pipeline.months
        self.categories = self.pipeline.categories
        self.chains = self.pipeline.chains
        self.brands = self.pipeline.brands

    def calculate_lead_lag_correlations(self, category: Optional[str] = None) -> Dict[str, float]:
        """Compute cross-correlation between Sell-in (lags 0, 1, 2) and Sell-out (EPOS)."""
        df = self.df if category is None else self.df[self.df["Category"] == category]
        monthly = df.groupby("Month").agg(
            Sell_in_Units=("Sell-in Units", "sum"),
            Sell_out_Units=("Sell-out Units", "sum"),
            Sell_in_Value=("Sell-in Value (SAR)", "sum"),
            Sell_out_Value=("Sell-out Value (SAR)", "sum")
        ).reset_index()
        corrs = {}
        s_out = monthly["Sell_out_Units"]
        for lag in [0, 1, 2, 3]:
            s_in_lag = monthly["Sell_in_Units"].shift(lag)
            valid_mask = ~s_in_lag.isna()
            if valid_mask.sum() > 2:
                corr = np.corrcoef(s_in_lag[valid_mask], s_out[valid_mask])[0, 1]
                corrs[f"Lag_{lag}_Months"] = float(np.round(corr, 4))
            else:
                corrs[f"Lag_{lag}_Months"] = 0.0
        return corrs

    def forecast_secondary_sales(
        self,
        horizon_months: int = 3,
        category: Optional[str] = None,
        chain: Optional[str] = None,
        brand: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Project secondary sales (Sell-out Units and Value) based on historical Sell-in,
        lagged pipeline dynamics, inventory buffer, and seasonality.
        """
        filtered = self.df.copy()
        if category:
            filtered = filtered[filtered["Category"] == category]
        if chain:
            filtered = filtered[filtered["Chain"] == chain]
        if brand:
            filtered = filtered[filtered["Brand"] == brand]

        monthly = filtered.groupby("Month").agg(
            Sell_in_Units=("Sell-in Units", "sum"),
            Sell_in_Value=("Sell-in Value (SAR)", "sum"),
            Sell_out_Units=("Sell-out Units", "sum"),
            Sell_out_Value=("Sell-out Value (SAR)", "sum"),
            Avg_Price=("Sell_out_Price", "mean")
        ).reset_index()

        monthly["Month_Idx"] = np.arange(len(monthly))
        monthly["Sell_in_Lag1"] = monthly["Sell_in_Units"].shift(1).fillna(monthly["Sell_in_Units"].iloc[0])
        monthly["Inventory_Buffer"] = (monthly["Sell_in_Units"] - monthly["Sell_out_Units"]).cumsum()
        
        # Monthly (May-July peak)
        month_nums = [int(m.split("-")[1]) for m in monthly["Month"]]
        monthly["Month_Num"] = month_nums
        X = monthly[["Month_Idx", "Sell_in_Units", "Sell_in_Lag1", "Inventory_Buffer"]].values
        y_units = monthly["Sell_out_Units"].values
        y_val = monthly["Sell_out_Value"].values

        model_units = Ridge(alpha=1.0)
        model_units.fit(X, y_units)
        
        model_val = Ridge(alpha=1.0)
        model_val.fit(X, y_val)

        # future month dates
        last_month = self.months[-1]
        last_year, last_m = map(int, last_month.split("-"))
        
        future_rows = []
        curr_inventory = monthly["Inventory_Buffer"].iloc[-1]
        last_sell_in = monthly["Sell_in_Units"].iloc[-1]
        last_price = monthly["Avg_Price"].iloc[-1] if monthly["Avg_Price"].iloc[-1] > 0 else 50.0
        for h in range(1, horizon_months + 1):
            next_m = last_m + h
            next_year = last_year + (next_m - 1) // 12
            next_m = ((next_m - 1) % 12) + 1
            month_str = f"{next_year:04d}-{next_m:02d}"
            month_idx = len(monthly) + h - 1
            seasonality_multiplier = 1.0 + 0.25 * np.sin((next_m - 1) * np.pi / 6.0)
            
            projected_sell_in = last_sell_in * seasonality_multiplier
            pred_x = np.array([[month_idx, projected_sell_in, last_sell_in, curr_inventory]])
            
            pred_units = float(max(100, model_units.predict(pred_x)[0] * (0.8 + 0.2 * seasonality_multiplier)))
            pred_val = float(max(5000, model_val.predict(pred_x)[0] * (0.8 + 0.2 * seasonality_multiplier)))
            
            inv_delta = projected_sell_in - pred_units
            curr_inventory += inv_delta
            days_cover = float((curr_inventory / (pred_units / 30.0))) if pred_units > 0 else 0.0
            
            # Stockout risk alert
            if days_cover < 15:
                risk = "HIGH STOCKOUT RISK (<15 Days)"
            elif days_cover > 90:
                risk = "EXCESS INVENTORY (>90 Days)"
            else:
                risk = "OPTIMAL BUFFER (15-90 Days)"

            future_rows.append({
                "Month": month_str,
                "Forecast_Type": "Projected Secondary Sales",
                "Projected_Sell_in_Units": int(np.round(projected_sell_in)),
                "Projected_Sell_out_Units": int(np.round(pred_units)),
                "Projected_Sell_out_Value_SAR": float(np.round(pred_val, 2)),
                "Projected_Pipeline_Inventory_Units": int(np.round(curr_inventory)),
                "Projected_Days_of_Cover": float(np.round(days_cover, 1)),
                "Stock_Health_Status": risk
            })
            last_sell_in = projected_sell_in

        return pd.DataFrame(future_rows)
    def forecast_offtakes_and_market_share(
        self,
        horizon_months: int = 3,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Forecast brand offtakes and market share trajectories factoring in competitive intensity,
        HHI index, and relative promotional pressure.
        """
        df = self.df.copy()
        if category:
            df = df[df["Category"] == category]

        # 1. Competitive Intensity (HHI)
        brand_shares = df.groupby("Brand")["Sell-out Value (SAR)"].sum()
        total_market_val = brand_shares.sum()
        share_pcts = (brand_shares / total_market_val) * 100.0
        hhi = float(np.sum((share_pcts) ** 2))
        
        # 2. Competitor Promotional Pressure
        promo_df = df.groupby(["Brand", "Is_Promoted"])["Sell-out Units"].sum().unstack(fill_value=0)
        promo_pressure = {}
        for b in df["Brand"].unique():
            if b in promo_df.index:
                total_b = promo_df.loc[b].sum()
                prom_b = promo_df.loc[b].get(True, 0)
                promo_pressure[b] = float(np.round((prom_b / total_b * 100.0) if total_b > 0 else 0.0, 2))

        # 3. Monthly Brand Trajectory & Projections
        brand_monthly = df.groupby(["Month", "Brand"])["Sell-out Value (SAR)"].sum().unstack(fill_value=0)
        projections = {}
        last_month_val = brand_monthly.iloc[-1]
        
        for brand in df["Brand"].unique():
            history = brand_monthly[brand].values if brand in brand_monthly.columns else np.zeros(len(self.months))
            # 3-month momentum trend
            if len(history) >= 3:
                recent_trend = (history[-1] - history[-3]) / (history[-3] + 1e-5)
            else:
                recent_trend = 0.0
            projected_vals = []
            cur_val = history[-1] if len(history) > 0 else 100000
            for h in range(1, horizon_months + 1):
                cur_val = max(5000, cur_val * (1.0 + recent_trend * 0.3))
                projected_vals.append(float(np.round(cur_val, 2)))
            projections[brand] = projected_vals

        # projected market shares
        proj_df_list = []
        last_m_str = self.months[-1]
        last_year, last_m = map(int, last_m_str.split("-"))
        future_months = []
        for h in range(1, horizon_months + 1):
            next_m = last_m + h
            next_year = last_year + (next_m - 1) // 12
            next_m = ((next_m - 1) % 12) + 1
            future_months.append(f"{next_year:04d}-{next_m:02d}")

        for i, fm in enumerate(future_months):
            month_total = sum(projections[b][i] for b in projections)
            for b in projections:
                b_val = projections[b][i]
                b_share = (b_val / month_total * 100.0) if month_total > 0 else 0.0
                proj_df_list.append({
                    "Month": fm,
                    "Brand": b,
                    "Projected_Offtake_Value_SAR": b_val,
                    "Projected_Market_Share_Pct": float(np.round(b_share, 2)),
                    "Is_Marico_Portfolio": b in self.pipeline.marico_brands,
                    "Promo_Intensity_Pct": promo_pressure.get(b, 0.0)
                })
        return {
            "category": category or "All Categories",
            "HHI_Concentration_Index": float(np.round(hhi, 2)),
            "Market_Structure": "Highly Competitive" if hhi < 1500 else ("Moderately Concentrated" if hhi < 2500 else "Highly Concentrated"),
            "Competitor_Promo_Pressure": promo_pressure,
            "Projections_Table": pd.DataFrame(proj_df_list)
        }
