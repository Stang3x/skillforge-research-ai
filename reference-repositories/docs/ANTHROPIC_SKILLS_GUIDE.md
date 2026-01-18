# Anthropic Official Skills - Production-Ready Skills for Claude

**Reference**: `references/anthropic-skills/`
**Source**: https://github.com/anthropics/skills
**Standard**: [Agent Skills Specification](https://agentskills.io/specification)

## Overview

The Anthropic skills repository contains **official, production-ready skills** that demonstrate what's possible with Claude's skills system. These skills power Claude's document capabilities and showcase best practices for skill development across creative, technical, and enterprise domains.

This repository is unique because it includes:
- **Source-available document skills** (DOCX, PDF, PPTX, XLSX) that power Claude.ai
- **Example skills** demonstrating patterns across multiple domains
- **Official skill creation guidance** from Anthropic
- **Agent Skills specification** (agentskills.io)

## Why Anthropic Skills for Agentic Workflows?

These skills represent **production-tested patterns** for:
1. **Building complex skills** - Document skills show how to handle intricate formats
2. **Progressive disclosure** - Multi-level loading system for context efficiency
3. **Bundled resources** - Scripts, references, and assets organization
4. **MCP server development** - mcp-builder skill teaches server creation
5. **Testing methodologies** - webapp-testing demonstrates Playwright integration
6. **Skill creation meta-skill** - skill-creator teaches how to build effective skills

## Skill Categories

### 1. Document Skills (Production, Source-Available)

These are the **actual skills** that power Claude's document capabilities.

#### DOCX Skill
**Location**: `skills/docx/`
**Purpose**: Create, edit, and analyze Microsoft Word documents
**License**: Source-available (not open source)

**Capabilities**:
- Create new documents with formatting
- Edit existing documents preserving structure
- Work with tracked changes (redlining)
- Add and manage comments
- Extract text and analyze content
- Handle complex OOXML structures

**Key Learnings**:
- Progressive disclosure with reference files
- Handling complex file formats (OOXML)
- Scripts for deterministic operations
- Template-based document creation

#### PDF Skill
**Location**: `skills/pdf/`
**Purpose**: PDF creation, editing, extraction, and form filling
**License**: Source-available (not open source)

**Capabilities**:
- Extract text and metadata from PDFs
- Create new PDFs from content
- Fill PDF forms programmatically
- Merge and split PDFs
- Extract images and embedded content
- Read form fields

**Key Learnings**:
- Multiple library integration (pdfplumber, PyPDF2, reportlab)
- Form field handling patterns
- Extraction vs creation workflows
- Binary file manipulation

#### PPTX Skill
**Location**: `skills/pptx/`
**Purpose**: PowerPoint presentation creation and editing
**License**: Source-available (not open source)

**Capabilities**:
- Create presentations from scratch
- Edit existing presentations
- Manage slides, layouts, and themes
- Add charts, images, and shapes
- Apply consistent branding
- Extract content from presentations

**Key Learnings**:
- Template-based slide generation
- Visual design automation
- Asset management (fonts, images)
- XML-based format handling

#### XLSX Skill
**Location**: `skills/xlsx/`
**Purpose**: Excel spreadsheet creation, editing, and analysis
**License**: Source-available (not open source)

**Capabilities**:
- Create spreadsheets with formulas
- Edit and update existing workbooks
- Read and analyze data
- Create charts and visualizations
- Format cells and ranges
- Handle multiple sheets

**Key Learnings**:
- Spreadsheet formula generation
- Data structure preservation
- Chart and visualization patterns
- Multi-sheet coordination

---

### 2. Creative & Design Skills (Open Source)

#### Algorithmic Art
**Location**: `skills/algorithmic-art/`
**Purpose**: Generate algorithmic and generative art

**Use Cases**:
- Procedural art generation
- SVG-based graphics
- Mathematical visualizations
- Creative coding projects

**Pattern**: Creative constraints with code generation

#### Canvas Design
**Location**: `skills/canvas-design/`
**Purpose**: Create design artifacts using Claude's canvas feature

**Use Cases**:
- Visual design creation
- Layout prototyping
- Design iteration workflows

**Pattern**: Visual creation within chat interface

#### Theme Factory
**Location**: `skills/theme-factory/`
**Purpose**: Generate consistent design themes and color palettes

**Use Cases**:
- Brand color generation
- Theme customization
- Design system creation

**Pattern**: Template-based generation with variations

---

### 3. Development & Technical Skills (Open Source)

#### MCP Builder ⭐
**Location**: `skills/mcp-builder/`
**Purpose**: Guide for creating high-quality MCP servers
**License**: Open source (Apache 2.0)

**Complete MCP Server Development Workflow**:

**Phase 1: Deep Research and Planning**
1. Understand modern MCP design principles
   - API coverage vs workflow tools balance
   - Tool naming and discoverability
   - Context management for agents
   - Actionable error messages
2. Study MCP protocol documentation (modelcontextprotocol.io)
3. Study framework documentation (TypeScript/Python SDKs)
4. Plan implementation (tool selection, API endpoints)

**Phase 2: Implementation**
1. Set up project structure (TypeScript recommended)
2. Implement core infrastructure
   - API client with authentication
   - Error handling helpers
   - Response formatting (JSON/Markdown)
   - Pagination support
3. Implement tools
   - Input schema (Zod/Pydantic)
   - Output schema with structuredContent
   - Tool descriptions and annotations
   - Async/await operations

**Phase 3: Review and Test**
1. Code quality review (DRY, type coverage, error handling)
2. Build and test with MCP Inspector
3. Verify against quality checklists

**Phase 4: Create Evaluations**
1. Understand evaluation purpose (test LLM effectiveness)
2. Create 10 complex evaluation questions
3. Ensure questions are independent, read-only, realistic
4. Verify answers manually
5. Output as XML evaluation file

**Recommended Stack**:
- **Language**: TypeScript (better SDK, static typing, good linting)
- **Transport**: Streamable HTTP (stateless, scalable)
- **Frameworks**: TypeScript SDK, FastMCP (Python)

**Reference Files Included**:
- `reference/mcp_best_practices.md` - Universal MCP guidelines
- `reference/node_mcp_server.md` - TypeScript implementation guide
- `reference/python_mcp_server.md` - Python/FastMCP guide
- `reference/evaluation.md` - Evaluation creation guide

**Key Learnings**:
- 4-phase MCP development workflow
- Evaluation-driven development
- Quality checklist approach
- Progressive disclosure in documentation

#### Webapp Testing
**Location**: `skills/webapp-testing/`
**Purpose**: Test local web applications using Playwright
**License**: Open source (Apache 2.0)

**Capabilities**:
- Verify frontend functionality
- Debug UI behavior
- Capture browser screenshots
- View browser console logs
- Manage server lifecycle

**Decision Tree Workflow**:
```
Is it static HTML?
├─ Yes → Read HTML directly, write Playwright script
└─ No (dynamic) → Is server running?
   ├─ No → Use with_server.py helper script
   └─ Yes → Reconnaissance-then-action pattern
```

**Reconnaissance-Then-Action Pattern**:
1. Navigate and wait for `networkidle`
2. Take screenshot or inspect DOM
3. Identify selectors from rendered state
4. Execute actions with discovered selectors

**Helper Scripts**:
- `scripts/with_server.py` - Manages server lifecycle (single or multiple servers)

**Key Learnings**:
- Black-box script usage (avoid context pollution)
- Reconnaissance before action pattern
- Server lifecycle management
- Wait strategies for dynamic content

#### Web Artifacts Builder
**Location**: `skills/web-artifacts-builder/`
**Purpose**: Build interactive web artifacts and demos

**Use Cases**:
- Rapid prototyping
- Interactive demonstrations
- Single-file web apps

**Pattern**: Self-contained HTML artifacts with embedded JS/CSS

#### Frontend Design
**Location**: `skills/frontend-design/`
**Purpose**: Design and prototype frontend interfaces

**Use Cases**:
- UI/UX prototyping
- Component design
- Layout exploration

**Pattern**: Asset-based templates with customization

---

### 4. Enterprise & Communication Skills (Open Source)

#### Brand Guidelines
**Location**: `skills/brand-guidelines/`
**Purpose**: Apply consistent brand guidelines to outputs

**Use Cases**:
- Brand-consistent document creation
- Marketing material generation
- Corporate communication

**Pattern**: Asset-based branding (logos, colors, fonts)

#### Doc Co-authoring
**Location**: `skills/doc-coauthoring/`
**Purpose**: Collaborative document creation workflows

**Use Cases**:
- Multi-author document workflows
- Review and feedback cycles
- Version control for documents

**Pattern**: Workflow-based collaborative editing

#### Internal Comms
**Location**: `skills/internal-comms/`
**Purpose**: Create internal communications following company standards

**Use Cases**:
- Email templates
- Announcements
- Internal documentation

**Pattern**: Template-based communication with tone/style guidance

#### Slack GIF Creator
**Location**: `skills/slack-gif-creator/`
**Purpose**: Create custom GIFs for Slack communication

**Use Cases**:
- Team communication enhancement
- Visual responses
- Custom reactions

**Pattern**: Creative generation with specific output format

---

### 5. Meta Skill: Skill Creator ⭐⭐⭐

**Location**: `skills/skill-creator/`
**Purpose**: Comprehensive guide for creating effective skills
**License**: Open source (Apache 2.0)

This is the **most important skill** for learning skill development.

#### Core Principles

**1. Concise is Key**
- Context window is a public good
- Default assumption: Claude is already smart
- Only add context Claude doesn't have
- Prefer examples over verbose explanations

**2. Set Appropriate Degrees of Freedom**
- **High freedom** (text instructions): Multiple valid approaches, context-dependent
- **Medium freedom** (pseudocode): Preferred pattern exists, some variation allowed
- **Low freedom** (specific scripts): Fragile operations, consistency critical

**3. Anatomy of a Skill**
```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/          - Executable code
    ├── references/       - Documentation loaded as needed
    └── assets/           - Files used in output
```

#### Progressive Disclosure System

**Three-level loading**:
1. **Metadata** (name + description) - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words, ideally <500 lines)
3. **Bundled resources** - As needed by Claude (unlimited)

#### Progressive Disclosure Patterns

**Pattern 1: High-level guide with references**
```markdown
# PDF Processing

## Quick start
[Core example]

## Advanced features
- **Form filling**: See [FORMS.md](FORMS.md)
- **API reference**: See [REFERENCE.md](REFERENCE.md)
```

**Pattern 2: Domain-specific organization**
```
bigquery-skill/
├── SKILL.md (overview + navigation)
└── reference/
    ├── finance.md
    ├── sales.md
    └── product.md
```

**Pattern 3: Conditional details**
```markdown
## Editing documents
For simple edits, modify XML directly.

**For tracked changes**: See [REDLINING.md](REDLINING.md)
```

#### Skill Creation Process (6 Steps)

**Step 1: Understand with Concrete Examples**
- Gather real usage examples
- Ask: "What should this skill support?"
- Ask: "Can you give examples of how this would be used?"
- Ask: "What would trigger this skill?"

**Step 2: Plan Reusable Contents**
For each example, identify:
- **Scripts**: Code that's repeatedly rewritten
- **References**: Documentation to load as needed
- **Assets**: Files used in output (templates, images)

**Step 3: Initialize the Skill**
```bash
scripts/init_skill.py <skill-name> --path <output-directory>
```

Creates:
- SKILL.md template with frontmatter
- Example resource directories
- Placeholder files

**Step 4: Edit the Skill**

**Learn Proven Patterns**:
- Multi-step processes → `references/workflows.md`
- Output formats/quality → `references/output-patterns.md`

**Start with Resources**:
- Implement scripts, references, assets first
- Test scripts by running them
- Delete unused example files

**Update SKILL.md**:
- Frontmatter: `name` and `description`
- Description is primary trigger mechanism
- Include "when to use" in description
- Body: Instructions for using the skill

**Step 5: Package the Skill**
```bash
scripts/package_skill.py <path/to/skill-folder>
```

Automatically:
1. Validates (frontmatter, naming, structure, references)
2. Packages as .skill file (zip with .skill extension)

**Step 6: Iterate**
1. Use skill on real tasks
2. Notice struggles/inefficiencies
3. Update SKILL.md or resources
4. Test again

#### What NOT to Include

Do NOT create:
- README.md
- INSTALLATION_GUIDE.md
- QUICK_REFERENCE.md
- CHANGELOG.md
- Any extraneous documentation

Skills should only contain what AI agents need to do the job.

#### Bundled Resources Deep Dive

**Scripts** (`scripts/`):
- Executable code (Python/Bash)
- When: Repeatedly rewritten code, need deterministic reliability
- Benefits: Token efficient, may execute without loading to context
- Example: `scripts/rotate_pdf.py` for PDF rotation

**References** (`references/`):
- Documentation loaded as needed
- When: Claude should reference while working
- Examples: Database schemas, API docs, company policies
- Benefits: Keeps SKILL.md lean, loaded only when needed
- Best practice: If >10k words, include grep search patterns in SKILL.md
- Avoid duplication: Info lives in SKILL.md OR references, not both

**Assets** (`assets/`):
- Files used in output (not loaded to context)
- When: Resources needed in final output
- Examples: Logos, templates, boilerplate, fonts
- Use cases: Templates, images, icons, sample documents
- Benefits: Separate output resources from documentation

---

## Installation

### Method 1: Marketplace (Recommended)

```bash
# Add marketplace
/plugin marketplace add anthropics/skills

# Install document skills (DOCX, PDF, PPTX, XLSX)
/plugin install document-skills@anthropic-agent-skills

# Install example skills (all open source skills)
/plugin install example-skills@anthropic-agent-skills
```

### Method 2: Manual Installation

```bash
# Already cloned in references
cd references/anthropic-skills

# Copy specific skills to Claude Code skills directory
cp -r skills/mcp-builder ~/.claude/skills/
cp -r skills/skill-creator ~/.claude/skills/
cp -r skills/webapp-testing ~/.claude/skills/
```

### Method 3: Use in Claude.ai

All example skills are already available to paid plans in Claude.ai. Upload custom skills following [Using skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude).

---

## Integration with Agentic Workflows

### Use Case 1: Building MCP Servers for Agents

Use the **mcp-builder** skill to create custom MCP servers:

```markdown
"Use the mcp-builder skill to create an MCP server for the Notion API"

Skills activate:
- mcp-builder guides through 4-phase development
- Provides TypeScript/Python implementation patterns
- Creates evaluation tests
```

**Result**: Production-ready MCP server with evaluations

### Use Case 2: Testing Agent Web Interfaces

Use **webapp-testing** for agent UI verification:

```markdown
"Use the webapp-testing skill to verify the agent dashboard loads correctly"

Skills activate:
- webapp-testing provides reconnaissance-then-action pattern
- Manages server lifecycle with with_server.py
- Captures screenshots for verification
```

**Result**: Automated UI testing for agent interfaces

### Use Case 3: Creating Custom Skills for Agent Workflows

Use **skill-creator** to build domain-specific skills:

```markdown
"Use the skill-creator skill to build a skill for our agent orchestration workflow"

Skills activate:
- skill-creator guides through 6-step process
- Provides progressive disclosure patterns
- Validates and packages skill
```

**Result**: Custom skill following Anthropic best practices

### Use Case 4: Document Generation for Agent Outputs

Use document skills for agent-generated reports:

```markdown
"Generate a PDF report of agent performance metrics"

Skills activate:
- pdf skill creates structured PDF with charts
- Uses templates from assets/
- Handles formatting and layout
```

**Result**: Professional PDF reports from agent data

---

## Key Patterns to Apply

### 1. Progressive Disclosure (From skill-creator)

**Apply to**: Any documentation or knowledge base

**Pattern**:
- Level 1: Metadata (always visible)
- Level 2: Core content (loaded when relevant)
- Level 3: Detailed references (loaded as needed)

**Example for Agent Documentation**:
```
agent-orchestration/
├── OVERVIEW.md (always loaded)
└── references/
    ├── langgraph-patterns.md
    ├── crewai-patterns.md
    └── autogpt-patterns.md
```

### 2. Bundled Resources (From all document skills)

**Apply to**: Complex agent workflows

**Pattern**:
- Scripts: Reusable automation code
- References: Documentation loaded conditionally
- Assets: Templates and resources for output

**Example for Agent Workflows**:
```
agent-workflow/
├── WORKFLOW.md
├── scripts/
│   ├── spawn_subagent.py
│   └── aggregate_results.py
├── references/
│   ├── state-management.md
│   └── error-handling.md
└── assets/
    └── workflow-templates/
```

### 3. Evaluation-Driven Development (From mcp-builder)

**Apply to**: Testing agent capabilities

**Pattern**:
1. Create 10 complex, realistic questions
2. Verify answers manually
3. Test agent performance
4. Iterate based on failures

**Example for Agent Testing**:
```xml
<evaluation>
  <qa_pair>
    <question>Given the agent loop from AutoGPT, what pattern does it use for task decomposition when faced with ambiguous goals?</question>
    <answer>Hierarchical task network with recursive decomposition</answer>
  </qa_pair>
</evaluation>
```

### 4. Reconnaissance-Then-Action (From webapp-testing)

**Apply to**: Agent exploration tasks

**Pattern**:
1. Observe current state
2. Gather information
3. Identify action targets
4. Execute actions

**Example for Codebase Exploration**:
```python
# 1. Reconnaissance
files = glob_search("**/*.py")
overview = read_file("README.md")

# 2. Identify targets
agent_files = grep_search("class.*Agent", files)

# 3. Execute
for agent_file in agent_files:
    extract_pattern(agent_file)
```

---

## Skill Development Best Practices

### From skill-creator

1. **Conciseness**: Challenge every sentence - "Does Claude really need this?"
2. **Degrees of Freedom**: Match specificity to task fragility
3. **Progressive Disclosure**: Keep SKILL.md under 500 lines, split into references
4. **Testing**: Run scripts to verify they work before packaging
5. **Validation**: Use `package_skill.py` for automatic validation

### From mcp-builder

1. **API Coverage**: Prioritize comprehensive coverage over convenience workflows
2. **Tool Naming**: Use consistent prefixes and action-oriented names
3. **Error Messages**: Make errors actionable with specific next steps
4. **Evaluations**: Create 10 complex questions to test effectiveness
5. **Documentation**: Load framework docs, study best practices

### From webapp-testing

1. **Black-box Scripts**: Use helper scripts without loading to context
2. **Wait Strategies**: Always wait for `networkidle` on dynamic apps
3. **Reconnaissance First**: Inspect before acting on dynamic content
4. **Server Management**: Use helpers for server lifecycle

---

## Resources

- **Repository**: `references/anthropic-skills/`
- **Agent Skills Spec**: https://agentskills.io/specification
- **Claude Skills Docs**: https://support.claude.com/en/articles/12512176-what-are-skills
- **Creating Skills**: https://support.claude.com/en/articles/12512198-creating-custom-skills
- **Engineering Blog**: https://anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills

### Included Skills

**Document Skills (Source-Available)**:
- DOCX - Microsoft Word documents
- PDF - PDF creation and extraction
- PPTX - PowerPoint presentations
- XLSX - Excel spreadsheets

**Development & Technical (Open Source)**:
- ⭐ mcp-builder - MCP server development guide
- ⭐ webapp-testing - Playwright-based testing
- web-artifacts-builder - Interactive web demos
- frontend-design - UI/UX prototyping

**Creative & Design (Open Source)**:
- algorithmic-art - Generative art
- canvas-design - Visual design creation
- theme-factory - Design theme generation

**Enterprise & Communication (Open Source)**:
- brand-guidelines - Consistent branding
- doc-coauthoring - Collaborative workflows
- internal-comms - Corporate communication
- slack-gif-creator - Custom Slack GIFs

**Meta Skill (Open Source)**:
- ⭐⭐⭐ skill-creator - Complete skill development guide

---

## Key Takeaways

1. **Production Patterns**: Document skills show real-world complexity handling
2. **Progressive Disclosure**: 3-level loading system manages context efficiently
3. **MCP Development**: mcp-builder provides complete server development workflow
4. **Skill Creation**: skill-creator teaches Anthropic's official methodology
5. **Bundled Resources**: Scripts, references, assets pattern for complex skills
6. **Evaluation-Driven**: Create 10 complex questions to test effectiveness
7. **Context Efficiency**: Keep SKILL.md under 500 lines, split into references
8. **Black-box Scripts**: Execute without loading to preserve context

---

**The Anthropic skills repository is the authoritative source for production-quality skill development. Study skill-creator and mcp-builder to understand official best practices, then apply these patterns to your agentic workflow development.**
