# Documentation Index

This directory contains comprehensive documentation for learning and working with agentic workflows in this workspace.

## Quick Start

1. **Beginner programmer?** Start with [BEGINNER_HANDS_ON_PATH.md](./BEGINNER_HANDS_ON_PATH.md) - Learn by building!
2. **New to this workspace?** Read [../CLAUDE.md](../CLAUDE.md)
3. **Want to learn from reference repos?** Follow [LEARNING_WORKFLOW.md](./LEARNING_WORKFLOW.md)
4. **Ready to install skills?** Use [SKILLS_INSTALLATION_GUIDE.md](./SKILLS_INSTALLATION_GUIDE.md)
5. **Exploring Claude Code tools?** Browse [CLAUDE_CODE_RESOURCES.md](./CLAUDE_CODE_RESOURCES.md)

## Documentation Files

### [BEGINNER_HANDS_ON_PATH.md](./BEGINNER_HANDS_ON_PATH.md)

**Purpose**: Hands-on learning path for beginner programmers (< 1 year experience)

**Contents**:

- **Level 1**: The simplest possible agent (30 minutes) - Single interaction → conversation loop
- **Level 2**: Adding tools (1 hour) - Calculator tool → file reading → multi-tool systems
- **Level 3**: Agent memory (1 hour) - File-based memory → semantic memory with fact extraction
- **Level 4**: Complete system (2 hours) - Research assistant combining memory + tools + purpose
- **Level 5**: Understanding reference repos - Guided path through nanocode → SimpleMem → agent-browser → autocoder
- All examples are runnable Python scripts in `experiments/` directory
- Progressive complexity: 20 lines → 250 lines
- Focuses on understanding concepts through building

**Use When**: You're a beginner wanting to understand agentic workflows through hands-on experimentation rather than reading theory

**Prerequisites**: Python 3.x installed, Anthropic API key

---

### [LEARNING_WORKFLOW.md](./LEARNING_WORKFLOW.md)
**Purpose**: Guide for extracting patterns from reference repositories

**Contents**:
- How to study AutoGPT, LangGraph, CrewAI, and n8n-nodes-starter
- Pattern extraction methodology
- Documentation templates
- Working with Claude Code to analyze repositories

**Use When**: You want to learn from the reference repositories in `references/`

---

### [CLAUDE_CODE_RESOURCES.md](./CLAUDE_CODE_RESOURCES.md)
**Purpose**: Comprehensive catalog of Claude Code extensions and tools

**Contents**:
- Skills & Agents (Superpowers, Context Engineering Kit, etc.)
- Tooling & Utilities (recall, ccflare, claudekit)
- Hooks & Integration (cchooks, TDD Guard)
- IDE Integrations (Neovim, VSCode, Emacs)
- Workflows & Frameworks (RIPER, AB Method, Claude CodePro)
- Orchestration Systems (Claude Squad, TSK, Ralph)
- Example CLAUDE.md files from production projects
- Getting started guide with phased approach

**Use When**: You want to extend Claude Code's capabilities or explore available tools

---

### [SKILLS_INSTALLATION_GUIDE.md](./SKILLS_INSTALLATION_GUIDE.md)
**Purpose**: Step-by-step guide for installing and configuring skills

**Contents**:
- Installation methods (Git clone, symlink, custom)
- Recommended skills for agentic workflows
- Verification and troubleshooting
- Creating custom skills
- Supporting tools installation
- Best practices and skill combinations

**Use When**: You're ready to install Claude Code skills and extensions

---

### [REPOS_INDEX_SUMMARY.md](./REPOS_INDEX_SUMMARY.md)
**Purpose**: Comprehensive summary of 100+ Claude Code repositories organized by category

**Contents**:
- 9 major categories (Systems Admin, Multi-Agent, Context Engineering, Workflows, etc.)
- Key patterns (Claude Space Pattern, Multi-Agent Orchestration)
- Notable repositories with descriptions
- Learning path for different use cases
- Integration examples and best practices

**Use When**: Researching how others build agentic systems, looking for specific implementation examples

---

### [N8N_SKILLS_GUIDE.md](./N8N_SKILLS_GUIDE.md)
**Purpose**: Complete guide to the 7 n8n-skills for building n8n workflows with Claude Code

**Contents**:
- n8n Expression Syntax patterns and gotchas
- n8n MCP Tools Expert guidance
- 5 proven workflow patterns (Webhook, HTTP API, Database, AI, Scheduled)
- Validation workflows and error interpretation
- Node configuration with property dependencies
- JavaScript and Python code patterns for Code nodes
- Top 5 error patterns covering 62%+ of failures
- Installation and integration instructions

**Use When**: Building n8n workflows programmatically, troubleshooting n8n issues, creating AI agent workflows

---

### [OBSIDIAN_SKILLS_SUMMARY.md](./OBSIDIAN_SKILLS_SUMMARY.md)
**Purpose**: Knowledge management with Obsidian skills for agentic research

**Contents**:
- 3 complementary skills (Obsidian Markdown, Bases, JSON Canvas)
- Wikilinks, embeds, callouts, and properties
- Recommended vault structure for agentic research
- Pattern documentation templates with frontmatter
- Daily research log templates
- MOCs (Maps of Content) for organizing concepts
- Integration with Claude Code for note creation

**Use When**: Setting up knowledge management system, documenting patterns with networked thinking, creating visual architecture diagrams

---

### [MCP_LAUNCHPAD_SUMMARY.md](./MCP_LAUNCHPAD_SUMMARY.md)
**Purpose**: Comprehensive catalog of 200+ MCP servers for agent tool integration

**Contents**:
- 25+ categories: Browser Automation, Cloud Platforms, Code Execution, Databases, Search, Communication, Developer Tools, etc.
- Docker-first deployment patterns
- Memory Storage MCP (100% complete) for persistent agent state
- A2A (Agent-to-Agent) compatibility standard
- Security considerations for tool access
- MCP server development templates and checklists
- Priority implementation plan
- Integration examples with agentic workflows

**Use When**: Adding tool capabilities to agents, deploying MCP servers, building agents with persistent memory, creating custom MCP servers

---

### [ANTHROPIC_SKILLS_GUIDE.md](./ANTHROPIC_SKILLS_GUIDE.md)
**Purpose**: Official Anthropic skills including production document skills and development guides

**Contents**:
- 4 production document skills (DOCX, PDF, PPTX, XLSX) - source-available
- Development skills: mcp-builder (MCP server creation), webapp-testing (Playwright)
- Meta skill: skill-creator (complete skill development methodology)
- Progressive disclosure: 3-level loading system for context efficiency
- Bundled resources pattern: scripts/, references/, assets/
- 6-step skill creation process
- Evaluation-driven development with 10-question methodology
- Best practices from production skills

**Use When**: Creating custom skills, building MCP servers, learning official Anthropic patterns, understanding production skill architecture, testing web applications

---

### [AWESOME_CLAUDE_SKILLS_CATALOG.md](./AWESOME_CLAUDE_SKILLS_CATALOG.md)
**Purpose**: Community-curated catalog of 50+ Claude Code skills across 11 categories

**Contents**:
- 11 categories: Document, Development, Data & Analysis, Scientific, Writing, Learning, Media, Health, Collaboration, Security, Utility
- 125+ scientific skills (bioinformatics, cheminformatics, clinical research, ML)
- Multi-model integration patterns (Claude + Gemini)
- TOON format innovation (30-60% token savings with Zig encoder)
- CLI tool wrapper skills
- Security-first patterns (varlock, postgres read-only)
- Notable contributors: @obra (Superpowers), @K-Dense-AI (scientific), @ComposioHQ (productivity)

**Use When**: Finding domain-specific skills, learning community patterns, discovering novel approaches, exploring multi-model orchestration, understanding specialized workflows

---

### [CLAUDE_TASK_SYSTEM_GUIDE.md](./CLAUDE_TASK_SYSTEM_GUIDE.md)
**Purpose**: Complete development lifecycle plugin with structured workflows and autonomous task execution

**Contents**:
- Three-phase development lifecycle (Define → Plan → Execute)
- 12 skills + 3 specialized agents (Orchestrator, Worker, Builder)
- Phase gates with human approval at each boundary
- Enforced test-driven development (locked tests)
- Continuous journaling of decisions and progress
- Git worktree parallelism for multiple simultaneous tasks
- Dynamic state derivation from filesystem/git
- Blocker resolution protocol for agent uncertainty
- Architecture Decision Records (ADRs) integration

**Use When**: Building structured agent workflows, enforcing TDD discipline, implementing phase gates, managing parallel tasks, handling distributed collaboration, documenting agent decisions automatically

---

### [BASIC_MEMORY_GUIDE.md](./BASIC_MEMORY_GUIDE.md)
**Purpose**: Local-first knowledge graph for persistent LLM memory through Markdown files

**Contents**:
- Bi-directional knowledge: Both humans and LLMs read and write same Markdown files
- Three core primitives: Entity (nodes), Observation (facts), Relation (links)
- Semantic Markdown format: `[category] content #tags (context)` + `relation_type [[WikiLink]]`
- SQLite knowledge graph with full-text search and fuzzy WikiLink resolution
- MCP server with 15+ tools: create_entities, read_entity, search_entities, traverse_relations, find_path
- Real-time bidirectional sync: File changes ↔ database synchronization
- Multi-LLM support: Works with Claude, ChatGPT, Gemini, Claude Code, Codex
- Project isolation: Multiple separate knowledge graphs per MCP server
- Cloud sync: Cross-device and multi-platform support with Basic Memory Cloud
- Importers: ChatGPT, Claude Conversations, Claude Projects

**Use When**: Building persistent agent memory systems, enabling cross-conversation context, implementing knowledge graphs with Markdown, creating local-first agent architectures, supporting multi-LLM workflows, designing traversable semantic networks

---

### [SUBAGENTS_CATALOG.md](./SUBAGENTS_CATALOG.md)
**Purpose**: Comprehensive catalog of 140+ specialized Claude Code subagents from VoltAgent

**Contents**:
- 10 categories: Core Development (11), Language Specialists (25), Infrastructure (14), Quality & Security (14), Data & AI (12), Developer Experience (13), Specialized Domains (12), Business & Product (10), Meta & Orchestration (10), Research & Analysis (6)
- Subagent architecture: Independent context windows, tool permissions, domain specialization
- Meta-agents for orchestration: multi-agent-coordinator, workflow-orchestrator, context-manager, error-coordinator
- Tool permission patterns: Read-only, Research, Code Writer, Documentation
- Installation methods: Claude Code plugin, manual, interactive installer, standalone installer, agent installer
- Usage patterns: Automatic invocation, manual invocation, multi-agent coordination workflows
- Integration with claude-task-system, GET SHIT DONE, MCP servers

**Use When**: Implementing multi-agent systems, delegating tasks to specialized agents, building orchestration layers, optimizing context usage, creating domain-specific agent teams

---

### [WSHOBSON_AGENTS_GUIDE.md](./WSHOBSON_AGENTS_GUIDE.md)
**Purpose**: Production-ready plugin system with 68 plugins, 100 agents, 110 skills, 15 orchestrators, 76 tools

**Contents**:
- Granular plugin architecture: 68 focused single-purpose plugins (average 3.4 components each)
- 100 specialized agents across 23 categories with strategic model assignment (Opus/Sonnet/Haiku)
- 110 agent skills with progressive disclosure (3-tier loading: metadata → instructions → resources)
- 15 multi-agent workflow orchestrators: full-stack, security hardening, ML pipeline, incident response
- Three-tier model strategy: Opus (42 agents) for critical work, Inherit (42) for flexibility, Sonnet (51) for support, Haiku (18) for fast ops
- Token efficiency: 99.45% reduction with progressive disclosure vs monolithic
- Cost optimization: Strategic model assignment saves 60-70% vs all-Opus
- Plugin composition: Mix and match for custom workflows
- Agent skills by domain: Python (5), JS/TS (4), K8s (4), Cloud (4), CI/CD (4), Backend (3), LLM (4), Blockchain (4)

**Use When**: Building production agentic systems with token efficiency, implementing progressive disclosure at scale, optimizing model costs, coordinating multiple agents with pre-built orchestrators, composing granular plugins

---

### [CLAUDE_FLOW_GUIDE.md](./CLAUDE_FLOW_GUIDE.md)
**Purpose**: Enterprise AI orchestration platform with self-learning neural capabilities and 54+ specialized agents

**Contents**:
- Self-learning architecture: SONA (<0.05ms adaptation, 89% accuracy), EWC++ (95%+ knowledge preservation), MoE (8 experts), ReasoningBank
- Coordinated agent swarms: 4 topologies (hierarchical, mesh, ring, star), 5 consensus algorithms (Raft, Byzantine, Gossip, CRDT, Quorum)
- Hive mind coordination: 3 queen types (Strategic, Tactical, Adaptive), 8 worker types, collective memory, Byzantine fault tolerance
- 54+ specialized agents: Core (5), Consensus (7), Hive Mind (5), Swarm Coordinators (4), GitHub Integration (13), Optimization (5), Domain Specialists (15+)
- RuVector intelligence layer: HNSW (150x-12,500x faster search), Flash Attention (2.49x-7.47x speedup), Hyperbolic embeddings, LoRA (128x compression), Int8 quantization (3.92x savings)
- 175+ MCP tools: Native Claude Code integration with swarm_init, agent_spawn, memory_search, consensus_vote, queen_coordinate
- 3-tier cost optimization: Free (WASM) → Cheap (Haiku) → Premium (Opus), 250% usage extension, 75% API cost savings
- Enterprise security: CVE-hardened, AIDefence (<10ms threat detection), input validation, sandbox execution
- 42+ skills system, 27 hooks with 4-step learning pipeline (RETRIEVE→JUDGE→DISTILL→CONSOLIDATE), 12 background workers
- Production memory: SQLite + AgentDB, 8 memory types, cross-session persistence

**Use When**: Building self-learning agent systems, coordinating large-scale agent swarms (10+ agents), implementing fault-tolerant consensus, optimizing API costs with intelligent routing, creating GitHub-centric workflows, deploying production agentic systems with enterprise security, requiring cross-session memory persistence

---

### [TRENDING_REPOS_GUIDE.md](./TRENDING_REPOS_GUIDE.md)
**Purpose**: Comprehensive guide to 7 production-ready repositories from GitHub Trending that extend agentic workflow capabilities

**Contents**:
- **SimpleMem**: Efficient lifelong memory through semantic lossless compression (43.24% F1, 30× fewer tokens, 12.5× faster)
- **agent-browser**: Headless browser automation CLI designed for AI agents (ref-based interaction, snapshot → @e1/@e2)
- **autocoder**: Long-running autonomous coding agent with multi-session persistence (SQLite features, React UI)
- **nanocode**: Minimal agent implementation in ~250 lines (educational reference, zero dependencies)
- **mcp-cli**: Lightweight CLI for on-demand MCP access (lazy connections, worker pool, token-efficient)
- **CodexMonitor**: Native macOS orchestration UI (multi-workspace, git worktrees, JSON-RPC streaming)
- **tuicr**: Terminal code review for AI changes (GitHub-style diff viewer, typed comments, batch feedback)
- Integration patterns combining all 7 repositories
- Comparison matrices: memory, tools, multi-agent, human-in-the-loop, learning curve
- Complete installation instructions and use cases

**Use When**: Exploring production patterns for memory management, browser automation, multi-session agents, MCP tooling, orchestration UIs, human-in-the-loop review; understanding minimal agent architecture; building token-efficient workflows

---

## Pattern Documentation

### [patterns/](./patterns/)
Contains documented patterns extracted from reference repositories:

- **[README.md](./patterns/README.md)** - Pattern documentation template and guide
- **[agent-loop-patterns.md](./patterns/agent-loop-patterns.md)** - Agent execution cycle patterns
- **[state-management-patterns.md](./patterns/state-management-patterns.md)** - State and memory management
- **[n8n-custom-node-patterns.md](./patterns/n8n-custom-node-patterns.md)** - n8n node development patterns
- **[gsd-workflow-patterns.md](./patterns/gsd-workflow-patterns.md)** - GET SHIT DONE workflow and context engineering
- **[structured-lifecycle-pattern.md](./patterns/structured-lifecycle-pattern.md)** - Three-phase development lifecycle with TDD enforcement
- **[mcp-server-integration.md](./patterns/mcp-server-integration.md)** - MCP server development and integration patterns
- **[progressive-disclosure-pattern.md](./patterns/progressive-disclosure-pattern.md)** - Context-efficient skill design with three-level loading

**Use When**: Documenting or referencing design patterns found in reference repositories

---

## Recommended Learning Path

### Phase 1: Foundation (Week 1)
1. Read [../CLAUDE.md](../CLAUDE.md) to understand the workspace
2. Browse reference repositories structure
3. Skim [LEARNING_WORKFLOW.md](./LEARNING_WORKFLOW.md)

### Phase 2: Skills Setup (Week 2)
1. Read [SKILLS_INSTALLATION_GUIDE.md](./SKILLS_INSTALLATION_GUIDE.md)
2. Install 2-3 recommended skills
3. Test skills with simple tasks

### Phase 3: Deep Learning (Week 3-4)
1. Follow [LEARNING_WORKFLOW.md](./LEARNING_WORKFLOW.md) systematically
2. Extract first pattern from AutoGPT or LangGraph
3. Document in `patterns/` directory

### Phase 4: Extension & Customization (Week 5-6)
1. Explore [CLAUDE_CODE_RESOURCES.md](./CLAUDE_CODE_RESOURCES.md)
2. Try advanced tools (orchestration, hooks, frameworks)
3. Create custom skill for your workflow

### Phase 5: Mastery (Ongoing)
1. Build agentic workflows using learned patterns
2. Contribute new patterns to documentation
3. Share learnings and improvements

## Quick Reference Commands

### Searching This Documentation
```bash
# Find specific topics
grep -r "agent loop" docs/

# Search pattern files
grep -r "LangGraph" docs/patterns/

# Find all examples
find docs/ -name "*.md" -exec grep -l "example" {} \;
```

### Working with Reference Repos
```bash
# List all reference repositories
ls -la references/

# Search for specific patterns in AutoGPT
grep -r "class.*Agent" references/AutoGPT/

# Find n8n node examples
find references/n8n-nodes-starter/ -name "*.ts"
```

### Managing Skills
```bash
# List installed skills
ls -la ~/.claude/skills/

# Update all skills
for skill in ~/.claude/skills/*/; do cd "$skill" && git pull; done

# Check skill documentation
cat ~/.claude/skills/superpowers/README.md
```

## Getting Help

### Ask Claude Code
- "Explain the agent loop pattern from AutoGPT"
- "Help me extract the state management pattern from LangGraph"
- "Create a custom n8n node based on n8n-nodes-starter examples"
- "What skills should I install for agentic workflow development?"

### External Resources
- **Awesome Claude Code**: https://github.com/hesreallyhim/awesome-claude-code
- **Claude Docs**: https://docs.claude.com/en/home
- **Reference Repos**: See `references/` directory

## Contributing to This Documentation

When you discover useful patterns or workflows:

1. **Document in appropriate pattern file** under `patterns/`
2. **Follow the template** in `patterns/README.md`
3. **Include source references** with file paths and line numbers
4. **Test before documenting** - verify patterns work
5. **Update this README** if adding new documentation files

## File Organization

```
docs/
├── README.md                          # This file
├── LEARNING_WORKFLOW.md               # How to learn from references
├── CLAUDE_CODE_RESOURCES.md           # Tools and extensions catalog
├── SKILLS_INSTALLATION_GUIDE.md       # Skills setup guide
├── REPOS_INDEX_SUMMARY.md             # 100+ Claude Code repositories index
├── N8N_SKILLS_GUIDE.md                # n8n skills for workflow building
├── OBSIDIAN_SKILLS_SUMMARY.md         # Obsidian knowledge management
├── MCP_LAUNCHPAD_SUMMARY.md           # 200+ MCP servers catalog
├── ANTHROPIC_SKILLS_GUIDE.md          # Official Anthropic skills & patterns
├── AWESOME_CLAUDE_SKILLS_CATALOG.md   # 50+ community skills catalog
├── CLAUDE_TASK_SYSTEM_GUIDE.md        # Structured development lifecycle plugin
└── patterns/
    ├── README.md                         # Pattern documentation guide
    ├── agent-loop-patterns.md            # Agent execution patterns
    ├── state-management-patterns.md      # State/memory patterns
    ├── n8n-custom-node-patterns.md       # n8n development patterns
    ├── gsd-workflow-patterns.md          # GET SHIT DONE workflow patterns
    ├── structured-lifecycle-pattern.md   # Three-phase development lifecycle
    ├── mcp-server-integration.md         # MCP server development patterns
    └── progressive-disclosure-pattern.md # Context-efficient skill design
```

---

**Start your journey**: Read [LEARNING_WORKFLOW.md](./LEARNING_WORKFLOW.md) to begin extracting patterns from reference repositories!
