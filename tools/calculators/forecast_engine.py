"""
Forecast Engine for Demand Forecasting Agent
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from datetime import datetime, timedelta
from tools.data_loader import get_data_loader
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)


def generate_demand_forecast(
    product_id: str,
    forecast_days: int = 30,
    confidence_level: float = 0.95
) -> Dict:
    """
    Generate demand forecast for a product.
    
    Args:
        product_id: Product ID to forecast
        forecast_days: Number of days to forecast ahead
        confidence_level: Confidence level for intervals (default: 0.95)
    
    Returns:
        Dict with forecast data
    """
    try:
        data_loader = get_data_loader()
        
        # Load historical demand
        demand_history = data_loader.load_demand_history(
            product_id=product_id,
            days_back=365
        )
        
        if len(demand_history) < 30:
            return {
                "product_id": product_id,
                "error": "Insufficient historical data",
                "forecast_days": forecast_days
            }
        
        # Prepare data
        demand_history = demand_history.sort_values("date")
        demand_history["days"] = (demand_history["date"] - demand_history["date"].min()).dt.days
        
        # Simple trend + seasonality model
        X = demand_history[["days", "weekday", "month"]].values
        y = demand_history["demand"].values
        
        # Train model
        model = LinearRegression()
        model.fit(X, y)
        
        # Generate forecast dates
        last_date = demand_history["date"].max()
        forecast_dates = pd.date_range(
            start=last_date + timedelta(days=1),
            periods=forecast_days,
            freq="D"
        )
        
        # Prepare forecast features
        forecast_data = []
        for i, date in enumerate(forecast_dates):
            days_from_start = (date - demand_history["date"].min()).days
            forecast_data.append({
                "days": days_from_start,
                "weekday": date.weekday(),
                "month": date.month
            })
        
        forecast_df = pd.DataFrame(forecast_data)
        X_forecast = forecast_df[["days", "weekday", "month"]].values
        
        # Generate predictions
        predictions = model.predict(X_forecast)
        predictions = np.maximum(predictions, 0)  # No negative demand
        
        # Calculate confidence intervals
        residuals = y - model.predict(X)
        std_error = np.std(residuals)
        z_score = 1.96 if confidence_level == 0.95 else 2.58  # 95% or 99%
        
        forecasts = []
        for i, (date, pred) in enumerate(zip(forecast_dates, predictions)):
            lower = max(0, pred - z_score * std_error)
            upper = pred + z_score * std_error
            
            forecasts.append({
                "date": date.strftime("%Y-%m-%d"),
                "forecast": int(pred),
                "lower_bound": int(lower),
                "upper_bound": int(upper)
            })
        
        # Calculate summary statistics
        avg_forecast = np.mean(predictions)
        trend = "INCREASING" if predictions[-1] > predictions[0] else "DECREASING" if predictions[-1] < predictions[0] else "STABLE"
        
        return {
            "product_id": product_id,
            "forecast_days": forecast_days,
            "forecasts": forecasts,
            "summary": {
                "average_demand": int(avg_forecast),
                "trend": trend,
                "confidence_level": confidence_level,
                "model_type": "Linear Regression with Seasonality"
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Forecast error: {e}")
        return {
            "product_id": product_id,
            "error": str(e),
            "forecast_days": forecast_days
        }


def detect_shortages(
    product_id: str,
    forecast_days: int = 30,
    current_stock: Optional[int] = None
) -> Dict:
    """
    Detect potential shortages based on forecast and inventory.
    
    Args:
        product_id: Product ID
        forecast_days: Days to analyze
        current_stock: Current stock level (if None, loads from data)
    
    Returns:
        Dict with shortage analysis
    """
    try:
        # Generate forecast
        forecast = generate_demand_forecast(product_id, forecast_days)
        
        if "error" in forecast:
            return forecast
        
        # Get current stock
        if current_stock is None:
            data_loader = get_data_loader()
            inventory = data_loader.load_inventory_data(product_id)
            if len(inventory) > 0:
                current_stock = inventory.iloc[0]["current_stock"]
            else:
                current_stock = 0
        
        # Calculate cumulative demand
        cumulative_demand = sum(f["forecast"] for f in forecast["forecasts"])
        
        # Calculate days until stockout
        daily_avg = cumulative_demand / forecast_days
        days_until_stockout = current_stock / daily_avg if daily_avg > 0 else float('inf')
        
        # Determine shortage risk
        if days_until_stockout < 7:
            risk_level = "CRITICAL"
        elif days_until_stockout < 14:
            risk_level = "HIGH"
        elif days_until_stockout < 30:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            "product_id": product_id,
            "current_stock": int(current_stock),
            "forecasted_demand": int(cumulative_demand),
            "days_until_stockout": int(days_until_stockout) if days_until_stockout != float('inf') else None,
            "shortage_risk": risk_level,
            "recommendations": _get_shortage_recommendations(risk_level, days_until_stockout),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Shortage detection error: {e}")
        return {
            "product_id": product_id,
            "error": str(e)
        }


def _get_shortage_recommendations(risk_level: str, days_until_stockout: float) -> list:
    """Get recommendations based on shortage risk."""
    if risk_level == "CRITICAL":
        return [
            "Immediate reorder required",
            "Contact suppliers for expedited delivery",
            "Consider alternative suppliers",
            "Implement allocation strategy"
        ]
    elif risk_level == "HIGH":
        return [
            "Place reorder immediately",
            "Increase safety stock levels",
            "Monitor demand closely"
        ]
    elif risk_level == "MEDIUM":
        return [
            "Plan for reorder within 1-2 weeks",
            "Review safety stock levels"
        ]
    else:
        return [
            "Continue monitoring",
            "Maintain current inventory levels"
        ]



