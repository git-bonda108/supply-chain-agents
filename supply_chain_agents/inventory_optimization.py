"""
Inventory Optimization Agent - Optimizes inventory levels
"""

from agents import Agent
from utils.tool_helpers import create_function_tool
from config.agent_configs import INVENTORY_OPTIMIZATION_INSTRUCTIONS
from tools.calculators.inventory_optimizer import optimize_inventory, calculate_reorder_point

# Create tools for the agent
def optimize_inventory_tool(
    product_id: str,
    risk_factor: float = None,
    service_level: float = 0.95
) -> dict:
    """Calculate optimal inventory levels considering risk factors and demand forecasts."""
    return optimize_inventory(product_id, risk_factor, service_level)

def calculate_reorder_point_tool(
    product_id: str,
    lead_time_days: int = None,
    service_level: float = 0.95
) -> dict:
    """Calculate reorder point for a product based on lead time and service level."""
    return calculate_reorder_point(product_id, lead_time_days, service_level)

# Create Tool objects
inventory_optimizer_tool = create_function_tool(
    name="optimize_inventory",
    description="Calculate optimal inventory levels for a product considering demand forecasts, risk factors, lead times, and service levels. Returns optimal stock level, reorder point, safety stock, and recommended actions.",
    func=optimize_inventory_tool
)

reorder_point_tool = create_function_tool(
    name="calculate_reorder_point",
    description="Calculate reorder point for a product based on average daily demand, lead time, and desired service level. Returns reorder point, safety stock, and current status.",
    func=calculate_reorder_point_tool
)

def create_inventory_agent():
    """
    Create the inventory optimization agent.
    
    Returns:
        Agent: Configured inventory optimization agent
    """
    agent = Agent(
        name="InventoryOptimization",
        instructions=INVENTORY_OPTIMIZATION_INSTRUCTIONS,
        tools=[inventory_optimizer_tool, reorder_point_tool]
    )
    
    return agent

# Create singleton instance
inventory_agent = create_inventory_agent()

