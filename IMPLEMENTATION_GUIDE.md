# Technical Implementation Guide
## Supply Chain Multi-Agent System with OpenAI Agents SDK

---

## Table of Contents
1. [Architecture Deep Dive](#architecture-deep-dive)
2. [Agent Implementation Details](#agent-implementation-details)
3. [Multi-Agent Orchestration Patterns](#multi-agent-orchestration-patterns)
4. [Data Pipeline](#data-pipeline)
5. [Tool Development](#tool-development)
6. [Session Management](#session-management)
7. [Testing Strategy](#testing-strategy)

---

## Architecture Deep Dive

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│              (CLI / Streamlit / API)                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Orchestrator Agent                          │
│  - Query Understanding                                   │
│  - Agent Routing                                         │
│  - Workflow Management                                   │
│  - Result Aggregation                                    │
└─────┬───────────┬───────────┬───────────┬───────────────┘
      │           │           │           │
      ▼           ▼           ▼           ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│   Risk   │ │  Demand  │ │ Supplier │ │Inventory │
│Intelligence│ │Forecasting│ │Assessment│ │Optimization│
└────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘
     │           │           │           │
     └───────────┴───────────┴───────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│          Executive Reporting Agent                       │
│  - Insight Aggregation                                  │
│  - Report Generation                                    │
│  - Visualization                                        │
└─────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

1. **User Query** → Orchestrator receives natural language query
2. **Query Analysis** → Orchestrator determines required agents
3. **Parallel/Sequential Execution** → Agents execute tasks
4. **Data Exchange** → Agents share results via session/handoffs
5. **Aggregation** → Executive Reporting Agent consolidates insights
6. **Output** → Formatted report returned to user

---

## Agent Implementation Details

### 1. Orchestrator Agent

**Purpose**: Central coordinator for all agent interactions

**Key Responsibilities**:
- Parse user intent
- Route to appropriate agents
- Manage agent handoffs
- Aggregate results
- Handle errors and retries

**Implementation Pattern**:
```python
from agents import Agent, Runner
from typing import List, Dict

class OrchestratorAgent:
    def __init__(self):
        self.agents = {
            'risk': risk_agent,
            'demand': demand_agent,
            'supplier': supplier_agent,
            'inventory': inventory_agent,
            'logistics': logistics_agent,
            'reporting': reporting_agent
        }
        
    async def process_query(self, query: str, session):
        # Analyze query intent
        intent = await self._analyze_intent(query)
        
        # Determine required agents
        required_agents = self._determine_agents(intent)
        
        # Execute agents (parallel or sequential)
        results = await self._execute_agents(required_agents, query, session)
        
        # Aggregate and return
        return await self._aggregate_results(results)
```

### 2. Risk Intelligence Agent

**Purpose**: Monitor and assess supply chain risks

**Tools Required**:
- `get_geopolitical_events()`: Fetch recent geopolitical events
- `check_export_controls()`: Check export control status
- `calculate_risk_score()`: Calculate risk scores
- `get_market_volatility()`: Fetch market volatility data

**Output Format**:
```json
{
    "risk_score": 0.75,
    "risk_level": "HIGH",
    "factors": [
        {"factor": "Export Controls", "impact": "HIGH", "details": "..."},
        {"factor": "Geopolitical Tension", "impact": "MEDIUM", "details": "..."}
    ],
    "recommendations": ["Monitor closely", "Diversify suppliers"]
}
```

### 3. Demand Forecasting Agent

**Purpose**: Predict demand and identify shortages

**Tools Required**:
- `load_historical_data()`: Load time series data
- `generate_forecast()`: Run forecasting model
- `detect_anomalies()`: Identify unusual patterns
- `calculate_confidence()`: Calculate confidence intervals

**Output Format**:
```json
{
    "forecast": {
        "next_month": 1000,
        "next_quarter": 3200,
        "next_year": 12000
    },
    "confidence_intervals": {
        "next_month": {"lower": 800, "upper": 1200},
        "next_quarter": {"lower": 2500, "upper": 3900}
    },
    "shortage_risk": "MEDIUM",
    "trend": "INCREASING"
}
```

### 4. Supplier Assessment Agent

**Purpose**: Evaluate suppliers and recommend alternatives

**Tools Required**:
- `get_supplier_data()`: Fetch supplier information
- `calculate_reliability_score()`: Score supplier reliability
- `find_alternatives()`: Find alternative suppliers
- `compare_suppliers()`: Compare supplier metrics

**Output Format**:
```json
{
    "current_suppliers": [
        {
            "id": "SUP001",
            "name": "Supplier A",
            "reliability_score": 0.65,
            "risk_level": "MEDIUM",
            "location": "China"
        }
    ],
    "alternatives": [
        {
            "id": "SUP002",
            "name": "Supplier B",
            "reliability_score": 0.85,
            "risk_level": "LOW",
            "location": "Vietnam",
            "match_score": 0.92
        }
    ],
    "recommendations": ["Consider Supplier B as backup"]
}
```

### 5. Inventory Optimization Agent

**Purpose**: Optimize inventory levels

**Tools Required**:
- `get_current_inventory()`: Fetch current stock levels
- `calculate_optimal_levels()`: Run optimization algorithm
- `calculate_costs()`: Calculate inventory costs
- `suggest_reorder_points()`: Suggest reorder points

**Output Format**:
```json
{
    "current_inventory": 5000,
    "optimal_inventory": 7500,
    "recommended_action": "INCREASE",
    "reorder_point": 3000,
    "safety_stock": 2000,
    "cost_analysis": {
        "current_cost": 500000,
        "optimal_cost": 525000,
        "service_level_improvement": 0.15
    }
}
```

### 6. Logistics Optimization Agent

**Purpose**: Optimize transportation and routing

**Tools Required**:
- `get_routes()`: Fetch available routes
- `calculate_costs()`: Calculate transportation costs
- `check_constraints()`: Check geopolitical/logistical constraints
- `suggest_alternatives()`: Suggest alternative routes

**Output Format**:
```json
{
    "current_route": {
        "route_id": "R001",
        "cost": 50000,
        "duration": 15,
        "risk_level": "HIGH"
    },
    "recommended_routes": [
        {
            "route_id": "R002",
            "cost": 55000,
            "duration": 18,
            "risk_level": "LOW",
            "savings_risk": "HIGH"
        }
    ]
}
```

### 7. Executive Reporting Agent

**Purpose**: Generate comprehensive reports

**Tools Required**:
- `aggregate_insights()`: Combine agent outputs
- `generate_summary()`: Create executive summary
- `create_visualizations()`: Generate charts
- `format_report()`: Format final report

**Output Format**:
- Executive Summary (text)
- Key Insights (bullet points)
- Recommendations (actionable items)
- Visualizations (charts/graphs)
- Detailed Analysis (full report)

---

## Multi-Agent Orchestration Patterns

### Pattern 1: Sequential Handoff

**Use Case**: When agents depend on each other's outputs

```python
async def sequential_workflow(query, session):
    # Step 1: Risk Assessment
    risk_result = await Runner.run(
        risk_agent,
        f"Assess risks for: {query}",
        session=session
    )
    
    # Step 2: Demand Forecasting (uses risk context)
    demand_result = await Runner.run(
        demand_agent,
        f"Forecast demand considering: {risk_result.final_output}",
        session=session
    )
    
    # Step 3: Inventory Optimization (uses both)
    inventory_result = await Runner.run(
        inventory_agent,
        f"Optimize inventory with risk: {risk_result.final_output} and demand: {demand_result.final_output}",
        session=session
    )
    
    return inventory_result
```

### Pattern 2: Parallel Execution

**Use Case**: When agents can work independently

```python
import asyncio

async def parallel_workflow(query, session):
    # Execute agents in parallel
    results = await asyncio.gather(
        Runner.run(risk_agent, f"Assess risks: {query}", session=session),
        Runner.run(demand_agent, f"Forecast demand: {query}", session=session),
        Runner.run(supplier_agent, f"Evaluate suppliers: {query}", session=session)
    )
    
    # Aggregate results
    aggregated = await Runner.run(
        reporting_agent,
        f"Create report from: {[r.final_output for r in results]}",
        session=session
    )
    
    return aggregated
```

### Pattern 3: Conditional Routing

**Use Case**: When agent selection depends on query analysis

```python
async def conditional_workflow(query, session):
    # Analyze query to determine required agents
    orchestrator_result = await Runner.run(
        orchestrator_agent,
        f"Analyze this query and determine which agents are needed: {query}",
        session=session
    )
    
    # Parse orchestrator decision
    required_agents = parse_agent_requirements(orchestrator_result)
    
    # Execute required agents
    results = []
    for agent_name in required_agents:
        agent = get_agent(agent_name)
        result = await Runner.run(agent, query, session=session)
        results.append(result)
    
    return results
```

### Pattern 4: Hierarchical Delegation

**Use Case**: Complex workflows with sub-teams

```python
# Master orchestrator delegates to team orchestrators
master_orchestrator = Agent(
    name="MasterOrchestrator",
    instructions="Coordinate supply chain analysis teams",
    handoffs=[risk_team_orchestrator, optimization_team_orchestrator]
)

# Team orchestrators manage their agents
risk_team_orchestrator = Agent(
    name="RiskTeamOrchestrator",
    instructions="Coordinate risk analysis",
    handoffs=[geopolitical_monitor, market_analyzer, export_tracker]
)
```

---

## Data Pipeline

### Data Sources

1. **Kaggle Datasets** (Static/Mock Data)
   - Supply chain operations data
   - Historical demand data
   - Supplier performance data

2. **Simulated Real-Time Data** (Mock APIs)
   - Geopolitical events
   - Market prices
   - Export control status
   - Supplier status

### Data Processing Pipeline

```python
# data_pipeline.py

class DataPipeline:
    def __init__(self):
        self.raw_data_path = "data/raw/"
        self.processed_data_path = "data/processed/"
        
    def load_kaggle_data(self, dataset_name):
        """Load and preprocess Kaggle dataset"""
        df = pd.read_csv(f"{self.raw_data_path}{dataset_name}.csv")
        # Preprocessing steps
        df = self._clean_data(df)
        df = self._enrich_data(df)
        return df
    
    def _clean_data(self, df):
        """Clean data: remove nulls, handle outliers"""
        # Implementation
        return df
    
    def _enrich_data(self, df):
        """Enrich data: add calculated fields"""
        # Implementation
        return df
    
    def get_supplier_data(self, supplier_id):
        """Get supplier data from processed dataset"""
        # Implementation
        pass
    
    def get_demand_history(self, product_id, period):
        """Get historical demand data"""
        # Implementation
        pass
```

### Mock API for Real-Time Data

```python
# tools/mock_apis.py

class MockGeopoliticalAPI:
    def get_recent_events(self, region):
        """Simulate geopolitical events"""
        return {
            "events": [
                {
                    "date": "2025-01-15",
                    "type": "Export Control",
                    "region": region,
                    "impact": "HIGH",
                    "description": "New export restrictions announced"
                }
            ]
        }
    
    def check_export_controls(self, country, product):
        """Simulate export control check"""
        return {
            "status": "RESTRICTED" if country == "China" else "ALLOWED",
            "restrictions": ["License required", "Quantity limits"]
        }
```

---

## Tool Development

### Tool Structure

```python
from agents import Tool

# Example: Risk Calculator Tool
risk_calculator = Tool(
    name="calculate_risk_score",
    description="Calculate supply chain risk score based on multiple factors",
    func=calculate_risk_score_impl
)

def calculate_risk_score_impl(
    geopolitical_risk: float,
    supplier_reliability: float,
    market_volatility: float,
    export_control_status: str
) -> dict:
    """
    Calculate overall risk score
    
    Args:
        geopolitical_risk: Risk score 0-1
        supplier_reliability: Reliability score 0-1
        market_volatility: Volatility score 0-1
        export_control_status: "RESTRICTED" or "ALLOWED"
    
    Returns:
        dict with risk_score and breakdown
    """
    # Weighted calculation
    base_score = (
        geopolitical_risk * 0.3 +
        (1 - supplier_reliability) * 0.3 +
        market_volatility * 0.2
    )
    
    # Adjust for export controls
    if export_control_status == "RESTRICTED":
        base_score += 0.2
    
    risk_score = min(base_score, 1.0)
    
    return {
        "risk_score": risk_score,
        "risk_level": "HIGH" if risk_score > 0.7 else "MEDIUM" if risk_score > 0.4 else "LOW",
        "breakdown": {
            "geopolitical": geopolitical_risk,
            "supplier": 1 - supplier_reliability,
            "market": market_volatility,
            "export_controls": export_control_status
        }
    }
```

### Tool Categories

1. **Data Access Tools**
   - `load_dataset()`
   - `get_supplier_data()`
   - `get_demand_history()`

2. **Analysis Tools**
   - `calculate_risk_score()`
   - `generate_forecast()`
   - `optimize_inventory()`

3. **External API Tools** (Mock)
   - `get_geopolitical_events()`
   - `check_export_controls()`
   - `get_market_data()`

4. **Reporting Tools**
   - `generate_summary()`
   - `create_visualization()`
   - `format_report()`

---

## Session Management

### Session Types

1. **SQLiteSession** (File-based, good for demos)
2. **RedisSession** (Distributed, production-ready)
3. **Custom Session** (For specific requirements)

### Session Usage

```python
from agents.extensions.memory import SQLiteSession

# Create session
session = SQLiteSession("user_123", "conversations.db")

# Use in agent runs
result = await Runner.run(
    agent,
    "Query here",
    session=session
)

# Session maintains context across interactions
result2 = await Runner.run(
    agent,
    "Follow-up question",
    session=session  # Agent remembers previous context
)
```

### Session Data Structure

```python
# Session stores conversation history
session_items = [
    {
        "role": "user",
        "content": "Assess memory chip supply chain risks"
    },
    {
        "role": "assistant",
        "content": "Risk assessment results..."
    },
    {
        "role": "tool",
        "name": "calculate_risk_score",
        "content": {"risk_score": 0.75}
    }
]
```

---

## Testing Strategy

### Unit Tests

Test individual agents in isolation:

```python
# tests/test_risk_agent.py

async def test_risk_agent():
    result = await Runner.run(
        risk_agent,
        "Assess risk for memory chips from China",
        session=None
    )
    assert "risk_score" in result.final_output
    assert result.status == "completed"
```

### Integration Tests

Test agent interactions:

```python
# tests/test_workflow.py

async def test_risk_to_forecast_handoff():
    session = SQLiteSession("test", ":memory:")
    
    # Risk assessment
    risk_result = await Runner.run(
        risk_agent,
        "Assess risks",
        session=session
    )
    
    # Demand forecast (should use risk context)
    forecast_result = await Runner.run(
        demand_agent,
        "Forecast demand",
        session=session
    )
    
    assert forecast_result.final_output is not None
```

### Scenario Tests

Test complete workflows:

```python
# tests/test_scenarios.py

async def test_memory_chip_shortage_scenario():
    query = "We're seeing delays in memory chip deliveries. Assess and recommend."
    
    result = await Runner.run(
        orchestrator,
        query,
        session=SQLiteSession("scenario_test", ":memory:")
    )
    
    # Verify all required agents were invoked
    # Verify recommendations are provided
    assert "recommendation" in result.final_output.lower()
```

---

## Performance Optimization

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_supplier_data_cached(supplier_id):
    """Cached supplier data retrieval"""
    return get_supplier_data(supplier_id)
```

### Parallel Execution

```python
# Use asyncio.gather for parallel agent execution
results = await asyncio.gather(
    agent1_task,
    agent2_task,
    agent3_task
)
```

### Batch Processing

```python
# Process multiple queries in batch
queries = ["query1", "query2", "query3"]
results = await asyncio.gather(*[
    Runner.run(agent, q, session=session) for q in queries
])
```

---

## Error Handling

### Agent-Level Error Handling

```python
try:
    result = await Runner.run(agent, query, session=session)
except Exception as e:
    # Log error
    logger.error(f"Agent error: {e}")
    # Return fallback response
    return {"error": str(e), "fallback": "Please try rephrasing your query"}
```

### Tool-Level Error Handling

```python
def safe_tool_func(*args, **kwargs):
    try:
        return actual_tool_func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Tool error: {e}")
        return {"error": "Tool execution failed", "details": str(e)}
```

---

## Next Steps

1. **Set up project structure** (Week 1)
2. **Implement core agents** (Week 2)
3. **Develop tools** (Week 2-3)
4. **Integrate datasets** (Week 3)
5. **Build orchestration** (Week 3)
6. **Create demo scenarios** (Week 4)
7. **Test and refine** (Week 4)

---

## Resources

- [OpenAI Agents SDK Docs](https://openai.github.io/openai-agents-python/)
- [Multi-Agent Tutorials](https://github.com/ed-donner/agents/tree/main/1_foundations)
- [Kaggle Datasets](https://www.kaggle.com/datasets?search=supply+chain)



