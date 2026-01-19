# GET SHIT DONE (GSD) Workflow Patterns

This document captures workflow patterns and architectural approaches from the [GET SHIT DONE](https://github.com/glittercowboy/get-shit-done) system for Claude Code.

**Repository**: `references/get-shit-done/`
**Purpose**: Meta-prompting and context engineering system for building projects with Claude Code
**Key Innovation**: Solves "context rot" through structured context management and fresh subagent execution

---

## Core Concepts

### Pattern: Context Engineering Foundation

**Source**: [get-shit-done](../../references/get-shit-done/)

**Purpose**: Prevent context degradation as Claude's context window fills during extended sessions

**Context**: Use when building complex projects that require extended Claude Code sessions

**Implementation**:

The system maintains curated persistent documents:
- `PROJECT.md` - Project vision and goals
- `REQUIREMENTS.md` - Scoped requirements (v1, v2, out-of-scope)
- `ROADMAP.md` - Phase-mapped milestones
- `STATE.md` - Current progress, decisions, blockers

Each document stays within quality thresholds, loading contextually during operations to prevent information overload.

**Trade-offs**:
- **Pros**: Prevents quality degradation, maintains consistency across sessions, enables project resumption
- **Cons**: Requires discipline to maintain documents, upfront structure overhead

**Related Patterns**: Fresh Subagent Execution, Session Persistence

---

## Pattern: Fresh Subagent Execution

**Source**: [get-shit-done](../../references/get-shit-done/)

**Purpose**: Execute each task in a clean context to avoid token accumulation and quality degradation

**Context**: For complex multi-step projects where context accumulation degrades performance

**Implementation**:

```
Rather than accumulating tokens in a single session:
1. Plan phase breaks down work into atomic tasks
2. Each task executes in a fresh subagent with full 200k token budget
3. No context pollution from previous tasks
4. Consistent quality throughout execution
```

**Key Insight**: "Each plan runs in a fresh subagent context — 200k tokens purely for implementation, zero degradation."

**Example Workflow**:
1. `/gsd:plan-phase` - Create atomic task list
2. `/gsd:execute-phase` - Each task gets fresh subagent
3. Results committed atomically per task

**Trade-offs**:
- **Pros**: Zero context degradation, consistent quality, parallel execution possible
- **Cons**: Requires good task decomposition, each subagent needs sufficient context

**Related Patterns**: XML-Structured Tasks, Atomic Git Commits

---

## Pattern: XML-Structured Task Format

**Source**: [get-shit-done](../../references/get-shit-done/)

**Purpose**: Eliminate ambiguity in task definitions and enable self-verification

**Context**: When tasks need clear acceptance criteria and verification steps

**Implementation**:

```xml
<task>
  <name>Clear task description</name>
  <files>
    <file>path/to/file1.py</file>
    <file>path/to/file2.py</file>
  </files>
  <action>
    Specific steps to complete the task
  </action>
  <verify>
    Steps to verify task completion
  </verify>
  <completion_criteria>
    Clear criteria for "done"
  </completion_criteria>
</task>
```

**Benefits**:
- Unambiguous task definition
- Built-in verification steps
- Clear file scope
- Self-documenting

**Trade-offs**:
- **Pros**: Clear expectations, enables automation, facilitates verification
- **Cons**: More verbose than free-form descriptions

**Related Patterns**: Progressive Verification, Atomic Git Commits

---

## Pattern: Atomic Git Commits

**Source**: [get-shit-done](../../references/get-shit-done/)

**Purpose**: Enable precise tracking, bisecting, and independent task reversion

**Context**: Projects requiring granular version control and easy rollback

**Implementation**:

Each task generates immediate commits with phase/date prefixes:
```
[Phase-1] 2025-01-15: Implement user authentication
[Phase-1] 2025-01-15: Add password hashing
[Phase-2] 2025-01-15: Create API endpoints
```

**Benefits**:
- Precise bisecting when bugs appear
- Independent task reversion
- Clear project timeline
- Easy progress tracking

**Trade-offs**:
- **Pros**: Excellent traceability, easy rollback, clear history
- **Cons**: More commits than traditional workflow (this is intentional)

**Related Patterns**: XML-Structured Tasks, Modular Adaptation

---

## Pattern: Modular Adaptation

**Source**: [get-shit-done](../../references/get-shit-done/)

**Purpose**: Maintain flexibility without breaking the workflow structure

**Context**: When requirements change mid-project or urgent work needs insertion

**Implementation**:

The system supports:
- **Add phases mid-milestone**: New requirements? Add phase without restructuring
- **Insert urgent work**: `/gsd:insert-phase` between existing phases
- **Remove phases**: Delete completed/irrelevant phases without cascade failures
- **Renumber phases**: Maintain logical order after changes

**Example**:
```bash
# Original plan: Phase 1, 2, 3
# Urgent security fix needed between 1 and 2
/gsd:insert-phase --after=1 --name="Security patch"
# Result: Phase 1, 1.5 (Security), 2, 3
```

**Trade-offs**:
- **Pros**: Adapts to reality, handles changing requirements, maintains structure
- **Cons**: Requires thoughtful phase design initially

**Related Patterns**: Session Persistence, Progressive Verification

---

## Pattern: Session Persistence

**Source**: [get-shit-done](../../references/get-shit-done/)

**Purpose**: Enable work across multiple sessions without losing context

**Context**: For projects spanning multiple days/weeks

**Implementation**:

`STATE.md` maintains:
- Current position in roadmap
- Recent decisions and rationale
- Active blockers
- Next steps

**Commands**:
```bash
# End of session
/gsd:pause-work

# Resume later (even days later)
/gsd:resume-work
```

STATE.md captures:
```markdown
## Current Position
Phase: 2/5
Last completed task: User authentication
Next task: API endpoint creation

## Recent Decisions
- Using JWT for auth (faster than sessions)
- PostgreSQL over MySQL (better JSON support)

## Blockers
- Waiting for API key from third-party service
- Need design review for dashboard layout
```

**Trade-offs**:
- **Pros**: Seamless session resumption, preserved context, no mental overhead
- **Cons**: Requires updating STATE.md (automated by GSD)

**Related Patterns**: Context Engineering Foundation

---

## Pattern: Progressive Verification

**Source**: [get-shit-done](../../references/get-shit-done/)

**Purpose**: Catch issues early through built-in verification at multiple levels

**Context**: Quality-critical projects requiring validation at each step

**Implementation**:

**Three verification layers**:

1. **Task-level**: Built into XML structure
   ```xml
   <verify>
     Run tests: pytest tests/auth/
     Check API response: curl localhost:8000/api/auth
     Verify database: SELECT COUNT(*) FROM users
   </verify>
   ```

2. **Phase-level**: After phase completion
   ```bash
   /gsd:verify-work
   # Claude runs verification steps
   # Reports issues found
   ```

3. **Milestone-level**: Before milestone completion
   ```bash
   /gsd:discuss-milestone
   # Review overall milestone objectives
   # Identify gaps or issues
   ```

**Trade-offs**:
- **Pros**: Early issue detection, quality assurance, confidence in progress
- **Cons**: Additional verification time (pays off in reduced debugging)

**Related Patterns**: XML-Structured Tasks, Atomic Git Commits

---

## Workflow Architectures

### Greenfield Project Workflow

**Pattern**: Structured project initialization from scratch

**Steps**:
1. `/gsd:new-project` — Vision extraction through dialogue
2. `/gsd:research-project` — Parallel investigation of domain ecosystem
3. `/gsd:define-requirements` — Scope v1/v2/out-of-scope boundaries
4. `/gsd:create-roadmap` — Phase-mapped requirements
5. `/gsd:plan-phase` — Break phase into atomic tasks
6. `/gsd:execute-phase` — Parallel task execution in fresh subagents

**Use When**: Starting a new project from scratch

**Example Flow**:
```bash
# 1. Initialize
/gsd:new-project
> Vision: Build a task management API

# 2. Research
/gsd:research-project
> Investigates: FastAPI vs Flask, PostgreSQL vs MongoDB, auth patterns

# 3. Define requirements
/gsd:define-requirements
> v1: Core API, user auth, task CRUD
> v2: Teams, permissions, notifications
> Out of scope: Mobile apps, real-time sync

# 4. Create roadmap
/gsd:create-roadmap
> Phase 1: Database setup, user model
> Phase 2: Authentication system
> Phase 3: Task CRUD endpoints
> Phase 4: Testing & deployment

# 5. Execute each phase
/gsd:plan-phase 1
/gsd:execute-phase 1
```

---

### Brownfield Project Workflow

**Pattern**: Onboarding GSD into existing codebase

**Steps**:
1. `/gsd:map-codebase` — Generate 7 analysis documents:
   - STACK.md - Technology stack
   - ARCHITECTURE.md - System architecture
   - STRUCTURE.md - Directory organization
   - CONVENTIONS.md - Coding standards
   - TESTING.md - Test approach
   - INTEGRATIONS.md - External dependencies
   - CONCERNS.md - Technical debt, risks

2. `/gsd:new-project` — Context-aware initialization
3. Continue standard workflow with existing code context

**Use When**: Adopting GSD for an existing project

**Benefits**:
- Understands existing patterns
- Respects established conventions
- Identifies technical debt
- Context-aware planning

---

## Integration Patterns

### Pattern: Human Feedback Loop

**Source**: [get-shit-done](../../references/get-shit-done/)

**Purpose**: Shape iteration before execution rather than fixing after failure

**Commands**:
```bash
# Discuss before planning
/gsd:discuss-phase
> Review phase objectives
> Clarify requirements
> Identify assumptions

# List assumptions for validation
/gsd:list-phase-assumptions
> Shows Claude's understanding
> Allows correction before execution

# Research specific aspects
/gsd:research-phase
> Deep dive into unclear areas
> Evaluate alternatives
```

**Philosophy**: "Users can discuss phases, list assumptions, and correct Claude's understanding before execution rather than after failure."

---

## Implementation Notes

### Installation

```bash
# NPX (easiest)
npx get-shit-done-cc

# Global installation
npm install -g get-shit-done-cc

# Local project installation
npm install get-shit-done-cc
```

**Recommended Setup**:
```bash
# Run with friction-free automation
claude --dangerously-skip-permissions

# For containers, set absolute config path
export CLAUDE_CONFIG_DIR=/full/path/to/.claude
```

### Directory Structure

```
project/
├── .claude/
│   └── skills/
│       └── get-shit-done/   # GSD skill files
├── docs/
│   ├── PROJECT.md           # Vision and goals
│   ├── REQUIREMENTS.md      # Scoped requirements
│   ├── ROADMAP.md          # Phase mappings
│   └── STATE.md            # Current state
└── [your code]
```

---

## Key Takeaways for Agentic Workflows

1. **Context Management is Critical**: Don't let context accumulate - use fresh subagents
2. **Structure Enables Freedom**: Rigid task format enables flexible adaptation
3. **Verification Prevents Waste**: Build verification into tasks, not after
4. **State Persistence Matters**: Document decisions and position for session resumption
5. **Human Guidance Shapes Quality**: Discuss and validate before executing

---

## Applying GSD Patterns

### For Your Agentic Workflows:

**Context Engineering**:
- Maintain core documents (vision, requirements, state)
- Load context selectively per task
- Keep documents within quality thresholds

**Fresh Execution**:
- Break complex workflows into atomic tasks
- Execute each in clean subagent context
- Avoid context pollution

**Structured Tasks**:
- Define clear inputs, actions, verification
- Include completion criteria
- Enable self-verification

**Adaptive Planning**:
- Plan phases but allow insertion/removal
- Support changing requirements
- Maintain flexibility in structure

---

## Next Steps

1. **Install GSD**: `npx get-shit-done-cc`
2. **Study the codebase**: `references/get-shit-done/`
3. **Try greenfield workflow**: Start small project with GSD
4. **Extract applicable patterns**: Document what works for your needs
5. **Adapt for agentic research**: Apply context engineering to agent development

---

**Related Documentation**:
- [LEARNING_WORKFLOW.md](../LEARNING_WORKFLOW.md) - How to extract patterns
- [CLAUDE_CODE_RESOURCES.md](../CLAUDE_CODE_RESOURCES.md) - Other workflow systems
- [agent-loop-patterns.md](./agent-loop-patterns.md) - Agent execution patterns
