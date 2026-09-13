"""
Demand Forecasting Agent - Predicts demand and identifies shortages
"""

from agents import Agent
from utils.tool_helpers import create_function_tool
from config.agent_configs import DEMAND_FORECASTING_INSTRUCTIONS
from tools.calculators.forecast_engine import generate_demand_forecast, detect_shortages

# Create tools for the agent
def generate_forecast_tool(
    product_id: str,
    forecast_days: int = 30,
    confidence_level: float = 0.95
) -> dict:
    """Generate demand forecast for a product using time series analysis."""
    return generate_demand_forecast(product_id, forecast_days, confidence_level)

def detect_shortages_tool(
    product_id: str,
    forecast_days: int = 30,
    current_stock: int = None
) -> dict:
    """Detect potential shortages based on forecast and current inventory."""
    return detect_shortages(product_id, forecast_days, current_stock)

# Create Tool objects
forecast_tool = create_function_tool(
    name="generate_demand_forecast",
    description="Generate demand forecast for a product using historical data and time series analysis. Returns forecasted demand with confidence intervals for specified number of days.",
    func=generate_forecast_tool
)

shortage_detection_tool = create_function_tool(
    name="detect_shortages",
    description="Detect potential product shortages by comparing forecasted demand with current inventory. Returns shortage risk level and days until stockout.",
    func=detect_shortages_tool
)

def create_demand_agent():
    """
    Create the demand forecasting agent.
    
    Returns:
        Agent: Configured demand forecasting agent
    """
    agent = Agent(
        name="DemandForecasting",
        instructions=DEMAND_FORECASTING_INSTRUCTIONS,
        tools=[forecast_tool, shortage_detection_tool]
    )
    
    return agent

# Create singleton instance
demand_agent = create_demand_agent()

