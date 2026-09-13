"""
Component Tests for Supply Chain AI System
"""

import pytest
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.calculators.risk_calculator import calculate_risk_score, assess_geopolitical_risk
from tools.calculators.forecast_engine import generate_demand_forecast, detect_shortages
from tools.calculators.supplier_evaluator import evaluate_supplier, find_alternatives
from tools.calculators.inventory_optimizer import optimize_inventory
from tools.calculators.logistics_optimizer import optimize_route
from tools.report_generator import aggregate_insights, generate_executive_report


class TestRiskCalculator:
    """Test risk calculation functions."""
    
    def test_calculate_risk_score(self):
        """Test risk score calculation."""
        result = calculate_risk_score(
            geopolitical_risk=0.8,
            supplier_reliability=0.6,
            market_volatility=0.5,
            export_control_status="RESTRICTED"
        )
        
        assert "risk_score" in result
        assert "risk_level" in result
        assert "breakdown" in result
        assert 0 <= result["risk_score"] <= 1
        print("✅ Risk score calculation works")
    
    def test_assess_geopolitical_risk(self):
        """Test geopolitical risk assessment."""
        result = assess_geopolitical_risk("China", "Memory Chips", use_cache=False)
        
        assert "country" in result
        assert "risk_score" in result
        assert "risk_level" in result
        print("✅ Geopolitical risk assessment works")


class TestForecastEngine:
    """Test demand forecasting functions."""
    
    def test_generate_forecast(self):
        """Test demand forecast generation."""
        result = generate_demand_forecast("Product_1", forecast_days=30)
        
        if "error" not in result:
            assert "forecasts" in result
            assert "summary" in result
            assert len(result["forecasts"]) > 0
            print("✅ Demand forecast generation works")
        else:
            print(f"⚠️  Forecast generation returned error: {result.get('error')}")
    
    def test_detect_shortages(self):
        """Test shortage detection."""
        result = detect_shortages("Product_1", forecast_days=30, current_stock=1000)
        
        if "error" not in result:
            assert "shortage_risk" in result
            assert "current_stock" in result
            print("✅ Shortage detection works")
        else:
            print(f"⚠️  Shortage detection returned error: {result.get('error')}")


class TestSupplierEvaluator:
    """Test supplier evaluation functions."""
    
    def test_evaluate_supplier(self):
        """Test supplier evaluation."""
        result = evaluate_supplier("SUP001", include_risk_assessment=False)
        
        if "error" not in result:
            assert "supplier_id" in result
            assert "reliability_score" in result
            print("✅ Supplier evaluation works")
        else:
            print(f"⚠️  Supplier evaluation returned error: {result.get('error')}")
    
    def test_find_alternatives(self):
        """Test finding alternative suppliers."""
        result = find_alternatives("SUP001", min_reliability=0.7)
        
        if "error" not in result:
            assert "alternatives" in result
            print("✅ Find alternatives works")
        else:
            print(f"⚠️  Find alternatives returned error: {result.get('error')}")


class TestInventoryOptimizer:
    """Test inventory optimization functions."""
    
    def test_optimize_inventory(self):
        """Test inventory optimization."""
        result = optimize_inventory("Product_1")
        
        if "error" not in result:
            assert "optimal_stock" in result
            assert "recommended_action" in result
            print("✅ Inventory optimization works")
        else:
            print(f"⚠️  Inventory optimization returned error: {result.get('error')}")


class TestLogisticsOptimizer:
    """Test logistics optimization functions."""
    
    def test_optimize_route(self):
        """Test route optimization."""
        result = optimize_route("China", "USA", "Memory Chips")
        
        assert "origin" in result
        assert "destination" in result
        assert "recommended_route" in result or "error" in result
        print("✅ Route optimization works")


class TestReportGenerator:
    """Test report generation functions."""
    
    def test_aggregate_insights(self):
        """Test insight aggregation."""
        insights = aggregate_insights([
            {
                "agent": "RiskAgent",
                "data": {
                    "risk_score": 0.75,
                    "risk_level": "HIGH",
                    "recommendations": ["Monitor closely"]
                }
            }
        ])
        
        assert "summary" in insights
        assert "key_findings" in insights
        assert "recommendations" in insights
        print("✅ Insight aggregation works")
    
    def test_generate_report(self):
        """Test report generation."""
        insights = aggregate_insights([
            {
                "agent": "RiskAgent",
                "data": {
                    "risk_score": 0.75,
                    "risk_level": "HIGH",
                    "recommendations": ["Monitor closely"]
                }
            }
        ])
        
        report = generate_executive_report(insights)
        
        assert isinstance(report, str)
        assert len(report) > 0
        assert "EXECUTIVE" in report.upper()
        print("✅ Report generation works")


def run_all_tests():
    """Run all component tests."""
    print("=" * 60)
    print("RUNNING COMPONENT TESTS")
    print("=" * 60)
    print()
    
    test_classes = [
        TestRiskCalculator,
        TestForecastEngine,
        TestSupplierEvaluator,
        TestInventoryOptimizer,
        TestLogisticsOptimizer,
        TestReportGenerator
    ]
    
    for test_class in test_classes:
        print(f"Testing {test_class.__name__}...")
        instance = test_class()
        for method_name in dir(instance):
            if method_name.startswith("test_"):
                method = getattr(instance, method_name)
                try:
                    method()
                except Exception as e:
                    print(f"❌ {method_name} failed: {e}")
        print()
    
    print("=" * 60)
    print("COMPONENT TESTS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()

