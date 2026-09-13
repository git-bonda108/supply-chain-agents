"""
Executive Reporting Agent - Generates comprehensive reports
"""

from agents import Agent
from utils.tool_helpers import create_function_tool
from config.agent_configs import EXECUTIVE_REPORTING_INSTRUCTIONS
from tools.report_generator import aggregate_insights, generate_executive_report

# Create tools for the agent
def aggregate_insights_tool(agent_outputs: list) -> dict:
    """Aggregate insights from multiple agent outputs."""
    return aggregate_insights(agent_outputs)

def generate_report_tool(insights: dict, format: str = "text") -> str:
    """Generate executive report from aggregated insights."""
    return generate_executive_report(insights, format)

# Create Tool objects
aggregate_tool = create_function_tool(
    name="aggregate_insights",
    description="Aggregate insights from multiple agent outputs into a unified view. Takes list of agent outputs and returns aggregated insights with summary, key findings, and recommendations.",
    func=aggregate_insights_tool
)

report_generator_tool = create_function_tool(
    name="generate_executive_report",
    description="Generate comprehensive executive report from aggregated insights. Returns formatted report with executive summary, key findings, risk assessment, and recommendations.",
    func=generate_report_tool
)

def create_reporting_agent():
    """
    Create the executive reporting agent.
    
    Returns:
        Agent: Configured executive reporting agent
    """
    agent = Agent(
        name="ExecutiveReporting",
        instructions=EXECUTIVE_REPORTING_INSTRUCTIONS,
        tools=[aggregate_tool, report_generator_tool]
    )
    
    return agent

# Create singleton instance
reporting_agent = create_reporting_agent()



