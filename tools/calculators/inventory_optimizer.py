"""
Inventory Optimization Tools for Inventory Optimization Agent
"""

from typing import Dict, Optional
from tools.data_loader import get_data_loader
from tools.calculators.forecast_engine import generate_demand_forecast
from tools.calculators.risk_calculator import assess_geopolitical_risk
import numpy as np
import logging

logger = logging.getLogger(__name__)


def optimize_inventory(
    product_id: str,
    risk_factor: Optional[float] = None,
    service_level: float = 0.95
) -> Dict:
    """
    Calculate optimal inventory levels considering risk and demand.
    
    Args:
        product_id: Product ID
        risk_factor: Optional risk factor (0-1), if None, calculates from data
        service_level: Desired service level (default: 0.95 = 95%)
    
    Returns:
        Dict with optimal inventory levels
    """
    try:
        data_loader = get_data_loader()
        
        # Get current inventory
        inventory = data_loader.load_inventory_data(product_id)
        if len(inventory) == 0:
            return {
                "product_id": product_id,
                "error": "Product inventory data not found"
            }
        
        current = inventory.iloc[0]
        current_stock = current["current_stock"]
        
        # Get demand forecast
        forecast = generate_demand_forecast(product_id, forecast_days=30)
        if "error" in forecast:
            return {
                "product_id": product_id,
                "error": f"Could not generate forecast: {forecast.get('error')}"
            }
        
        avg_daily_demand = forecast["summary"]["average_demand"] / 30
        lead_time = current["lead_time_days"]
        
        # Calculate risk factor if not provided
        if risk_factor is None:
            # Get supplier risk (simplified - in real scenario, would check all suppliers)
            suppliers = data_loader.load_supplier_data()
            product_suppliers = suppliers[suppliers["product_category"].str.contains(product_id, case=False, na=False)]
            if len(product_suppliers) > 0:
                risk_factor = product_suppliers["geopolitical_risk"].mean()
            else:
                risk_factor = 0.3  # Default medium risk
        
        # Calculate safety stock with risk adjustment
        # Higher risk = higher safety stock
        risk_multiplier = 1 + (risk_factor * 0.5)  # 0-50% increase based on risk
        
        # Z-score for service level (95% = 1.645)
        z_scores = {0.90: 1.28, 0.95: 1.645, 0.99: 2.33}
        z = z_scores.get(service_level, 1.645)
        
        # Calculate demand variability (simplified)
        demand_std = avg_daily_demand * 0.2  # Assume 20% variability
        
        # Safety stock calculation
        safety_stock = z * demand_std * np.sqrt(lead_time) * risk_multiplier
        
        # Reorder point
        reorder_point = (avg_daily_demand * lead_time) + safety_stock
        
        # Optimal inventory level (EOQ-like with risk consideration)
        holding_cost = current["unit_cost"] * current["holding_cost_rate"]
        # Simplified optimal level
        optimal_level = reorder_point + (avg_daily_demand * 7)  # 1 week buffer
        
        # Determine action
        if current_stock < reorder_point:
            action = "IMMEDIATE_REORDER"
        elif current_stock < optimal_level * 0.8:
            action = "REORDER_SOON"
        elif current_stock > optimal_level * 1.5:
            action = "REDUCE_STOCK"
        else:
            action = "MAINTAIN"
        
        return {
            "product_id": product_id,
            "current_stock": int(current_stock),
            "optimal_stock": int(optimal_level),
            "reorder_point": int(reorder_point),
            "safety_stock": int(safety_stock),
            "recommended_action": action,
            "analysis": {
                "risk_factor": round(risk_factor, 3),
                "risk_multiplier": round(risk_multiplier, 3),
                "average_daily_demand": round(avg_daily_demand, 2),
                "lead_time_days": int(lead_time),
                "service_level": service_level
            },
            "cost_analysis": {
                "current_inventory_value": round(current_stock * current["unit_cost"], 2),
                "optimal_inventory_value": round(optimal_level * current["unit_cost"], 2),
                "difference": round((optimal_level - current_stock) * current["unit_cost"], 2)
            },
            "recommendations": _get_inventory_recommendations(action, current_stock, optimal_level)
        }
        
    except Exception as e:
        logger.error(f"Inventory optimization error: {e}")
        return {
            "product_id": product_id,
            "error": str(e)
        }


def calculate_reorder_point(
    product_id: str,
    lead_time_days: Optional[int] = None,
    service_level: float = 0.95
) -> Dict:
    """
    Calculate reorder point for a product.
    
    Args:
        product_id: Product ID
        lead_time_days: Optional lead time override
        service_level: Desired service level
    
    Returns:
        Dict with reorder point calculation
    """
    try:
        data_loader = get_data_loader()
        
        # Get inventory data
        inventory = data_loader.load_inventory_data(product_id)
        if len(inventory) == 0:
            return {
                "product_id": product_id,
                "error": "Product inventory data not found"
            }
        
        current = inventory.iloc[0]
        lead_time = lead_time_days or current["lead_time_days"]
        
        # Get demand forecast
        forecast = generate_demand_forecast(product_id, forecast_days=lead_time + 7)
        if "error" in forecast:
            return {
                "product_id": product_id,
                "error": f"Could not generate forecast: {forecast.get('error')}"
            }
        
        avg_daily_demand = forecast["summary"]["average_demand"] / 30
        
        # Z-score for service level
        z_scores = {0.90: 1.28, 0.95: 1.645, 0.99: 2.33}
        z = z_scores.get(service_level, 1.645)
        
        # Demand variability
        demand_std = avg_daily_demand * 0.2
        
        # Safety stock
        safety_stock = z * demand_std * np.sqrt(lead_time)
        
        # Reorder point
        reorder_point = (avg_daily_demand * lead_time) + safety_stock
        
        return {
            "product_id": product_id,
            "reorder_point": int(reorder_point),
            "safety_stock": int(safety_stock),
            "lead_time_days": int(lead_time),
            "average_daily_demand": round(avg_daily_demand, 2),
            "service_level": service_level,
            "current_stock": int(current["current_stock"]),
            "status": "BELOW_REORDER" if current["current_stock"] < reorder_point else "ABOVE_REORDER"
        }
        
    except Exception as e:
        logger.error(f"Reorder point calculation error: {e}")
        return {
            "product_id": product_id,
            "error": str(e)
        }


def _get_inventory_recommendations(action: str, current: int, optimal: int) -> list:
    """Get recommendations based on inventory action."""
    recommendations = {
        "IMMEDIATE_REORDER": [
            "Place reorder immediately",
            "Stock level is below reorder point",
            "Consider expedited delivery if critical"
        ],
        "REORDER_SOON": [
            "Plan reorder within next few days",
            "Monitor stock levels closely",
            "Ensure supplier capacity available"
        ],
        "REDUCE_STOCK": [
            "Current stock is above optimal level",
            "Consider reducing order quantities",
            "Review demand forecasts for accuracy"
        ],
        "MAINTAIN": [
            "Current stock levels are appropriate",
            "Continue monitoring",
            "Maintain current ordering patterns"
        ]
    }
    return recommendations.get(action, ["Review inventory levels"])



