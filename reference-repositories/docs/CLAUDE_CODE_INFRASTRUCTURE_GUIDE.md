# Claude Code Infrastructure Guide

**Source:** [claude-code-infrastructure-showcase](https://github.com/diet103/claude-code-infrastructure-showcase)
**Original Article:** [Claude Code is a Beast - Tips from 6 Months of Hardcore Use](https://dev.to/diet-code103/claude-code-is-a-beast-tips-from-6-months-of-hardcore-use-572n)

> "Ask not what Claude can do for you, ask what context you can give to Claude."

---

## Overview

This guide captures production-tested patterns from 6 months of real-world Claude Code usage on a 300k+ LOC TypeScript project. The key breakthrough is **skill auto-activation** via hooks.

### Key Components
- **Skills**: Auto-activating knowledge bases (5 production skills)
- **Hooks**: Scripts that run at specific workflow points (6 hooks)
- **Agents**: Specialized autonomous sub-tasks (10 agents)
- **Dev Docs**: Context-preserving documentation pattern
- **Slash Commands**: Repeated workflows packaged as commands

---

## 1. Skills Auto-Activation System

### The Problem
Skills sit unused because Claude doesn't automatically reference them, even with explicit keywords.

### The Solution: Hook-Driven Activation

**UserPromptSubmit Hook** runs BEFORE Claude responds:
1. Reads `skill-rules.json` for trigger patterns
2. Analyzes user prompt for keywords and intent
3. Checks which files user is working with
4. Injects skill suggestions into Claude's context

### skill-rules.json Configuration

```json
{
  "skill-name": {
    "type": "domain | guardrail",
    "enforcement": "suggest | block",
    "priority": "high | medium | low",
    "promptTriggers": {
      "keywords": ["backend", "API", "route"],
      "intentPatterns": ["(create|add).*(feature|route)"]
    },
    "fileTriggers": {
      "pathPatterns": ["src/api/**/*.ts"],
      "contentPatterns": ["import.*Prisma"]
    }
  }
}
```

### Enforcement Levels
- **suggest**: Skill appears as suggestion, doesn't block
- **block**: Must use skill before proceeding (guardrail for critical patterns)

### 500-Line Rule (Progressive Disclosure)
Large skills hit context limits. Solution:

```
skill-name/
  SKILL.md                  # <500 lines, high-level guide
  resources/
    topic-1.md              # <500 lines each
    topic-2.md
```

Claude loads main skill first, then resources only when needed. This improved token efficiency 40-60%.

---

## 2. Available Skills

| Skill | Purpose | Lines | Customization |
|-------|---------|-------|---------------|
| **skill-developer** | Meta-skill for creating skills | 426 | None |
| **backend-dev-guidelines** | Node.js/Express/Prisma patterns | 304+ | Path patterns |
| **frontend-dev-guidelines** | React/MUI v7/TypeScript | 398+ | Path patterns |
| **route-tester** | JWT cookie auth testing | 389 | Auth setup |
| **error-tracking** | Sentry integration | ~250 | Path patterns |

### Creating Custom Skills

```markdown
---
name: my-skill
description: What this skill does
---

# My Skill Title

## Purpose
[Why this skill exists]

## When to Use This Skill
[Auto-activation scenarios]

## Quick Reference
[Key patterns and examples]

## Resource Files
- [topic-1.md](resources/topic-1.md)
```

---

## 3. Hooks System

### Essential Hooks (Copy As-Is)

#### skill-activation-prompt (UserPromptSubmit)
```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "hooks": [{
        "type": "command",
        "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/skill-activation-prompt.sh"
      }]
    }]
  }
}
```

#### post-tool-use-tracker (PostToolUse)
```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit|MultiEdit|Write",
      "hooks": [{
        "type": "command",
        "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-tool-use-tracker.sh"
      }]
    }]
  }
}
```

### Hook Pipeline
```
Claude finishes responding
    ↓
Hook 1: Build checker runs → TypeScript errors caught immediately
    ↓
Hook 2: Error reminder runs → Gentle self-check
    ↓
If errors found → Claude fixes
    ↓
Result: Clean, error-free code
```

### Stop Event Hook (Error Handling Reminder)
Runs after Claude responds, analyzes edited files for risky patterns:
- try-catch blocks
- async operations
- database calls
- controllers

Displays gentle self-check questions:
- "Did you add error handling?"
- "Using repository pattern?"

---

## 4. Available Agents

| Agent | Purpose | Customization |
|-------|---------|---------------|
| code-architecture-reviewer | Review code for consistency | None |
| code-refactor-master | Plan and execute refactoring | None |
| documentation-architect | Generate comprehensive docs | None |
| frontend-error-fixer | Debug frontend errors | Screenshot paths |
| plan-reviewer | Review development plans | None |
| refactor-planner | Create refactoring strategies | None |
| web-research-specialist | Research technical issues | None |
| auth-route-tester | Test authenticated endpoints | JWT setup |
| auth-route-debugger | Debug auth issues | JWT setup |
| auto-error-resolver | Fix TypeScript errors | Paths |

### When to Use Agents vs Skills

| Agents | Skills |
|--------|--------|
| Multi-step tasks | Inline guidance |
| Complex analysis | Best practices |
| Autonomous work | Maintain control |
| Clear end goal | Ongoing development |
| "Review all controllers" | "Creating a new route" |

---

## 5. Dev Docs System (Context Preservation)

> "Claude is like an extremely confident junior dev with extreme amnesia."

### Three-File Structure
For each task, create: `dev/active/[task-name]/`

1. **[task-name]-plan.md** - The accepted implementation plan
2. **[task-name]-context.md** - Key files, architectural decisions, dependencies
3. **[task-name]-tasks.md** - Checklist of work items

### Workflow
1. **Planning Mode** - Use strategic-plan-architect subagent
2. **Review Plan** - Catch mistakes before implementation
3. **Create Dev Docs** - `/dev-docs` command populates files
4. **Stage Implementation** - 1-2 sections at a time
5. **Continuous Updates** - Remind Claude to update tasks/context
6. **Pre-Compaction** - `/update-dev-docs` before context loss
7. **New Session** - Read all three files; say "continue"

---

## 6. Critical Prompting Best Practices

### Planning is King
"You wouldn't have a builder start without blueprints." Always use planning mode before implementation.

### Be Specific
- Describe exactly what you want
- If unsure, ask Claude to research and propose solutions

### Avoid Leading Questions
Don't ask "Is this good or bad?" - Claude tends to tell you what it thinks you want to hear.

### Re-prompt Often
Use double-ESC to access previous prompts. "You'd be amazed how often you can get way better results armed with the knowledge of what you don't want."

### Step In When Needed
If Claude struggles for 30 minutes on something fixable in 2 minutes, fix it yourself. "Think of it like teaching someone to ride a bike."

### Self-Reflect on Output Quality
Problems often stem from:
- Lazy prompting at end of day
- Stochastic model variance
- Ambiguous wording
- Missing context

---

## 7. Documentation Architecture

### Old Problems
- Massive BEST_PRACTICES.md (1,400+ lines) that Claude ignored
- CLAUDE.md trying to do too much
- Pattern guidance mixed with project specifics

### New Structure

**Skills contain:** Reusable patterns, best practices, how-to guides

**CLAUDE.md contains (~200 lines):**
- Quick commands
- Service-specific configuration
- Task management workflow
- Testing authenticated routes

**Separate Documentation contains:**
- System architecture & integration details
- Data flow diagrams
- API references

---

## 8. Supporting Tools

### PM2 Process Management (Backend)
```javascript
// ecosystem.config.js
module.exports = {
  apps: [{
    name: 'form-service',
    script: 'npm',
    args: 'start',
    cwd: './form',
    error_file: './form/logs/error.log',
    out_file: './form/logs/out.log',
  }]
};
```

Benefits:
- Claude can read service logs in real-time
- `pm2 logs email --lines 200` for debugging
- Automatic restarts on crashes

### Scripts Attached to Skills
Pattern: Attach utility scripts so Claude has ready-to-use tools:

```bash
node scripts/test-auth-route.js http://localhost:3002/api/endpoint
```

Scripts handle:
1. Get refresh token from auth provider
2. Sign token with JWT secret
3. Create cookie header
4. Make authenticated request

---

## 9. Slash Commands

| Command | Purpose |
|---------|---------|
| `/dev-docs` | Create strategic plan |
| `/dev-docs-update` | Update docs before compaction |
| `/code-review` | Architectural code review |
| `/build-and-fix` | Run builds and fix errors |
| `/route-research-for-testing` | Find routes and launch tests |

---

## 10. Integration Checklist

### Phase 1: Skill Activation (15 min)
1. Copy skill-activation-prompt hook
2. Copy post-tool-use-tracker hook
3. Update settings.json
4. Install hook dependencies

### Phase 2: Add First Skill (10 min)
1. Pick ONE relevant skill
2. Copy skill directory
3. Create/update skill-rules.json
4. Customize path patterns

### Phase 3: Test & Iterate (5 min)
1. Edit a file - skill should activate
2. Ask a question - skill should be suggested
3. Add more skills as needed

### Phase 4: Optional Enhancements
- Add agents
- Add slash commands
- Customize Stop hooks (advanced)

---

## Key Takeaways

### Must-Have
1. Plan everything before implementation
2. Implement skills + hooks auto-activation
3. Use dev docs to maintain context
4. Have Claude review its own code
5. For backend: PM2 logging

### Nice-to-Have
1. Specialized agents for common tasks
2. Slash commands for repeated workflows
3. Comprehensive project documentation
4. Utility scripts attached to skills

### Mindset
- Treat Claude like a junior dev requiring oversight
- Planning and communication > any tool
- Quality comes from workflow design
- Iteration and review prevent problems
- Context is everything

---

## Reference

**Repository:** `references/claude-code-infrastructure-showcase/`

**Key Files:**
- `.claude/skills/` - 5 production skills
- `.claude/hooks/` - 6 automation hooks
- `.claude/agents/` - 10 specialized agents
- `.claude/commands/` - 3 slash commands
- `skill-rules.json` - Skill activation configuration
