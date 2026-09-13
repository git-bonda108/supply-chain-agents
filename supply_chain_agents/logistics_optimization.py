"""
Logistics Optimization Agent - Optimizes transportation and routing
"""

from agents import Agent
from utils.tool_helpers import create_function_tool
from config.agent_configs import LOGISTICS_OPTIMIZATION_INSTRUCTIONS
from tools.calculators.logistics_optimizer import optimize_route, compare_transportation_modes

# Create tools for the agent
def optimize_route_tool(
    origin: str,
    destination: str,
    product_category: str = None,
    exclude_countries: list = None
) -> dict:
    """Optimize transportation route considering geopolitical risks."""
    return optimize_route(origin, destination, product_category, exclude_countries)

def compare_transportation_modes_tool(
    origin: str,
    destination: str,
    product_category: str = None
) -> dict:
    """Compare different transportation modes for a route."""
    return compare_transportation_modes(origin, destination, product_category)

# Create Tool objects
route_optimizer_tool = create_function_tool(
    name="optimize_route",
    description="Optimize transportation route from origin to destination considering geopolitical risks, export controls, and transit times. Returns recommended route with risk assessment and alternatives.",
    func=optimize_route_tool
)

transportation_mode_tool = create_function_tool(
    name="compare_transportation_modes",
    description="Compare different transportation modes (air, sea, rail) for a route. Returns cost, transit time, reliability, and risk comparison for each mode.",
    func=compare_transportation_modes_tool
)

def create_logistics_agent():
    """
    Create the logistics optimization agent.
    
    Returns:
        Agent: Configured logistics optimization agent
    """
    agent = Agent(
        name="LogisticsOptimization",
        instructions=LOGISTICS_OPTIMIZATION_INSTRUCTIONS,
        tools=[route_optimizer_tool, transportation_mode_tool]
    )
    
    return agent

# Create singleton instance
logistics_agent = create_logistics_agent()



