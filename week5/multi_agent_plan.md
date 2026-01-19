Week 5 Multi-Agent Plan

Objective:
- Build a robust Supervisor to coordinate Researcher, Analyst, and Writer agents.
- Provide reliable task delegation, timeouts, retries, and result aggregation.
- Integrate evaluation (ResearchEvaluator) and observability for latency and token usage.

Phases:
1. Design: define agent roles, message schemas, success criteria, and failure modes.
2. Implement supervisor core (registration, dispatch, delegation, gather, concurrency control).
3. Integrate local skill adapters and `reference-repositories/agent_skills/` for pluggable agents.
4. Add evaluation harness (pairwise/aggregate scoring) and CI tests.
5. Run benchmarks, collect metrics, improve retry/backoff and caching strategy.

Supervisor API (current `week5/agent_supervisor.py`):
- `register(name, handler, **metadata)`: register a sync/async handler with optional metadata.
- `unregister(name)`: remove an agent from registry.
- `list_agents() -> List[str]`: list registered agent names.
- `dispatch(to, message, timeout=5.0, retries=1, backoff=0.25) -> TaskResult`: send message with timeout and retry.
- `delegate_first_response(agents, message, timeout=5.0) -> TaskResult`: fan-out and return first successful response.
- `gather_all(agents, message, timeout=5.0) -> List[TaskResult]`: fan-out and return all results.

Design notes & recommendations:
- Use in-memory LRU (already available) for hot-path cache; consider Redis for multi-host deployments.
- Emit structured logs (JSON) for supervisor events: dispatch/start/finish/error, elapsed_ms, agent, task_id.
- Expose metrics: concurrency, queue depth, cache hit-rate, average latency per agent.
- Start with local-test agents (sync/async stubs) and add adapter layer to wrap real ChatAgent instances.

Deliverables:
- `week5/agent_supervisor.py` (enhanced supervisor with demo)
- `week5/scenarios/` (scenario YAML examples) — (skeletons)
- `evaluation/test_supervisor.py` (local test harness)
- Integration guide in `week5/README.md` for running supervisor demos and integrating with `research-assistant`.
