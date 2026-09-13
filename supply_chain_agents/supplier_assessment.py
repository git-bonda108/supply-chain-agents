"""
Supplier Assessment Agent - Evaluates suppliers and recommends alternatives
"""

from agents import Agent
from utils.tool_helpers import create_function_tool
from config.agent_configs import SUPPLIER_ASSESSMENT_INSTRUCTIONS
from tools.calculators.supplier_evaluator import evaluate_supplier, find_alternatives

# Create tools for the agent
def evaluate_supplier_tool(
    supplier_id: str,
    include_risk_assessment: bool = True
) -> dict:
    """Evaluate a supplier's reliability, performance, and risk factors."""
    return evaluate_supplier(supplier_id, include_risk_assessment)

def find_alternatives_tool(
    current_supplier_id: str,
    product_category: str = None,
    exclude_countries: list = None,
    min_reliability: float = 0.7
) -> dict:
    """Find alternative suppliers for a given supplier based on product category and reliability."""
    return find_alternatives(current_supplier_id, product_category, exclude_countries, min_reliability)

# Create Tool objects
supplier_evaluation_tool = create_function_tool(
    name="evaluate_supplier",
    description="Evaluate a supplier's reliability, performance metrics, and risk factors. Returns reliability score, rating, and detailed metrics including real-time geopolitical risk assessment.",
    func=evaluate_supplier_tool
)

find_alternatives_tool_obj = create_function_tool(
    name="find_alternatives",
    description="Find alternative suppliers for a given supplier. Returns list of alternative suppliers with match scores, reliability scores, and recommendations for diversification.",
    func=find_alternatives_tool
)

def create_supplier_agent():
    """
    Create the supplier assessment agent.
    
    Returns:
        Agent: Configured supplier assessment agent
    """
    agent = Agent(
        name="SupplierAssessment",
        instructions=SUPPLIER_ASSESSMENT_INSTRUCTIONS,
        tools=[supplier_evaluation_tool, find_alternatives_tool_obj]
    )
    
    return agent

# Create singleton instance
supplier_agent = create_supplier_agent()

