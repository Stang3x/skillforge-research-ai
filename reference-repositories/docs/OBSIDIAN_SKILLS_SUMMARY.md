# Obsidian Skills - Knowledge Management for Agentic Workflows

**Reference**: `references/obsidian-skills/`
**Source**: https://github.com/kepano/obsidian-skills
**Standard**: [Agent Skills Specification](https://agentskills.io/specification)

## Overview

Obsidian-skills provides **3 complementary skills** that teach Claude Code how to work with Obsidian's knowledge management formats. These skills are valuable for organizing your agentic workflows research, documentation, and pattern extraction.

## Why Obsidian for Agentic Workflows Research?

Obsidian is a powerful knowledge management system built on plain text files, perfect for:
- **Networked Thinking**: Link concepts through wikilinks (e.g., `[[Agent Patterns]]`)
- **Version Control**: Plain text `.md` files work with Git
- **Visual Organization**: Canvas for mapping agent architectures
- **Structured Data**: Frontmatter for metadata and properties
- **Embeds**: Reference patterns and examples across notes

## The 3 Skills

### 1. Obsidian Markdown

**Purpose**: Create and edit Obsidian Flavored Markdown with wikilinks, embeds, callouts

**Key Features for Research**:

**Wikilinks (Internal Linking)**:
```markdown
[[Agent Loop Patterns]]
[[LangGraph#State Management]]
[[CrewAI Architecture|Crew Architecture]]
```

**Embeds (Reference Content)**:
```markdown
![[Pattern Documentation Template]]
![[GET SHIT DONE#Context Engineering]]
![[agent-diagram.png|500]]
```

**Callouts (Highlighted Notes)**:
```markdown
> [!important] Key Insight
> Context management is critical for agent quality

> [!example] LangGraph Pattern
> State graphs enable complex branching logic

> [!warning] Common Pitfall
> Don't let context accumulate - use fresh subagents
```

**Properties (Metadata)**:
```yaml
---
title: Multi-Agent Orchestration Pattern
source: Panel of Claude
date: 2025-01-15
tags:
  - pattern
  - multi-agent
  - orchestration
status: documented
---
```

**Tags**:
```markdown
#pattern/agent-loop
#framework/langgraph
#research/agentic-systems
```

**Task Lists (Track Progress)**:
```markdown
- [x] Clone reference repositories
- [x] Install skills
- [ ] Extract patterns from AutoGPT
  - [ ] Document agent loop
  - [ ] Document memory management
- [ ] Build first agentic workflow
```

---

### 2. Obsidian Bases

**Purpose**: Work with `.base` files (structured data format)

**Use Case**: Structured knowledge bases for agent configurations, patterns catalog

**Example Structure**:
```yaml
# Agent Patterns Database

[[Pattern: Fresh Subagent Execution]]
source: GET SHIT DONE
category: Context Management
description: Execute each task in clean context to avoid degradation
```

---

### 3. JSON Canvas

**Purpose**: Create and edit `.canvas` files (visual node-based documents)

**Use Case**: Visual architecture diagrams for agentic systems

**Applications**:
- Map agent architectures
- Document workflow pipelines
- Visual pattern libraries
- Research concept maps

**Canvas Structure**:
```json
{
  "nodes": [
    {
      "id": "node1",
      "type": "text",
      "text": "Agent Orchestrator",
      "x": 0,
      "y": 0,
      "width": 250,
      "height": 100
    },
    {
      "id": "node2",
      "type": "file",
      "file": "patterns/orchestration.md",
      "x": 300,
      "y": 0
    }
  ],
  "edges": [
    {
      "id": "edge1",
      "fromNode": "node1",
      "toNode": "node2"
    }
  ]
}
```

---

## Installation

### Prerequisites
- Obsidian installed (optional but recommended)
- Claude Code

### Install Skills

**Method 1: Marketplace** (Recommended)
```bash
/plugin marketplace add kepano/obsidian-skills
/plugin install obsidian@obsidian-skills
```

**Method 2: Manual**
```bash
# Already cloned in references
cp -r references/obsidian-skills/skills/* ~/.claude/skills/

# Or add to your Obsidian vault
cp -r references/obsidian-skills/.claude /path/to/your/vault/
```

---

## Integration with Your Workspace

### Recommended Obsidian Vault Structure for Agentic Research

```
Agentic-Workflows-Vault/
├── 00-Inbox/                    # Quick captures
├── 01-Reference-Repos/          # Notes on each repo
│   ├── AutoGPT.md
│   ├── LangGraph.md
│   ├── CrewAI.md
│   └── GET-SHIT-DONE.md
├── 02-Patterns/                 # Extracted patterns
│   ├── Agent-Loop-Patterns.md
│   ├── State-Management.md
│   ├── Context-Engineering.md
│   └── Multi-Agent-Orchestration.md
├── 03-Implementations/          # Your projects
├── 04-Learning-Log/             # Daily notes
├── 05-Resources/                # External links, papers
├── Templates/                   # Note templates
│   ├── Pattern-Template.md
│   ├── Repository-Analysis.md
│   └── Agent-Config-Template.md
└── Canvas/                      # Visual maps
    ├── Agentic-Systems-Map.canvas
    └── Reference-Repos-Overview.canvas
```

### Pattern Documentation Template (Obsidian)

```markdown
---
title: {{pattern-name}}
source: "[[{{source-repo}}]]"
category: {{category}}
date: {{date}}
tags:
  - pattern
  - {{category-tag}}
status: draft
---

# {{pattern-name}}

## Overview

**Source**: [[{{source-repo}}]] - `{{file-path}}:{{line-number}}`

**Purpose**: {{one-sentence-description}}

## Context

When to use this pattern:
- {{use-case-1}}
- {{use-case-2}}

## Implementation

```{{language}}
{{code-example}}
```

## Trade-offs

> [!success] Pros
> - {{benefit-1}}
> - {{benefit-2}}

> [!warning] Cons
> - {{limitation-1}}
> - {{limitation-2}}

## Related Patterns

- [[{{related-pattern-1}}]]
- [[{{related-pattern-2}}]]

## Examples

![[{{reference-repo}}#{{example-section}}]]

## Notes

{{additional-notes}}
```

### Daily Research Log Template

```markdown
---
date: {{date}}
tags:
  - daily-log
  - research
---

# Research Log - {{date}}

## Today's Focus

- [ ] {{task-1}}
- [ ] {{task-2}}

## Repositories Studied

- [[{{repo-name}}]] - {{what-you-learned}}

## Patterns Extracted

- [[{{pattern-name}}]] - {{brief-note}}

## Code Examples

```{{language}}
{{interesting-code-snippet}}
```

## Insights

> [!important] Key Insight
> {{your-insight}}

## Questions

- {{question-1}}
- {{question-2}}

## Tomorrow's Goals

- {{goal-1}}
- {{goal-2}}

## Links

- [[{{related-note}}]]
```

---

## Using Obsidian with Claude Code

### Ask Claude to Create Obsidian Notes

```
"Create an Obsidian note documenting the agent loop pattern from AutoGPT"

Skills activate:
- Obsidian Markdown (formats with wikilinks, callouts, frontmatter)
- Creates properly structured .md file
```

### Build Visual Maps

```
"Create a canvas showing the architecture of GET SHIT DONE's context engineering system"

Skills activate:
- JSON Canvas (creates .canvas file with nodes and connections)
```

### Organize Research

```
"Create a daily research log for today with wikilinks to the patterns I extracted"

Skills activate:
- Obsidian Markdown (creates log with proper linking)
```

---

## Key Patterns to Apply

### 1. Networked Knowledge

Instead of isolated files, create a knowledge graph:

```markdown
# Multi-Agent Orchestration

See also: [[Agent Loop Patterns]], [[State Management]]

Implementations:
- [[Panel of Claude]] - Expert panel simulation
- [[CrewAI]] - Role-based agents
- [[Claude Squad]] - Parallel workspaces

Related concepts: [[Context Engineering]], [[Agent Coordination]]
```

### 2. Progressive Summarization

Use callouts to highlight key insights:

```markdown
> [!tldr] Summary
> Fresh subagent execution prevents context degradation

> [!important] Critical Pattern
> Each task runs in 200k token clean context

> [!example] Implementation
> GET SHIT DONE uses XML-structured tasks
```

### 3. Atomic Notes

One concept per note, heavily linked:

```markdown
# Fresh Subagent Execution

A pattern from [[GET SHIT DONE]] where each task executes in a clean context.

Prevents: [[Context Rot]]
Enables: [[Consistent Quality]]
Implementation: [[Task-Based Agent Spawning]]
```

### 4. MOCs (Maps of Content)

Create index notes linking related content:

```markdown
# Agentic Systems Patterns MOC

## Agent Architecture
- [[Agent Loop Patterns]]
- [[State Management Patterns]]
- [[Multi-Agent Orchestration]]

## Context Management
- [[Context Engineering]]
- [[Fresh Subagent Execution]]
- [[Session Persistence]]

## Workflow Design
- [[GET SHIT DONE Workflow]]
- [[RIPER Framework]]
- [[Claude Spaces Pattern]]
```

---

## Benefits for Your Research

### Immediate Wins

1. **Linked Thinking**: Connect patterns across repos with `[[wikilinks]]`
2. **Visual Organization**: Canvas for agent architecture diagrams
3. **Quick Capture**: Fast note creation with proper structure
4. **Progress Tracking**: Task lists for learning goals

### Long-term Value

1. **Knowledge Graph**: Build interconnected understanding of agentic systems
2. **Pattern Library**: Searchable, linked collection of extracted patterns
3. **Research Journal**: Chronicle your learning journey
4. **Reference System**: Quick access to examples and implementations

---

## Example Workflow

**Day 1: Study AutoGPT**
```
1. Create note: [[AutoGPT Analysis]]
2. Add frontmatter with date, tags, status
3. Document agent loop with code examples
4. Create wikilinks to [[Agent Loop Patterns]]
5. Add callouts for key insights
6. Embed diagram: ![[agent-loop-diagram.png]]
```

**Day 2: Extract Pattern**
```
1. Create note: [[Agent Loop Pattern - AutoGPT]]
2. Use pattern template with wikilinks
3. Link to [[AutoGPT Analysis]]
4. Add to [[Agentic Systems Patterns MOC]]
5. Create task list for next patterns
```

**Day 3: Visual Mapping**
```
1. Create: [[Agent Architectures.canvas]]
2. Add nodes for each framework
3. Link to pattern notes
4. Show relationships visually
```

---

## Next Steps

1. **Install Skills**: Use marketplace or manual method
2. **Create Vault**: Set up Obsidian vault for research
3. **Use Templates**: Adopt pattern and log templates
4. **Link Actively**: Connect concepts with wikilinks
5. **Build MOCs**: Create index notes for major topics

---

## Resources

- **Obsidian**: https://obsidian.md/
- **Agent Skills Spec**: https://agentskills.io/specification
- **Skills Repository**: `references/obsidian-skills/`
- **Obsidian Help**: https://help.obsidian.md/

---

**Obsidian + Claude Code = Powerful knowledge management for agentic systems research. Start building your interconnected understanding today!**
