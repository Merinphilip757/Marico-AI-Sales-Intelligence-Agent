"""Store & Chain-Level Activation Targeting Optimizer
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional

class ActivationOptimizer:
    def __init__(self, data_pipeline):
        self.pipeline = data_pipeline
        self.df = self.pipeline.df_merged if self.pipeline.df_merged is not None else self.pipeline.load_and_process()
        self.chains = self.pipeline.chains
        self.categories = self.pipeline.categories

    def compute_chain_opportunity_matrix(self, category: Optional[str] = None) -> pd.DataFrame:
        """
        Compute BDI (Brand Development Index), CDI (Category Development Index),
        Fair Share Index (FSI), and Revenue Opportunity Gap in SAR per Chain.
        """
        df = self.df.copy()
        if category:
            df = df[df["Category"] == category]

        total_cat_val = df["Sell-out Value (SAR)"].sum()
        marico_df = df[df["Is_Marico_Portfolio"]]
        total_marico_val = marico_df["Sell-out Value (SAR)"].sum()
        overall_marico_ms = (total_marico_val / total_cat_val * 100.0) if total_cat_val > 0 else 0.0

        chain_matrix = []
        for ch in sorted(df["Chain"].unique()):
            ch_df = df[df["Chain"] == ch]
            ch_cat_val = ch_df["Sell-out Value (SAR)"].sum()
            ch_marico_val = ch_df[ch_df["Is_Marico_Portfolio"]]["Sell-out Value (SAR)"].sum()
            
            ch_ms = (ch_marico_val / ch_cat_val * 100.0) if ch_cat_val > 0 else 0.0
            
            # CDI: Share of category in this chain vs market
            cdi = (ch_cat_val / total_cat_val) / (1.0 / len(self.chains)) * 100.0
            
            # BDI: Marico's sales in chain vs category turnover
            bdi = (ch_marico_val / total_marico_val) / (ch_cat_val / total_cat_val) * 100.0 if total_marico_val > 0 and ch_cat_val > 0 else 100.0
            
            # Fair Share Index (FSI)
            fsi = (ch_ms / overall_marico_ms * 100.0) if overall_marico_ms > 0 else 100.0
            
            # Opportunity Gap: Gap between chain share and overall portfolio share
            gap_pct = max(0.0, overall_marico_ms - ch_ms)
            opportunity_sar = (gap_pct / 100.0) * ch_cat_val
            if cdi >= 95.0 and fsi < 98.0:
                quadrant = "Q1: Priority Attack (High Category Size, Under-Indexed Share)"
                priority = "HIGH PRIORITY (Tier 1)"
                tactic = "Deploy ATL Billboards, Endcap Displays, Gondola Headers & EPOS Digital Signage"
            elif cdi >= 95.0 and fsi >= 98.0:
                quadrant = "Q2: Core Fortress (High Category Size, High Share)"
                priority = "DEFEND & GROW (Tier 2)"
                tactic = "Eye-level Shelf Maximization, Defensive Secondary Islands, Loyalty Co-op"
            elif cdi < 95.0 and fsi < 98.0:
                quadrant = "Q3: Opportunistic (Low Category Size, Low Share)"
                priority = "SELECTIVE (Tier 4)"
                tactic = "Promotional Bundling, Basic Shelf Compliance"
            else:
                quadrant = "Q4: Niche Efficiency (Low Category Size, High Share)"
                priority = "HARVEST (Tier 3)"
                tactic = "Margin Optimization, Maintain Core SKUs"

            chain_matrix.append({
                "Chain": ch,
                "Category": category or "All Categories",
                "Total_Chain_Category_Sales_SAR": float(np.round(ch_cat_val, 2)),
                "Marico_Sales_SAR": float(np.round(ch_marico_val, 2)),
                "Marico_Market_Share_Pct": float(np.round(ch_ms, 2)),
                "Portfolio_Benchmark_Share_Pct": float(np.round(overall_marico_ms, 2)),
                "BDI_Index": float(np.round(bdi, 1)),
                "CDI_Index": float(np.round(cdi, 1)),
                "Fair_Share_Index_FSI": float(np.round(fsi, 1)),
                "Opportunity_Revenue_Gap_SAR": float(np.round(opportunity_sar, 2)),
                "Strategic_Quadrant": quadrant,
                "Activation_Priority": priority,
                "Recommended_Tactics": tactic
            })

        matrix_df = pd.DataFrame(chain_matrix)
        return matrix_df.sort_values(by="Opportunity_Revenue_Gap_SAR", ascending=False).reset_index(drop=True)

    def get_activation_budget_allocation(self, total_budget_sar: float = 500000.0, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Allocate trade marketing & ATL activation budget proportional to Opportunity Gap and Strategic Priority.
        """
        matrix_df = self.compute_chain_opportunity_matrix(category=category)
        
        # Calculation
        matrix_df["Weight"] = np.where(
            matrix_df["Activation_Priority"].str.contains("Tier 1"), 3.0,
            np.where(matrix_df["Activation_Priority"].str.contains("Tier 2"), 2.0,
            np.where(matrix_df["Activation_Priority"].str.contains("Tier 3"), 1.0, 0.5))
        )
        score = matrix_df["Opportunity_Revenue_Gap_SAR"] * matrix_df["Weight"]
        total_score = score.sum()
        
        matrix_df["Allocated_Budget_SAR"] = np.where(
            total_score > 0,
            np.round((score / total_score) * total_budget_sar, 2),
            np.round(total_budget_sar / len(matrix_df), 2)
        )
        matrix_df["Budget_Share_Pct"] = np.round((matrix_df["Allocated_Budget_SAR"] / total_budget_sar) * 100.0, 1)

        tier1_chains = matrix_df[matrix_df["Activation_Priority"].str.contains("Tier 1")]["Chain"].tolist()
        
        return {
            "Total_Activation_Budget_SAR": total_budget_sar,
            "Category_Scope": category or "All Categories",
            "Top_Target_Chains": tier1_chains,
            "Allocation_Plan": matrix_df[[
                "Chain", "Marico_Market_Share_Pct", "Fair_Share_Index_FSI",
                "Opportunity_Revenue_Gap_SAR", "Activation_Priority",
                "Allocated_Budget_SAR", "Budget_Share_Pct", "Recommended_Tactics"
            ]]
        }
