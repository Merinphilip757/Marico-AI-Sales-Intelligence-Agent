"""Verifies data pipeline, analytical engines, econometric models, and AI agent reasoning.
"""
import unittest
import pandas as pd
import numpy as np
from sales_agent import (
    SalesDataPipeline,
    SalesForecaster,
    RPIEngine,
    ActivationOptimizer,
    PromotionROIEngine,
    DistributionEngine,
    SalesIntelligenceAgent
)

class TestSalesIntelligenceSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pipeline = SalesDataPipeline()
        cls.df = cls.pipeline.load_and_process()
        cls.forecaster = SalesForecaster(cls.pipeline)
        cls.rpi_engine = RPIEngine(cls.pipeline)
        cls.activation_optimizer = ActivationOptimizer(cls.pipeline)
        cls.promotion_roi = PromotionROIEngine(cls.pipeline)
        cls.distribution_engine = DistributionEngine(cls.pipeline)
        cls.agent = SalesIntelligenceAgent()

    def test_01_data_pipeline_integrity(self):
        """Verify data sanitization, feature engineering, and price derivations."""
        self.assertIsNotNone(self.df)
        self.assertEqual(len(self.df), 14416)
        self.assertEqual(len(self.pipeline.months), 12)
        self.assertEqual(len(self.pipeline.chains), 8)
        self.assertEqual(len(self.pipeline.categories), 3)
        self.assertEqual(len(self.pipeline.brands), 11)
        self.assertIn("TRESemme", self.pipeline.brands)
        self.assertNotIn("TRESemm", self.pipeline.brands)

        # Check positive unit prices
        self.assertTrue((self.df["Sell_in_Price"] >= 0).all())
        self.assertTrue((self.df["Sell_out_Price"] >= 0).all())

        # Check Marico flagging
        marico_rows = self.df[self.df["Is_Marico_Portfolio"]]
        self.assertTrue(set(marico_rows["Brand"].unique()).issubset({"Marico", "Parachute"}))

        stats = self.pipeline.get_summary_stats()
        self.assertGreater(stats["total_sell_out_value"], 100000000)
        self.assertGreater(stats["marico_value_share_pct"], 10.0)

    def test_02_pipeline_inventory_and_forecasting(self):
        """Verify pipeline inventory calculation, lead-lag correlations, and secondary sales forecasts."""
        monthly_pipeline = self.pipeline.get_monthly_pipeline()
        self.assertEqual(len(monthly_pipeline), 12)
        self.assertTrue("Cumulative_Pipeline_Units" in monthly_pipeline.columns)
        self.assertTrue("Days_of_Cover" in monthly_pipeline.columns)
        lead_lag = self.forecaster.calculate_lead_lag_correlations()
        self.assertIn("Lag_0_Months", lead_lag)
        self.assertIn("Lag_1_Months", lead_lag)

        # Multi month forecast
        forecast_df = self.forecaster.forecast_secondary_sales(horizon_months=3)
        self.assertEqual(len(forecast_df), 3)
        self.assertTrue((forecast_df["Projected_Sell_out_Units"] > 0).all())
        self.assertTrue((forecast_df["Projected_Sell_out_Value_SAR"] > 0).all())

        offtake_res = self.forecaster.forecast_offtakes_and_market_share(horizon_months=3)
        self.assertIn("HHI_Concentration_Index", offtake_res)
        self.assertGreater(offtake_res["HHI_Concentration_Index"], 500)
        self.assertEqual(len(offtake_res["Projections_Table"]), 3 * len(self.pipeline.brands))

    def test_03_rpi_and_pricing_optimization(self):
        """Verify RPI calculations, elasticity regressions, and optimal corridor discovery."""
        rpi_summary = self.rpi_engine.calculate_rpi_summary()
        self.assertGreater(len(rpi_summary), 0)
        self.assertTrue((rpi_summary["Avg_RPI"] > 70).all())
        self.assertTrue((rpi_summary["Avg_RPI"] < 140).all())

        ped_res = self.rpi_engine.calculate_price_elasticity(category="Hair Oils")
        self.assertIn("Own_Price_Elasticity_PED", ped_res)

        optimal_corridor = self.rpi_engine.discover_optimal_rpi_corridor(category="Hair Oils", brand="Parachute")
        self.assertIn("Optimal_RPI_Corridor", optimal_corridor)
        self.assertGreater(optimal_corridor["Revenue_Maximizing_RPI"], 80)
        self.assertLess(optimal_corridor["Revenue_Maximizing_RPI"], 120)

    def test_04_activation_targeting_and_opportunity(self):
        """Verify EPOS chain opportunity matrix, Fair Share Index, and budget allocations."""
        opp_matrix = self.activation_optimizer.compute_chain_opportunity_matrix()
        self.assertEqual(len(opp_matrix), len(self.pipeline.chains))
        self.assertTrue("BDI_Index" in opp_matrix.columns)
        self.assertTrue("CDI_Index" in opp_matrix.columns)
        self.assertTrue("Fair_Share_Index_FSI" in opp_matrix.columns)
        self.assertTrue("Opportunity_Revenue_Gap_SAR" in opp_matrix.columns)

        budget_plan = self.activation_optimizer.get_activation_budget_allocation(total_budget_sar=500000.0)
        self.assertEqual(budget_plan["Total_Activation_Budget_SAR"], 500000.0)
        self.assertGreater(len(budget_plan["Top_Target_Chains"]), 0)

    def test_05_promotion_roi_and_category_elasticity(self):
        """Verify BTL scheme evaluation, incremental lift, and category elasticity profiling."""
        schemes_df = self.promotion_roi.evaluate_schemes()
        self.assertGreater(len(schemes_df), 0)
        self.assertTrue("Spend_ROI_Pct" in schemes_df.columns)
        self.assertTrue("Volume_Lift_Pct" in schemes_df.columns)

        elasticity_df = self.promotion_roi.analyze_category_elasticity()
        self.assertEqual(len(elasticity_df), 3)
        self.assertTrue("Elasticity_Profile" in elasticity_df.columns)

    def test_06_distribution_impact_and_simulation(self):
        """Verify Weighted Distribution calculations and expansion scenario simulations."""
        dist_df = self.distribution_engine.calculate_distribution_metrics()
        self.assertGreater(len(dist_df), 0)
        self.assertTrue((dist_df["Weighted_Distribution_WD_Pct"] >= 0).all())

        wd_quant = self.distribution_engine.quantify_wd_impact_on_market_share(category="Hair Oils")
        self.assertIn("WD_Share_Multiplier_Beta", wd_quant)

        sim_res = self.distribution_engine.simulate_distribution_expansion(category="Hair Oils", target_chain="Panda", brand="Parachute")
        self.assertIn("Simulated_Market_Share_Gain_Pct", sim_res)
        self.assertGreater(sim_res["Incremental_Annual_Revenue_Uplift_SAR"], 0)

    def test_07_ai_sales_intelligence_agent(self):
        """Verify Natural Language AI reasoning across all 6 core query domains."""
        summary = self.agent.get_executive_summary()
        self.assertIn("Marico_Portfolio_Revenue_SAR", summary)
        self.assertIn("Key_Commercial_Priorities", summary)

        # Test NL query intents
        queries_to_test = [
            ("What is our projected secondary sales next quarter?", "secondary_sales_forecast"),
            ("What is the optimal RPI for Parachute in Hair Oils?", "rpi_optimization"),
            ("Which retail chains are top targets for ATL activation?", "activation_targeting"),
            ("Which BTL promotional scheme gives highest ROI in Shampoo?", "promotion_roi"),
            ("What is the impact of expanding weighted distribution in Panda?", "distribution_impact"),
            ("Give me a comprehensive executive diagnostic.", "executive_summary")
        ]

        for query_str, expected_intent in queries_to_test:
            res = self.agent.ask(query_str)
            self.assertEqual(res["intent"], expected_intent)
            self.assertIsNotNone(res["text_response"])
            self.assertGreater(len(res["text_response"]), 50)

if __name__ == "__main__":
    unittest.main()
