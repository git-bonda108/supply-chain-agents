"""
Quick test script for agents
"""

import asyncio
from agents import Runner
from supply_chain_agents import risk_agent, demand_agent, supplier_agent, inventory_agent
import os

async def test_agents():
    """Test each agent with a simple query."""
    os.makedirs("data", exist_ok=True)
    # Session will be created automatically by Runner if needed
    session = None
    
    print("=" * 60)
    print("Testing Supply Chain Agents")
    print("=" * 60)
    print()
    
    # Test Risk Intelligence Agent
    print("1. Testing Risk Intelligence Agent...")
    try:
        result = await Runner.run(
            risk_agent,
            "Assess the geopolitical risk for memory chips from China",
            session=session
        )
        print(f"✅ Risk Agent Response: {result.final_output[:200]}...")
    except Exception as e:
        print(f"❌ Risk Agent Error: {e}")
    
    print()
    
    # Test Demand Forecasting Agent
    print("2. Testing Demand Forecasting Agent...")
    try:
        result = await Runner.run(
            demand_agent,
            "Forecast demand for Product_1 for the next 30 days",
            session=session
        )
        print(f"✅ Demand Agent Response: {result.final_output[:200]}...")
    except Exception as e:
        print(f"❌ Demand Agent Error: {e}")
    
    print()
    
    # Test Supplier Assessment Agent
    print("3. Testing Supplier Assessment Agent...")
    try:
        result = await Runner.run(
            supplier_agent,
            "Evaluate supplier SUP001 and find alternatives",
            session=session
        )
        print(f"✅ Supplier Agent Response: {result.final_output[:200]}...")
    except Exception as e:
        print(f"❌ Supplier Agent Error: {e}")
    
    print()
    
    # Test Inventory Optimization Agent
    print("4. Testing Inventory Optimization Agent...")
    try:
        result = await Runner.run(
            inventory_agent,
            "Optimize inventory for Product_1",
            session=session
        )
        print(f"✅ Inventory Agent Response: {result.final_output[:200]}...")
    except Exception as e:
        print(f"❌ Inventory Agent Error: {e}")
    
    print()
    print("=" * 60)
    print("Agent Testing Complete")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_agents())

