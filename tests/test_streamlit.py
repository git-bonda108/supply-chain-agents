"""
Test Cases for Streamlit Application
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from streamlit_app import (
    load_supplier_data,
    load_inventory_data,
    load_demand_data,
    run_agent_async
)
from tools.data_loader import get_data_loader
from demo.scenarios import get_scenario, list_scenarios


class TestDataLoading:
    """Test data loading functions."""
    
    def test_load_supplier_data(self):
        """Test supplier data loading."""
        data = load_supplier_data()
        assert data is not None
        assert len(data) > 0
        assert 'supplier_id' in data.columns
        assert 'reliability_score' in data.columns
        print("✅ Supplier data loading works")
    
    def test_load_inventory_data(self):
        """Test inventory data loading."""
        data = load_inventory_data()
        assert data is not None
        assert len(data) > 0
        assert 'product_id' in data.columns
        assert 'current_stock' in data.columns
        print("✅ Inventory data loading works")
    
    def test_load_demand_data(self):
        """Test demand data loading."""
        data = load_demand_data()
        assert data is not None
        assert len(data) > 0
        assert 'date' in data.columns or 'product_id' in data.columns
        print("✅ Demand data loading works")


class TestDataIntegrity:
    """Test data integrity and quality."""
    
    def test_supplier_data_quality(self):
        """Test supplier data quality."""
        data = load_supplier_data()
        
        # Check for required columns
        required_cols = ['supplier_id', 'supplier_name', 'country', 'reliability_score']
        for col in required_cols:
            assert col in data.columns, f"Missing column: {col}"
        
        # Check data types
        assert data['reliability_score'].dtype in ['float64', 'float32'], "Reliability score should be float"
        
        # Check value ranges
        assert (data['reliability_score'] >= 0).all(), "Reliability scores should be >= 0"
        assert (data['reliability_score'] <= 1).all(), "Reliability scores should be <= 1"
        
        print("✅ Supplier data quality checks passed")
    
    def test_inventory_data_quality(self):
        """Test inventory data quality."""
        data = load_inventory_data()
        
        # Check for required columns
        required_cols = ['product_id', 'current_stock', 'reorder_point']
        for col in required_cols:
            assert col in data.columns, f"Missing column: {col}"
        
        # Check data types
        assert data['current_stock'].dtype in ['int64', 'int32', 'float64'], "Current stock should be numeric"
        
        # Check value ranges
        assert (data['current_stock'] >= 0).all(), "Stock levels should be >= 0"
        
        print("✅ Inventory data quality checks passed")
    
    def test_demand_data_quality(self):
        """Test demand data quality."""
        data = load_demand_data()
        
        # Check for required columns
        assert len(data.columns) > 0, "Demand data should have columns"
        
        # Check for date column if exists
        if 'date' in data.columns:
            assert pd.api.types.is_datetime64_any_dtype(data['date']) or 'date' in str(data['date'].dtype).lower(), "Date column should be datetime"
        
        print("✅ Demand data quality checks passed")


class TestScenarios:
    """Test demo scenarios."""
    
    def test_list_scenarios(self):
        """Test scenario listing."""
        scenarios = list_scenarios()
        assert len(scenarios) > 0, "Should have at least one scenario"
        assert isinstance(scenarios, list), "Scenarios should be a list"
        print(f"✅ Found {len(scenarios)} scenarios")
    
    def test_get_scenario(self):
        """Test getting a specific scenario."""
        scenarios = list_scenarios()
        if scenarios:
            scenario = get_scenario(scenarios[0])
            assert scenario is not None, "Scenario should not be None"
            assert 'name' in scenario, "Scenario should have name"
            assert 'query' in scenario, "Scenario should have query"
            assert 'expected_agents' in scenario, "Scenario should have expected_agents"
            print("✅ Scenario retrieval works")
    
    def test_scenario_structure(self):
        """Test scenario structure."""
        scenarios = list_scenarios()
        for scenario_id in scenarios:
            scenario = get_scenario(scenario_id)
            assert 'name' in scenario, f"Scenario {scenario_id} missing name"
            assert 'description' in scenario, f"Scenario {scenario_id} missing description"
            assert 'query' in scenario, f"Scenario {scenario_id} missing query"
            assert 'expected_agents' in scenario, f"Scenario {scenario_id} missing expected_agents"
            assert isinstance(scenario['expected_agents'], list), "Expected agents should be a list"
        print("✅ All scenarios have correct structure")


class TestAgentIntegration:
    """Test agent integration with Streamlit."""
    
    def test_agent_imports(self):
        """Test that all agents can be imported."""
        from supply_chain_agents import (
            orchestrator_agent,
            risk_agent,
            demand_agent,
            supplier_agent,
            inventory_agent,
            logistics_agent,
            reporting_agent
        )
        
        assert orchestrator_agent is not None
        assert risk_agent is not None
        assert demand_agent is not None
        assert supplier_agent is not None
        assert inventory_agent is not None
        assert logistics_agent is not None
        assert reporting_agent is not None
        
        print("✅ All agents imported successfully")
    
    def test_agent_tools(self):
        """Test that agents have tools."""
        from supply_chain_agents import risk_agent, demand_agent
        
        assert hasattr(risk_agent, 'tools'), "Risk agent should have tools"
        assert len(risk_agent.tools) > 0, "Risk agent should have at least one tool"
        
        assert hasattr(demand_agent, 'tools'), "Demand agent should have tools"
        assert len(demand_agent.tools) > 0, "Demand agent should have at least one tool"
        
        print("✅ Agent tools verified")


class TestRealDataUsage:
    """Test that real data is being used (not just mock)."""
    
    def test_data_source(self):
        """Test that data comes from actual data loader."""
        loader = get_data_loader()
        
        # Test supplier data
        suppliers = loader.load_supplier_data()
        assert len(suppliers) > 0, "Should have supplier data"
        
        # Test inventory data
        inventory = loader.load_inventory_data()
        assert len(inventory) > 0, "Should have inventory data"
        
        # Test demand data
        demand = loader.load_demand_history(days_back=30)
        assert len(demand) > 0, "Should have demand data"
        
        print("✅ Real data sources verified")
    
    def test_data_freshness(self):
        """Test that data can be refreshed."""
        # Clear cache and reload
        loader = get_data_loader()
        loader.clear_cache()
        
        # Reload data
        suppliers = loader.load_supplier_data()
        assert len(suppliers) > 0, "Should reload supplier data"
        
        print("✅ Data refresh works")


def run_all_tests():
    """Run all Streamlit tests."""
    import pandas as pd
    
    print("=" * 60)
    print("RUNNING STREAMLIT APPLICATION TESTS")
    print("=" * 60)
    print()
    
    test_classes = [
        TestDataLoading,
        TestDataIntegrity,
        TestScenarios,
        TestAgentIntegration,
        TestRealDataUsage
    ]
    
    passed = 0
    failed = 0
    
    for test_class in test_classes:
        print(f"Testing {test_class.__name__}...")
        instance = test_class()
        for method_name in dir(instance):
            if method_name.startswith("test_"):
                method = getattr(instance, method_name)
                try:
                    method()
                    passed += 1
                except Exception as e:
                    print(f"❌ {method_name} failed: {e}")
                    failed += 1
        print()
    
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    import pandas as pd
    success = run_all_tests()
    sys.exit(0 if success else 1)



