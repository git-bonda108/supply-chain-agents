#!/usr/bin/env python3
"""
Quick Demo Runner
Run: python run_demo.py [scenario_id]
"""

import asyncio
import sys
from demo.demo_runner import DemoRunner

async def main():
    """Run demo."""
    runner = DemoRunner()
    
    if len(sys.argv) > 1:
        scenario_id = sys.argv[1]
        await runner.run_scenario(scenario_id)
    else:
        print("Usage: python run_demo.py [scenario_id]")
        print("\nAvailable scenarios:")
        from demo.scenarios import list_scenarios
        for scenario_id in list_scenarios():
            print(f"  - {scenario_id}")

if __name__ == "__main__":
    asyncio.run(main())



