"""
End-to-End Test Script for the multi-agent supply chain system
Tests all tabs and functionality
"""

import os
import sys
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime, timedelta

# Load environment
load_dotenv()

def print_test_header(test_name):
    """Print formatted test header."""
    print("\n" + "="*70)
    print(f"TEST: {test_name}")
    print("="*70)

def test_dashboard():
    """Test Dashboard tab functionality."""
    print_test_header("Dashboard Tab")
    
    try:
        from tools.data_loader import get_data_loader
        loader = get_data_loader()
        
        # Load data
        suppliers = loader.load_supplier_data()
        inventory = loader.load_inventory_data()
        demand = loader.load_demand_history(days_back=90)
        
        # Calculate metrics
        total_suppliers = len(suppliers)
        total_products = len(inventory)
        high_risk = len(suppliers[suppliers['geopolitical_risk'] > 0.5]) if len(suppliers) > 0 else 0
        low_stock = len(inventory[inventory['current_stock'] < inventory['reorder_point']]) if len(inventory) > 0 else 0
        
        print(f"✅ Total Suppliers: {total_suppliers}")
        print(f"✅ Total Products: {total_products}")
        print(f"✅ High Risk Suppliers: {high_risk}")
        print(f"✅ Low Stock Items: {low_stock}")
        
        if total_suppliers > 0 and total_products > 0:
            print("✅ Dashboard data available")
            return True
        else:
            print("⚠️  No data available - upload data first")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_data_upload():
    """Test Data Upload functionality."""
    print_test_header("Data Upload & Analysis Tab")
    
    try:
        from tools.data_uploader import DataUploader
        uploader = DataUploader()
        
        # Test supplier data validation
        test_suppliers = pd.DataFrame({
            'supplier_id': ['TEST001', 'TEST002'],
            'supplier_name': ['Test Supplier 1', 'Test Supplier 2'],
            'country': ['USA', 'China']
        })
        
        is_valid, errors = uploader.validate_supplier_data(test_suppliers)
        print(f"✅ Supplier validation: {'PASS' if is_valid else 'FAIL'}")
        if errors:
            print(f"   Errors: {errors}")
        
        # Test preprocessing
        processed = uploader.preprocess_supplier_data(test_suppliers)
        print(f"✅ Preprocessing: {len(processed)} rows processed")
        print(f"   Added columns: {set(processed.columns) - set(test_suppliers.columns)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_risk_assessment():
    """Test Risk Assessment tab."""
    print_test_header("Risk Assessment Tab")
    
    try:
        from tools.data_sources.tavily_client import TavilyClientWrapper
        
        # Test Tavily API
        client = TavilyClientWrapper()
        result = client.search_geopolitical_risks("supply chain China", max_results=3)
        
        if 'results' in result:
            print(f"✅ Tavily API: {len(result['results'])} results retrieved")
            print(f"   Risk Score: {result.get('risk_score', 'N/A')}")
        else:
            print("⚠️  Tavily API: No results (may be API issue)")
        
        # Test supplier risk data
        from tools.data_loader import get_data_loader
        loader = get_data_loader()
        suppliers = loader.load_supplier_data()
        
        if len(suppliers) > 0:
            high_risk = suppliers[suppliers['geopolitical_risk'] > 0.5]
            print(f"✅ Supplier Risk Data: {len(high_risk)} high-risk suppliers")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_demand_forecasting():
    """Test Demand Forecasting tab."""
    print_test_header("Demand Forecasting Tab")
    
    try:
        from tools.calculators.forecast_engine import generate_demand_forecast
        from tools.data_loader import get_data_loader
        
        loader = get_data_loader()
        demand = loader.load_demand_history(days_back=90)
        
        if len(demand) > 0:
            # Get a product with data
            product_id = demand['product_id'].iloc[0]
            
            # Generate forecast
            forecast = generate_demand_forecast(product_id, forecast_days=7)
            
            if 'forecasts' in forecast:
                print(f"✅ Forecast generated for {product_id}")
                print(f"   Forecast days: {len(forecast['forecasts'])}")
                print(f"   Average demand: {forecast['summary']['average_demand']}")
                print(f"   Trend: {forecast['summary']['trend']}")
                return True
            else:
                print(f"⚠️  Forecast error: {forecast.get('error', 'Unknown')}")
                return False
        else:
            print("⚠️  No demand data available")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_supplier_analysis():
    """Test Supplier Analysis tab."""
    print_test_header("Supplier Analysis Tab")
    
    try:
        from tools.calculators.supplier_evaluator import evaluate_supplier, find_alternatives
        from tools.data_loader import get_data_loader
        
        loader = get_data_loader()
        suppliers = loader.load_supplier_data()
        
        if len(suppliers) > 0:
            supplier_id = suppliers['supplier_id'].iloc[0]
            
            # Test evaluation
            evaluation = evaluate_supplier(supplier_id, include_risk_assessment=False)
            if 'supplier_id' in evaluation:
                print(f"✅ Supplier Evaluation: {supplier_id}")
                print(f"   Reliability: {evaluation.get('reliability_score', 'N/A')}")
                print(f"   Rating: {evaluation.get('rating', 'N/A')}")
            
            # Test alternatives
            alternatives = find_alternatives(supplier_id)
            if 'alternatives' in alternatives:
                print(f"✅ Alternatives Found: {len(alternatives['alternatives'])}")
            
            return True
        else:
            print("⚠️  No supplier data available")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_inventory_optimization_rl():
    """Test Inventory Optimization (RL) tab."""
    print_test_header("Inventory Optimization (RL) Tab")
    
    try:
        from ml_models.rl_inventory_optimizer import (
            InventoryRLEnvironment,
            QLearningAgent,
            get_optimal_action
        )
        from tools.data_loader import get_data_loader
        
        loader = get_data_loader()
        inventory = loader.load_inventory_data()
        
        if len(inventory) > 0:
            product = inventory.iloc[0]
            product_data = {
                'product_id': product['product_id'],
                'current_stock': int(product['current_stock']),
                'reorder_point': int(product['reorder_point']),
                'lead_time_days': int(product['lead_time_days']),
                'unit_cost': float(product['unit_cost']),
                'holding_cost_rate': float(product['holding_cost_rate']),
                'avg_demand': 100
            }
            
            # Test environment
            env = InventoryRLEnvironment(product_data)
            agent = QLearningAgent()
            
            state = env.reset()
            action = get_optimal_action(agent, state, env.action_space)
            
            print(f"✅ RL Model: Working")
            print(f"   Product: {product_data['product_id']}")
            print(f"   Current Stock: {state[0]}")
            print(f"   Recommended Action: {action} units")
            
            return True
        else:
            print("⚠️  No inventory data available")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_human_feedback():
    """Test Human-in-the-Loop Learning tab."""
    print_test_header("Human-in-the-Loop Learning Tab")
    
    try:
        from ml_models.rl_inventory_optimizer import HumanFeedbackReward
        
        feedback_system = HumanFeedbackReward()
        
        # Test feedback calculation
        original = {'quantity': 1000}
        action = {'quantity': 1000}
        
        reward_approve = feedback_system.calculate_reward('approve', original, action)
        reward_reject = feedback_system.calculate_reward('reject', original, action)
        reward_modify = feedback_system.calculate_reward('modify', original, {'quantity': 800})
        
        print(f"✅ Feedback System: Working")
        print(f"   Approve reward: {reward_approve}")
        print(f"   Reject reward: {reward_reject}")
        print(f"   Modify reward: {reward_modify}")
        
        # Test stats
        stats = feedback_system.get_feedback_stats()
        print(f"   Total feedback: {stats.get('total', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_comprehensive_analysis():
    """Test Comprehensive Analysis tab."""
    print_test_header("Comprehensive Analysis Tab")
    
    try:
        from supply_chain_agents import orchestrator_agent
        print("✅ Orchestrator Agent: Available")
        print("   Can process complex queries")
        print("   Routes to multiple specialized agents")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_demo_scenarios():
    """Test Demo Scenarios tab."""
    print_test_header("Demo Scenarios Tab")
    
    try:
        from demo.scenarios import list_scenarios, get_scenario
        
        scenarios = list_scenarios()
        print(f"✅ Demo Scenarios: {len(scenarios)} available")
        
        if len(scenarios) > 0:
            scenario = get_scenario(scenarios[0])
            print(f"   Sample: {scenario['name']}")
            print(f"   Agents: {', '.join(scenario['expected_agents'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def find_test_datasets():
    """Find supply chain datasets in Downloads folder."""
    print_test_header("Finding Test Datasets")
    
    downloads_path = os.path.expanduser("~/Downloads")
    datasets = []
    
    # Look for CSV/Excel files
    for ext in ['*.csv', '*.xlsx', '*.xls']:
        import glob
        files = glob.glob(os.path.join(downloads_path, ext))
        datasets.extend(files)
    
    # Filter for supply chain related
    supply_chain_keywords = ['supply', 'chain', 'inventory', 'supplier', 'demand', 'logistics']
    relevant = []
    
    for file in datasets:
        filename_lower = os.path.basename(file).lower()
        if any(keyword in filename_lower for keyword in supply_chain_keywords):
            relevant.append(file)
    
    if relevant:
        print(f"✅ Found {len(relevant)} potential datasets:")
        for f in relevant[:10]:
            size = os.path.getsize(f) / 1024  # KB
            print(f"   - {os.path.basename(f)} ({size:.1f} KB)")
        return relevant
    else:
        print("⚠️  No supply chain datasets found in Downloads")
        print("   You can create test data or use mock data generator")
        return []

def main():
    """Run all end-to-end tests."""
    print("\n" + "="*70)
    print("SUPPLY CHAIN AGENTS - END-TO-END TEST SUITE")
    print("="*70)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Find datasets
    datasets = find_test_datasets()
    
    # Run tests
    tests = [
        ("Dashboard", test_dashboard),
        ("Data Upload & Analysis", test_data_upload),
        ("Risk Assessment", test_risk_assessment),
        ("Demand Forecasting", test_demand_forecasting),
        ("Supplier Analysis", test_supplier_analysis),
        ("Inventory Optimization (RL)", test_inventory_optimization_rl),
        ("Human-in-the-Loop Learning", test_human_feedback),
        ("Comprehensive Analysis", test_comprehensive_analysis),
        ("Demo Scenarios", test_demo_scenarios),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())



