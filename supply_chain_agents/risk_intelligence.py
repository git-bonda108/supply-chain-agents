"""
Risk Intelligence Agent - Monitors and assesses supply chain risks
Uses real-time Tavily API for geopolitical risk monitoring
"""

from agents import Agent
from utils.tool_helpers import create_function_tool
from config.agent_configs import RISK_INTELLIGENCE_INSTRUCTIONS
from tools.calculators.risk_calculator import calculate_risk_score, assess_geopolitical_risk
from tools.data_sources import get_tavily_client

# Create tools for the agent
def calculate_risk_score_tool(
    geopolitical_risk: float,
    supplier_reliability: float,
    market_volatility: float,
    export_control_status: str
) -> dict:
    """Calculate overall supply chain risk score."""
    return calculate_risk_score(
        geopolitical_risk,
        supplier_reliability,
        market_volatility,
        export_control_status
    )

def assess_geopolitical_risk_tool(
    country: str,
    product: str = None,
    use_cache: bool = True
) -> dict:
    """Assess geopolitical risk for a country/product using real-time Tavily API."""
    return assess_geopolitical_risk(country, product, use_cache)

def search_geopolitical_risks_tool(
    query: str,
    region: str = None,
    max_results: int = 10
) -> dict:
    """Search for geopolitical risks using Tavily real-time search."""
    try:
        tavily = get_tavily_client()
        return tavily.search_geopolitical_risks(query, region, max_results)
    except Exception as e:
        return {
            "error": str(e),
            "query": query,
            "region": region
        }

def search_export_controls_tool(
    country: str,
    product: str = None
) -> dict:
    """Search for export control information using Tavily."""
    try:
        tavily = get_tavily_client()
        return tavily.search_export_controls(country, product)
    except Exception as e:
        return {
            "error": str(e),
            "country": country,
            "product": product
        }

# Create Tool objects
risk_calculator_tool = create_function_tool(
    name="calculate_risk_score",
    description="Calculate overall supply chain risk score based on geopolitical risk, supplier reliability, market volatility, and export control status. Returns risk score (0-1), risk level, and breakdown.",
    func=calculate_risk_score_tool
)

geopolitical_risk_tool = create_function_tool(
    name="assess_geopolitical_risk",
    description="Assess geopolitical risk for a specific country and product using real-time Tavily API. Returns risk score, export control status, and recent events.",
    func=assess_geopolitical_risk_tool
)

geopolitical_search_tool = create_function_tool(
    name="search_geopolitical_risks",
    description="Search for geopolitical risks and events affecting supply chains using real-time Tavily search. Returns relevant articles and risk scores.",
    func=search_geopolitical_risks_tool
)

export_control_search_tool = create_function_tool(
    name="search_export_controls",
    description="Search for export control information for a country/product using Tavily. Returns export control status and restrictions.",
    func=search_export_controls_tool
)

def create_risk_agent():
    """
    Create the risk intelligence agent with real-time data tools.
    
    Returns:
        Agent: Configured risk intelligence agent
    """
    agent = Agent(
        name="RiskIntelligence",
        instructions=RISK_INTELLIGENCE_INSTRUCTIONS,
        tools=[
            risk_calculator_tool,
            geopolitical_risk_tool,
            geopolitical_search_tool,
            export_control_search_tool
        ]
    )
    
    return agent

# Create singleton instance
risk_agent = create_risk_agent()

