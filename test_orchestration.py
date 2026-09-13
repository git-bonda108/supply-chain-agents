"""
Test Multi-Agent Orchestration
"""

import asyncio
import os
from dotenv import load_dotenv
from agents import Runner
from supply_chain_agents import orchestrator_agent

# Load environment variables
load_dotenv()

async def test_orchestration():
    """Test orchestrator with a complex query."""
    os.makedirs("data", exist_ok=True)
    # Session will be created automatically by Runner if needed
    session = None
    
    print("=" * 60)
    print("Testing Multi-Agent Orchestration")
    print("=" * 60)
    print()
    
    # Test query that requires multiple agents
    query = "We're seeing delays in memory chip deliveries from China. Assess the risks, forecast demand, evaluate our suppliers, and recommend actions."
    
    print(f"Query: {query}")
    print()
    print("Orchestrator will coordinate multiple agents...")
    print()
    
    try:
        result = await Runner.run(
            orchestrator_agent,
            query,
            session=session
        )
        
        print("=" * 60)
        print("ORCHESTRATOR RESULT")
        print("=" * 60)
        print(result.final_output)
        print()
        print("=" * 60)
        print(f"Status: {result.status}")
        print(f"Steps: {len(result.steps) if hasattr(result, 'steps') else 'N/A'}")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_orchestration())

