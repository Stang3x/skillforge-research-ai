# Pattern Documentation

This directory contains documented patterns extracted from reference repositories and other sources. The goal is to capture reusable architectural patterns, code structures, and best practices for building agentic workflows.

## How to Use This Directory

### For Documenting New Patterns
When you discover a useful pattern in a reference repository or through experimentation:

1. Choose the appropriate pattern file (or create a new one)
2. Follow the template structure below
3. Include concrete code examples
4. Link to the source repository or file

### Pattern Documentation Template

```markdown
## Pattern Name

**Source**: [Repository Name](link) - file/path/here.py:line_number

**Purpose**: One-sentence description of what this pattern solves

**Context**: When to use this pattern and what problems it addresses

**Implementation**:
```language
# Code example showing the pattern
# Include comments explaining key parts
```

**Trade-offs**:
- Pros: Benefits of using this pattern
- Cons: Drawbacks or limitations

**Related Patterns**: Links to related patterns in this documentation
```

## Pattern Categories

### Agent Loop Patterns
Document in [agent-loop-patterns.md](./agent-loop-patterns.md)
- Core agent execution cycles
- Decision-making loops
- Task iteration patterns

### State Management Patterns
Document in [state-management-patterns.md](./state-management-patterns.md)
- State persistence approaches
- Multi-agent state coordination
- Memory and context management

### n8n Custom Node Patterns
Document in [n8n-custom-node-patterns.md](./n8n-custom-node-patterns.md)
- Custom node structure and setup
- Parameter handling
- API integration within nodes
- Error handling in nodes

## Contributing Patterns

As you work with the reference repositories:
1. Read and understand the implementation
2. Extract the core pattern (remove project-specific details)
3. Document with clear examples
4. Test the pattern in your own code before documenting
