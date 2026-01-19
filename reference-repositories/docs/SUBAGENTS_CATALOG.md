# Awesome Claude Code Subagents Catalog

**Reference**: `references/awesome-claude-code-subagents/`
**Source**: https://github.com/VoltAgent/awesome-claude-code-subagents
**Maintainer**: VoltAgent Team

## Overview

A comprehensive collection of **140+ specialized Claude Code subagents** organized into 10 categories. Each subagent is a domain-specific AI assistant with task-focused expertise, isolated context windows, and granular tool permissions.

## Why Subagents for Agentic Workflows?

Subagents demonstrate advanced patterns for:
1. **Multi-agent orchestration** - Specialized agents coordinating on complex tasks
2. **Context isolation** - Independent context windows prevent cross-contamination
3. **Tool permission management** - Fine-grained control over agent capabilities
4. **Domain specialization** - Deep expertise in specific technical domains
5. **Team collaboration** - Shareable agents ensure consistent development practices

## Subagent Architecture

### Core Advantages

**Independent Context Windows**
- Each subagent operates in isolated context space
- Prevents main conversation from becoming cluttered
- Maintains clarity in primary thread

**Domain-Specific Intelligence**
- Carefully crafted instructions for specialized tasks
- Superior performance on domain-specific work
- Pre-configured best practices and patterns

**Shared Across Projects**
- Global agents: `~/.claude/agents/` (all projects)
- Project agents: `.claude/agents/` (current project only)
- Project-specific agents override global ones

**Granular Tool Permissions**
- Read-only agents: `Read, Grep, Glob`
- Research agents: `Read, Grep, Glob, WebFetch, WebSearch`
- Code writers: `Read, Write, Edit, Bash, Glob, Grep`
- Documentation agents: `Read, Write, Edit, Glob, Grep, WebFetch, WebSearch`

### Subagent Template Structure

```yaml
---
name: subagent-name
description: When this agent should be invoked
tools: Read, Write, Edit, Bash, Glob, Grep
---

You are a [role description and expertise areas]...

[Agent-specific checklists, patterns, and guidelines]...

## Communication Protocol
Inter-agent communication specifications...

## Development Workflow
Structured implementation phases...
```

## 10 Categories of Subagents (140+ Total)

### 1. Core Development (11 agents)
**Plugin**: `voltagent-core-dev`

Essential development subagents for everyday coding tasks.

| Agent | Expertise |
|-------|-----------|
| **api-designer** | REST and GraphQL API architect |
| **backend-developer** | Server-side expert for scalable APIs |
| **electron-pro** | Desktop application expert |
| **frontend-developer** | UI/UX specialist for React, Vue, Angular |
| **fullstack-developer** | End-to-end feature development |
| **graphql-architect** | GraphQL schema and federation expert |
| **microservices-architect** | Distributed systems designer |
| **mobile-developer** | Cross-platform mobile specialist |
| **ui-designer** | Visual design and interaction specialist |
| **websocket-engineer** | Real-time communication specialist |
| **wordpress-master** | WordPress development and optimization |

### 2. Language Specialists (25 agents)
**Plugin**: `voltagent-lang`

Language-specific experts with deep framework knowledge.

**Notable Agents**:
- **typescript-pro** - TypeScript specialist
- **python-pro** - Python ecosystem master
- **golang-pro** - Go concurrency specialist
- **rust-engineer** - Systems programming expert
- **java-architect** - Enterprise Java expert
- **nextjs-developer** - Next.js 14+ full-stack specialist
- **react-specialist** - React 18+ modern patterns expert
- **vue-expert** - Vue 3 Composition API expert
- **angular-architect** - Angular 15+ enterprise patterns
- **dotnet-core-expert** - .NET 8 cross-platform specialist
- **laravel-specialist** - Laravel 10+ PHP framework expert
- **rails-expert** - Rails 8.1 rapid development expert
- **spring-boot-engineer** - Spring Boot 3+ microservices expert
- **flutter-expert** - Flutter 3+ cross-platform mobile
- **swift-expert** - iOS and macOS specialist
- **kotlin-specialist** - Modern JVM language expert
- **elixir-expert** - Elixir and OTP fault-tolerant systems
- **powershell-7-expert** - Cross-platform PowerShell 7+ automation
- **powershell-5.1-expert** - Windows PowerShell 5.1 and .NET Framework

### 3. Infrastructure (14 agents)
**Plugin**: `voltagent-infra`

DevOps, cloud, and deployment specialists.

| Agent | Expertise |
|-------|-----------|
| **cloud-architect** | AWS/GCP/Azure specialist |
| **kubernetes-specialist** | Container orchestration master |
| **terraform-engineer** | Infrastructure as Code expert |
| **devops-engineer** | CI/CD and automation expert |
| **sre-engineer** | Site reliability engineering |
| **platform-engineer** | Platform architecture expert |
| **security-engineer** | Infrastructure security |
| **database-administrator** | Database management expert |
| **network-engineer** | Network infrastructure |
| **azure-infra-engineer** | Azure infrastructure and Az PowerShell |
| **windows-infra-admin** | Active Directory, DNS, DHCP, GPO automation |
| **deployment-engineer** | Deployment automation |
| **incident-responder** | System incident response |
| **devops-incident-responder** | DevOps incident management |

### 4. Quality & Security (14 agents)
**Plugin**: `voltagent-qa-sec`

Testing, security, and code quality experts.

**Key Agents**:
- **code-reviewer** - Code quality guardian
- **security-auditor** - Security vulnerability expert
- **penetration-tester** - Ethical hacking specialist
- **qa-expert** - Test automation specialist
- **test-automator** - Test automation framework expert
- **performance-engineer** - Performance optimization
- **accessibility-tester** - A11y compliance expert
- **compliance-auditor** - Regulatory compliance
- **chaos-engineer** - System resilience testing
- **debugger** - Advanced debugging specialist
- **error-detective** - Error analysis and resolution
- **architect-reviewer** - Architecture review specialist
- **ad-security-reviewer** - Active Directory security and GPO audit
- **powershell-security-hardening** - PowerShell security hardening

### 5. Data & AI (12 agents)
**Plugin**: `voltagent-data-ai`

Data engineering, ML, and AI specialists.

| Agent | Expertise |
|-------|-----------|
| **ai-engineer** | AI system design and deployment |
| **llm-architect** | Large language model architect |
| **ml-engineer** | Machine learning specialist |
| **mlops-engineer** | MLOps and model deployment |
| **data-engineer** | Data pipeline architect |
| **data-scientist** | Analytics and insights expert |
| **data-analyst** | Data insights and visualization |
| **nlp-engineer** | Natural language processing |
| **prompt-engineer** | Prompt optimization specialist |
| **machine-learning-engineer** | Machine learning systems |
| **database-optimizer** | Database performance |
| **postgres-pro** | PostgreSQL database expert |

### 6. Developer Experience (13 agents)
**Plugin**: `voltagent-dev-exp`

Tooling and developer productivity experts.

**Notable Agents**:
- **mcp-developer** - Model Context Protocol specialist
- **cli-developer** - Command-line tool creator
- **documentation-engineer** - Technical documentation expert
- **dx-optimizer** - Developer experience optimization
- **git-workflow-manager** - Git workflow and branching expert
- **legacy-modernizer** - Legacy code modernization
- **refactoring-specialist** - Code refactoring expert
- **build-engineer** - Build system specialist
- **tooling-engineer** - Developer tooling specialist
- **dependency-manager** - Package and dependency specialist
- **powershell-ui-architect** - PowerShell UI/UX for WinForms, WPF, Metro, TUIs
- **powershell-module-architect** - PowerShell module and profile architecture
- **slack-expert** - Slack platform and @slack/bolt specialist

### 7. Specialized Domains (12 agents)
**Plugin**: `voltagent-domains`

Domain-specific technology experts.

| Agent | Expertise |
|-------|-----------|
| **blockchain-developer** | Web3 and crypto specialist |
| **game-developer** | Game development expert |
| **iot-engineer** | IoT systems developer |
| **embedded-systems** | Embedded and real-time systems |
| **fintech-engineer** | Financial technology |
| **payment-integration** | Payment systems expert |
| **quant-analyst** | Quantitative analysis |
| **mobile-app-developer** | Mobile application specialist |
| **api-documenter** | API documentation specialist |
| **risk-manager** | Risk assessment and management |
| **seo-specialist** | Search engine optimization |
| **m365-admin** | Microsoft 365, Exchange, Teams, SharePoint |

### 8. Business & Product (10 agents)
**Plugin**: `voltagent-biz`

Product management and business analysis.

**Key Agents**:
- **product-manager** - Product strategy expert
- **project-manager** - Project management specialist
- **business-analyst** - Requirements specialist
- **scrum-master** - Agile methodology expert
- **ux-researcher** - User research expert
- **technical-writer** - Technical documentation specialist
- **customer-success-manager** - Customer success expert
- **sales-engineer** - Technical sales expert
- **content-marketer** - Content marketing specialist
- **legal-advisor** - Legal and compliance specialist

### 9. Meta & Orchestration (10 agents)
**Plugin**: `voltagent-meta`

Agent coordination and meta-programming - **MOST RELEVANT FOR AGENTIC WORKFLOWS**.

| Agent | Purpose |
|-------|---------|
| **agent-installer** | Browse and install agents from repository via GitHub |
| **multi-agent-coordinator** | Advanced multi-agent orchestration |
| **agent-organizer** | Multi-agent coordinator |
| **workflow-orchestrator** | Complex workflow automation |
| **task-distributor** | Task allocation specialist |
| **context-manager** | Context optimization expert |
| **error-coordinator** | Error handling and recovery specialist |
| **knowledge-synthesizer** | Knowledge aggregation expert |
| **performance-monitor** | Agent performance optimization |
| **it-ops-orchestrator** | IT operations workflow orchestration |
| **pied-piper** | Orchestrate Team of AI Subagents for repetitive SDLC workflows |

### 10. Research & Analysis (6 agents)
**Plugin**: `voltagent-research`

Research, search, and analysis specialists.

- **research-analyst** - Comprehensive research specialist
- **search-specialist** - Advanced information retrieval
- **trend-analyst** - Emerging trends and forecasting
- **competitive-analyst** - Competitive intelligence
- **market-researcher** - Market analysis and consumer insights
- **data-researcher** - Data discovery and analysis

## Installation Methods

### Method 1: Claude Code Plugin (Recommended)
```bash
claude plugin marketplace add VoltAgent/awesome-claude-code-subagents
claude plugin install voltagent-meta    # Meta & orchestration
claude plugin install voltagent-lang    # Language specialists
claude plugin install voltagent-infra   # Infrastructure
```

### Method 2: Manual Installation
```bash
# Clone repository
git clone https://github.com/VoltAgent/awesome-claude-code-subagents.git

# Copy desired agents
cp categories/09-meta-orchestration/*.md ~/.claude/agents/      # Global
cp categories/09-meta-orchestration/*.md .claude/agents/        # Project
```

### Method 3: Interactive Installer
```bash
git clone https://github.com/VoltAgent/awesome-claude-code-subagents.git
cd awesome-claude-code-subagents
./install-agents.sh
```

### Method 4: Standalone Installer (No Clone)
```bash
curl -sO https://raw.githubusercontent.com/VoltAgent/awesome-claude-code-subagents/main/install-agents.sh
chmod +x install-agents.sh
./install-agents.sh
```

### Method 5: Agent Installer (Use Claude Code)
```bash
curl -s https://raw.githubusercontent.com/VoltAgent/awesome-claude-code-subagents/main/categories/09-meta-orchestration/agent-installer.md -o ~/.claude/agents/agent-installer.md
```

Then: "Use the agent-installer to show me available categories"

## Usage Patterns

### Automatic Invocation
Claude Code automatically delegates to subagents based on their description field:

```
> Review my authentication code for security issues
# Claude delegates to security-auditor subagent
```

### Manual Invocation
Explicitly request a specific subagent:

```
> Have the code-reviewer subagent analyze my latest commits
> Ask the llm-architect to design a RAG system
> Let the multi-agent-coordinator plan this feature implementation
```

### Managing Subagents
```bash
/agents                    # Open subagent manager
/agents create            # Create new subagent
/agents list              # List all available subagents
```

## Tool Permission Patterns

### Read-Only Pattern (Reviewers, Auditors)
```yaml
tools: Read, Grep, Glob
```
**Use Case**: Code review, security audits, compliance checks
**Example**: code-reviewer, security-auditor, architect-reviewer

### Research Pattern (Analysts, Researchers)
```yaml
tools: Read, Grep, Glob, WebFetch, WebSearch
```
**Use Case**: Information gathering, competitive analysis, trend research
**Example**: research-analyst, search-specialist, trend-analyst

### Code Writer Pattern (Developers, Engineers)
```yaml
tools: Read, Write, Edit, Bash, Glob, Grep
```
**Use Case**: Feature implementation, refactoring, bug fixes
**Example**: backend-developer, frontend-developer, fullstack-developer

### Documentation Pattern (Writers, Documenters)
```yaml
tools: Read, Write, Edit, Glob, Grep, WebFetch, WebSearch
```
**Use Case**: Technical documentation, API docs, guides
**Example**: documentation-engineer, technical-writer, api-documenter

## Patterns for Agentic Workflows

### Pattern 1: Multi-Agent Coordination
**Agent**: `multi-agent-coordinator`

Orchestrates multiple specialized agents for complex tasks:
1. Analyzes task requirements
2. Identifies needed specialists
3. Delegates sub-tasks to appropriate agents
4. Aggregates results
5. Ensures coherent final output

**Example**:
```
> Build a payment processing system with security audit

multi-agent-coordinator delegates to:
- backend-developer (API implementation)
- security-auditor (Security review)
- payment-integration (Payment logic)
- test-automator (Test suite)
- documentation-engineer (API docs)
```

### Pattern 2: Workflow Orchestration
**Agent**: `workflow-orchestrator`

Manages complex multi-step workflows with dependencies:
1. Defines workflow stages
2. Manages stage transitions
3. Handles failures and retries
4. Tracks progress across stages

**Example**:
```
> Deploy new microservice to production

workflow-orchestrator manages:
1. code-reviewer → Review changes
2. test-automator → Run test suite
3. build-engineer → Create build artifacts
4. deployment-engineer → Deploy to staging
5. qa-expert → Smoke tests
6. deployment-engineer → Production deployment
7. sre-engineer → Monitor rollout
```

### Pattern 3: Knowledge Synthesis
**Agent**: `knowledge-synthesizer`

Aggregates information from multiple sources/agents:
1. Collects outputs from multiple agents
2. Identifies patterns and conflicts
3. Synthesizes coherent summary
4. Provides recommendations

### Pattern 4: Context Management
**Agent**: `context-manager`

Optimizes context usage across agent invocations:
1. Tracks what context each agent needs
2. Loads only relevant information
3. Manages context handoffs between agents
4. Prevents context bloat

### Pattern 5: Error Coordination
**Agent**: `error-coordinator`

Centralized error handling and recovery:
1. Detects failures across agents
2. Analyzes root causes
3. Coordinates recovery strategies
4. Delegates to specialized debuggers

## Integration with Agentic Workflows

### With claude-task-system
Subagents enhance the task execution phase:

```
Feature Definition → Plan → Generate Tasks → Execute

During Execute:
- Orchestrator uses multi-agent-coordinator
- Workers spawn specialized subagents (backend-developer, test-automator)
- context-manager optimizes token usage
- error-coordinator handles failures
```

### With GET SHIT DONE
Fresh subagent execution pattern:

```
For each atomic task:
1. workflow-orchestrator spawns clean subagent context
2. Subagent completes task independently
3. Results returned to orchestrator
4. Next task gets fresh context
```

### With MCP Servers
Subagents can use MCP tools:

```yaml
---
name: database-developer
tools: Read, Write, Edit, Bash, postgres-mcp
---
```

## Key Learnings for Agentic Workflows

1. **Context Isolation is Critical**: Independent contexts prevent interference
2. **Tool Permissions Matter**: Minimal necessary permissions improve security
3. **Specialization Over Generalization**: Domain experts outperform generalists
4. **Orchestration Enables Complexity**: Coordinators manage multi-agent workflows
5. **Shared Agents Ensure Consistency**: Team-wide agents standardize approaches
6. **Meta-Agents Are Multipliers**: agent-installer, multi-agent-coordinator enable scale

## Priority Agents to Install for Agentic Research

**Must-Have** (Meta & Orchestration):
1. `multi-agent-coordinator` - Multi-agent orchestration
2. `workflow-orchestrator` - Complex workflow automation
3. `agent-installer` - Browse and install agents
4. `context-manager` - Context optimization
5. `error-coordinator` - Error handling and recovery

**Recommended** (Development):
6. `backend-developer` - Server-side development
7. `frontend-developer` - UI development
8. `code-reviewer` - Code quality
9. `test-automator` - Testing
10. `documentation-engineer` - Documentation

**Optional** (Based on Stack):
- `python-pro`, `typescript-pro`, `golang-pro` (language-specific)
- `kubernetes-specialist`, `terraform-engineer` (infrastructure)
- `llm-architect`, `ai-engineer` (AI/ML work)

## Related Patterns

- [[agent-loop-patterns]] - Agent execution cycles
- [[structured-lifecycle-pattern]] - Phase-based development
- [[state-management-patterns]] - Memory and context management
- [[mcp-server-integration]] - Tool integration via MCP

## References

- [Awesome Claude Code Subagents Repository](c:\Users\Stang3x\Documents\Personal - Dan\Agentic Workflows\references\awesome-claude-code-subagents\)
- [VoltAgent Framework](https://github.com/voltagent/voltagent)
- [Claude Code Documentation](https://docs.anthropic.com/claude-code)

## Key Takeaways

1. **140+ specialized subagents** across 10 categories
2. **Independent context windows** prevent cross-contamination
3. **Granular tool permissions** enable security and control
4. **Meta-agents enable orchestration** at scale
5. **Domain specialization outperforms** general-purpose agents
6. **Shared across projects** ensures team consistency
7. **Tool permission patterns** match agent roles (read-only, research, code writer, documentation)
8. **Multi-agent coordination** enables complex workflows
