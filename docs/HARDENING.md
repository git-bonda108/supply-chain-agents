# Hardening

Current security and operational posture as found in the code, followed by a staged ladder to production readiness. This is a single-tenant analysis demo today; the ladder is ordered accordingly.

## Current posture

**Authentication and access.** None. The Streamlit app binds locally with no login, no roles, and no per-user isolation; anyone who can reach port 8501 can query agents (spending OpenAI/Tavily/NewsAPI quota), upload data, and trigger RL training. The CLI is equivalent.

**Secrets handling.** Keys are read from environment variables via `python-dotenv`; `.env` is gitignored and no `.env` file is committed. `utils/helpers.py` checks key presence at startup. However, real key values had been pasted into two markdown files at HEAD (see the bottom of this document); they are now redacted, but the values remain in git history and must be rotated. Five "optional provider" keys (Anthropic, DeepSeek, Groq, Gemini, Serper) are validated for presence but consumed by no code path — dead configuration surface that invites unnecessary secret sprawl.

**Error handling.** Uniformly fail-soft: tools return error dicts, external clients degrade to fallbacks, the UI renders exceptions as messages. Two consequences worth naming: agent runs are single-attempt (the retry helper in `utils/error_handling.py` is unused), and degraded data is only marked by a `warning`/`source` field that the LLM may or may not surface to the reader.

**Observability.** Python `logging` with a configurable level; no structured logs, no request IDs, no Agents SDK tracing configured, no token/cost accounting, no metrics endpoint. The SQLite cache exposes stats via `get_stats()` but nothing reads them.

**Other exposure worth knowing about.**
- No model is pinned; agents run on the SDK's default model, so behavior can shift with SDK upgrades.
- RL models are `pickle` files loaded from disk; unpickling attacker-supplied files executes arbitrary code. Fine while the directory is app-written only; a hazard the moment model files become uploadable or shared.
- Uploaded CSV/Excel files are parsed by pandas with validation of columns/ranges but no size limits or content-type enforcement beyond the extension.
- Dependencies are floor-pinned (`>=`), so builds are not reproducible.
- Rate limits protect upstream quotas, not the app itself — there is no inbound throttling.
- No LICENSE file: as published, the repository grants no reuse rights.

## Ladder to production

**Stage 1 — identity and keys (do first).**
- Rotate every credential listed at the bottom of this file, then purge history (`git filter-repo`) since redaction at HEAD does not remove the values from earlier commits.
- Add a committed `.env.example` with placeholder values; drop the five unused provider keys from validation or wire them to real code.
- Put authentication in front of Streamlit (reverse proxy with OIDC/basic auth, or Streamlit's own auth options); never expose 8501 directly.
- Pin the model explicitly on each `Agent`, and pin dependency versions (lockfile).
- Add secret scanning (pre-commit + CI) so key material cannot re-enter the tree.

**Stage 2 — monitoring.**
- Enable Agents SDK tracing so every run's handoffs and tool calls are inspectable.
- Structured JSON logs with a request ID per `Runner.run`; log tool errors and fallback activations (the `source: fallback_data` path) as first-class events.
- Track per-run token usage and API spend; alert on anomalies — an unauthenticated or newly authenticated endpoint that spends money per request needs a budget circuit breaker.
- Surface cache hit rates (`CacheManager.get_stats`) and upstream failure rates.

**Stage 3 — deployment.**
- Containerize; run Streamlit behind TLS-terminating reverse proxy; healthcheck endpoint.
- Replace the "generate mock data on missing file" fallback with an explicit demo-mode flag, so production cannot silently fabricate dashboards.
- Enforce upload limits (size, row count, MIME sniffing) before pandas parsing; store uploads outside the app image.
- Use the actually-wired retry path: adopt `safe_agent_run` (or SDK-native retries) for agent calls; start `DataRefresher` deliberately or delete it.
- Swap pickle for a safe serialization of Q-tables (JSON of the table dict) if model files ever cross a trust boundary.
- CI that runs the component and hermetic integration suites (see `docs/EVALUATION.md`) on every push.

**Stage 4 — compliance and data governance.**
- Choose and commit a LICENSE.
- Classify uploaded supply-chain data (supplier names, costs, volumes are commercially sensitive); define retention/deletion for `data/uploads/`, `data/processed/`, and the response cache, which stores third-party API content.
- Document that export-control status emitted by the risk tools is a search-derived heuristic, not legal advice, before any compliance-adjacent use.
- Review upstream terms (OpenAI, Tavily, NewsAPI) for the data being sent — queries embed supplier and product names.

---

## Secrets removed from HEAD — rotate these credentials and purge history

- `VERIFICATION_REPORT.md` — contained a complete Google Gemini API key and a complete Serper API key in plaintext; both values replaced with `<REDACTED-ROTATE-ME>`.
- `README.md` — contained a complete NewsAPI key and identifying prefixes of DeepSeek, Groq, Gemini, and Serper keys in the example configuration; removed in the rewrite.

Rotation of all listed providers (Gemini, Serper, NewsAPI — and, defensively, any key whose prefix appeared: DeepSeek, Groq) is required: the values remain retrievable from git history until it is rewritten (`git filter-repo`) and force-pushed, and any clone made before that retains them regardless.
