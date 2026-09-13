"""
Supply Chain AI Demo - Main Entry Point
Multi-Agent System using OpenAI Agents SDK
"""

import asyncio
import os
from dotenv import load_dotenv
from agents import Agent, Runner

# Load environment variables
load_dotenv()

# Setup logging
from utils.helpers import setup_logging, validate_api_keys
setup_logging()

# Import data infrastructure
from tools.data_loader import get_data_loader
from tools.mock_data_generator import MockDataGenerator

# Import agents
from supply_chain_agents import risk_agent, demand_agent, supplier_agent, inventory_agent
# from supply_chain_agents.orchestrator import orchestrator_agent

async def main():
    """Main demo function"""
    print("=" * 60)
    print("Supply Chain AI Demo - Multi-Agent System")
    print("Built with OpenAI Agents SDK for Bristlecone")
    print("=" * 60)
    print()
    
    # Validate API keys
    print("Validating API keys...")
    api_keys = validate_api_keys()
    for key, valid in api_keys.items():
        status = "✅" if valid else "❌"
        print(f"  {status} {key}")
    
    if not all(api_keys.values()):
        print("\n⚠️  Warning: Some API keys are missing. Some features may not work.")
        print("   Check your .env file.\n")
    
    # Initialize data infrastructure
    print("\nInitializing data infrastructure...")
    data_loader = get_data_loader()
    
    # Generate mock data if needed
    if not os.path.exists("data/processed/suppliers.csv"):
        print("Generating mock data...")
        generator = MockDataGenerator()
        generator.generate_all_data()
    
    print("✅ Data infrastructure ready\n")
    
    # Session will be created automatically by Runner if needed
    os.makedirs("data", exist_ok=True)
    session = None
    
    # Example query
    print("=" * 60)
    query = input("Enter your supply chain query (or 'demo' for example): ").strip()
    
    if query.lower() == 'demo':
        query = "We're seeing delays in memory chip deliveries. Assess the situation and recommend actions."
        print(f"\nRunning demo scenario: {query}\n")
    
    # Run orchestrator agent
    from agents import Runner
    from supply_chain_agents import orchestrator_agent
    
    print("Processing query with orchestrator...")
    print()
    
    try:
        result = await Runner.run(
            orchestrator_agent,
            query,
            session=session
        )
        
        print("\n" + "=" * 60)
        print("RESULT")
        print("=" * 60)
        print(result.final_output if hasattr(result, 'final_output') else result)
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nNote: Make sure your OPENAI_API_KEY is set correctly in .env file")

if __name__ == "__main__":
    asyncio.run(main())

