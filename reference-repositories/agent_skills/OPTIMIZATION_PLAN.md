# Optimization & Compression Plan for Integrated Agent Skills

## Goal
Reduce lines of code while preserving functionality, improve modularity, and speed up runtime by extracting common utilities and producing compact adapters for integration.

## Steps
1. Inventory duplicate utilities (token counting, embeddings, io, config). Move to `agent_skills/_common/`.
2. Create small adapter modules in main project (`orchestration/`, `evaluation/`, `memory-systems/`) that import from canonical modules.
3. Remove or archive large examples and tests into `examples/` to shrink primary modules.
4. Replace heavyweight dependencies in examples with optional imports and lazy loading.
5. Run static analysis (flake8) and simple refactor: extract repeated code into helper functions.
6. Measure LOC and runtime before/after; aim for 30-50% LOC reduction for non-essential code while keeping core algorithms intact.

## Quick Wins
- Factor out `AgentMessage`, `AgentCommunication`, and serialization into `_common/comm.py`.
- Extract token counting helpers to `_common/tokens.py` and reuse across modules.
- Replace inline CLI examples with small `examples/` scripts and keep core modules focused.
- Use simple code compression: shorter variable names only within local scope, but prefer clarity for public APIs.

## Deliverables
- `agent_skills/_common/` with token, io, and embedding helpers
- Adapter modules in `orchestration/`, `evaluation/`, `memory-systems/`
- `OPTIMIZED/` folder containing compressed versions (annotated) of large modules
- Benchmarks: `evaluation/benchmark_optimization.py`

## Questions for you
- Prioritize readability vs maximum compression? (I recommend readability for core modules.)
- Approve creating `_common/` and moving shared code there?
