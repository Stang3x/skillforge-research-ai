# Claude Code Deep Learning Resources

This document contains curated resources from the [Awesome Claude Code](https://github.com/hesreallyhim/awesome-claude-code) repository for extending and mastering Claude Code.

## Table of Contents
- [Skills & Agents](#skills--agents)
- [Tooling & Utilities](#tooling--utilities)
- [Hooks & Integration](#hooks--integration)
- [IDE Integrations](#ide-integrations)
- [Workflows & Frameworks](#workflows--frameworks)
- [Orchestration Systems](#orchestration-systems)
- [Example CLAUDE.md Files](#example-claudemd-files)
- [Getting Started Guide](#getting-started-guide)

---

## Skills & Agents

### Claude Codex Settings
**Repository**: https://github.com/fcakyon/claude-codex-settings
**Description**: Well-organized plugins covering core developer activities
**Includes**:
- GitHub integration
- Azure integration
- MongoDB support
- Tavily search
- Playwright automation

**Use Case**: Comprehensive skill set for full-stack development

### Superpowers
**Repository**: https://github.com/obra/superpowers
**Description**: Consolidated engineering best practices
**Focus Areas**:
- Planning workflows
- Code review processes
- Testing strategies
- Debugging techniques

**Use Case**: Professional development workflow enhancement

### Context Engineering Kit
**Repository**: https://github.com/NeoLabHQ/context-engineering-kit
**Description**: Advanced patterns with minimal token usage
**Benefits**:
- Improved agent quality
- Efficient context management
- Pattern-based approaches

**Use Case**: Optimizing Claude Code performance and quality

---

## Tooling & Utilities

### ccflare
**Repository**: https://github.com/snipeship/ccflare
**Type**: Web dashboard
**Features**:
- Usage metrics tracking
- Cost monitoring
- Analytics dashboard

**Use Case**: Monitor and optimize Claude Code usage

### recall
**Repository**: https://github.com/zippoxer/recall
**Type**: Search tool
**Features**:
- Full-text search across sessions
- Terminal interface
- Historical conversation lookup

**Use Case**: Finding patterns and solutions from past sessions

### claudekit
**Repository**: https://github.com/carlrannaberg/claudekit
**Type**: CLI toolkit
**Features**:
- Checkpointing functionality
- Quality hooks
- 20+ specialized subagents
- Task management

**Use Case**: Advanced workflow management and quality control

### Container Use
**Repository**: https://github.com/dagger/container-use
**Type**: Development environment
**Features**:
- Sandboxed environments
- Multi-agent support
- Isolated workspaces

**Use Case**: Safe, isolated development for multiple agents

---

## Hooks & Integration

### cchooks
**Repository**: https://github.com/GowayLee/cchooks
**Type**: Python SDK
**Features**:
- Clean API design
- Hook development framework
- Lightweight implementation

**Use Case**: Building custom hooks for Claude Code

### Claudio
**Repository**: https://github.com/ctoth/claudio
**Type**: Notification system
**Features**:
- OS-native sound notifications
- Hook-based triggers
- Event monitoring

**Use Case**: Audio feedback for Claude Code events

### TDD Guard
**Repository**: https://github.com/nizos/tdd-guard
**Type**: Development enforcer
**Features**:
- Real-time file monitoring
- TDD principle enforcement
- Automated testing workflows

**Use Case**: Maintaining test-driven development discipline

---

## IDE Integrations

### claude-code.nvim
**Repository**: https://github.com/greggh/claude-code.nvim
**IDE**: Neovim
**Features**: Seamless integration with Neovim

**Use Case**: Using Claude Code within Neovim

### Claudix
**Repository**: https://github.com/Haleclipse/Claudix
**IDE**: VSCode
**Features**:
- Chat interface
- File operations
- Terminal execution
- Full VSCode integration

**Use Case**: Enhanced VSCode experience with Claude Code

### claude-code-ide.el
**Repository**: https://github.com/manzaltu/claude-code-ide.el
**IDE**: Emacs
**Features**:
- LSP diagnostics integration
- MCP tool support
- Emacs-native interface

**Use Case**: Emacs integration for Claude Code

---

## Workflows & Frameworks

### AB Method
**Repository**: https://github.com/ayoubben18/ab-method
**Type**: Spec-driven workflow
**Approach**:
- Transform problems into specifications
- Incremental mission completion
- Structured problem-solving

**Use Case**: Systematic approach to complex projects

### RIPER Workflow
**Repository**: https://github.com/tony/claude-code-riper-5
**Type**: Phased workflow
**Phases**:
1. **R**esearch - Gather information
2. **I**nnovate - Generate solutions
3. **P**lan - Design implementation
4. **E**xecute - Build the solution
5. **Review** - Evaluate and refine

**Use Case**: Comprehensive project lifecycle management

### Claude CodePro
**Repository**: https://github.com/maxritter/claude-codepro
**Type**: Professional environment
**Features**:
- Spec-driven workflow
- Test-Driven Development (TDD)
- Semantic search
- Quality controls

**Use Case**: Professional-grade development setup

---

## Orchestration Systems

### Ralph Wiggum Technique

#### ralph-orchestrator
**Repository**: https://github.com/mikeyobrien/ralph-orchestrator
**Description**: Robust orchestration system for autonomous task completion
**Features**:
- Well-tested framework
- Autonomous agent management
- Task orchestration

#### Ralph for Claude Code
**Repository**: https://github.com/frankbria/ralph-claude-code
**Features**:
- Iterative framework
- Rate limiting
- Safety guardrails
- Controlled automation

**Use Case**: Safe autonomous task execution

### Claude Squad
**Repository**: https://github.com/smtg-ai/claude-squad
**Type**: Multi-agent orchestrator
**Features**:
- Terminal application
- Parallel agent management
- Multiple workspaces
- Agent coordination

**Use Case**: Managing multiple Claude Code instances

### TSK
**Repository**: https://github.com/dtormoen/tsk
**Type**: Rust CLI orchestrator
**Features**:
- Task delegation
- Docker sandboxes
- Agent isolation
- Performance optimization

**Use Case**: High-performance, isolated agent execution

---

## Status Lines & Monitoring

### CCometixLine
**Repository**: https://github.com/Haleclipse/CCometixLine
**Type**: Status line (Rust)
**Features**:
- Git integration
- Usage tracking
- Performance metrics
- Real-time monitoring

### claudia-statusline
**Repository**: https://github.com/hagan/claudia-statusline
**Features**:
- SQLite persistence
- Burn rate calculation
- XDG-compliant
- Cost tracking

**Use Case**: Monitoring Claude Code usage and costs

---

## Example CLAUDE.md Files

### Metabase
**Repository**: https://github.com/metabase/metabase/blob/master/CLAUDE.md
**Highlights**:
- REPL-driven development workflow
- Clojure/ClojureScript patterns
- Interactive development guide

**Learn From**: REPL workflow patterns

### HASH
**Repository**: https://github.com/hashintel/hash/blob/main/CLAUDE.md
**Highlights**:
- Repository structure guidelines
- Rust documentation patterns
- Large-scale project organization

**Learn From**: Structuring large codebases for Claude Code

### Basic Memory
**Repository**: https://github.com/basicmachines-co/basic-memory/blob/main/CLAUDE.md
**Highlights**:
- AI-human collaboration framework
- Model Context Protocol (MCP) integration
- Agent memory patterns

**Learn From**: MCP integration and agent memory management

---

## Getting Started Guide

### Phase 1: Explore & Understand (Week 1-2)

1. **Read Example CLAUDE.md Files**
   ```bash
   # Clone and study these examples
   git clone https://github.com/metabase/metabase
   git clone https://github.com/hashintel/hash
   git clone https://github.com/basicmachines-co/basic-memory

   # Read their CLAUDE.md files
   cat metabase/CLAUDE.md
   cat hash/CLAUDE.md
   cat basic-memory/CLAUDE.md
   ```

2. **Install Basic Utilities**
   - Start with **recall** for session search
   - Add **ccflare** for usage tracking
   - Consider **claudia-statusline** for monitoring

3. **Study Workflows**
   - Review **RIPER Workflow** documentation
   - Explore **AB Method** for spec-driven development
   - Understand **Claude CodePro** setup

### Phase 2: Skills & Extensions (Week 3-4)

1. **Install Your First Skill**
   - Start with **Superpowers** for best practices
   - Or **Claude Codex Settings** for comprehensive tooling
   - Document what works for your workflow

2. **Experiment with Hooks**
   - Try **cchooks** Python SDK
   - Build a simple notification hook
   - Integrate with your development workflow

3. **Set Up IDE Integration**
   - If using VSCode: Install **Claudix**
   - Configure for optimal workflow
   - Customize to your preferences

### Phase 3: Advanced Patterns (Week 5-6)

1. **Implement Orchestration**
   - For multi-agent work: **Claude Squad**
   - For isolated tasks: **TSK**
   - For autonomous workflows: **Ralph orchestrator**

2. **Optimize Context**
   - Apply **Context Engineering Kit** patterns
   - Refine your CLAUDE.md
   - Document learned patterns

3. **Build Custom Skills**
   - Create agentic workflow-specific skills
   - Use **cchooks** for custom automation
   - Share learnings in `docs/patterns/`

### Phase 4: Integration & Mastery (Ongoing)

1. **Combine Tools**
   - Workflow + Skills + Hooks + Monitoring
   - Create your personalized setup
   - Document in CLAUDE.md

2. **Contribute Back**
   - Document unique patterns you discover
   - Share workflows that work well
   - Consider contributing to awesome-claude-code

3. **Continuous Learning**
   - Follow new tools added to awesome-claude-code
   - Experiment with different approaches
   - Refine based on experience

---

## Recommended Starting Stack

For agentic workflows research, consider this stack:

### Essential
- **Superpowers** - Best practices and workflows
- **recall** - Search past sessions for patterns
- **claudia-statusline** - Monitor usage and costs

### For Development
- **TDD Guard** - Maintain testing discipline
- **cchooks** - Custom automation
- **Claudix** (VSCode) - Enhanced IDE experience

### For Advanced Work
- **Context Engineering Kit** - Optimize agent quality
- **Claude Squad** - Multi-agent orchestration
- **Ralph orchestrator** - Autonomous task execution

### For Learning
- Study **Metabase**, **HASH**, **Basic Memory** CLAUDE.md files
- Clone **Claude CodePro** for comprehensive setup example
- Review **RIPER Workflow** for structured approach

---

## Quick Actions

### Install a Skill
```bash
# Example: Installing Superpowers
git clone https://github.com/obra/superpowers ~/.claude/skills/superpowers
```

### Clone Example CLAUDE.md
```bash
# Create examples directory
mkdir -p docs/claude-md-examples
cd docs/claude-md-examples

# Clone examples
git clone --depth 1 https://github.com/metabase/metabase metabase
git clone --depth 1 https://github.com/hashintel/hash hash
git clone --depth 1 https://github.com/basicmachines-co/basic-memory basic-memory
```

### Set Up Monitoring
```bash
# Install ccflare for usage tracking
npm install -g ccflare

# Or install claudia-statusline
cargo install claudia-statusline
```

---

## Next Steps

1. Choose 2-3 tools from the recommended starting stack
2. Install and configure them
3. Document your setup in CLAUDE.md
4. Experiment with different workflows
5. Refine based on what works for your agentic workflows research

## Official Resources

- **Anthropic Documentation**: https://docs.claude.com/en/home
- **Claude Code GitHub Actions**: https://github.com/anthropics/claude-code-action
- **Awesome Claude Code**: https://github.com/hesreallyhim/awesome-claude-code

---

*Resources curated from awesome-claude-code (CC BY-NC-ND 4.0)*
