"""
Demo Scenarios for Supply Chain AI System
"""

from typing import Dict, List

# Demo scenario definitions
DEMO_SCENARIOS = {
    "memory_chip_shortage": {
        "name": "Memory Chip Shortage Crisis",
        "description": "Assess risks and recommend actions for memory chip delivery delays from China",
        "query": "We're seeing delays in memory chip deliveries from China. Assess the geopolitical risks, forecast demand for the next 3 months, evaluate our current suppliers, optimize inventory levels, and provide comprehensive recommendations.",
        "expected_agents": ["RiskIntelligence", "DemandForecasting", "SupplierAssessment", "InventoryOptimization", "ExecutiveReporting"],
        "key_metrics": ["risk_score", "shortage_risk", "alternative_suppliers", "optimal_inventory"]
    },
    "geopolitical_risk_assessment": {
        "name": "Geopolitical Risk Assessment",
        "description": "Evaluate supply chain exposure to export controls",
        "query": "Evaluate our supply chain exposure to China export controls for rare earth materials. Assess risks, identify affected suppliers, suggest alternative routes, and provide mitigation strategies.",
        "expected_agents": ["RiskIntelligence", "SupplierAssessment", "LogisticsOptimization", "ExecutiveReporting"],
        "key_metrics": ["export_control_status", "affected_suppliers", "alternative_routes", "risk_level"]
    },
    "demand_spike_prediction": {
        "name": "Demand Spike Prediction",
        "description": "Predict demand spike and optimize inventory",
        "query": "Predict demand for Product_1 over the next 6 months. Identify potential shortages, optimize inventory levels considering current risks, and recommend actions.",
        "expected_agents": ["DemandForecasting", "InventoryOptimization", "ExecutiveReporting"],
        "key_metrics": ["forecast_trend", "shortage_risk", "optimal_stock", "reorder_point"]
    },
    "supplier_diversification": {
        "name": "Supplier Diversification Strategy",
        "description": "Evaluate and diversify supplier base",
        "query": "Evaluate our current supplier SUP001 for memory chips. Find alternative suppliers, assess their reliability and risk factors, and recommend a diversification strategy.",
        "expected_agents": ["SupplierAssessment", "RiskIntelligence", "ExecutiveReporting"],
        "key_metrics": ["current_supplier_score", "alternatives_count", "diversification_recommendations"]
    },
    "comprehensive_analysis": {
        "name": "Comprehensive Supply Chain Analysis",
        "description": "Full end-to-end supply chain analysis",
        "query": "Perform a comprehensive analysis of our supply chain: assess all geopolitical risks, forecast demand for our top 5 products, evaluate all suppliers, optimize inventory across all products, analyze logistics routes, and provide an executive summary with actionable recommendations.",
        "expected_agents": ["RiskIntelligence", "DemandForecasting", "SupplierAssessment", "InventoryOptimization", "LogisticsOptimization", "ExecutiveReporting"],
        "key_metrics": ["overall_risk", "inventory_optimization", "supplier_reliability", "logistics_efficiency"]
    }
}


def get_scenario(scenario_id: str) -> Dict:
    """Get a demo scenario by ID."""
    return DEMO_SCENARIOS.get(scenario_id, {})


def list_scenarios() -> List[str]:
    """List all available scenario IDs."""
    return list(DEMO_SCENARIOS.keys())


def get_scenario_summary() -> str:
    """Get a summary of all scenarios."""
    summary = "Available Demo Scenarios:\n" + "=" * 60 + "\n\n"
    for scenario_id, scenario in DEMO_SCENARIOS.items():
        summary += f"ID: {scenario_id}\n"
        summary += f"Name: {scenario['name']}\n"
        summary += f"Description: {scenario['description']}\n"
        summary += f"Expected Agents: {', '.join(scenario['expected_agents'])}\n"
        summary += "\n"
    return summary



