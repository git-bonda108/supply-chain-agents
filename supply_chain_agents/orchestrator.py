"""
Orchestrator Agent - Coordinates all agent interactions with handoffs
"""

from agents import Agent
from config.agent_configs import ORCHESTRATOR_INSTRUCTIONS
from supply_chain_agents.risk_intelligence import risk_agent
from supply_chain_agents.demand_forecasting import demand_agent
from supply_chain_agents.supplier_assessment import supplier_agent
from supply_chain_agents.inventory_optimization import inventory_agent
from supply_chain_agents.logistics_optimization import logistics_agent
from supply_chain_agents.executive_reporting import reporting_agent

def create_orchestrator_agent():
    """
    Create the orchestrator agent with handoffs to all specialized agents.
    
    Returns:
        Agent: Configured orchestrator agent with handoffs
    """
    orchestrator = Agent(
        name="Orchestrator",
        instructions=ORCHESTRATOR_INSTRUCTIONS,
        handoffs=[
            risk_agent,
            demand_agent,
            supplier_agent,
            inventory_agent,
            logistics_agent,
            reporting_agent
        ]
    )
    
    return orchestrator

# Create singleton instance
orchestrator_agent = create_orchestrator_agent()
