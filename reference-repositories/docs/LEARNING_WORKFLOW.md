# Learning Workflow: Extracting Patterns from Reference Repositories

This guide explains how to effectively learn from the reference repositories and document useful patterns for your agentic workflow projects.

## Overview

The `references/` directory contains cloned GitHub repositories that demonstrate best practices for building agentic systems. Your goal is to:
1. Study these implementations
2. Extract reusable patterns
3. Document them for future reference
4. Apply them in your own projects

## Reference Repositories

### AutoGPT
**Location**: `references/AutoGPT/`
**Focus**: Autonomous task execution and goal-driven agent behavior
**Key Areas to Study**:
- Agent loop implementation
- Task decomposition strategies
- Memory and context management
- Tool/plugin architecture

### LangGraph
**Location**: `references/langgraph/`
**Focus**: Graph-based agent orchestration and state management
**Key Areas to Study**:
- State graph definitions
- Checkpointing and persistence
- Conditional edges and branching
- Multi-agent coordination via graphs

### CrewAI
**Location**: `references/crewAI/`
**Focus**: Multi-agent collaboration with role-based agents
**Key Areas to Study**:
- Role definition and agent specialization
- Inter-agent communication
- Task delegation patterns
- Sequential vs parallel execution

### n8n-nodes-starter
**Location**: `references/n8n-nodes-starter/`
**Focus**: Custom n8n node development
**Key Areas to Study**:
- Node structure and TypeScript patterns
- Parameter handling and validation
- Credential management
- Error handling and user feedback

## Learning Workflow

### Phase 1: Exploration
1. **Browse the repository structure**
   ```bash
   cd references/[repo-name]
   ls -R  # or explore in VSCode
   ```

2. **Find example implementations**
   - Look for `/examples/`, `/tutorials/`, or `/docs/` directories
   - Check README files for getting started guides
   - Identify core modules (usually in `/src/` or `/lib/`)

3. **Ask Claude Code to help**
   - "Read and explain the main agent loop in AutoGPT"
   - "Find examples of state management in LangGraph"
   - "Show me how CrewAI defines agent roles"

### Phase 2: Deep Dive
1. **Read specific files**
   - Start with examples, then move to core implementation
   - Focus on one pattern at a time
   - Trace code execution paths

2. **Understand the pattern's purpose**
   - What problem does this pattern solve?
   - When should it be used vs alternatives?
   - What are the trade-offs?

3. **Note the implementation details**
   - Key classes and functions
   - Data structures used
   - Error handling approaches
   - Testing strategies

### Phase 3: Documentation
1. **Choose the appropriate pattern file**
   - Agent loops → `docs/patterns/agent-loop-patterns.md`
   - State management → `docs/patterns/state-management-patterns.md`
   - n8n nodes → `docs/patterns/n8n-custom-node-patterns.md`
   - New category → Create a new file

2. **Follow the documentation template**
   ```markdown
   ## Pattern Name

   **Source**: [Repo](link) - path/to/file.py:line_number

   **Purpose**: One sentence describing what it solves

   **Context**: When to use this pattern

   **Implementation**:
   \`\`\`language
   # Simplified code example
   \`\`\`

   **Trade-offs**:
   - Pros: Benefits
   - Cons: Limitations

   **Related Patterns**: Links to related docs
   ```

3. **Simplify and generalize**
   - Remove project-specific details
   - Extract the core pattern
   - Add comments explaining key concepts
   - Make it adaptable to different use cases

### Phase 4: Application
1. **Try the pattern in your own code**
   - Create a small test implementation
   - Adapt it to your specific needs
   - Document any modifications or insights

2. **Update pattern documentation**
   - Add notes about your experience
   - Document any gotchas or edge cases
   - Link to your implementation as an example

## Working with Claude Code

### Asking for Analysis
```
"Read references/AutoGPT/[path/to/file] and explain the agent loop pattern"
"Compare how LangGraph and CrewAI handle state management"
"Extract the credential handling pattern from n8n-nodes-starter"
```

### Generating Code Based on Patterns
```
"Using the agent loop pattern from AutoGPT, create a simple goal-directed agent for [my use case]"
"Implement state checkpointing similar to LangGraph for [my workflow]"
"Create a custom n8n node following the patterns in n8n-nodes-starter for [my API integration]"
```

### Pattern Documentation
```
"Help me document the [specific pattern] I found in [repo]"
"Review my pattern documentation in docs/patterns/[file] and suggest improvements"
```

## Best Practices

### Do:
- Start with official examples and documentation
- Understand the "why" before the "how"
- Document patterns as you discover them (don't wait)
- Test patterns in isolation before integrating
- Keep pattern documentation concise and practical
- Update documentation when you learn better approaches

### Don't:
- Copy entire files without understanding them
- Document every detail (focus on reusable patterns)
- Skip testing patterns before documenting
- Forget to link to source code locations
- Create overly complex examples in documentation
- Document patterns you haven't actually tried

## Iteration and Improvement

As you work with these patterns:
1. **Refine your documentation** - Update when you gain new insights
2. **Create cross-references** - Link related patterns together
3. **Build a pattern library** - Collect your most-used patterns
4. **Share learnings** - Document what works and what doesn't
5. **Evolve patterns** - Adapt patterns as you discover better approaches

## Getting Started Checklist

- [ ] Browse each reference repository's README
- [ ] Identify 1-2 patterns that interest you
- [ ] Read the source code for those patterns
- [ ] Document them in the appropriate pattern file
- [ ] Try implementing one pattern in a small test project
- [ ] Update documentation with your learnings

## Questions to Ask When Studying Code

1. **Architecture**: How is the code organized? What are the main components?
2. **Data Flow**: How does data move through the system?
3. **Error Handling**: How are errors detected and handled?
4. **Extensibility**: How easy is it to add new functionality?
5. **Testing**: How is the code tested?
6. **Configuration**: How are options and settings managed?
7. **Dependencies**: What external libraries are used and why?
8. **Performance**: Are there any performance optimizations?

## Helpful Commands

```bash
# Find files by name pattern
find references/[repo]/ -name "*agent*"

# Search for specific code patterns
grep -r "class.*Agent" references/[repo]/

# View repository structure
tree references/[repo]/ -L 3

# Check repository documentation
cat references/[repo]/README.md
```

Remember: The goal is not to copy code, but to understand patterns and principles you can apply to your own agentic workflow projects.
