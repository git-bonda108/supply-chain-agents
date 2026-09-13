"""
Demo Runner for Supply Chain AI System
"""

import asyncio
import os
from typing import Dict, List
from dotenv import load_dotenv
from agents import Runner
from supply_chain_agents import orchestrator_agent
from demo.scenarios import get_scenario, list_scenarios, get_scenario_summary
from utils.helpers import setup_logging, validate_api_keys
import time

# Load environment variables
load_dotenv()
setup_logging()


class DemoRunner:
    """Run demo scenarios with comprehensive testing."""
    
    def __init__(self):
        """Initialize demo runner."""
        self.orchestrator = orchestrator_agent
        self.results = []
    
    async def run_scenario(self, scenario_id: str, verbose: bool = True) -> Dict:
        """
        Run a demo scenario.
        
        Args:
            scenario_id: Scenario ID from scenarios.py
            verbose: Whether to print detailed output
        
        Returns:
            Dict with scenario results
        """
        scenario = get_scenario(scenario_id)
        if not scenario:
            return {"error": f"Scenario '{scenario_id}' not found"}
        
        if verbose:
            print("=" * 60)
            print(f"SCENARIO: {scenario['name']}")
            print("=" * 60)
            print(f"Description: {scenario['description']}")
            print(f"Query: {scenario['query']}")
            print()
            print("Running orchestrator...")
            print()
        
        start_time = time.time()
        
        try:
            result = await Runner.run(
                self.orchestrator,
                scenario['query'],
                session=None
            )
            
            elapsed_time = time.time() - start_time
            
            scenario_result = {
                "scenario_id": scenario_id,
                "scenario_name": scenario['name'],
                "status": result.status if hasattr(result, 'status') else "completed",
                "final_output": result.final_output if hasattr(result, 'final_output') else str(result),
                "elapsed_time": round(elapsed_time, 2),
                "expected_agents": scenario['expected_agents'],
                "success": True
            }
            
            if verbose:
                print("=" * 60)
                print("RESULT")
                print("=" * 60)
                print(f"Status: {scenario_result['status']}")
                print(f"Time: {scenario_result['elapsed_time']}s")
                print()
                print("Response:")
                print("-" * 60)
                print(scenario_result['final_output'])
                print("=" * 60)
            
            self.results.append(scenario_result)
            return scenario_result
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            error_result = {
                "scenario_id": scenario_id,
                "scenario_name": scenario['name'],
                "status": "error",
                "error": str(e),
                "elapsed_time": round(elapsed_time, 2),
                "success": False
            }
            
            if verbose:
                print("=" * 60)
                print("ERROR")
                print("=" * 60)
                print(f"Error: {e}")
                print("=" * 60)
            
            self.results.append(error_result)
            return error_result
    
    async def run_all_scenarios(self, verbose: bool = True) -> List[Dict]:
        """Run all demo scenarios."""
        scenarios = list_scenarios()
        results = []
        
        if verbose:
            print("=" * 60)
            print("RUNNING ALL DEMO SCENARIOS")
            print("=" * 60)
            print(f"Total scenarios: {len(scenarios)}")
            print()
        
        for i, scenario_id in enumerate(scenarios, 1):
            if verbose:
                print(f"\n[{i}/{len(scenarios)}] Running scenario: {scenario_id}")
                print()
            
            result = await self.run_scenario(scenario_id, verbose=verbose)
            results.append(result)
            
            # Small delay between scenarios
            await asyncio.sleep(1)
        
        return results
    
    def print_summary(self):
        """Print summary of all results."""
        print("\n" + "=" * 60)
        print("DEMO SUMMARY")
        print("=" * 60)
        
        total = len(self.results)
        successful = sum(1 for r in self.results if r.get('success', False))
        failed = total - successful
        
        print(f"Total Scenarios: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print()
        
        if self.results:
            avg_time = sum(r.get('elapsed_time', 0) for r in self.results) / total
            print(f"Average Time: {avg_time:.2f}s")
            print()
            
            print("Scenario Results:")
            print("-" * 60)
            for result in self.results:
                status = "✅" if result.get('success') else "❌"
                print(f"{status} {result.get('scenario_name', 'Unknown')}: {result.get('status', 'unknown')} ({result.get('elapsed_time', 0)}s)")
        
        print("=" * 60)


async def main():
    """Main demo runner."""
    # Validate API keys
    print("Validating API keys...")
    api_keys = validate_api_keys()
    for key, valid in api_keys.items():
        status = "✅" if valid else "❌"
        print(f"  {status} {key}")
    
    if not all(api_keys.values()):
        print("\n⚠️  Warning: Some API keys are missing. Some features may not work.")
        print("   Check your .env file.\n")
    
    # Show available scenarios
    print("\n" + get_scenario_summary())
    
    # Create runner
    runner = DemoRunner()
    
    # Run scenarios
    import sys
    if len(sys.argv) > 1:
        # Run specific scenario
        scenario_id = sys.argv[1]
        await runner.run_scenario(scenario_id)
    else:
        # Run all scenarios
        await runner.run_all_scenarios()
    
    # Print summary
    runner.print_summary()


if __name__ == "__main__":
    asyncio.run(main())

