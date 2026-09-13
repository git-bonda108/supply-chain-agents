# Architecture

This document describes the system as it exists in the code. Where a capability is scaffolded but not wired in, that is stated explicitly.

## Component map

| Layer | Files | Responsibility |
|-------|-------|----------------|
| UI | `streamlit_app.py` | 10-section Streamlit app; builds query strings from widget values and runs agents. `streamlit_app_new_sections.py` duplicates three sections and is imported nowhere (dead file). |
| CLI | `main.py`, `run_demo.py`, `demo/demo_runner.py`, `demo/scenarios.py` | Interactive CLI and five scripted scenarios, all routed through the orchestrator. |
| Agents | `supply_chain_agents/orchestrator.py` + six specialist modules | One `Agent` per module, constructed at import time as a module-level singleton. The orchestrator lists the six specialists as `handoffs`. |
| Prompts | `config/agent_configs.py` | Instruction strings for all seven agents. The `TOOL_DESCRIPTIONS` dict at the bottom is unused. |
| Tool wrapper | `utils/tool_helpers.py` | `create_function_tool` reflects a Python function's signature into a JSON schema and wraps it as an Agents SDK `FunctionTool`. |
| Calculators | `tools/calculators/` (risk, forecast, supplier, inventory, logistics) | Deterministic analysis: weighted risk scoring, linear-regression forecasting, supplier scoring/ranking, EOQ-style inventory math, route comparison. |
| Data access | `tools/data_loader.py`, `tools/data_uploader.py`, `tools/mock_data_generator.py` | CSV load with mock-data generation fallback; upload validation/preprocessing; synthetic dataset generation (50 suppliers, 20 products, 365 days of demand). |
| External data | `tools/data_sources/` | Tavily and NewsAPI clients (rate-limited), SQLite TTL cache, and a `DataRefresher` background loop that is defined but never started by any entry point. |
| ML | `ml_models/rl_inventory_optimizer.py` | Simulation environment, tabular Q-learning agent, human-feedback reward shaping, train/act functions. Independent of the LLM agents. |
| Reporting | `tools/report_generator.py` | Aggregation and text-report helpers exposed as tools to the reporting agent. |
| Utilities | `utils/helpers.py`, `utils/error_handling.py` | Logging setup, API-key presence checks; a retry wrapper `safe_agent_run` and `handle_errors` decorator that are defined but not used by the application. |

## Data flow, end to end

A Streamlit interaction (for example, "Assess Risk" on the Risk Assessment page):

1. The page handler formats a natural-language query from widget values (`f"Assess the geopolitical risk for {product} from {country}"`).
2. `run_agent_async` creates a **new event loop** and calls `Runner.run(risk_agent, query, session=None)`.
3. The Agents SDK loop calls the model with the agent's instructions and tool schemas; the model emits tool calls.
4. Tool execution goes through the `on_invoke_tool` wrapper into a calculator, e.g. `assess_geopolitical_risk`, which:
   - checks the SQLite cache (`geopolitical_risk:{country}:{product}` key, 1 h TTL),
   - on miss, issues two Tavily searches (export controls + general risk), scores them, caches the result,
   - on API failure, falls back to the mean `geopolitical_risk` column of the local supplier CSV, and to a fixed `0.5 / MEDIUM / UNKNOWN` result if no suppliers match.
5. Tool results (dicts) return to the model, which composes `final_output`; the handler renders it as markdown.

The orchestrator path ("Comprehensive Analysis", "Demo Scenarios", `main.py`) is identical except step 3 starts at the orchestrator, and the model's first decision is a handoff to one of the six specialists.

The RL sections bypass agents entirely: the UI builds a `product_data` dict from the inventory/demand CSVs and calls `train_rl_model` / `get_optimal_action` directly.

## Orchestration analysis: what is parallel, sequential, async

- **Handoffs are sequential control transfer.** In the Agents SDK, a handoff replaces the running agent; the orchestrator does not fan out to multiple specialists concurrently. The orchestrator prompt speaks of handing off "in sequence or parallel", but the mechanism the code configures (`handoffs=[...]`) executes one agent at a time.
- **No application-level concurrency.** There is no `asyncio.gather`, no task group, and no threaded agent execution anywhere in the app. Each Streamlit button press is one blocking `Runner.run` on a private event loop that is closed afterwards.
- **Tool calls within a turn** are executed by the SDK as the model emits them; this code does not configure or depend on parallel tool execution.
- **Async is scaffolded, not exercised.** `main.py` and the demo runner are `async` because `Runner.run` is a coroutine, but each awaits a single run. `DataRefresher.run_refresh_loop` (hourly Tavily/NewsAPI cache warm-up) is a genuine background async loop, but no entry point calls `get_data_refresher()` or `start()`, so it never runs.
- **Why this shape is reasonable for the code's purpose:** every specialist's tools are fast, deterministic local functions or cached API calls, so the latency budget is dominated by model turns; sequential handoffs keep the trace understandable in a demo setting. The cost is that "Comprehensive Analysis" pays for its breadth serially.

## State and context engineering

- **Conversation memory: none.** Every call site passes `session=None`, so each query is a fresh, single-turn run; nothing an agent learns in one interaction is visible to the next. `aiosqlite`/`sqlalchemy` are in `requirements.txt` for the SDK's session support, but no session store is constructed.
- **UI state:** Streamlit `session_state` keeps `feedback_history`, the `HumanFeedbackReward` instance, and the last RL recommendation — per browser session, lost on reload.
- **API cache:** `data/cache.db` (SQLite) with MD5-hashed keys and a 1-hour default TTL, toggleable via `ENABLE_CACHE`.
- **Data cache:** `DataLoader` keeps an in-instance DataFrame cache, but `get_data_loader()` constructs a new `DataLoader` on every call (the "singleton" comment notwithstanding), so this cache rarely survives beyond one function. The effective caching for the UI is Streamlit's `@st.cache_data` on the three loaders.
- **RL state:** Q-tables pickled per product at `ml_models/rl_models/inventory_{product_id}.pkl`; training resumes from an existing pickle when present.
- **Context assembly:** context given to the model is deliberately narrow — the per-agent instruction block plus a short synthesized query string. Bulk data never enters the prompt; agents reach it through tools that return compact summary dicts (forecast summaries, top-5 result lists, score breakdowns), which bounds context size structurally.

## Design decisions and trade-offs visible in the code

1. **Numbers come from Python, narrative from the model.** All scoring, forecasting, and optimization is deterministic code; the LLM selects tools and writes up results. This avoids hallucinated arithmetic at the cost of rigid formulas (e.g. fixed 0.3/0.3/0.2 risk weights, +0.2 for restricted export status).
2. **Hand-rolled tool schema generation.** `create_function_tool` maps annotations to JSON types by reflection instead of using the SDK's decorator. It handles flat primitives; `list`/`dict` parameters get bare `array`/`object` types without item schemas, and unannotated parameters default to `string`. Simple and uniform, but weaker parameter validation than typed schemas.
3. **Graceful degradation over failure.** Every tool returns an error dict rather than raising; risk assessment falls back from live search to CSV averages to a fixed neutral value. The app stays up when APIs fail, but degraded answers are only distinguishable by a `warning`/`source` field.
4. **Derived, not authoritative, risk signals.** Tavily relevance scores are averaged into a "risk score", and export-control status is inferred by thresholding that score (`RESTRICTED` if > 0.5) — a proxy, not a compliance determination. Logistics routes are hardcoded mock options (two routes with fixed cost/transit figures), noted as such in the code.
5. **Mock-data-first operation.** Missing CSVs are silently regenerated with synthetic data, which makes the demo self-contained but means an empty deployment produces plausible-looking, fabricated dashboards unless real data is uploaded.
6. **RL is decoupled from the agent loop.** The Q-learning optimizer is driven directly by the UI, not exposed as an agent tool; the "InventoryOptimization" agent uses the deterministic optimizer in `tools/calculators/` instead. Human feedback shapes rewards by replaying feedback entries into training episodes.
