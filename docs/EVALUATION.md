# Evaluation

An honest account of what is tested today, what edge-case handling the code demonstrably contains, and what an evaluation harness for this system should look like. Anything not implemented is labeled **Proposed**.

## What automated tests exist

All test files are runnable scripts with custom pass/fail runners (pytest is in `requirements.txt` and the classes are pytest-compatible, but nothing depends on it).

| File | Run with | What it covers |
|------|----------|----------------|
| `tests/test_components.py` | `python tests/test_components.py` | Unit-level checks of the deterministic calculators: risk score ranges and levels, forecast structure, shortage detection fields, supplier evaluation/alternatives, inventory optimization output, route optimization, report aggregation/generation. Asserts on output shape and value ranges. |
| `tests/test_streamlit.py` | `python tests/test_streamlit.py` | Data loading and integrity (required columns, score ranges), demo-scenario structure, agent imports, and per-agent tool counts. |
| `test_all_integrations.py` | `python test_all_integrations.py` | Eight integration checks: API-key presence, **live** Tavily and NewsAPI calls, data uploader validation/preprocessing, RL environment/agent mechanics, data loader, agent imports, tool functions. Requires real API keys; network-dependent. |
| `test_end_to_end.py` | `python test_end_to_end.py` | Broader end-to-end sweep across data infrastructure, APIs, calculators, and agents. Network-dependent. |
| `test_agents.py` | `python test_agents.py` | Imports and runs individual agents with sample queries (spends OpenAI tokens). |
| `test_orchestration.py` | `python test_orchestration.py` | One live orchestrator run on a multi-agent query; prints the final output and step count. Verifies the handoff pipeline executes, not the answer quality. |

Recorded results: `VERIFICATION_REPORT.md` (in-repo, from the original development pass) records the integration suite at 8/8 passing on the author's machine. No CI runs these tests; there are no coverage measurements. The response-time and throughput figures quoted in earlier revisions of the README had no measurement source in the repository and are not reproduced here.

## Edge cases the code visibly handles

Enumerated from the code, not aspiration:

- **External API failure:** every Tavily/NewsAPI call is wrapped in try/except and returns an error dict with empty results instead of raising (`tools/data_sources/tavily_client.py`, `news_api_client.py`).
- **Layered fallback for risk assessment:** live search → mean of the supplier CSV's `geopolitical_risk` for that country (tagged `source: fallback_data` with a warning) → fixed `0.5 / MEDIUM / UNKNOWN` result (`tools/calculators/risk_calculator.py`).
- **Rate limiting:** `@limits(calls=100, period=60)` with `@sleep_and_retry` on all Tavily/NewsAPI methods — callers block rather than exceed the quota.
- **Caching with TTL and failure tolerance:** SQLite cache errors are logged and treated as cache misses; expired entries are filtered at read time (`tools/data_sources/cache_manager.py`).
- **Insufficient data:** forecasting returns an explicit error when fewer than 30 days of history exist; shortage detection propagates it. Missing product inventory yields an error dict; missing stock during shortage detection defaults to 0.
- **Missing data files:** loaders regenerate mock CSVs when `data/processed/*.csv` is absent rather than crashing.
- **Input validation on uploads:** per-data-type required-column checks, value-range checks (e.g. scores in 0–1, non-negative stock), typed error lists surfaced in the UI; preprocessing fills missing values with medians/defaults (`tools/data_uploader.py`).
- **Forecast sanity:** predictions clamped to non-negative; trend classified only from endpoint comparison.
- **Missing RL model:** loading a nonexistent Q-table logs a warning and starts from an empty table; the UI distinguishes trained vs. untrained products.
- **UI resilience:** every Streamlit section wraps data loading and agent calls in try/except and renders the error instead of crashing the app.

Also present but **unused**: `utils/error_handling.py` contains a `safe_agent_run` retry wrapper (3 attempts, output validation) and a `handle_errors` decorator that no call site imports. Agent runs in the app are single-attempt.

## What is not evaluated

- No assertions on LLM output quality, correctness, or format — live-agent tests check only that a run completes.
- No test of handoff routing (does the orchestrator pick the right specialist for a query?).
- No golden datasets, no regression baseline, no CI gate, no cost/latency tracking.
- Forecast accuracy is never measured against held-out history.

## Proposed evaluation harness

None of the following exists; this is the design the system should grow into.

1. **Golden query set.** 30–50 queries spanning the six specialists and multi-agent scenarios, each with: expected routed agent(s), expected tool calls (names + key arguments), and a rubric for the final answer. Store as JSON next to `demo/scenarios.py`, which already defines `expected_agents` per scenario and is the natural seed.
2. **Trajectory assertions.** Run each golden query through `Runner.run` against a pinned model and assert on the result's step/tool-call sequence: correct handoff target, required tools invoked, no error dicts silently narrated as facts (check for `source: fallback_data` leakage).
3. **Deterministic-layer gates.** Freeze a fixture dataset (a committed copy of the mock CSVs) so calculator outputs are exact-match testable; add forecast backtesting (train on days 1–300, score MAPE on days 301–365) with a regression threshold rather than an absolute target.
4. **LLM-judged answer quality.** For the narrative layer, an LLM judge scoring groundedness (claims traceable to tool outputs), completeness against the rubric, and format compliance with each agent's "Always provide" prompt contract; gate on score deltas versus the previous baseline.
5. **Operational metrics.** Record tokens, latency, and tool-call counts per golden run; alert on drift. Mock Tavily/NewsAPI in CI (recorded responses) so the suite is hermetic; run the live integration checks on a schedule instead.
6. **Gates.** CI order: unit (components) → hermetic integration → trajectory suite → judged quality. Merges blocked on the first three; quality regressions >5% flagged for human review.
