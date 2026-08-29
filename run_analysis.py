"""Executes complete analytics suite across all 6 case study scope requirements.
"""
import sys
from sales_agent import SalesIntelligenceAgent

def main():
    print("=" * 80)
    print("      MARICO SALES INTELLIGENCE AGENT — COMMERCIAL ANALYTICS SUITE      ")
    print("=" * 80)

    agent = SalesIntelligenceAgent()
    stats = agent.pipeline.get_summary_stats()

    print(f"\n[1] DATASET OVERVIEW & RECONCILIATION")
    print(f"  • Total Transaction Rows: {stats['total_rows']:,}")
    print(f"  • Time Period: {stats['months_range']} ({stats['months_count']} Months)")
    print(f"  • Retail Chains ({stats['chains_count']}): {', '.join(agent.pipeline.chains)}")
    print(f"  • Categories ({stats['categories_count']}): {', '.join(agent.pipeline.categories)}")
    print(f"  • Brands ({stats['brands_count']}): {', '.join(agent.pipeline.brands)}")
    print(f"  • Total EPOS Sell-Out Revenue: {stats['total_sell_out_value']:,.2f} SAR")
    print(f"  • Total Internal Sell-In Revenue: {stats['total_sell_in_value']:,.2f} SAR")
    print(f"  • Marico Portfolio Revenue: {stats['marico_sell_out_value']:,.2f} SAR ({stats['marico_value_share_pct']:.2f}% Market Share)")
    print("\n" + "=" * 80)
    print("[2] SECONDARY SALES PROJECTION & PIPELINE INVENTORY HEALTH")
    print("=" * 80)
    corrs = agent.forecaster.calculate_lead_lag_correlations()
    print("  • Lead-Lag Cross-Correlation (Sell-in -> EPOS Sell-out):")
    for lag, val in corrs.items():
        print(f"    - {lag}: {val:.4f}")
    
    forecast_df = agent.forecaster.forecast_secondary_sales(horizon_months=3)
    print("\n  • Forward 3-Month Secondary Sales Projections:")
    print(forecast_df[["Month", "Projected_Sell_in_Units", "Projected_Sell_out_Units", "Projected_Sell_out_Value_SAR", "Projected_Days_of_Cover", "Stock_Health_Status"]].to_string(index=False))
    print("\n" + "=" * 80)
    print("[3] OFFTAKES & MARKET SHARE DYNAMICS UNDER COMPETITIVE INTENSITY")
    print("=" * 80)
    offtake_res = agent.forecaster.forecast_offtakes_and_market_share(horizon_months=3)
    print(f"  • Category HHI Concentration Index: {offtake_res['HHI_Concentration_Index']} ({offtake_res['Market_Structure']})")
    print(f"  • Competitor Promotional Pressure Summary:")
    for b, p in list(offtake_res['Competitor_Promo_Pressure'].items())[:5]:
        print(f"    - {b}: {p}% of volume on active promo")
    print("\n" + "=" * 80)
    print("[4] RELATIVE PRICE INDEX (RPI) & OPTIMAL PRICING CORRIDORS")
    print("=" * 80)
    for cat in agent.pipeline.categories:
        opt = agent.rpi_engine.discover_optimal_rpi_corridor(category=cat, brand="Parachute")
        print(f"\n  • Category: {cat} (Parachute)")
        print(f"    - Current RPI: {opt['Current_RPI']} | Benchmark Price: {opt['Category_Benchmark_Price_SAR']:.2f} SAR | Parachute Price: {opt['Current_Avg_Price_SAR']:.2f} SAR")
        print(f"    - Revenue-Maximizing RPI: {opt['Revenue_Maximizing_RPI']} | Optimal Balanced Corridor: {opt['Optimal_RPI_Corridor']}")
        print(f"    - Strategic Action: {opt['Recommended_Commercial_Action']}")

    print("\n" + "=" * 80)
    print("[5] STORE / CHAIN ACTIVATION TARGETING (ATL & VISIBILITY ALLOCATION)")
    print("=" * 80)
    opp_matrix = agent.activation_optimizer.compute_chain_opportunity_matrix()
    print(opp_matrix[["Chain", "Marico_Market_Share_Pct", "BDI_Index", "CDI_Index", "Fair_Share_Index_FSI", "Opportunity_Revenue_Gap_SAR", "Activation_Priority"]].to_string(index=False))

    budget_plan = agent.activation_optimizer.get_activation_budget_allocation(total_budget_sar=500000.0)
    print(f"\n  • Top Recommended Activation Accounts: {', '.join(budget_plan['Top_Target_Chains'])}")
    print("\n" + "=" * 80)
    print("[6] SPEND ROI & PROMOTIONAL ELASTICITY (BTL SCHEMES)")
    print("=" * 80)

    schemes_df = agent.promotion_roi.evaluate_schemes()
    print(schemes_df[["Scheme", "Volume_Lift_Pct", "Incremental_Revenue_SAR", "Estimated_Trade_Spend_SAR", "Spend_ROI_Pct", "Commercial_Effectiveness"]].to_string(index=False))

    elasticity_df = agent.promotion_roi.analyze_category_elasticity()
    print("\n  • Category Elasticity Profile & Strategy:")
    print(elasticity_df[["Category", "Estimated_PED", "Elasticity_Profile", "Highest_ROI_Scheme"]].to_string(index=False))
    print("\n" + "=" * 80)
    print("[7] WEIGHTED DISTRIBUTION (WD) IMPACT & EXPANSION SIMULATION")
    print("=" * 80)

    wd_impact = agent.distribution_engine.quantify_wd_impact_on_market_share()
    print(f"  • {wd_impact['Commercial_Rule_of_Thumb']}")
    
    sim_exp = agent.distribution_engine.simulate_distribution_expansion(category="Hair Oils", target_chain="Panda", brand="Parachute")
    print(f"  • Expansion Simulation (Parachute in Panda):")
    print(f"    - Current Share in Panda: {sim_exp['Current_Chain_Market_Share_Pct']}% -> Target Share: {sim_exp['Projected_New_Chain_Market_Share_Pct']}%")
    print(f"    - Incremental Annual Revenue Prize: {sim_exp['Incremental_Annual_Revenue_Uplift_SAR']:,.2f} SAR")
    print("\n" + "=" * 80)
    print("                 ANALYSIS COMPLETE — SYSTEM OPERATIONAL                ")
    print("=" * 80)

if __name__ == "__main__":
    main()
