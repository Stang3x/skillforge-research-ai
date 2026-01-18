Week 5 — Multi-Agent Phase

Goal: prepare scaffolding and operational guidance for multi-agent orchestration, evaluation, and integration.

Contents:
- `multi_agent_plan.md`: high-level plan, Supervisor API, and design notes
- `tasks.md`: prioritized tasks and milestones
- `agent_supervisor.py`: enhanced supervisor module (timeouts, retries, delegation, concurrency)

Quick start (local demo):
1. From the project root run the supervisor demo directly:

```powershell
python week5/agent_supervisor.py
```

2. Or run via the main research assistant entrypoint:

```powershell
python research-assistant/research_assistant.py --supervisor-test
```

3. Run the local unit test for the supervisor:

```powershell
python evaluation/test_supervisor.py
```

Integration notes:
- The supervisor accepts sync or async handlers and is designed to be wrapped around existing `ChatAgent` instances or simple local stubs for testing.
- For production, attach structured logging and export metrics (Prometheus) for latency, success rate, and cache hit-rate.

Next steps:
- Add scenario YAMLs under `week5/scenarios/` and example adapters for `skill_loader` agents.
- Add CI job to run `evaluation/test_supervisor.py` on PRs.
