# Week 5 Milestone Checklist (Jan 27 - Feb 2)

This file captures the short milestone checklist for Week 5 and owners.

Milestone: Multi-agent orchestration and memory systems

- [ ] Multi-agent orchestration: finalize `orchestration/orchestrator.py` integration and smoke tests. **Owner:** Dev
- [ ] Memory: prototype `memory/knowledge-graph.py` and documentation. **Owner:** Dev
- [ ] Production OTLP config: template env examples + secrets guidance (`METRICS_OTLP_URL`, headers). **Owner:** Ops
- [ ] Exemplars verification: run CI with `METRICS_COLLECTOR_URL` and validate `harness-collector-log` artifact. **Owner:** Dev/Infra
- [ ] TokenTracker budgets: add per-tool budgets and alert rules; dashboard. **Owner:** Ops/Dev
- [ ] Cache scale tests: run `tools/cache_benchmark.py` and publish report. **Owner:** Perf

Acceptance criteria:

- Orchestrator completes at least one end-to-end scenario within target latency.
- Knowledge graph prototype can store/retrieve N entities with acceptable latency.
- CI produces an exemplar verification artifact or documented mitigation.

Notes:

- Use `tools/exemplar_harness.py` for local verification and CI testbed when `METRICS_COLLECTOR_URL` is not available.
- CI workflow: `.github/workflows/exemplar-harness.yml` will start the local testbed and upload logs.
