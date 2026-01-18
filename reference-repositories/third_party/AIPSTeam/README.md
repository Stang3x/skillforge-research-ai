# voytas75/AIPSTeam — AI PowerShell Team (RAG)

Summary (expert):
- Purpose: A PowerShell-based AI "team" implementation that simulates multiple specialist agents (Requirements Analyst, Architect, Dev, QA, Doc) and uses Retrieval-Augmented Generation (RAG) via web search providers and multiple LLM backends (Azure OpenAI, Ollama, LM Studio).
- Why it matters: This repo is directly agentic — it implements an agent-team orchestration pattern, state management, streaming outputs, and integration with external LLMs and search providers. It's a practical PowerShell example of multi-agent workflows and RAG.

Relevance to our project:
- High. The repo contains concrete patterns for agent roles, sequential workflows, logging, feedback loops, and RAG configuration that map well to the multi-agent orchestration and evaluation work planned for Week 5.

Recommended integration steps:
1. Inventory key artifacts: `AIPSTeam.ps1`, `docs/`, and `README.md`.
2. Extract orchestration patterns: review `ProjectTeam` class and sequence processing logic; capture prompts and role definitions into `reference-repositories/agent_patterns/` as examples.
3. Create a short migration guide in `reference-repositories/third_party/AIPSTeam/MIGRATE.md` describing how to port ideas into Python (agents, RAG connectors, streaming) and how to wire Telemetry (`TokenTracker` / exemplars).
4. Add a runnable demo recipe: a minimal translation (pseudo-code) showing how an agent in `research-assistant` could emulate one of the PowerShell specialists (e.g., Documentation Specialist) using our `TokenTracker` and `SearchResultCache`.

Notes / caveats:
- The repo is PowerShell-centric and depends on PSAOAI and PSScriptAnalyzer; porting to Python requires adapter work and mapping of PowerShell modules to Python equivalents.
- Useful for prompt engineering patterns, role decomposition, and RAG data-source fallback logic.

Local path: reference-repositories/third_party/AIPSTeam
