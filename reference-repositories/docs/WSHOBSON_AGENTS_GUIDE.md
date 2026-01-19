# wshobson/agents - Production Plugin System

**Reference**: `references/agents/`
**Source**: https://github.com/wshobson/agents
**Maintainer**: wshobson

## Overview

A comprehensive **production-ready plugin system** combining:
- **68 focused plugins** - Granular, single-purpose plugins optimized for minimal token usage
- **100 specialized agents** - Domain experts across all development disciplines
- **110 agent skills** - Modular knowledge packages with progressive disclosure
- **15 workflow orchestrators** - Multi-agent coordination for complex operations
- **76 development tools** - Utilities for scaffolding, security, testing, and infrastructure

**Key Innovation**: Granular plugin architecture where each plugin is completely isolated with average 3.4 components (agents + commands + skills), following Anthropic's 2-8 component pattern for optimal token efficiency.

## Why wshobson/agents for Agentic Workflows?

This system demonstrates advanced patterns for:
1. **Granular plugin architecture** - Single-purpose plugins with minimal token overhead
2. **Progressive disclosure at scale** - 110 skills with 3-tier loading (metadata → instructions → resources)
3. **Three-tier model strategy** - Strategic Opus/Sonnet/Haiku assignment for cost optimization
4. **Multi-agent orchestration** - 15 pre-built workflow coordinators
5. **Production-ready patterns** - Real-world implementation with comprehensive tooling
6. **Token efficiency** - Average 3.4 components per plugin vs monolithic designs

## Core Architecture

### Plugin Philosophy

**Granular Design Principles**:
- **Single responsibility** - Each plugin does one thing well
- **Minimal token usage** - Only load what you need
- **Composable** - Mix and match for complex workflows
- **Clear boundaries** - Focused purpose per plugin
- **100% coverage** - All 100 agents accessible across plugins

**Example**:
```bash
# Installing python-development loads:
# - 3 Python agents (python-pro, django-pro, fastapi-pro)
# - 1 scaffolding tool
# - 5 specialized skills (~300 tokens total)
# NOT the entire marketplace
```

### Three-Tier Model Strategy

Strategic model assignment for optimal performance and cost:

| Tier | Model | Count | Use Case | Cost |
|------|-------|-------|----------|------|
| **Tier 1** | Opus 4.5 | 42 agents | Critical architecture, security, ALL code review, production coding | $5/$25 per M tokens |
| **Tier 2** | Inherit | 42 agents | Complex tasks - user chooses model via `--model` flag | Varies |
| **Tier 3** | Sonnet 4.5 | 51 agents | Support with intelligence (docs, testing, debugging) | $3/$15 per M tokens |
| **Tier 4** | Haiku 4.5 | 18 agents | Fast operational tasks (SEO, deployment, simple docs) | $1/$5 per M tokens |

**Why Opus 4.5 for Tier 1?**
- 80.9% on SWE-bench (industry-leading)
- 65% fewer tokens for complex tasks
- Best for architecture decisions and security audits
- Token reduction often offsets higher rate

**Tier 2 Flexibility (`inherit`)**:
```bash
# Control model per session
claude --model opus    # Use Opus for AI/ML work
claude --model sonnet  # Use Sonnet for cost control
claude --model haiku   # Fast prototyping
```

**Orchestration Pattern**:
```
Opus (architecture) → Sonnet (development) → Haiku (deployment)
```

### Progressive Disclosure (Skills)

**Three-tier loading architecture**:

1. **Metadata** (Always loaded, ~50 tokens):
   ```yaml
   ---
   name: async-python-patterns
   description: AsyncIO, async/await, concurrency patterns for Python
   ---
   ```

2. **Instructions** (Loaded when activated, ~500 tokens):
   ```markdown
   # AsyncIO Patterns

   ## Core Patterns
   - Event loop management
   - Async context managers
   - Concurrent execution
   ```

3. **Resources** (Loaded on demand, unlimited):
   ```
   skills/async-python-patterns/
   ├── examples/
   ├── templates/
   └── references/
   ```

**Token Savings Example**:
- Without progressive disclosure: 10,000 tokens loaded always
- With progressive disclosure: 50 tokens always + 500 when activated + resources on-demand
- **99.5% reduction** in idle token usage

## 23 Plugin Categories (68 Total Plugins)

### 1. Development (4 plugins)
- **debugging-tools** - Advanced debugging, root-cause analysis
- **backend-development** - API design, backend architecture (3 skills)
- **frontend-development** - UI/UX, frontend frameworks
- **multi-platform-development** - Cross-platform mobile/desktop

### 2. Documentation (3 plugins)
- **code-documentation** - Inline docs, docstrings, comments
- **api-documentation** - OpenAPI, API specs, endpoint docs
- **architecture-documentation** - C4 diagrams, architecture docs

### 3. Workflows (4 plugins)
- **git-workflows** - Branching strategies, git operations
- **full-stack-orchestration** - Multi-agent full-stack development (15 workflow orchestrators)
- **tdd-workflows** - Test-driven development patterns
- **conductor** - Context-driven development with track management (3 skills)

### 4. Testing (2 plugins)
- **test-generation** - Unit test automation
- **tdd-practice** - TDD methodology and workflows

### 5. Quality (3 plugins)
- **code-review-ai** - AI-powered code review
- **comprehensive-review** - Multi-agent review (architect + code + security)
- **performance-analysis** - Performance profiling and optimization

### 6. AI & ML (4 plugins)
- **llm-applications** - LangChain, RAG, prompt engineering (4 skills)
- **agent-orchestration** - Multi-agent coordination
- **context-engineering** - Context optimization for LLMs
- **mlops** - ML pipeline deployment

### 7. Data (2 plugins)
- **data-engineering** - ETL, data pipelines
- **data-validation** - Data quality, validation rules

### 8. Database (2 plugins)
- **database-design** - Schema design, normalization
- **database-migrations** - Migration management

### 9. Operations (4 plugins)
- **incident-response** - On-call, incident management
- **system-diagnostics** - Debugging, troubleshooting
- **distributed-debugging** - Multi-service debugging
- **observability** - Monitoring, logging, tracing

### 10. Performance (2 plugins)
- **application-performance** - App-level optimization
- **infrastructure-performance** - Database, cloud optimization

### 11. Infrastructure (5 plugins)
- **deployment-automation** - Deployment scripts, automation
- **infrastructure-validation** - IaC validation
- **kubernetes-operations** - K8s deployments, Helm (4 skills)
- **cloud-infrastructure** - AWS/Azure/GCP multi-cloud (4 skills)
- **ci-cd-pipelines** - Pipeline design, GitHub Actions, GitLab CI (4 skills)

### 12. Security (4 plugins)
- **security-scanning** - SAST, dependency scanning (1 skill)
- **compliance-automation** - Regulatory compliance
- **backend-api-security** - API security, authentication
- **frontend-mobile-security** - Client-side security

### 13. Languages (7 plugins)
- **python-development** - Python, Django, FastAPI (5 skills)
- **javascript-typescript** - JS/TS development (4 skills)
- **systems-programming** - Rust, C/C++, Go
- **jvm-languages** - Java, Kotlin, Scala
- **scripting-languages** - Bash, PowerShell, Ruby
- **functional-programming** - Haskell, Elixir, Clojure
- **embedded-languages** - C, assembly, embedded systems

### 14. Blockchain (1 plugin)
- **blockchain-web3** - Smart contracts, DeFi, NFTs (4 skills)

### 15. Finance (1 plugin)
- **quantitative-trading** - Trading algorithms, risk management

### 16. Payments (1 plugin)
- **payment-processing** - Stripe, PayPal, billing integration

### 17. Gaming (1 plugin)
- **game-development** - Unity, game engines, Minecraft plugins

### 18. Marketing (4 plugins)
- **seo-content** - SEO writing, content optimization
- **technical-seo** - Technical SEO audits
- **seo-analysis** - Analytics, reporting
- **content-marketing** - Content strategy, campaigns

### 19. Business (3 plugins)
- **business-analytics** - BI, metrics, dashboards
- **hr-legal** - HR processes, legal compliance
- **customer-sales** - CRM, sales processes

### 20-23. Specialized Domains
Additional plugins for mobile, IoT, migration, and more.

[→ Complete plugin catalog](../references/agents/docs/plugins.md)

## 110 Agent Skills

Modular knowledge packages following Anthropic's progressive disclosure architecture.

### Language Development Skills

**Python Development** (5 skills):
- `async-python-patterns` - AsyncIO and concurrency
- `python-testing-patterns` - pytest and fixtures
- `python-packaging` - setuptools, Poetry, distribution
- `python-performance` - Profiling, optimization
- `uv-package-manager` - Fast dependency management

**JavaScript/TypeScript** (4 skills):
- `advanced-typescript` - Advanced type patterns
- `nodejs-patterns` - Node.js best practices
- `javascript-testing` - Jest, Vitest, testing patterns
- `modern-javascript` - ES6+, async/await, modules

### Infrastructure Skills

**Kubernetes** (4 skills):
- `k8s-manifests` - Deployment, Service, ConfigMap patterns
- `helm-charts` - Chart development, templating
- `k8s-gitops` - ArgoCD, Flux workflows
- `k8s-security` - Network policies, RBAC, secrets

**Cloud Infrastructure** (4 skills):
- `terraform-patterns` - IaC best practices
- `multi-cloud-architecture` - AWS/Azure/GCP patterns
- `cloud-networking` - VPC, hybrid networking
- `cost-optimization` - Resource optimization strategies

**CI/CD** (4 skills):
- `pipeline-design` - CI/CD architecture
- `github-actions` - Workflow patterns
- `gitlab-ci` - Pipeline configuration
- `secrets-management` - Vault, sealed secrets

### Backend & Architecture Skills

**Backend Development** (3 skills):
- `api-design-patterns` - REST, GraphQL, gRPC
- `backend-architecture` - Microservices, event-driven
- `distributed-systems` - CAP theorem, consensus

**LLM Applications** (4 skills):
- `langchain-development` - LangChain patterns
- `prompt-engineering` - Prompt design, optimization
- `rag-systems` - Retrieval-augmented generation
- `llm-evaluation` - Benchmarking, testing

### Specialized Skills

**Blockchain** (4 skills):
- `defi-protocols` - DeFi patterns, liquidity
- `nft-standards` - ERC-721, ERC-1155
- `solidity-security` - Smart contract security
- `web3-testing` - Hardhat, Foundry testing

**Conductor** (3 skills):
- `context-driven-development` - Context management patterns
- `track-management` - Workflow tracking
- `conductor-patterns` - Orchestration patterns

**And more**: Framework migration, observability, payment processing, ML operations, security scanning

[→ Complete skills documentation](../references/agents/docs/agent-skills.md)

## Installation

### Step 1: Add Marketplace
```bash
/plugin marketplace add wshobson/agents
```
This makes all 68 plugins available but **does not load any agents** into context.

### Step 2: Install Plugins
```bash
# Essential development
/plugin install python-development@claude-code-workflows
/plugin install javascript-typescript@claude-code-workflows
/plugin install backend-development@claude-code-workflows

# Infrastructure
/plugin install kubernetes-operations@claude-code-workflows
/plugin install cloud-infrastructure@claude-code-workflows

# Security & quality
/plugin install security-scanning@claude-code-workflows
/plugin install code-review-ai@claude-code-workflows

# Full-stack orchestration
/plugin install full-stack-orchestration@claude-code-workflows
```

Each installed plugin loads **only its specific agents, commands, and skills**.

### Common Errors

**"Plugin not found"**:
- Use plugin names, not agent names
- Add `@claude-code-workflows` suffix

**Plugins not loading**:
```bash
# Clear cache and reinstall
rm -rf ~/.claude/plugins/cache/claude-code-workflows
rm ~/.claude/plugins/installed_plugins.json
```

## Usage Patterns

### Pattern 1: Full-Stack Feature Development
```bash
/full-stack-orchestration:full-stack-feature "user authentication with OAuth2"
```

**Orchestration Flow**:
1. **backend-architect** (Opus) - API design
2. **database-architect** (Opus) - Schema design
3. **frontend-developer** (Inherit) - UI implementation
4. **test-automator** (Sonnet) - Test suite
5. **security-auditor** (Opus) - Security review
6. **deployment-engineer** (Haiku) - Deployment
7. **observability-engineer** (Sonnet) - Monitoring setup

**Model Cost Optimization**: Critical decisions (Opus) → Development (Inherit) → Deployment (Haiku)

### Pattern 2: Security Hardening
```bash
/security-scanning:security-hardening --level comprehensive
```

**Multi-agent coordination**:
- **security-scanner** agent activates `security-scanning` skill
- Runs SAST, dependency scanning
- **security-auditor** (Opus) performs code review
- **compliance-auditor** checks regulatory requirements

### Pattern 3: Python Development with Skills
```bash
/python-development:python-scaffold fastapi-microservice
```

**Skills activated automatically**:
- `async-python-patterns` - AsyncIO patterns
- `python-testing-patterns` - pytest fixtures
- `uv-package-manager` - Fast dependency management
- `python-packaging` - Project structure

**Progressive disclosure in action**:
1. Metadata loaded: 50 tokens (always)
2. Instructions loaded when scaffolding: 2,000 tokens
3. Resources loaded on-demand: Example FastAPI projects

### Pattern 4: Kubernetes Deployment
```bash
"Create production Kubernetes deployment with Helm chart and GitOps"
```

**kubernetes-architect agent activates 4 skills**:
- `k8s-manifests` - Deployment/Service patterns
- `helm-charts` - Chart templating
- `k8s-gitops` - ArgoCD configuration
- `k8s-security` - Network policies, RBAC

## Workflow Orchestrators (15 Total)

Multi-agent coordination systems included in `full-stack-orchestration` plugin:

| Orchestrator | Agents Coordinated | Use Case |
|--------------|-------------------|----------|
| **full-stack-feature** | 7+ agents | End-to-end feature development |
| **security-hardening** | 3-4 agents | Comprehensive security audit |
| **ml-pipeline** | 5-6 agents | ML model development to deployment |
| **incident-response** | 4-5 agents | Production incident handling |
| **database-migration** | 3 agents | Safe database schema changes |
| **api-design-implement** | 4 agents | API design through deployment |
| **performance-optimization** | 3-4 agents | End-to-end performance tuning |

[→ View all 15 orchestrators](../references/agents/docs/usage.md#multi-agent-workflow-examples)

## Repository Structure

```
claude-agents/
├── .claude-plugin/
│   └── marketplace.json          # 68 plugin definitions
├── plugins/
│   ├── python-development/
│   │   ├── agents/               # python-pro, django-pro, fastapi-pro
│   │   ├── commands/             # python-scaffold tool
│   │   └── skills/               # 5 Python skills
│   ├── kubernetes-operations/
│   │   ├── agents/               # kubernetes-architect
│   │   ├── commands/             # K8s deployment tools
│   │   └── skills/               # 4 K8s skills
│   ├── full-stack-orchestration/
│   │   ├── agents/               # full-stack-orchestrator
│   │   └── commands/             # 15 workflow commands
│   └── ... (65 more plugins)
├── docs/
│   ├── plugins.md                # Complete plugin catalog
│   ├── agents.md                 # All 100 agents
│   ├── agent-skills.md           # 110 skills guide
│   ├── usage.md                  # Commands and workflows
│   └── architecture.md           # Design principles
└── README.md
```

## Patterns for Agentic Workflows

### Pattern 1: Granular Plugin Composition

**Anti-pattern** (Monolithic):
```bash
# Loads all 100 agents + 110 skills (~50,000 tokens)
/plugin install everything
```

**Best practice** (Granular):
```bash
# Loads only 3 agents + 5 skills (~300 tokens)
/plugin install python-development@claude-code-workflows
```

**Benefit**: 99.4% token reduction

### Pattern 2: Progressive Disclosure at Scale

**110 skills with 3-tier loading**:
- Tier 1 (Metadata): 50 tokens × 110 = 5,500 tokens always loaded
- Tier 2 (Instructions): 500 tokens loaded only when activated
- Tier 3 (Resources): Unlimited, loaded on-demand

**Traditional approach**: ~1,000,000 tokens always loaded
**Progressive approach**: 5,500 tokens + on-demand activation
**Savings**: 99.45% reduction

### Pattern 3: Strategic Model Assignment

**Cost-optimized orchestration**:
```
User request: "Build authentication system"
↓
full-stack-orchestrator (Sonnet) analyzes
↓
1. backend-architect (Opus) - Critical design decisions
2. security-auditor (Opus) - Security-critical review
3. backend-developer (Inherit) - User chooses model
4. test-automator (Sonnet) - Test generation
5. deployment-engineer (Haiku) - Fast deployment
```

**Cost Calculation**:
- Opus: 2 agents × 10k tokens = 20k @ $5 = $0.10
- Inherit (Sonnet): 1 agent × 50k tokens = 50k @ $3 = $0.15
- Sonnet: 1 agent × 30k tokens = 30k @ $3 = $0.09
- Haiku: 1 agent × 5k tokens = 5k @ $1 = $0.005
- **Total**: $0.345 vs $1.00+ all-Opus

### Pattern 4: Multi-Agent Orchestration

**15 pre-built orchestrators** eliminate need to manually coordinate:

```python
# Manual coordination (error-prone)
backend_design = call_agent("backend-architect", task)
db_design = call_agent("database-architect", backend_design)
frontend = call_agent("frontend-developer", {backend_design, db_design})
# ... 4 more agents

# Orchestrated (built-in)
/full-stack-orchestration:full-stack-feature "user authentication"
# Automatically coordinates all 7 agents with proper context flow
```

## Key Learnings for Agentic Workflows

1. **Granular beats monolithic** - 3.4 components per plugin optimal
2. **Progressive disclosure scales** - 110 skills with 99.45% token reduction
3. **Strategic model assignment** - Right model for right task saves cost
4. **Orchestrators eliminate coordination complexity** - Pre-built workflows
5. **Plugin composition** - Mix and match for custom workflows
6. **100% agent coverage** - All agents accessible via focused plugins
7. **Production-ready patterns** - Real-world implementation with tooling
8. **Token efficiency is critical** - Average 300 tokens per plugin vs 50,000+ monolithic

## Integration with Other Systems

### With claude-task-system
```
Feature Definition → Plan → Generate Tasks → Execute

During Execute:
- Use full-stack-orchestrator for task coordination
- Workers activate relevant skills (python-testing-patterns, k8s-manifests)
- Strategic model assignment per task type
```

### With awesome-claude-code-subagents
```
VoltAgent's 140 agents + wshobson's 100 agents = Comprehensive coverage

Install wshobson plugins for:
- Progressive disclosure (110 skills)
- Pre-built orchestrators (15 workflows)
- Granular composition

Keep VoltAgent for:
- Additional domain specialists
- Meta-orchestration (multi-agent-coordinator)
```

### With MCP Servers
Skills can reference MCP tools:
```yaml
---
name: database-operations
tools: Read, Write, postgres-mcp, supabase-mcp
---
```

## Priority Plugins to Install

**Essential** (Start here):
1. `python-development` - 5 skills, production scaffolding
2. `javascript-typescript` - 4 skills, modern JS/TS
3. `backend-development` - 3 architecture skills
4. `code-review-ai` - AI-powered code review
5. `full-stack-orchestration` - 15 workflow orchestrators

**Infrastructure**:
6. `kubernetes-operations` - 4 K8s skills
7. `cloud-infrastructure` - 4 cloud skills
8. `ci-cd-pipelines` - 4 pipeline skills

**Quality & Security**:
9. `security-scanning` - SAST + dependency scanning
10. `comprehensive-review` - Multi-agent review

**Advanced**:
11. `llm-applications` - 4 LLM/RAG skills
12. `conductor` - Context-driven development (3 skills)
13. `mlops` - ML pipeline deployment

## Related Patterns

- [[agent-loop-patterns]] - Agent execution cycles
- [[progressive-disclosure-pattern]] - Context efficiency
- [[structured-lifecycle-pattern]] - Phase-based development
- [[mcp-server-integration]] - Tool integration
- [[subagents-catalog]] - VoltAgent's 140 subagents

## References

- [wshobson/agents Repository](../references/agents/)
- [Plugin Reference](../references/agents/docs/plugins.md) - All 68 plugins
- [Agent Reference](../references/agents/docs/agents.md) - All 100 agents
- [Agent Skills Guide](../references/agents/docs/agent-skills.md) - All 110 skills
- [Usage Guide](../references/agents/docs/usage.md) - Commands and workflows
- [Architecture](../references/agents/docs/architecture.md) - Design principles

## Key Takeaways

1. **68 granular plugins** - Average 3.4 components each
2. **100 specialized agents** - Strategic model assignment (Opus/Sonnet/Haiku)
3. **110 agent skills** - Progressive disclosure with 99.45% token reduction
4. **15 workflow orchestrators** - Pre-built multi-agent coordination
5. **76 development tools** - Production utilities
6. **Token efficiency** - 300 tokens per plugin vs 50,000+ monolithic
7. **Cost optimization** - Right model for right task
8. **Production-ready** - Real-world patterns and comprehensive tooling
