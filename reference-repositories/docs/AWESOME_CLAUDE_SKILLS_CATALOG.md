# Awesome Claude Skills - Community Skills Catalog

**Reference**: `references/awesome-claude-skills/`
**Source**: https://github.com/BehiSecc/awesome-claude-skills
**Curator**: [@Behi_Sec](https://x.com/Behi_Sec)

## Overview

Awesome Claude Skills is a **community-curated catalog of 50+ Claude Code skills** across 11 categories, from document processing to scientific research. Unlike official Anthropic skills, this catalog showcases the breadth of community innovation, demonstrating what developers worldwide are building with the Agent Skills specification.

This catalog is valuable for:
- **Discovering domain-specific skills** not available officially
- **Learning from community patterns** and implementations
- **Finding production solutions** for specialized workflows
- **Understanding skill diversity** across industries and use cases

## Why This Catalog Matters for Agentic Workflows

1. **Real-World Solutions** - Community skills solve actual production problems
2. **Domain Specialization** - Skills for bioinformatics, materials science, health, security
3. **Integration Examples** - See how skills integrate with external services (Linear, AWS, Postgres)
4. **Innovation Showcase** - Novel approaches like TOON format (30-60% token savings)
5. **Production Patterns** - 125+ scientific skills show how to scale skill development

## Skill Categories (50+ Skills)

### 1. Document Skills (5 Skills)

#### Anthropic Document Skills (Official)
- **docx** - Create, edit, analyze Word docs with tracked changes, comments, formatting
- **pdf** - Extract text, tables, metadata, merge & annotate PDFs
- **pptx** - Read, generate, adjust slides, layouts, templates
- **xlsx** - Spreadsheet manipulation: formulas, charts, data transformations

**See**: [ANTHROPIC_SKILLS_GUIDE.md](./ANTHROPIC_SKILLS_GUIDE.md) for complete documentation

#### Community Document Skills

**revealjs-skill**
- **Author**: [@ryanbbrown](https://github.com/ryanbbrown)
- **Repository**: https://github.com/ryanbbrown/revealjs-skill
- **Purpose**: Generate polished, professional presentations using Reveal.js HTML framework
- **Use Case**: Interactive web-based presentations with animations, themes, and embeds
- **Pattern**: HTML artifact generation with JavaScript framework integration

---

### 2. Development & Code Tools (11 Skills)

#### web-artifacts-builder (Anthropic Official)
- **Repository**: https://github.com/anthropics/skills/tree/main/skills/web-artifacts-builder
- **Purpose**: Suite for creating elaborate, multi-component claude.ai HTML artifacts
- **Technologies**: React, Tailwind CSS, shadcn/ui
- **Use Case**: Interactive web demos and prototypes in Claude chat
- **Pattern**: Modern frontend stack with component libraries

#### test-driven-development (Superpowers)
- **Repository**: https://github.com/obra/superpowers/tree/main/skills/test-driven-development
- **Purpose**: Use when implementing any feature or bugfix, before writing implementation code
- **Workflow**: Test-first development methodology
- **Trigger**: Before writing implementation code
- **Pattern**: TDD workflow automation

#### using-git-worktrees (Superpowers)
- **Repository**: https://github.com/obra/superpowers/blob/main/skills/using-git-worktrees
- **Purpose**: Creates isolated git worktrees with smart directory selection and safety verification
- **Use Case**: Parallel development branches without switching contexts
- **Pattern**: Advanced git workflow management

#### finishing-a-development-branch (Superpowers)
- **Repository**: https://github.com/obra/superpowers/tree/main/skills/finishing-a-development-branch
- **Purpose**: Guides completion of development work by presenting clear options and handling chosen workflow
- **Use Case**: PR creation, branch merging, cleanup
- **Pattern**: Workflow decision tree with guided options

#### pypict-claude-skill
- **Author**: [@omkamal](https://github.com/omkamal)
- **Repository**: https://github.com/omkamal/pypict-claude-skill
- **Purpose**: Design comprehensive test cases using PICT (Pairwise Independent Combinatorial Testing)
- **Technique**: Generates optimized test suites with pairwise coverage
- **Use Case**: Requirements or code test case generation
- **Pattern**: Combinatorial testing methodology

#### aws-skills
- **Author**: [@zxkane](https://github.com/zxkane)
- **Repository**: https://github.com/zxkane/aws-skills
- **Purpose**: AWS development with CDK best practices, cost optimization MCP servers, serverless/event-driven architecture patterns
- **Coverage**: CDK patterns, cost optimization, serverless architecture
- **Use Case**: AWS infrastructure as code
- **Pattern**: Cloud platform specialization with MCP integration

#### claude-starter ⭐
- **Author**: [@raintree-technology](https://github.com/raintree-technology)
- **Repository**: https://github.com/raintree-technology/claude-starter
- **Purpose**: Production-ready Claude Code configuration template
- **Features**:
  - 40 auto-activating skills across 8 domains
  - TOON format support for 30-60% token savings
  - Native Zig encoder/decoder
- **Use Case**: Enterprise Claude Code deployment
- **Pattern**: Multi-domain skill orchestration with token optimization

**TOON Format Innovation**:
- 30-60% token savings through efficient encoding
- Native Zig implementation for performance
- Production-tested across 40 skills

#### move-code-quality-skill
- **Author**: [@1NickPappas](https://github.com/1NickPappas)
- **Repository**: https://github.com/1NickPappas/move-code-quality-skill
- **Purpose**: Analyzes Move language packages against official Move Book Code Quality Checklist
- **Target**: Move 2024 Edition compliance and best practices
- **Use Case**: Smart contract quality assurance
- **Pattern**: Language-specific quality checklist automation

#### claude-code-terminal-title
- **Author**: [@bluzername](https://github.com/bluzername)
- **Repository**: https://github.com/bluzername/claude-code-terminal-title
- **Purpose**: Gives each Claude Code terminal window a dynamic title describing work being done
- **Use Case**: Managing multiple concurrent Claude Code sessions
- **Pattern**: Developer experience enhancement

#### plugin-authoring
- **Author**: [@ivan-magda](https://github.com/ivan-magda)
- **Repository**: https://github.com/ivan-magda/claude-code-plugin-template
- **Purpose**: Ambient guidance for creating, modifying, and debugging Claude Code plugins
- **Features**: Schemas, templates, validation workflows, troubleshooting
- **Use Case**: Claude Code plugin development
- **Pattern**: Meta-skill for plugin ecosystem

---

### 3. Data & Analysis (3 Skills)

#### root-cause-tracing (Superpowers)
- **Repository**: https://github.com/obra/superpowers/tree/main/skills/root-cause-tracing
- **Purpose**: Trace back from deep execution errors to find original trigger
- **Trigger**: Errors deep in execution stack
- **Use Case**: Complex debugging scenarios
- **Pattern**: Systematic error tracing methodology

#### csv-data-summarizer-claude-skill
- **Author**: [@coffeefuelbump](https://github.com/coffeefuelbump)
- **Repository**: https://github.com/coffeefuelbump/csv-data-summarizer-claude-skill
- **Purpose**: Automatically analyzes CSVs: columns, distributions, missing data, correlations
- **Analysis**: Statistical summaries and data quality checks
- **Use Case**: Exploratory data analysis
- **Pattern**: Automated data profiling

#### postgres
- **Author**: [@sanjay3290](https://github.com/sanjay3290)
- **Repository**: https://github.com/sanjay3290/ai-skills/tree/main/skills/postgres
- **Purpose**: Execute safe read-only SQL queries against PostgreSQL databases
- **Features**: Multi-connection support, defense-in-depth security
- **Use Case**: Database exploration and analysis
- **Pattern**: Safe data access with security constraints

---

### 4. Scientific & Research Tools (3 Skills)

#### claude-scientific-skills ⭐⭐⭐
- **Author**: [@K-Dense-AI](https://github.com/K-Dense-AI)
- **Repository**: https://github.com/K-Dense-AI/claude-scientific-skills
- **Purpose**: 125+ scientific skills for bioinformatics, cheminformatics, clinical research, and machine learning
- **Domains**:
  - Bioinformatics (sequence analysis, protein structure)
  - Cheminformatics (molecular modeling, drug discovery)
  - Clinical research (trial design, data analysis)
  - Machine learning (model training, evaluation)
- **Use Case**: Scientific computing and research automation
- **Pattern**: Massive domain-specific skill collection

**Significance**: Demonstrates how to build comprehensive domain libraries (125+ skills)

#### materials-simulation-skills
- **Author**: [@HeshamFS](https://github.com/HeshamFS)
- **Repository**: https://github.com/HeshamFS/materials-simulation-skills
- **Purpose**: Agent skills for computational materials science
- **Coverage**:
  - Numerical stability and time-stepping
  - Linear solvers and mesh generation
  - Simulation validation
  - Parameter optimization and post-processing
- **Use Case**: Materials science simulations
- **Pattern**: Domain-specific computational workflow

#### deep-research
- **Author**: [@sanjay3290](https://github.com/sanjay3290)
- **Repository**: https://github.com/sanjay3290/ai-skills/tree/main/skills/deep-research
- **Purpose**: Execute autonomous multi-step research using Gemini Deep Research Agent
- **Capabilities**: Market analysis, competitive landscaping, literature reviews
- **Use Case**: Automated research workflows
- **Pattern**: Multi-agent research orchestration (Claude + Gemini)

---

### 5. Writing & Research (5 Skills)

#### article-extractor (Tapestry)
- **Author**: [@michalparkola](https://github.com/michalparkola)
- **Repository**: https://github.com/michalparkola/tapestry-skills-for-claude-code/tree/main/article-extractor
- **Purpose**: Extract full article text and metadata from web pages
- **Use Case**: Web content extraction for analysis
- **Pattern**: Web scraping with metadata extraction

#### content-research-writer
- **Author**: [@ComposioHQ](https://github.com/ComposioHQ)
- **Repository**: https://github.com/ComposioHQ/awesome-claude-skills/tree/master/content-research-writer
- **Purpose**: Assists in writing high-quality content
- **Features**: Research, citations, hooks, outlines, real-time section feedback
- **Use Case**: Content creation with research integration
- **Pattern**: Writing workflow with research orchestration

#### internal-comms (Anthropic Official)
- **Repository**: https://github.com/anthropics/skills/tree/main/skills/internal-comms
- **Purpose**: Create internal communications
- **Types**: Status reports, leadership updates, newsletters, FAQs, incident reports, project updates
- **Use Case**: Corporate communication templates
- **Pattern**: Template-based communication with tone consistency

#### brainstorming (Superpowers)
- **Repository**: https://github.com/obra/superpowers/tree/main/skills/brainstorming
- **Purpose**: Transform rough ideas into fully-formed designs
- **Method**: Structured questioning and alternative exploration
- **Use Case**: Ideation and design thinking
- **Pattern**: Socratic questioning methodology

#### family-history-research
- **Author**: [@emaynard](https://github.com/emaynard)
- **Repository**: https://github.com/emaynard/claude-family-history-research-skill
- **Purpose**: Assistance with planning family history and genealogy research projects
- **Use Case**: Genealogy and historical research
- **Pattern**: Research planning and organization

---

### 6. Learning & Knowledge (2 Skills)

#### tapestry
- **Author**: [@michalparkola](https://github.com/michalparkola)
- **Repository**: https://github.com/michalparkola/tapestry-skills-for-claude-code/tree/main/tapestry
- **Purpose**: Interlink and summarize related documents into knowledge networks
- **Use Case**: Building knowledge graphs from documents
- **Pattern**: Networked knowledge management

#### ship-learn-next
- **Author**: [@michalparkola](https://github.com/michalparkola)
- **Repository**: https://github.com/michalparkola/tapestry-skills-for-claude-code/tree/main/ship-learn-next
- **Purpose**: Iterate on what to build or learn next, based on feedback loops
- **Use Case**: Continuous learning and project prioritization
- **Pattern**: Feedback loop-driven decision making

---

### 7. Media & Content (5 Skills)

#### youtube-transcript (Tapestry)
- **Author**: [@michalparkola](https://github.com/michalparkola)
- **Repository**: https://github.com/michalparkola/tapestry-skills-for-claude-code/tree/main/youtube-transcript
- **Purpose**: Fetch transcripts from YouTube videos and prepare summaries
- **Use Case**: Video content analysis
- **Pattern**: Transcript extraction and summarization

#### video-downloader
- **Author**: [@ComposioHQ](https://github.com/ComposioHQ)
- **Repository**: https://github.com/ComposioHQ/awesome-claude-skills/tree/master/video-downloader
- **Purpose**: Downloads videos from YouTube and other platforms
- **Use Case**: Offline viewing, editing, archival
- **Pattern**: Multi-platform media download

#### image-enhancer
- **Author**: [@ComposioHQ](https://github.com/ComposioHQ)
- **Repository**: https://github.com/ComposioHQ/awesome-claude-skills/tree/master/image-enhancer
- **Purpose**: Improves the quality of images, especially screenshots
- **Use Case**: Image quality enhancement for documentation
- **Pattern**: AI-powered image processing

#### imagen
- **Author**: [@sanjay3290](https://github.com/sanjay3290)
- **Repository**: https://github.com/sanjay3290/ai-skills/tree/main/skills/imagen
- **Purpose**: Generate images using Google Gemini's image generation API
- **Use Case**: UI mockups, icons, visual assets
- **Pattern**: Multi-model integration (Claude + Gemini)

#### claude-epub-skill
- **Author**: [@smerchek](https://github.com/smerchek)
- **Repository**: https://github.com/smerchek/claude-epub-skill
- **Purpose**: Parse and analyze EPUB ebook contents
- **Use Case**: Ebook querying and summarization
- **Pattern**: Structured document parsing

---

### 8. Health & Life Sciences (1 Skill)

#### claude-ally-health
- **Author**: [@huifer](https://github.com/huifer)
- **Repository**: https://github.com/huifer/Claude-Ally-Health
- **Purpose**: Comprehensive health assistant
- **Features**: Medical report analysis, health metrics tracking, personalized wellness suggestions
- **Use Case**: Personal health management
- **Pattern**: Domain-specific health data analysis

---

### 9. Collaboration & Project Management (6 Skills)

#### git-pushing
- **Author**: [@mhattingpete](https://github.com/mhattingpete)
- **Repository**: https://github.com/mhattingpete/claude-skills-marketplace
- **Purpose**: Automate git operations and repository interactions
- **Use Case**: Git workflow automation
- **Pattern**: Git command orchestration

#### linear-claude-skill
- **Author**: [@wrsmith108](https://github.com/wrsmith108)
- **Repository**: https://github.com/wrsmith108/linear-claude-skill
- **Purpose**: Manage Linear issues, projects, and teams
- **Integration**: MCP tools, SDK scripts, GraphQL fallbacks
- **Use Case**: Project tracking and issue management
- **Pattern**: Multi-layer API integration (MCP → SDK → GraphQL)

#### linear-cli-skill
- **Author**: [@Valian](https://github.com/Valian)
- **Repository**: https://github.com/Valian/linear-cli-skill
- **Purpose**: Teaching Claude how to use linear-CLI
- **Note**: Meant to replace linear MCP
- **Use Case**: Linear CLI automation
- **Pattern**: CLI wrapper skill (includes CLI tool)

#### meeting-insights-analyzer
- **Author**: [@ComposioHQ](https://github.com/ComposioHQ)
- **Repository**: https://github.com/ComposioHQ/awesome-claude-skills/blob/master/meeting-insights-analyzer
- **Purpose**: Transforms meeting transcripts into actionable insights about communication patterns
- **Use Case**: Meeting analysis and feedback
- **Pattern**: Transcript analysis with behavioral insights

#### review-implementing
- **Author**: [@mhattingpete](https://github.com/mhattingpete)
- **Repository**: https://github.com/mhattingpete/claude-skills-marketplace
- **Purpose**: Evaluate code implementation plans and align with specs
- **Use Case**: Code review automation
- **Pattern**: Specification alignment checking

#### test-fixing
- **Author**: [@mhattingpete](https://github.com/mhattingpete)
- **Repository**: https://github.com/mhattingpete/claude-skills-marketplace
- **Purpose**: Detect failing tests and propose patches or fixes
- **Use Case**: Test maintenance automation
- **Pattern**: Test failure diagnosis and remediation

---

### 10. Security & Web Testing (5 Skills)

#### defense-in-depth (Superpowers)
- **Repository**: https://github.com/obra/superpowers/blob/main/skills/defense-in-depth
- **Purpose**: Implement multi-layered testing and security best practices
- **Use Case**: Security hardening
- **Pattern**: Layered security approach

#### ffuf_claude_skill
- **Author**: [@jthack](https://github.com/jthack)
- **Repository**: https://github.com/jthack/ffuf_claude_skill
- **Purpose**: Integrate Claude with FFUF (fuzzing) and analyze results for vulnerabilities
- **Use Case**: Security fuzzing and vulnerability detection
- **Pattern**: Security tool integration

#### systematic-debugging (Superpowers)
- **Repository**: https://github.com/obra/superpowers/blob/main/skills/systematic-debugging
- **Purpose**: Use when encountering any bug, test failure, or unexpected behavior
- **Trigger**: Before proposing fixes
- **Use Case**: Structured debugging methodology
- **Pattern**: Systematic investigation workflow

#### varlock-claude-skill
- **Author**: [@wrsmith108](https://github.com/wrsmith108)
- **Repository**: https://github.com/wrsmith108/varlock-claude-skill
- **Purpose**: Secure environment variable management
- **Security**: Ensures secrets never appear in Claude sessions, terminals, logs, or git commits
- **Use Case**: Secret management in development
- **Pattern**: Security-first environment variable handling

#### webapp-testing (Anthropic Official)
- **Repository**: https://github.com/anthropics/skills/tree/main/skills/webapp-testing
- **Purpose**: Toolkit for interacting with and testing local web applications using Playwright
- **Use Case**: Automated web application testing
- **Pattern**: Playwright automation

**See**: [ANTHROPIC_SKILLS_GUIDE.md](./ANTHROPIC_SKILLS_GUIDE.md) for complete documentation

---

### 11. Utility & Automation (5 Skills)

#### file-organizer
- **Author**: [@ComposioHQ](https://github.com/ComposioHQ)
- **Repository**: https://github.com/ComposioHQ/awesome-claude-skills/tree/master/file-organizer
- **Purpose**: Intelligently organizes files and folders across your computer
- **Use Case**: File system organization automation
- **Pattern**: Intelligent file categorization

#### invoice-organizer
- **Author**: [@ComposioHQ](https://github.com/ComposioHQ)
- **Repository**: https://github.com/ComposioHQ/awesome-claude-skills/blob/master/invoice-organizer
- **Purpose**: Automatically organizes invoices and receipts for tax preparation
- **Use Case**: Financial document management
- **Pattern**: Document categorization and organization

#### skill-creator (Anthropic Official)
- **Repository**: https://github.com/anthropics/skills/tree/main/skills/skill-creator
- **Purpose**: Template/helper to build new Claude skills
- **Use Case**: Skill development
- **Pattern**: Meta-skill for skill creation

**See**: [ANTHROPIC_SKILLS_GUIDE.md](./ANTHROPIC_SKILLS_GUIDE.md) for complete 6-step process

#### template-skill (Anthropic Official)
- **Repository**: https://github.com/anthropics/skills/tree/main/template
- **Purpose**: Minimal skeleton for a new skill project structure
- **Use Case**: Quick skill scaffolding
- **Pattern**: Basic skill template

#### PinMe (Deployment)
- **Author**: [@glitternetwork](https://github.com/glitternetwork)
- **Repository**: https://github.com/glitternetwork/skills/tree/main/pinme
- **Purpose**: Zero-config frontend deployment tool
- **Features**: No servers, no accounts, no setup
- **Use Case**: Instant frontend deployment
- **Pattern**: Frictionless deployment automation

---

## Key Patterns from Community Skills

### 1. Multi-Model Integration

**Pattern**: Skills that orchestrate multiple AI models

**Examples**:
- **deep-research**: Claude + Gemini Deep Research Agent
- **imagen**: Claude + Gemini image generation

**Application**: Combine strengths of different models for specialized tasks

### 2. Domain-Specific Skill Collections

**Pattern**: Comprehensive skill sets for specialized domains

**Examples**:
- **claude-scientific-skills**: 125+ skills for bioinformatics, cheminformatics, clinical research
- **materials-simulation-skills**: Computational materials science workflows
- **claude-starter**: 40 auto-activating skills across 8 domains

**Application**: Build deep expertise in specific industries or research areas

### 3. CLI Tool Wrapper Skills

**Pattern**: Skills that teach Claude to use existing CLI tools

**Examples**:
- **linear-cli-skill**: Includes linear-CLI tool
- **ffuf_claude_skill**: Integrates FFUF fuzzing tool

**Application**: Leverage existing command-line tools through Claude interface

### 4. Multi-Layer API Integration

**Pattern**: Fallback layers for API access (MCP → SDK → GraphQL → REST)

**Examples**:
- **linear-claude-skill**: MCP tools, SDK scripts, GraphQL fallbacks

**Application**: Ensure reliable API access with multiple fallback options

### 5. Token Optimization Innovations

**Pattern**: Novel encoding/compression for context efficiency

**Examples**:
- **claude-starter**: TOON format (30-60% token savings) with native Zig encoder

**Application**: Maximize context window utilization for complex skills

### 6. Security-First Skills

**Pattern**: Skills designed with security constraints

**Examples**:
- **varlock-claude-skill**: Secret management
- **postgres**: Read-only queries with defense-in-depth
- **defense-in-depth**: Multi-layered security

**Application**: Safe automation with security guardrails

### 7. Workflow Orchestration

**Pattern**: Skills that guide multi-step processes

**Examples**:
- **finishing-a-development-branch**: Guided workflow completion
- **test-driven-development**: TDD workflow automation
- **content-research-writer**: Writing with research integration

**Application**: Complex workflow automation with decision trees

---

## Integration with Your Agentic Workflows

### Use Case 1: Scientific Computing Agent

Combine skills for research automation:

```markdown
Skills:
- claude-scientific-skills (125+ bioinformatics/cheminformatics skills)
- deep-research (Gemini research agent integration)
- postgres (database access for results)
- article-extractor (literature extraction)

Workflow:
1. deep-research gathers relevant papers
2. article-extractor extracts full text
3. claude-scientific-skills analyzes data
4. postgres stores results
```

**Result**: Automated scientific research pipeline

### Use Case 2: Development Workflow Automation

Stack skills for complete dev cycle:

```markdown
Skills:
- test-driven-development (TDD workflow)
- systematic-debugging (structured debugging)
- using-git-worktrees (parallel development)
- finishing-a-development-branch (PR workflow)
- varlock-claude-skill (secret management)

Workflow:
1. TDD guides test-first development
2. systematic-debugging handles issues
3. git-worktrees enables parallel work
4. finishing-a-development-branch completes PR
5. varlock ensures security
```

**Result**: Complete, secure development workflow

### Use Case 3: Content Production Pipeline

Combine media and writing skills:

```markdown
Skills:
- youtube-transcript (extract video content)
- article-extractor (web content extraction)
- content-research-writer (writing with citations)
- image-enhancer (improve screenshots)
- tapestry (knowledge network)

Workflow:
1. Extract content from videos and articles
2. Research and write with citations
3. Enhance images for documentation
4. Build knowledge network
```

**Result**: Multi-source content production with research

### Use Case 4: Project Management Automation

Orchestrate collaboration tools:

```markdown
Skills:
- linear-claude-skill (issue tracking)
- meeting-insights-analyzer (meeting analysis)
- git-pushing (repo operations)
- review-implementing (code review)
- test-fixing (test maintenance)

Workflow:
1. meeting-insights extracts action items
2. linear-claude-skill creates issues
3. Code review with review-implementing
4. test-fixing maintains test suite
5. git-pushing automates git ops
```

**Result**: Automated project coordination

---

## Installation

### Method 1: Individual Skill Installation

Clone specific skills you need:

```bash
# Example: Clone scientific skills
git clone https://github.com/K-Dense-AI/claude-scientific-skills ~/.claude/skills/scientific-skills

# Example: Clone Linear integration
git clone https://github.com/wrsmith108/linear-claude-skill ~/.claude/skills/linear-claude-skill
```

### Method 2: Browse and Select

1. Visit https://github.com/BehiSecc/awesome-claude-skills
2. Find relevant skills for your use case
3. Follow individual repository installation instructions

### Method 3: Production Template

Use claude-starter for enterprise deployment:

```bash
git clone https://github.com/raintree-technology/claude-starter
# Follow setup instructions for 40-skill deployment with TOON format
```

---

## Notable Community Contributors

### @obra - Superpowers Collection
- test-driven-development
- systematic-debugging
- defense-in-depth
- brainstorming
- root-cause-tracing
- finishing-a-development-branch
- using-git-worktrees

**Focus**: Engineering best practices and development workflows

### @michalparkola - Tapestry Skills
- tapestry (knowledge networks)
- article-extractor
- youtube-transcript
- ship-learn-next

**Focus**: Knowledge management and learning workflows

### @ComposioHQ - Utility Skills
- content-research-writer
- file-organizer
- invoice-organizer
- video-downloader
- image-enhancer
- meeting-insights-analyzer

**Focus**: Productivity automation and content tools

### @sanjay3290 - AI Integration
- deep-research (Gemini integration)
- imagen (Gemini image generation)
- postgres (database access)

**Focus**: Multi-model AI orchestration

### @K-Dense-AI - Scientific Computing
- claude-scientific-skills (125+ skills)

**Focus**: Scientific research automation

### @raintree-technology - Enterprise
- claude-starter (40-skill production template with TOON)

**Focus**: Enterprise deployment and token optimization

---

## Key Takeaways

1. **Community Innovation** - 50+ skills demonstrate diverse use cases beyond official offerings
2. **Domain Specialization** - Deep skill collections (125+ scientific skills) show scalability
3. **Multi-Model Integration** - Skills orchestrate Claude with Gemini, external APIs, and tools
4. **Token Optimization** - TOON format innovation (30-60% savings) improves efficiency
5. **Security Patterns** - Multiple security-focused skills provide production safety
6. **Workflow Orchestration** - Skills guide complex multi-step processes with decision trees
7. **CLI Integration** - Wrapper skills leverage existing command-line tools
8. **Real-World Solutions** - Community skills solve actual production problems across industries

---

## Resources

- **Repository**: `references/awesome-claude-skills/`
- **Catalog**: https://github.com/BehiSecc/awesome-claude-skills
- **Curator**: [@Behi_Sec](https://x.com/Behi_Sec)
- **Agent Skills Spec**: https://agentskills.io/specification
- **Contribution**: Fork, improve, submit PR to awesome-claude-skills

---

**The awesome-claude-skills catalog showcases the breadth of community innovation. From 125+ scientific skills to TOON format optimization, it demonstrates what's possible when developers build domain-specific solutions with the Agent Skills specification.**
