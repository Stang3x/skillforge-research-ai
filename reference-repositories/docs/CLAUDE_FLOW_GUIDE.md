# Claude-Flow v3: Enterprise AI Orchestration Platform

**Reference**: `references/claude-flow/`
**Source**: https://github.com/ruvnet/claude-flow
**Maintainer**: ruvnet
**Version**: v3.0.0-alpha

## Overview

Claude-Flow v3 is a production-ready **enterprise AI orchestration platform** that transforms Claude Code into a powerful multi-agent development system. It enables deployment, coordination, and optimization of 54+ specialized AI agents working together on complex software engineering tasks with **self-learning neural capabilities** that no other agent framework offers.

## Why Claude-Flow for Agentic Workflows?

Claude-Flow represents the **most advanced agent orchestration system** in the ecosystem, combining:

1. **Self-Learning Neural Architecture (SONA)** - Learns optimal routing from task outcomes (<0.05ms adaptation)
2. **Zero Forgetting (EWC++)** - Preserves successful patterns while learning new ones
3. **Coordinated Agent Swarms** - 4 topologies, 5 consensus algorithms, unlimited concurrent agents
4. **Production-Grade Memory** - HNSW vector search (150x-12,500x faster), SQLite persistence
5. **Intelligent Cost Optimization** - 3-tier routing extends Claude Max usage by 250%, saves 75% on API costs
6. **Enterprise Security** - CVE-hardened, AIDefence threat detection, input validation

## Architecture

### System Flow

```
User → Claude-Flow (CLI/MCP) → Router → Swarm → Agents → Memory → LLM Providers
                       ↑                          ↓
                       └──── Learning Loop ←──────┘
```

### Key Layers

| Layer | Components | What It Does |
|-------|------------|--------------|
| **User** | Claude Code, CLI | Interface to control and run commands |
| **Orchestration** | MCP Server, Router, Hooks | Routes requests to the right agents |
| **Agents** | 54+ specialized types | Domain experts (coder, tester, reviewer, architect, security, etc.) |
| **Swarm** | Queen, Consensus, Topology | Coordinates teams with fault-tolerant voting |
| **Intelligence** | SONA, MoE, ReasoningBank | Self-learning routing and pattern storage |
| **Memory** | HNSW, AgentDB, Cache | 150x faster vector search with persistence |
| **Providers** | Anthropic, OpenAI, Google, Ollama | 6 LLM providers with automatic failover |

## Core Capabilities

### 1. Self-Learning Neural Capabilities (Unique to Claude-Flow)

**SONA (Self-Optimizing Neural Architecture)**
- Learns which agents perform best for each task type
- Routes work to specialized experts automatically
- <0.05ms adaptation time
- 89% routing accuracy

**EWC++ (Elastic Weight Consolidation)**
- Prevents catastrophic forgetting of successful patterns
- Preserves 95%+ knowledge when learning new patterns
- Consolidates learnings across sessions

**MoE (Mixture of 8 Experts)**
- Routes tasks through 8 specialized expert networks
- Dynamic gating based on task characteristics
- Automatic expert selection

**ReasoningBank**
- Stores successful patterns with trajectory learning
- 5-phase learning loop: RETRIEVE → JUDGE → DISTILL → CONSOLIDATE → ROUTE
- Pattern reuse across sessions

### 2. Coordinated Agent Swarms

**Hive Mind Architecture**
- 🐝 **3 Queen Types**: Strategic (planning), Tactical (execution), Adaptive (optimization)
- 👷 **8 Worker Types**: Researcher, Coder, Analyst, Tester, Architect, Reviewer, Optimizer, Documenter
- 🗳️ **5 Consensus Algorithms**: Majority, Weighted (Queen 3x), Byzantine (f < n/3), Raft, Gossip
- 🧠 **Collective Memory**: Shared knowledge base with LRU cache, SQLite persistence

**4 Swarm Topologies**
1. **Hierarchical** - Queen-led with worker delegation
2. **Mesh** - Peer-to-peer collaboration
3. **Ring** - Circular task passing
4. **Star** - Central coordinator with spoke workers

**Performance**
- 10-20x faster batch spawning
- 84.8% SWE-Bench solve rate
- Fault-tolerant: Handles up to 1/3 failing agents (Byzantine)

### 3. Production-Grade Memory System

**HNSW (Hierarchical Navigable Small World)**
- 150x-12,500x faster vector search
- Local ONNX runtime (no API calls needed)
- 75x faster than API-based embeddings

**AgentDB**
- SQLite with WAL mode for concurrent access
- Cross-session persistence
- 8 memory types: Task, Pattern, Success, Failure, Context, Relationship, Performance, Knowledge

**Hyperbolic Embeddings**
- Poincaré ball model for hierarchical code relationships
- Better representation of nested structures
- Compact vector space

### 4. Intelligent Cost Optimization

**3-Tier Model Routing**

| Complexity | Handler | Speed | Cost |
|------------|---------|-------|------|
| **Simple** | Agent Booster (WASM) | <1ms | Free (352x speedup) |
| **Medium** | Haiku/Sonnet | ~500ms | Low |
| **Complex** | Opus + Swarm | 2-5s | Premium |

**Savings**
- Extends Claude Max usage by 250%
- 75% reduction in API costs
- 85% cost savings with multi-provider routing
- 30-50% token reduction via compression and caching

**Agent Booster**
- WASM-based code transforms for simple edits
- Skips LLM entirely for AST-based changes
- <1ms execution time
- Free operations

### 5. Enterprise Security (AIDefence)

**Threat Detection**
- <10ms analysis time
- Prompt injection prevention
- Input validation with Zod
- Path traversal blocking
- Command injection detection

**Security Practices**
- bcrypt for credential hashing
- Safe credential handling
- CVE-hardened dependencies
- Sandbox execution for code transforms

### 6. Native Claude Code Integration (MCP)

**175+ MCP Tools** available directly in Claude Code:
- `swarm_init` - Initialize agent swarms
- `agent_spawn` - Spawn specialized agents
- `memory_search` - Search patterns with HNSW
- `hooks_route` - Intelligent task routing
- `consensus_vote` - Byzantine fault-tolerant decisions
- `queen_coordinate` - Hive mind orchestration
- And 169+ more tools...

**Installation**:
```bash
claude mcp add claude-flow -- npx -y claude-flow@v3alpha
claude mcp list  # Verify installation
```

## 54+ Specialized Agents

### Core Agents (5)
- **coder** - Code implementation specialist
- **planner** - Task decomposition and planning
- **researcher** - Information gathering and analysis
- **reviewer** - Code review and quality assurance
- **tester** - Test automation and validation

### Consensus Agents (7)
- **byzantine-coordinator** - Byzantine fault tolerance (f < n/3)
- **raft-manager** - Raft consensus protocol
- **gossip-coordinator** - Epidemic-style coordination
- **crdt-synchronizer** - Conflict-free replicated data types
- **quorum-manager** - Quorum-based decisions
- **performance-benchmarker** - Consensus performance analysis
- **security-manager** - Secure consensus protocols

### Hive Mind Agents (5)
- **queen-coordinator** - Strategic/Tactical/Adaptive queen types
- **worker-specialist** - 8 specialized worker types
- **scout-explorer** - Task exploration and discovery
- **swarm-memory-manager** - Collective memory management
- **collective-intelligence-coordinator** - Swarm intelligence orchestration

### Swarm Coordinators (4)
- **hierarchical-coordinator** - Queen-led hierarchy
- **mesh-coordinator** - Peer-to-peer mesh
- **adaptive-coordinator** - Self-organizing swarms
- **ring-coordinator** - Circular topology (planned)

### GitHub Integration Agents (13)
- **pr-manager** - Pull request automation
- **issue-tracker** - Issue management
- **release-manager** - Release coordination
- **code-review-swarm** - Multi-agent code review
- **repo-architect** - Repository structure design
- **workflow-automation** - GitHub Actions automation
- **sync-coordinator** - Cross-repo synchronization
- **project-board-sync** - Project board management
- **swarm-pr** - PR swarm coordination
- **swarm-issue** - Issue swarm coordination
- **release-swarm** - Release swarm coordination
- **multi-repo-swarm** - Multi-repository coordination
- **github-modes** - GitHub workflow modes

### Optimization Agents (5)
- **performance-monitor** - Performance tracking
- **load-balancer** - Load distribution
- **resource-allocator** - Resource optimization
- **topology-optimizer** - Swarm topology optimization
- **benchmark-suite** - Performance benchmarking

### Specialized Domain Agents (15+)
- **dev-backend-api** - Backend API development
- **spec-mobile-react-native** - React Native mobile development
- **data-ml-model** - Machine learning model development
- **ops-cicd-github** - CI/CD pipeline automation
- **docs-api-openapi** - OpenAPI documentation generation
- **arch-system-design** - System architecture design
- **code-analyzer** - Code quality analysis
- **analyze-code-quality** - Quality metrics analysis
- **sona-learning-optimizer** - SONA optimization
- **safla-neural** - Neural network optimization
- And more...

### SPARC Agents (4)
Framework for structured development:
- **specification** - Requirements specification
- **pseudocode** - Algorithm design
- **architecture** - System architecture
- **refinement** - Iterative refinement

### Template Agents (9)
Pre-configured workflows:
- **coordinator-swarm-init** - Swarm initialization
- **orchestrator-task** - Task orchestration
- **implementer-sparc-coder** - SPARC implementation
- **github-pr-manager** - GitHub PR management
- **memory-coordinator** - Memory management
- **performance-analyzer** - Performance analysis
- **automation-smart-agent** - Smart automation
- **sparc-coordinator** - SPARC coordination
- **migration-plan** - Migration planning

## RuVector Intelligence Layer

Standalone intelligence system (`npx ruvector`) integrated into Claude-Flow:

| Component | Purpose | Performance |
|-----------|---------|-------------|
| **SONA** | Self-Optimizing Neural Architecture | <0.05ms adaptation |
| **EWC++** | Elastic Weight Consolidation | 95%+ knowledge preservation |
| **Flash Attention** | Optimized attention computation | 2.49x-7.47x speedup |
| **HNSW** | Hierarchical vector search | 150x-12,500x faster |
| **ReasoningBank** | Pattern storage with trajectory learning | RETRIEVE→JUDGE→DISTILL |
| **Hyperbolic** | Poincaré ball embeddings | Better code relationships |
| **LoRA/MicroLoRA** | Low-Rank Adaptation | 128x compression, <5MB |
| **Int8 Quantization** | Memory-efficient weights | 3.92x memory reduction |
| **9 RL Algorithms** | Q-Learning, SARSA, PPO, DQN, etc. | Task-specific learning |

## 42+ Skills System

Pre-built skill modules for specialized tasks:
- Development & Code Quality (coder, reviewer, analyzer)
- Security & Compliance (security audits, vulnerability scanning)
- Multi-Agent Swarms (coordination, consensus, hive mind)
- Performance & Optimization (benchmarking, profiling)
- GitHub & DevOps (PR management, CI/CD)
- Spec-Driven Development (SPARC framework)
- Learning & Intelligence (SONA, ReasoningBank)

## 27 Hooks System

### 4-Step Learning Pipeline
1. **RETRIEVE** - Fetch relevant patterns from memory
2. **JUDGE** - Evaluate pattern quality and applicability
3. **DISTILL** - Extract key learnings
4. **CONSOLIDATE** - Update memory with new patterns

### Hook Categories

**Tool Lifecycle Hooks (6)**
- `before_tool_call` - Pre-execution validation
- `after_tool_call` - Post-execution learning
- `tool_error` - Error handling
- `tool_validation` - Input validation
- `tool_retry` - Automatic retry logic
- `tool_cache` - Result caching

**Intelligence & Routing Hooks (8)**
- `route_task` - Intelligent agent selection
- `learn_from_result` - Pattern extraction
- `update_expertise` - Agent capability tracking
- `context_analysis` - Context understanding
- `provider_select` - LLM provider routing
- `cost_optimize` - Cost-based routing
- `quality_check` - Output quality validation
- `pattern_match` - Pattern recognition

**Session Management Hooks (4)**
- `session_start` - Session initialization
- `session_end` - Session cleanup
- `session_restore` - Context restoration
- `session_export` - Session export

**Intelligence System Hooks (9)**
- `sona_adapt` - SONA adaptation
- `ewc_consolidate` - EWC pattern consolidation
- `moe_route` - MoE expert routing
- `reasoning_bank_store` - Pattern storage
- `flash_attention_optimize` - Attention optimization
- `hnsw_search` - Vector search
- `lora_fine_tune` - LoRA fine-tuning
- `quantize_weights` - Int8 quantization
- `hyperbolic_embed` - Hyperbolic embeddings

### 12 Background Workers (Auto-Triggered)

Context-aware workers that auto-dispatch on events:
- **ultralearn** - Continuous learning from all tasks
- **audit** - Security and quality audits
- **optimize** - Performance optimization
- **cleanup** - Cache and resource cleanup
- **sync** - Cross-session synchronization
- **backup** - Automatic backups
- **monitor** - Performance monitoring
- **validate** - Continuous validation
- **index** - Code indexing
- **analyze** - Static analysis
- **benchmark** - Performance benchmarking
- **update** - Dependency updates

## Key Learnings for Agentic Workflows

### 1. Self-Learning is the Differentiator
- Claude-Flow is the **only** framework with SONA + EWC++ self-learning
- Competitors (CrewAI, LangGraph, AutoGen, Manus) require manual routing
- System improves autonomously over time

### 2. Swarm Coordination Enables Scale
- Hierarchical topology: Queen delegates to workers
- Byzantine consensus: Fault-tolerant decisions (f < n/3)
- Claims system: Manages human-agent task ownership
- Collective memory: Shared knowledge across all agents

### 3. Memory Architecture is Critical
- HNSW vector search: 150x-12,500x faster than traditional approaches
- Hyperbolic embeddings: Better for hierarchical code relationships
- Cross-session persistence: Context survives restarts
- 8 memory types: Comprehensive pattern storage

### 4. Cost Optimization is Achievable
- 3-tier routing: Free (WASM) → Cheap (Haiku) → Premium (Opus)
- 250% extension of Claude Max usage
- 75% API cost reduction
- 30-50% token reduction via compression

### 5. MCP Integration is Native
- 175+ tools available directly in Claude Code
- Seamless swarm spawning from Claude Code sessions
- No context switching between tools
- Full access to intelligence layer

### 6. Enterprise Security is Built-In
- AIDefence threat detection (<10ms)
- CVE-hardened dependencies
- Input validation and sanitization
- Sandbox execution for code transforms

### 7. GitHub Integration is First-Class
- 13 specialized GitHub agents
- PR/Issue swarm coordination
- Multi-repo management
- Workflow automation

### 8. Consensus Algorithms Enable Reliability
- **Raft**: Leader-based consensus with log replication
- **Byzantine**: Fault-tolerant voting (f < n/3 failures)
- **Gossip**: Epidemic-style coordination
- **CRDT**: Conflict-free replicated data types
- **Quorum**: Majority-based decisions

## Installation & Quick Start

### Prerequisites
- Node.js 18+ or Bun 1.0+
- Claude Code installed globally
- npm/pnpm/bun package manager

### Installation

```bash
# Install Claude Code first
npm install -g @anthropic-ai/claude-code

# Install Claude-Flow
npm install claude-flow@v3alpha
npx claude-flow@v3alpha init

# Add MCP server to Claude Code
claude mcp add claude-flow -- npx -y claude-flow@v3alpha

# Verify installation
claude mcp list
```

### Quick Start Commands

```bash
# Initialize configuration
npx claude-flow@v3alpha init

# Start MCP server
npx claude-flow@v3alpha mcp start

# Run task with specific agent
npx claude-flow@v3alpha --agent coder --task "Implement user authentication"

# List available agents
npx claude-flow@v3alpha --list

# Initialize swarm
npx claude-flow@v3alpha swarm init --topology hierarchical

# Check intelligence layer status
npx claude-flow@v3alpha hooks intelligence --status

# Standalone RuVector (intelligence layer)
npx ruvector
```

### MCP Integration Usage

Once added as MCP server, use these tools directly in Claude Code:

```
# Initialize a coding swarm
> Use swarm_init to create a hierarchical swarm for building authentication

# Spawn specialized agents
> Use agent_spawn to create a security-auditor and a coder agent

# Search memory for patterns
> Use memory_search to find authentication patterns we've used before

# Route tasks intelligently
> Use hooks_route to determine which agent should handle OAuth implementation

# Coordinate with queens
> Use queen_coordinate with strategic queen for high-level planning
```

## Comparison to Other Frameworks

### vs. CrewAI
- **Self-Learning**: Claude-Flow has SONA + EWC++, CrewAI requires manual routing
- **Swarm Topologies**: Claude-Flow has 4 types, CrewAI has 1
- **Consensus**: Claude-Flow has 5 algorithms (Raft, Byzantine, etc.), CrewAI has none
- **Memory**: Claude-Flow has HNSW (150x faster), CrewAI has none
- **Background Workers**: Claude-Flow has 12 auto-triggered, CrewAI has none

### vs. LangGraph
- **Learning**: Claude-Flow learns from results, LangGraph is static
- **Vector Memory**: Claude-Flow has HNSW built-in, LangGraph requires plugins
- **MCP Integration**: Claude-Flow has 175+ tools, LangGraph has none
- **Consensus**: Claude-Flow has 5 algorithms, LangGraph has none
- **Skills System**: Claude-Flow has 42+ pre-built, LangGraph requires custom code

### vs. AutoGen
- **Swarm Coordination**: Claude-Flow has queen-led hierarchy, AutoGen has basic groups
- **Memory Persistence**: Claude-Flow has SQLite + HNSW, AutoGen session-only
- **Consensus**: Claude-Flow has 5 protocols, AutoGen has none
- **Cost Optimization**: Claude-Flow has 3-tier routing, AutoGen single provider
- **Security**: Claude-Flow has AIDefence, AutoGen has standard protections

### vs. Manus
- **Self-Learning**: Claude-Flow has SONA (<0.05ms), Manus is static
- **Swarm Topologies**: Claude-Flow has 4 types, Manus has 1
- **LLM Providers**: Claude-Flow has 6 with failover, Manus has 1
- **Background Workers**: Claude-Flow has 12 auto-triggered, Manus has none
- **MCP Integration**: Claude-Flow has 175+ tools, Manus has none

## When to Use Claude-Flow

**Use Claude-Flow when you need**:
1. **Self-learning orchestration** - System improves autonomously from results
2. **Large-scale agent coordination** - 10+ agents working together with consensus
3. **Production-grade reliability** - Byzantine fault tolerance, automatic failover
4. **Cost optimization** - 3-tier routing saves 75% on API costs
5. **Enterprise security** - CVE-hardened with AIDefence threat detection
6. **Cross-session memory** - Persistent patterns and learnings
7. **GitHub-centric workflows** - 13 specialized GitHub agents
8. **Multi-provider flexibility** - 6 LLM providers with intelligent routing

**Don't use Claude-Flow when**:
- Single agent is sufficient
- No need for coordination/consensus
- Lightweight scripting tasks
- Budget constraints (requires compute for WASM, vector search)

## Integration with Other Agentic Patterns

### With claude-task-system
- Use Claude-Flow swarms for Task Execution phase
- Queen-led hierarchy for Feature Definition
- Byzantine consensus for phase gate approvals
- Background workers for continuous testing

### With GET SHIT DONE
- Fresh subagent contexts via Claude-Flow agents
- Swarm coordination for parallel atomic tasks
- Memory persistence across GSD sessions
- Background workers for quality enforcement

### With wshobson/agents
- Combine Claude-Flow orchestration with wshobson skills
- Progressive disclosure skills load on-demand
- Claude-Flow agents + wshobson specialized skills
- Three-tier model routing for cost efficiency

### With VoltAgent Subagents
- Claude-Flow meta-orchestration layer
- VoltAgent domain specialists as workers
- Shared HNSW memory system
- Tool permission integration

## Advanced Patterns

### Pattern 1: Hierarchical Swarm for Full-Stack Development

```
Strategic Queen (Opus) → Task decomposition
├── Tactical Queen (Sonnet) → Backend implementation
│   ├── Worker: coder (backend-api)
│   ├── Worker: tester (API tests)
│   └── Worker: reviewer (code quality)
└── Tactical Queen (Sonnet) → Frontend implementation
    ├── Worker: coder (UI components)
    ├── Worker: tester (E2E tests)
    └── Worker: reviewer (accessibility)
```

### Pattern 2: Byzantine Consensus for Critical Decisions

```
Task: Approve production deployment
├── Agent 1: security-auditor → APPROVE
├── Agent 2: performance-monitor → APPROVE
├── Agent 3: code-reviewer → REJECT (performance concern)
├── Agent 4: tester → APPROVE
└── Agent 5: architect → APPROVE

Byzantine Consensus: 4/5 approve (80% > 66% threshold)
Decision: APPROVE with performance monitoring
```

### Pattern 3: SONA Learning Loop

```
1. RETRIEVE: Find similar authentication tasks in memory
2. JUDGE: Evaluate which patterns worked (95% success rate for OAuth)
3. DISTILL: Extract key learnings (token refresh critical)
4. CONSOLIDATE: Update memory with new OAuth 2.0 pattern
5. ROUTE: Assign to security-auditor + coder agents

Result: 89% routing accuracy, <0.05ms adaptation
```

### Pattern 4: 3-Tier Cost Optimization

```
Task: "Add logout button to header"

Analysis:
├── Complexity: Simple (UI change only)
├── Handler: Agent Booster (WASM)
├── Cost: Free
└── Time: <1ms

Task: "Implement OAuth 2.0 flow"

Analysis:
├── Complexity: Complex (security, tokens, refresh)
├── Handler: Opus + Swarm (security-auditor + coder)
├── Cost: Premium
└── Time: 2-5s

Savings: 250% usage extension, 75% cost reduction
```

## Resources & Documentation

**Repository**:
- Main README: `references/claude-flow/README.md` (comprehensive, 2500+ lines)
- Plugin Documentation: `references/claude-flow/.claude-plugin/docs/`
- Agent Definitions: `references/claude-flow/.claude/agents/`

**Organized Agent Collections**:
- Core: `references/claude-flow/.claude/agents/core/`
- Consensus: `references/claude-flow/.claude/agents/consensus/`
- Hive Mind: `references/claude-flow/.claude/agents/hive-mind/`
- Swarm: `references/claude-flow/.claude/agents/swarm/`
- GitHub: `references/claude-flow/.claude/agents/github/`
- Optimization: `references/claude-flow/.claude/agents/optimization/`
- SPARC: `references/claude-flow/.claude/agents/sparc/`
- Templates: `references/claude-flow/.claude/agents/templates/`

**Key Documentation Files**:
- Installation: `references/claude-flow/.claude-plugin/docs/INSTALLATION.md`
- Quickstart: `references/claude-flow/.claude-plugin/docs/QUICKSTART.md`
- Plugin Summary: `references/claude-flow/.claude-plugin/docs/PLUGIN_SUMMARY.md`
- Structure: `references/claude-flow/.claude-plugin/docs/STRUCTURE.md`

## Related Patterns

- [[agent-loop-patterns]] - SONA learning loop architecture
- [[state-management-patterns]] - AgentDB and collective memory
- [[swarm-coordination-patterns]] - Hierarchical and mesh topologies (to be created)
- [[consensus-algorithms-patterns]] - Byzantine, Raft, Gossip implementations (to be created)
- [[mcp-server-integration]] - Claude-Flow as MCP server

## Key Takeaways

1. **Only framework with self-learning** - SONA + EWC++ enable autonomous improvement
2. **Production-grade swarm coordination** - 4 topologies, 5 consensus algorithms
3. **150x-12,500x faster memory** - HNSW vector search with hyperbolic embeddings
4. **250% usage extension** - 3-tier routing saves 75% API costs
5. **175+ MCP tools** - Native Claude Code integration
6. **54+ specialized agents** - Domain experts for every task type
7. **Enterprise security** - CVE-hardened with AIDefence (<10ms threat detection)
8. **Cross-session persistence** - SQLite + AgentDB with 8 memory types
9. **Background intelligence** - 12 workers + 27 hooks for continuous optimization
10. **GitHub-first** - 13 specialized agents for GitHub workflows

Claude-Flow v3 represents the **cutting edge of agent orchestration**, combining neural self-learning, fault-tolerant coordination, and production-grade infrastructure into a unified platform that learns and improves autonomously.
