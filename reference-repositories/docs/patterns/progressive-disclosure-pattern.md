---
title: Progressive Disclosure Pattern
source: "[[anthropic-skills]]"
category: Context Efficiency
tags:
  - pattern
  - context-management
  - skill-design
  - token-optimization
---

# Progressive Disclosure Pattern

## Pattern Overview

Progressive Disclosure is a context management pattern that loads information in layers based on necessity. Instead of dumping all knowledge into context upfront, it reveals information progressively as the AI agent determines it needs it.

**Key Principle**: The context window is a public good. Every token loaded competes with conversation history, other skills, and the user's actual request. Default assumption: Claude is already very smart. Only add context Claude doesn't already have.

## The Three-Level Loading System

Skills use a three-level hierarchy to manage context efficiently:

### Level 1: Metadata (Always in Context)
**Size**: ~100 words
**When Loaded**: Always present in every conversation
**Contents**:
- Skill name
- Skill description (primary triggering mechanism)

**Example**:
```yaml
---
name: docx
description: "Comprehensive document creation, editing, and analysis with support for tracked changes, comments, formatting preservation, and text extraction. When Claude needs to work with professional documents (.docx files) for: (1) Creating new documents, (2) Modifying or editing content, (3) Working with tracked changes, (4) Adding comments, or any other document tasks"
---
```

**Critical**: The description field must include:
- What the skill does
- Specific triggers/contexts for when to use it
- All "when to use" information (since body only loads after triggering)

### Level 2: SKILL.md Body (Conditional Loading)
**Size**: <5k words (keep under 500 lines)
**When Loaded**: Only when skill triggers based on metadata
**Contents**:
- Essential workflows and procedures
- Quick start examples
- Navigation to Level 3 resources
- Selection guidance for variants/frameworks

**Example Structure**:
```markdown
# PDF Processing

## Quick start

Extract text with pdfplumber:
[concise code example]

## Advanced features

- **Form filling**: See [FORMS.md](FORMS.md) for complete guide
- **API reference**: See [REFERENCE.md](REFERENCE.md) for all methods
- **Examples**: See [EXAMPLES.md](EXAMPLES.md) for common patterns
```

**Guidelines**:
- Keep to essentials only
- Challenge each paragraph: "Does Claude really need this explanation?"
- Prefer concise examples over verbose explanations
- Include clear pointers to Level 3 resources
- Avoid duplication with reference files

### Level 3: Bundled Resources (On-Demand Loading)
**Size**: Unlimited (scripts can execute without loading into context)
**When Loaded**: As needed by Claude during execution
**Contents**: Three types of resources:

#### Scripts (`scripts/`)
Executable code for deterministic operations.

**When to Include**:
- Same code being rewritten repeatedly
- Deterministic reliability needed
- Complex operations prone to errors

**Example**:
```python
# scripts/rotate_pdf.py
import sys
from PyPDF2 import PdfReader, PdfWriter

def rotate_pdf(input_path, output_path, rotation):
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        page.rotate(rotation)
        writer.add_page(page)

    with open(output_path, 'wb') as output:
        writer.write(output)

if __name__ == '__main__':
    rotate_pdf(sys.argv[1], sys.argv[2], int(sys.argv[3]))
```

**Benefits**:
- Token efficient (can execute without reading)
- Deterministic output
- Reusable across multiple uses

#### References (`references/`)
Documentation and reference material loaded as needed.

**When to Include**:
- Database schemas
- API documentation
- Domain knowledge
- Company policies
- Detailed workflow guides

**Example Organization**:
```
bigquery-skill/
├── SKILL.md (overview and navigation)
└── references/
    ├── finance.md (revenue, billing metrics)
    ├── sales.md (opportunities, pipeline)
    ├── product.md (API usage, features)
    └── marketing.md (campaigns, attribution)
```

When user asks about sales metrics, Claude only reads `sales.md`.

**Best Practices**:
- Files >10k words should include grep search patterns in SKILL.md
- Avoid duplication with SKILL.md (information should live in one place)
- Prefer references files for detailed information
- Include table of contents for files >100 lines

#### Assets (`assets/`)
Files used in output, not loaded into context.

**When to Include**:
- Templates to copy/modify
- Images, icons, logos
- Boilerplate code
- Fonts, sample documents

**Example**:
```
frontend-webapp-builder/
├── SKILL.md
└── assets/
    ├── hello-world/
    │   ├── index.html
    │   ├── styles.css
    │   └── app.js
    ├── logo.png
    └── font.ttf
```

**Benefits**:
- Separates output resources from documentation
- Claude can copy/modify without loading into context
- Supports visual/binary files

## Progressive Disclosure Patterns

### Pattern 1: High-Level Guide with References

**Use When**: Skill has multiple advanced features that aren't always needed.

**Structure**:
```markdown
# SKILL.md (Core workflows)

## Quick start
[Essential code example]

## Advanced features
- **Form filling**: See [FORMS.md](FORMS.md) for complete guide
- **API reference**: See [REFERENCE.md](REFERENCE.md) for all methods
- **Examples**: See [EXAMPLES.md](EXAMPLES.md) for common patterns
```

**Example from DOCX skill**:
```markdown
# DOCX Processing

## Creating documents
Use docx-js for new documents. See [DOCX-JS.md](DOCX-JS.md).

## Editing documents
For simple edits, modify the XML directly.

**For tracked changes**: See [REDLINING.md](REDLINING.md)
**For OOXML details**: See [OOXML.md](OOXML.md)
```

Claude reads REDLINING.md or OOXML.md only when user needs those features.

### Pattern 2: Domain-Specific Organization

**Use When**: Skill supports multiple domains or frameworks.

**Structure**:
```
cloud-deploy/
├── SKILL.md (workflow + provider selection)
└── references/
    ├── aws.md (AWS deployment patterns)
    ├── gcp.md (GCP deployment patterns)
    └── azure.md (Azure deployment patterns)
```

**SKILL.md Content**:
```markdown
# Cloud Deployment

## Workflow
1. Choose provider (AWS, GCP, Azure)
2. Configure application
3. Deploy infrastructure
4. Verify deployment

## Provider-Specific Patterns
- **AWS**: See [aws.md](references/aws.md)
- **GCP**: See [gcp.md](references/gcp.md)
- **Azure**: See [azure.md](references/azure.md)
```

When user chooses AWS, Claude only reads `aws.md`.

### Pattern 3: Conditional Details

**Use When**: Basic usage is common, advanced usage is rare.

**Structure**:
```markdown
# Image Processing

## Basic operations
[Resize, rotate, crop examples]

## Advanced features (load only when needed)
**Face detection**: See [FACE-DETECTION.md](FACE-DETECTION.md)
**Color correction**: See [COLOR-CORRECTION.md](COLOR-CORRECTION.md)
**Batch processing**: See [BATCH.md](BATCH.md)
```

## Implementation Guidelines

### 1. Avoid Deeply Nested References
Keep references one level deep from SKILL.md. All reference files should link directly from SKILL.md.

**Good**:
```
SKILL.md → ADVANCED.md
SKILL.md → EXAMPLES.md
SKILL.md → REFERENCE.md
```

**Bad**:
```
SKILL.md → ADVANCED.md → SUBSECTION.md → DETAILS.md
```

### 2. Structure Longer Reference Files
For files >100 lines, include table of contents at top so Claude can see full scope when previewing.

**Example**:
```markdown
# API Reference

## Table of Contents
- Authentication
- User Management
- Data Operations
- Error Handling
- Rate Limiting

## Authentication
[Details...]
```

### 3. Challenge Every Token
Before adding content, ask:
- "Does Claude really need this explanation?"
- "Does this paragraph justify its token cost?"
- "Can this be a concise example instead of verbose explanation?"

### 4. Avoid Duplication
Information should live in **one place**:
- SKILL.md for essential workflows
- References for detailed information
- Not both

## Real-World Example: DOCX Skill

### Level 1: Metadata (Always Loaded)
```yaml
---
name: docx
description: "Comprehensive document creation, editing, and analysis with support for tracked changes, comments, formatting preservation, and text extraction. When Claude needs to work with professional documents (.docx files) for: (1) Creating new documents, (2) Modifying or editing content, (3) Working with tracked changes, (4) Adding comments, or any other document tasks"
---
```

### Level 2: SKILL.md Body (Loaded When Triggered)
```markdown
# DOCX creation, editing, and analysis

## Workflow Decision Tree

### Creating New Document
Use "Creating a new Word document" workflow

### Editing Existing Document
- **Your own document + simple changes**
  Use "Basic OOXML editing" workflow
- **Someone else's document**
  Use **"Redlining workflow"** (recommended default)

## Creating a new Word document
1. **MANDATORY - READ ENTIRE FILE**: Read [`docx-js.md`](docx-js.md)
2. Create JavaScript/TypeScript file using Document, Paragraph, TextRun
3. Export as .docx using Packer.toBuffer()

## Editing an existing Word document
1. **MANDATORY - READ ENTIRE FILE**: Read [`ooxml.md`](ooxml.md)
2. Unpack: `python ooxml/scripts/unpack.py <file> <dir>`
3. Create and run Python script using Document library
4. Pack: `python ooxml/scripts/pack.py <dir> <file>`
```

### Level 3: Bundled Resources (Loaded On-Demand)
```
docx/
├── SKILL.md (workflow decision tree)
├── references/
│   ├── docx-js.md (~500 lines - docx-js library guide)
│   └── ooxml.md (~600 lines - OOXML manipulation guide)
└── scripts/
    ├── unpack.py (extract .docx to XML)
    └── pack.py (package XML to .docx)
```

**Token Savings**:
- Without progressive disclosure: ~1,200 lines always loaded
- With progressive disclosure:
  - Level 1: ~50 words always loaded
  - Level 2: ~200 lines loaded when skill triggers
  - Level 3: ~1,100 lines loaded only when specific workflows chosen

**Result**: ~80-90% token reduction for most requests.

## Degrees of Freedom

Match specificity to task fragility and variability:

### High Freedom (Text-Based Instructions)
**Use When**:
- Multiple approaches are valid
- Decisions depend on context
- Heuristics guide the approach

**Example**:
```markdown
## Code Review Workflow
1. Read the code changes
2. Identify potential issues (bugs, style, performance)
3. Suggest improvements with reasoning
4. Prioritize critical issues first
```

### Medium Freedom (Pseudocode/Scripts with Parameters)
**Use When**:
- Preferred pattern exists
- Some variation is acceptable
- Configuration affects behavior

**Example**:
```python
# scripts/process_data.py --format {json|csv} --validate {strict|lenient}
def process_data(input_file, format, validate_level):
    data = read_file(input_file, format)
    if validate_level == 'strict':
        enforce_schema(data)
    return transform(data)
```

### Low Freedom (Specific Scripts, Few Parameters)
**Use When**:
- Operations are fragile and error-prone
- Consistency is critical
- Specific sequence must be followed

**Example**:
```python
# scripts/rotate_pdf.py <input> <output> <rotation>
# Rotation must be: 0, 90, 180, or 270
# No variation - exact implementation required
```

**Analogy**: Think of Claude as exploring a path:
- Narrow bridge with cliffs = specific guardrails (low freedom)
- Open field = many valid routes (high freedom)

## Context vs Execution Trade-offs

| Approach | Context Cost | Reliability | Use Case |
|----------|--------------|-------------|----------|
| **Text instructions** | Low | Medium | General workflows, creative tasks |
| **Pseudocode with parameters** | Medium | High | Structured workflows, configurable tasks |
| **Executable scripts** | Zero (if not read) | Highest | Fragile operations, repeated tasks |

**Key Insight**: Scripts can be executed **without loading into context**, making them effectively "free" for token budget.

## Related Patterns

- [[structured-lifecycle-pattern]] - Uses progressive disclosure for phase-specific documentation
- [[mcp-server-integration]] - MCP tools as on-demand context (similar to Level 3 resources)
- [[gsd-workflow-patterns]] - Fresh subagent execution prevents context accumulation

## References

- [skill-creator](c:\Users\Stang3x\Documents\Personal - Dan\Agentic Workflows\references\anthropic-skills\skills\skill-creator\SKILL.md) - Official guide for creating skills
- [Agent Skills Specification](https://agentskills.io/specification) - Standard for skill metadata
- [DOCX skill](c:\Users\Stang3x\Documents\Personal - Dan\Agentic Workflows\references\anthropic-skills\skills\docx\SKILL.md) - Production example
- [PDF skill](c:\Users\Stang3x\Documents\Personal - Dan\Agentic Workflows\references\anthropic-skills\skills\pdf\SKILL.md) - Production example

## Key Takeaways

1. **Context is expensive** - Every token loaded competes with user requests and conversation history
2. **Three levels of loading** - Metadata (always) → Body (when triggered) → Resources (as needed)
3. **Challenge every token** - Default to assuming Claude already knows; only add unique context
4. **Organize by domain/variant** - Load only relevant sections for specific use cases
5. **Scripts are "free"** - Can execute without loading into context
6. **One level deep** - Avoid nested references; link directly from SKILL.md
7. **Match freedom to fragility** - Narrow tasks need specific scripts; open tasks allow text instructions
