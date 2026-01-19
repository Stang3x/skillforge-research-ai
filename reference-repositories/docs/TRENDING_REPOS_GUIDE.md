# GitHub Trending Repositories Guide

**Purpose**: Comprehensive guide to 7 production-ready repositories from GitHub Trending that extend agentic workflow capabilities

**Last Updated**: 2026-01-16

---

## 📑 Table of Contents

- [Overview](#overview)
- [Repository Summaries](#repository-summaries)
- [SimpleMem - Memory Architecture](#simplemem---memory-architecture)
- [agent-browser - Browser Automation](#agent-browser---browser-automation)
- [autocoder - Multi-Session Agents](#autocoder---multi-session-agents)
- [nanocode - Minimal Agent Reference](#nanocode---minimal-agent-reference)
- [mcp-cli - MCP Tooling](#mcp-cli---mcp-tooling)
- [CodexMonitor - Multi-Agent Orchestration](#codexmonitor---multi-agent-orchestration)
- [tuicr - Human-in-the-Loop Review](#tuicr---human-in-the-loop-review)
- [Integration Patterns](#integration-patterns)
- [Comparison Matrix](#comparison-matrix)

---

## Overview

This guide documents 7 carefully selected repositories from GitHub Trending (2026-01-16) that provide production-ready patterns for building agentic systems. These repositories were chosen from 29 candidates based on their relevance to AI agents, automation workflows, and development tooling.

### Selection Criteria

From 29 repositories analyzed, these 7 met the criteria:
- **High Relevance** to agentic workflows
- **Production Quality** with active development
- **Novel Patterns** not covered by existing references
- **Practical Value** with real-world use cases
- **Documentation** sufficient for pattern extraction

### How These Extend Your Reference Collection

| New Repository | Complements Existing | Unique Contribution |
|----------------|---------------------|---------------------|
| **SimpleMem** | basic-memory | Production-grade semantic compression, 12.5× faster retrieval |
| **agent-browser** | n8n custom nodes | Headless browser automation designed for AI agents |
| **autocoder** | claude-task-system | Multi-session persistence with SQLite feature management |
| **nanocode** | claude-flow | Minimal agent implementation (~250 lines) for education |
| **mcp-cli** | MCP-Launchpad | Lightweight CLI for on-demand MCP tool access |
| **CodexMonitor** | awesome-claude-code-subagents | Native macOS UI for multi-agent orchestration |
| **tuicr** | (new capability) | Human-in-the-loop code review for AI-generated changes |

---

## Repository Summaries

### 🧠 SimpleMem - Memory Architecture
**Repository**: https://github.com/aiming-lab/SimpleMem
**Stars**: Trending
**Language**: Python
**Category**: Memory Management

**One-Line Summary**: Efficient lifelong memory for LLM agents through semantic lossless compression

**Key Innovation**: Three-stage pipeline (semantic compression → structured indexing → adaptive retrieval) achieving 43.24% F1 score with 30× fewer tokens than full-context methods

**Best For**: Production agents requiring fast, token-efficient long-term memory

---

### 🌐 agent-browser - Browser Automation
**Repository**: https://github.com/vercel-labs/agent-browser
**Stars**: Trending
**Language**: Rust + Node.js
**Category**: Tool Integration

**One-Line Summary**: Headless browser automation CLI explicitly designed for AI agents

**Key Innovation**: Ref-based interaction model (snapshot → stable element IDs) enabling deterministic automation without DOM re-queries

**Best For**: AI agents that need to interact with web applications

---

### 🤖 autocoder - Multi-Session Agents
**Repository**: https://github.com/leonvanzyl/autocoder
**Stars**: Trending
**Language**: Python (Claude Agent SDK)
**Category**: Multi-Session Workflows

**One-Line Summary**: Long-running autonomous coding agent with feature persistence across sessions

**Key Innovation**: Two-agent pattern (initializer + coding agent) with SQLite-based feature management and React monitoring UI

**Best For**: Building complete applications over multiple sessions with automated tracking

---

### ⚡ nanocode - Minimal Agent Reference
**Repository**: https://github.com/1rgs/nanocode
**Stars**: Trending
**Language**: Python
**Category**: Educational

**One-Line Summary**: Minimal agentic coding assistant in a single Python file (~250 lines)

**Key Innovation**: Complete agent loop with zero dependencies demonstrating fundamental architecture

**Best For**: Learning agent architecture, prototyping, educational reference

---

### 🔌 mcp-cli - MCP Tooling
**Repository**: https://github.com/philschmid/mcp-cli
**Stars**: Trending
**Language**: TypeScript (Bun)
**Category**: MCP Infrastructure

**One-Line Summary**: Lightweight CLI for on-demand MCP server interaction

**Key Innovation**: Lazy connection model with worker pool concurrency, minimizing context window usage

**Best For**: Token-efficient MCP access, shell-scriptable AI workflows

---

### 📊 CodexMonitor - Multi-Agent Orchestration
**Repository**: https://github.com/Dimillian/CodexMonitor
**Stars**: Trending
**Language**: TypeScript + Rust (Tauri)
**Category**: Orchestration UI

**One-Line Summary**: Native macOS app for orchestrating multiple Codex agents across workspaces

**Key Innovation**: JSON-RPC event streaming with git worktree management and turn-level interruption

**Best For**: Managing multiple agents with visual interface and git integration

---

### ✅ tuicr - Human-in-the-Loop Review
**Repository**: https://github.com/agavra/tuicr
**Stars**: Trending
**Language**: Rust
**Category**: Quality Control

**One-Line Summary**: Terminal code review interface for AI-generated changes

**Key Innovation**: Batch feedback workflow reducing iteration cycles with typed comments exported as structured Markdown

**Best For**: Maintaining human oversight in AI-assisted development

---

## SimpleMem - Memory Architecture

### Architecture Overview

SimpleMem addresses the fundamental challenge of **efficient long-term memory for LLM agents** through a three-stage pipeline:

```
┌─────────────────────────────────────────────────────────────┐
│                    Stage 1: Compression                     │
│  Raw Dialogue → Semantic Structured Compression → Atoms    │
│  "He'll meet Bob tomorrow at 2pm"                          │
│       ↓                                                     │
│  "Alice will meet Bob at Starbucks on 2025-11-16T14:00:00" │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Stage 2: Indexing                         │
│  Atomic Facts → Multi-View Structured Indexing → Molecules │
│  • Semantic Layer: Vector embeddings (1024-d)              │
│  • Lexical Layer: BM25-style keyword index                 │
│  • Symbolic Layer: Timestamps, entities, persons           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Stage 3: Retrieval                         │
│  Query → Complexity-Aware Adaptive Retrieval → Context     │
│  Low complexity: ~100 tokens (molecular headers)            │
│  High complexity: ~1000 tokens (atomic contexts)            │
└─────────────────────────────────────────────────────────────┘
```

### Performance Highlights

**LoCoMo-10 Benchmark (GPT-4.1-mini)**:

| Model | ⏱️ Retrieval Time | 🎯 Average F1 | Tokens Used |
|:------|:----------------:|:-------------:|:-----------:|
| A-Mem | 796.7s | 32.58% | ~30,000 |
| LightMem | 577.1s | 24.63% | ~5,000 |
| Mem0 | 583.4s | 34.20% | ~10,000 |
| **SimpleMem** ⭐ | **388.3s** | **43.24%** | **~550** |

**Key Advantages**:
- 🏆 **Highest F1 Score**: +26.4% vs. Mem0, +75.6% vs. LightMem
- ⚡ **Fastest Retrieval**: 32.7% faster than LightMem
- 💰 **Token Efficiency**: 30× fewer tokens than full-context methods

### Core Implementation

#### 1. Semantic Lossless Compression

```python
from main import SimpleMemSystem

# Initialize system
system = SimpleMemSystem(clear_db=True)

# Add dialogues with absolute timestamps
system.add_dialogue(
    speaker="Alice",
    content="Bob, let's meet at Starbucks tomorrow at 2pm",
    timestamp="2025-11-15T14:30:00"
)

system.add_dialogue(
    speaker="Bob",
    content="Sure, I'll bring the market analysis report",
    timestamp="2025-11-15T14:31:00"
)

# Finalize: Transforms dialogue into atomic entries
# "Alice will meet Bob at Starbucks on 2025-11-16T14:00:00" [absolute, atomic]
system.finalize()
```

**Write-Time Disambiguation**:
- Resolves coreferences ("he" → "Alice")
- Converts relative to absolute timestamps
- Creates self-contained atomic facts

#### 2. Multi-View Indexing

```python
# Three-layer structured indexing
class MultiViewIndex:
    def __init__(self):
        # Semantic: Dense vector embeddings
        self.vector_store = LanceDB()
        self.embedder = QwenEmbedding("Qwen3-Embedding-0.6B")  # 1024-d

        # Lexical: Sparse BM25 keyword index
        self.bm25_index = BM25Index()

        # Symbolic: Metadata filtering
        self.metadata_index = {
            "timestamps": [],
            "entities": [],
            "persons": []
        }

    def index_atom(self, atom: AtomicFact):
        # Semantic layer
        embedding = self.embedder.embed(atom.content)
        self.vector_store.add(embedding, atom)

        # Lexical layer
        self.bm25_index.add_document(atom.content, atom.id)

        # Symbolic layer
        self.metadata_index["timestamps"].append(atom.timestamp)
        self.metadata_index["entities"].extend(atom.entities)
        self.metadata_index["persons"].extend(atom.persons)
```

#### 3. Complexity-Aware Adaptive Retrieval

```python
# Dynamic retrieval depth based on query complexity
def adaptive_retrieval(query: str, k_base: int = 5, delta: float = 0.5):
    # Estimate query complexity (0.0 - 1.0)
    complexity = estimate_complexity(query)

    # Adjust retrieval depth
    k_dynamic = math.floor(k_base * (1 + delta * complexity))

    # Retrieve with dynamic depth
    results = system.ask(query, k=k_dynamic)

    return results

# Low complexity query
answer = system.ask("Where will they meet?")
# Retrieves ~100 tokens (molecular headers)

# High complexity query
answer = system.ask("What are all the events Alice participated in during November 2025?")
# Retrieves ~1000 tokens (detailed atomic contexts)
```

### MCP Server Integration

SimpleMem is available as a cloud-hosted memory service:

```json
{
  "mcpServers": {
    "simplemem": {
      "url": "https://mcp.simplemem.cloud/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN"
      }
    }
  }
}
```

**MCP Features**:
- **Streamable HTTP**: MCP 2025-03-26 protocol
- **Multi-tenant Isolation**: Per-user data tables
- **Hybrid Retrieval**: Semantic + lexical + metadata
- **Production Optimized**: OpenRouter integration

### Integration with Other Patterns

**With basic-memory**:
```python
# Combine bi-directional Markdown with semantic compression
from basic_memory import Entity, Observation
from simplemem import SimpleMemSystem

# Store structured knowledge in basic-memory
entity = Entity(title="Meeting", entity_type="event")
entity.observations.append(
    Observation(category="schedule", content="Alice and Bob meet at Starbucks 2025-11-16")
)

# Use SimpleMem for fast retrieval
simplemem = SimpleMemSystem()
simplemem.add_dialogue("System", entity.observations[0].content, datetime.now().isoformat())
simplemem.finalize()

# Fast semantic search
results = simplemem.ask("When is the next meeting?")
```

**With claude-task-system**:
```python
# Use SimpleMem for feature context retrieval
features_memory = SimpleMemSystem()

# Index all features
for feature in task_system.get_all_features():
    features_memory.add_dialogue(
        speaker="feature",
        content=f"{feature.name}: {feature.description}",
        timestamp=feature.created_at
    )

features_memory.finalize()

# Fast feature lookup during coding
relevant_features = features_memory.ask("What features relate to authentication?")
```

### Use Cases

1. **Conversational Agents**: Maintain context across long conversations with minimal tokens
2. **Customer Support**: Recall past interactions with semantic search
3. **Research Assistants**: Build knowledge from papers/documents with efficient retrieval
4. **Multi-Session Coding**: Remember design decisions and implementation details

---

## agent-browser - Browser Automation

### Architecture Overview

agent-browser uses a **client-daemon architecture** optimized for AI agents:

```
┌─────────────────────────────────────────────────────────────┐
│                      Rust CLI (Client)                      │
│  • Fast command parsing                                     │
│  • Communicates with daemon via IPC                         │
│  • Fallback to Node.js if binary unavailable               │
└─────────────────────────────────────────────────────────────┘
                            ↓ IPC
┌─────────────────────────────────────────────────────────────┐
│                   Node.js Daemon (Server)                   │
│  • Manages Playwright browser instance                      │
│  • Persists between commands for fast operations           │
│  • Handles WebSocket streaming for preview                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Chromium (Browser)                       │
│  • Headless by default (--headed for debugging)            │
│  • Isolated sessions with --session flag                   │
│  • CDP support for Electron/WebView2                       │
└─────────────────────────────────────────────────────────────┘
```

### Key Innovation: Ref-Based Interaction

Traditional browser automation requires fragile selectors:
```bash
# CSS selector (breaks if class changes)
agent-browser click "#login-button"

# XPath (breaks if DOM structure changes)
agent-browser click "xpath=//button[contains(text(), 'Login')]"
```

**Ref-based interaction** provides deterministic selection:

```bash
# 1. Get snapshot with refs
$ agent-browser open example.com
$ agent-browser snapshot -i

# Output:
# - heading "Example Domain" [ref=e1] [level=1]
# - button "Submit" [ref=e2]
# - textbox "Email" [ref=e3] [placeholder="user@example.com"]
# - link "Learn more" [ref=e4]

# 2. Use refs to interact (deterministic, no re-query)
$ agent-browser click @e2                   # Click the button
$ agent-browser fill @e3 "test@example.com" # Fill the textbox
$ agent-browser get text @e1                # Get heading text
```

**Why Refs?**
- **Deterministic**: Ref points to exact element from snapshot
- **Fast**: No DOM re-query needed
- **AI-friendly**: Snapshot + ref workflow optimal for LLMs

### Optimal AI Workflow

```bash
# 1. Navigate and get snapshot
agent-browser open example.com
agent-browser snapshot -i --json   # AI parses tree and refs

# JSON output:
# {
#   "success": true,
#   "data": {
#     "snapshot": "- button \"Submit\" [ref=e2]...",
#     "refs": {
#       "e1": {"role": "heading", "name": "Title"},
#       "e2": {"role": "button", "name": "Submit"},
#       "e3": {"role": "textbox", "name": "Email"}
#     }
#   }
# }

# 2. AI identifies target refs from snapshot
# 3. Execute actions using refs
agent-browser click @e2
agent-browser fill @e3 "input text"

# 4. Get new snapshot if page changed
agent-browser snapshot -i --json
```

### Snapshot Filtering

Reduce output size for token efficiency:

```bash
# Interactive elements only (buttons, inputs, links)
agent-browser snapshot -i

# Compact (remove empty structural elements)
agent-browser snapshot -c

# Limit depth to 3 levels
agent-browser snapshot -d 3

# Scope to specific selector
agent-browser snapshot -s "#main"

# Combine options
agent-browser snapshot -i -c -d 5
```

### Session Management

Run multiple isolated browser instances:

```bash
# Different sessions
agent-browser --session agent1 open site-a.com
agent-browser --session agent2 open site-b.com

# Or via environment variable
AGENT_BROWSER_SESSION=agent1 agent-browser click "#btn"

# List active sessions
agent-browser session list
# Output:
# Active sessions:
# -> default
#    agent1
#    agent2
```

**Each session has its own**:
- Browser instance
- Cookies and storage
- Navigation history
- Authentication state

### Authenticated Sessions

Skip login flows with header-based authentication:

```bash
# Headers scoped to api.example.com only
agent-browser open api.example.com --headers '{"Authorization": "Bearer token123"}'

# Requests to api.example.com include auth header
agent-browser snapshot -i --json
agent-browser click @e2

# Navigate to another domain - headers NOT sent (safe!)
agent-browser open other-site.com
```

### WebSocket Streaming (Pair Browsing)

Stream the browser viewport for live preview:

```bash
# Start with streaming enabled
AGENT_BROWSER_STREAM_PORT=9223 agent-browser open example.com
```

**WebSocket Protocol** (`ws://localhost:9223`):

Receive frames:
```json
{
  "type": "frame",
  "data": "<base64-encoded-jpeg>",
  "metadata": {
    "deviceWidth": 1280,
    "deviceHeight": 720,
    "pageScaleFactor": 1,
    "scrollOffsetY": 0
  }
}
```

Send mouse events:
```json
{
  "type": "input_mouse",
  "eventType": "mousePressed",
  "x": 100,
  "y": 200,
  "button": "left",
  "clickCount": 1
}
```

**Use Cases**:
- Human watches AI agent navigate
- Remote control for debugging
- Collaborative human-AI browsing

### Core Commands

```bash
# Navigation
agent-browser open <url>              # Navigate to URL
agent-browser back                    # Go back
agent-browser forward                 # Go forward
agent-browser reload                  # Reload page

# Interaction
agent-browser click <sel>             # Click element
agent-browser fill <sel> <text>       # Clear and fill
agent-browser type <sel> <text>       # Type into element
agent-browser press <key>             # Press key (Enter, Tab)
agent-browser hover <sel>             # Hover element

# Information
agent-browser snapshot                # Accessibility tree with refs
agent-browser get text <sel>          # Get text content
agent-browser get html <sel>          # Get innerHTML
agent-browser get url                 # Get current URL
agent-browser get title               # Get page title

# Screenshots
agent-browser screenshot [path]       # Take screenshot
agent-browser screenshot --full       # Full page screenshot
agent-browser pdf <path>              # Save as PDF

# State
agent-browser is visible <sel>        # Check if visible
agent-browser is enabled <sel>        # Check if enabled
agent-browser is checked <sel>        # Check if checked

# Wait
agent-browser wait <selector>         # Wait for element
agent-browser wait <ms>               # Wait for time
agent-browser wait --text "Welcome"   # Wait for text
agent-browser wait --url "**/dash"    # Wait for URL pattern
```

### Integration with AI Agents

#### Claude Code Skill

```bash
# Install skill
cp -r node_modules/agent-browser/skills/agent-browser .claude/skills/
```

#### System Prompt Integration

```markdown
## Browser Automation

Use `agent-browser` for web automation. Core workflow:

1. `agent-browser open <url>` - Navigate to page
2. `agent-browser snapshot -i` - Get interactive elements with refs (@e1, @e2)
3. `agent-browser click @e1` / `fill @e2 "text"` - Interact using refs
4. Re-snapshot after page changes

Run `agent-browser --help` for all commands.
```

### Use Cases

1. **Web Scraping**: Extract data from JavaScript-heavy sites
2. **E2E Testing**: Automate testing of web applications
3. **Form Automation**: Fill forms and submit data
4. **UI Validation**: Verify UI elements and behavior
5. **Multi-Site Workflows**: Orchestrate actions across multiple sites

---

## autocoder - Multi-Session Agents

### Architecture Overview

autocoder uses a **two-agent pattern** for building complete applications across multiple sessions:

```
┌─────────────────────────────────────────────────────────────┐
│                   Session 1: Initializer                    │
│  • Reads app specification                                  │
│  • Generates feature test cases                             │
│  • Stores features in SQLite (features.db)                  │
│  • Sets up project structure + git                          │
│  • Exits after initialization                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                Session 2-N: Coding Agent                    │
│  • Picks up where previous session left off                │
│  • Gets next pending feature from SQLite                    │
│  • Implements feature + writes tests                        │
│  • Marks feature as passing in database                     │
│  • Auto-continues to next session (3 second delay)          │
│  • Ctrl+C to pause, resume with start script               │
└─────────────────────────────────────────────────────────────┘
```

### Feature Management with MCP

Features are stored in **SQLite** and exposed via **MCP server**:

```python
# Database schema (SQLAlchemy)
class Feature(Base):
    __tablename__ = "features"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String, default="pending")  # pending, passing, skipped
    priority = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
```

**MCP Tools** (exposed to agent):

```python
# Get next feature to implement
feature = feature_get_next()
# Returns: Feature with highest priority and "pending" status

# Mark feature complete
feature_mark_passing(feature_id=42)

# Skip feature (move to end of queue)
feature_skip(feature_id=42)

# Get progress statistics
stats = feature_get_stats()
# Returns: {"passing": 45, "total": 200, "percentage": 22.5}

# Get random passing features for regression testing
regression_features = feature_get_for_regression(count=5)
```

### Session Persistence

```
generations/my_project/
├── features.db               # SQLite database with feature state
├── prompts/
│   ├── app_spec.txt          # Application specification
│   ├── initializer_prompt.md # First session prompt
│   └── coding_prompt.md      # Continuation session prompt
├── init.sh                   # Environment setup script
├── claude-progress.txt       # Session progress notes
├── .git/                     # Version control
└── [application files]       # Generated application code
```

**Persistence Mechanisms**:
1. **SQLite Database**: Feature state, test results
2. **Git Commits**: Code changes with descriptive messages
3. **Progress File**: Session notes, decision tracking
4. **MCP Server**: State management tools

### Security Model

Defense-in-depth approach (see `security.py`):

```python
# Bash command allowlist
ALLOWED_COMMANDS = [
    # File inspection
    "ls", "cat", "head", "tail", "wc", "grep",

    # Node.js
    "npm", "node",

    # Version control
    "git",

    # Process management
    "ps", "lsof", "sleep", "pkill"  # dev processes only
]

# Filesystem restrictions
def validate_file_operation(path: str):
    project_root = Path("/path/to/project")
    resolved_path = Path(path).resolve()

    # Block operations outside project directory
    if not str(resolved_path).startswith(str(project_root)):
        raise SecurityError(f"Access denied: {path} is outside project")
```

**Security Layers**:
1. **OS-level Sandbox**: Isolated environment for bash commands
2. **Filesystem Restrictions**: File operations restricted to project directory
3. **Bash Allowlist**: Only specific commands permitted
4. **Security Hook**: Blocks commands not in allowlist

### Web UI

React-based monitoring interface:

```bash
# Start Web UI
./start_ui.sh   # macOS/Linux
start_ui.bat    # Windows

# Launches at http://localhost:5173
```

**UI Features**:
- Project selection and creation
- Kanban board view of features
- Real-time agent output streaming (WebSocket)
- Start/pause/stop controls
- Progress tracking

**WebSocket Events** (`/ws/projects/{project_name}`):
```typescript
// Progress updates
{
  "type": "progress",
  "passing": 45,
  "total": 200
}

// Agent status
{
  "type": "agent_status",
  "status": "running" | "paused" | "stopped" | "crashed"
}

// Log output
{
  "type": "log",
  "line": "[Tool: feature_mark_passing] Feature #42 marked as passing"
}

// Feature updates
{
  "type": "feature_update",
  "feature_id": 42,
  "status": "passing"
}
```

### Example Workflow

```python
# 1. Create project with /create-spec command
# User describes app: "Build a todo list with user authentication"

# 2. Initializer agent generates features.db
# Features generated:
# 1. User registration with email/password
# 2. Login/logout functionality
# 3. Create todo items
# 4. Mark todos as complete
# ... (50+ features total)

# 3. Coding agent starts implementing
session_2_output = """
[Feature: User registration with email/password]
[Implementing authentication routes...]
[Writing user model with password hashing...]
[Creating registration tests...]
[Tests passing: 1/50]
"""

# 4. Progress persists across sessions
# - features.db tracks which features are done
# - Git commits provide change history
# - Agent can pause and resume anytime

# 5. Final result: Complete application
# All 50 features implemented, tested, committed
```

### Integration with Other Patterns

**With claude-task-system**:
```python
# autocoder uses SQLite features
# claude-task-system uses git worktrees + filesystem state

# Combine for advanced workflow:
# 1. autocoder manages high-level features
# 2. claude-task-system manages sub-tasks per feature
# 3. Git worktrees isolate parallel work
```

**With tuicr**:
```bash
# After autocoder generates code, review with tuicr
cd generations/my_project
git status
tuicr

# Review all changes
# Add comments for issues
# Export feedback to clipboard
# Paste back to autocoder for fixes
```

### Use Cases

1. **Greenfield Projects**: Build new applications from specifications
2. **MVP Development**: Rapid prototyping with feature tracking
3. **Learning Projects**: Study how agents implement complete features
4. **Long-Running Tasks**: Projects spanning hours/days with session persistence

---

## nanocode - Minimal Agent Reference

### Architecture Overview

nanocode demonstrates a **complete agent loop in ~250 lines** with zero dependencies:

```
┌─────────────────────────────────────────────────────────────┐
│                    User Input                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Agent Loop (Main)                          │
│  while True:                                                │
│    1. Build messages array (system + conversation history) │
│    2. Call LLM with messages + tools                        │
│    3. Parse response for tool calls                         │
│    4. Execute tools and collect results                     │
│    5. Add tool results to conversation history             │
│    6. If no more tool calls, output final answer           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     Tool Registry                           │
│  • read(file_path, offset, limit)                          │
│  • write(file_path, content)                               │
│  • edit(file_path, old_string, new_string)                 │
│  • glob(pattern)                                           │
│  • grep(pattern, path)                                     │
│  • bash(command, timeout)                                  │
└─────────────────────────────────────────────────────────────┘
```

### Core Implementation

```python
#!/usr/bin/env python3
import json
import os
import subprocess
from pathlib import Path
from anthropic import Anthropic

# Tool definitions
TOOLS = [
    {
        "name": "read",
        "description": "Read file with line numbers, offset/limit",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string"},
                "offset": {"type": "number"},
                "limit": {"type": "number"}
            },
            "required": ["file_path"]
        }
    },
    # ... (write, edit, glob, grep, bash)
]

# Tool implementations
def tool_read(file_path: str, offset: int = 0, limit: int = None):
    with open(file_path) as f:
        lines = f.readlines()

    if limit:
        lines = lines[offset:offset + limit]

    # Return with line numbers (cat -n format)
    return "".join(f"{i+offset+1:6}→{line}" for i, line in enumerate(lines))

def tool_edit(file_path: str, old_string: str, new_string: str):
    with open(file_path) as f:
        content = f.read()

    if content.count(old_string) != 1:
        return f"Error: old_string must be unique (found {content.count(old_string)} matches)"

    new_content = content.replace(old_string, new_string)

    with open(file_path, 'w') as f:
        f.write(new_content)

    return "✓ Edit successful"

# Main agent loop
def agent_loop(user_message: str, conversation_history: list):
    messages = conversation_history + [{"role": "user", "content": user_message}]

    while True:
        # Call LLM with tools
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=8000,
            tools=TOOLS,
            messages=messages
        )

        # Check for tool calls
        if response.stop_reason == "end_turn":
            # No more tool calls, return final answer
            return response.content[0].text

        # Execute tools
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })

        # Add tool results to conversation
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

# Entry point
if __name__ == "__main__":
    conversation_history = []

    while True:
        user_input = input("❯ ")

        if user_input in ["/q", "exit"]:
            break

        if user_input == "/c":
            conversation_history = []
            continue

        response = agent_loop(user_input, conversation_history)
        print(response)

        conversation_history.append({"role": "user", "content": user_input})
        conversation_history.append({"role": "assistant", "content": response})
```

### Key Design Decisions

1. **Zero Dependencies**: Only uses Python stdlib + anthropic SDK
2. **Single File**: All code in one file for easy understanding
3. **Minimal Tools**: Six core tools cover most coding tasks
4. **Colored Output**: Terminal formatting for readability
5. **Conversation History**: Maintains context across turns

### Tool Implementations

```python
# glob: Find files by pattern (sorted by mtime)
def tool_glob(pattern: str):
    files = sorted(Path.cwd().glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return "\n".join(str(f) for f in files)

# grep: Search files for regex
def tool_grep(pattern: str, path: str = "."):
    result = subprocess.run(
        ["grep", "-rn", pattern, path],
        capture_output=True,
        text=True
    )
    return result.stdout

# bash: Run shell command
def tool_bash(command: str, timeout: int = 120):
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout
    )
    return result.stdout + result.stderr
```

### Example Session

```
────────────────────────────────────────
❯ what files are here?
────────────────────────────────────────

⏺ Glob(**/*.py)
  ⎿  nanocode.py

⏺ There's one Python file: nanocode.py

────────────────────────────────────────
❯ add a function that calculates fibonacci
────────────────────────────────────────

⏺ Read(nanocode.py)
⏺ Edit(nanocode.py)
  ⎿  Added fibonacci function

⏺ I've added a fibonacci function that uses recursion with memoization.

────────────────────────────────────────
❯ /q
```

### OpenRouter Support

Use any model via OpenRouter:

```bash
export OPENROUTER_API_KEY="your-key"
export MODEL="openai/gpt-5.2"
python nanocode.py
```

### Educational Value

**Learning Points**:
1. **Agent Loop Structure**: Demonstrates basic agent architecture
2. **Tool Use Pattern**: How LLMs call tools and process results
3. **State Management**: Simple conversation history
4. **Error Handling**: Basic error messages and recovery
5. **Terminal UI**: Colored output and commands

**Comparison to Production Systems**:

| Feature | nanocode | claude-flow |
|---------|----------|-------------|
| **Lines of Code** | ~250 | ~50,000+ |
| **Dependencies** | 1 (anthropic) | 100+ |
| **Tools** | 6 basic | 175+ MCP tools |
| **State** | In-memory list | HNSW + SQLite |
| **Multi-Agent** | No | Hive mind + swarms |
| **Learning** | No | Self-optimizing neural |
| **Use Case** | Education | Production |

### Use Cases

1. **Learning**: Understand agent fundamentals
2. **Prototyping**: Quick experiments with agent patterns
3. **Teaching**: Demonstrate agent architecture to others
4. **Reference**: Study minimal implementation before scaling up
5. **Customization**: Fork and modify for specific needs

---

## mcp-cli - MCP Tooling

### Architecture Overview

mcp-cli uses a **lazy, on-demand connection strategy** for token efficiency:

```
┌─────────────────────────────────────────────────────────────┐
│                      USER COMMANDS                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
    ┌───────────────────────┼───────────────────────┐
    │                       │                       │
    ▼                       ▼                       ▼
┌─────────┐          ┌─────────┐          ┌─────────────┐
│mcp-cli  │          │mcp-cli  │          │mcp-cli      │
│(list)   │          │grep "*" │          │server/tool  │
└─────────┘          └─────────┘          └─────────────┘
    │                       │                       │
    ▼                       ▼                       ▼
┌─────────┐          ┌─────────┐          ┌─────────────┐
│Connect  │          │Connect  │          │Connect to   │
│to ALL   │          │to ALL   │          │ONE server   │
│servers  │          │servers  │          │only         │
└─────────┘          └─────────┘          └─────────────┘
    │                       │                       │
    ▼                       ▼                       ▼
List tools          Search tools          Execute tool
    │                       │                       │
    ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  CLOSE CONNECTIONS                          │
└─────────────────────────────────────────────────────────────┘
```

**When are servers connected?**

| Command | Servers Connected |
|---------|-------------------|
| `mcp-cli` (list) | All N servers in parallel |
| `mcp-cli grep "*pattern*"` | All N servers in parallel |
| `mcp-cli server` | Only the specified server |
| `mcp-cli server/tool` | Only the specified server |
| `mcp-cli server/tool '{}'` | Only the specified server |

### Worker Pool Concurrency

For commands connecting to multiple servers:

```
┌─────────────────────────────────────────────────────────────┐
│              50 SERVERS CONFIGURED                          │
│   ┌────┐ ┌────┐ ┌────┐ ... ┌────┐ ┌────┐ ┌────┐           │
│   │ S1 │ │ S2 │ │ S3 │     │S48 │ │S49 │ │S50 │           │
│   └────┘ └────┘ └────┘     └────┘ └────┘ └────┘           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│         WORKER POOL (5 concurrent by default)               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Worker 1    Worker 2    Worker 3    Worker 4    W5  │   │
│  │    ▼           ▼           ▼           ▼        ▼    │   │
│  │  [S1]→[S6]→  [S2]→[S7]→  [S3]→[S8]→  [S4]→[S9]→[S5]→│   │
│  │   [S11]→...   [S12]→...   [S13]→...   [S14]→...[S10]→│   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  Total Time ≈ (N / concurrency) × avg_connection_time      │
│  50 servers @ 5 concurrency: ~10 batches × ~2s = ~20s      │
└─────────────────────────────────────────────────────────────┘
```

**Configuration**:
```bash
# Set concurrency (default: 5)
MCP_CONCURRENCY=10 mcp-cli

# Or export globally
export MCP_CONCURRENCY=10
```

### Automatic Retry with Exponential Backoff

```
┌───────────────────────────────────────────────────────────────┐
│                     INITIAL ATTEMPT                           │
└───────────────────────────────────────────────────────────────┘
                           ↓
                    ┌──────────────┐
                    │   FAILED?    │
                    └──────────────┘
                      │ YES      │ NO
                      ▼          ▼
            ┌──────────────┐   SUCCESS
            │  TRANSIENT?  │
            └──────────────┘
              │ YES    │ NO
              ▼        ▼
         RETRY with    FAIL with
         exponential   error message
         backoff
         (1s → 2s → 4s,
          max 3 retries)
```

**Transient errors** (auto-retried):
- Network: `ECONNREFUSED`, `ETIMEDOUT`, `ECONNRESET`
- HTTP: `502`, `503`, `504`, `429`

**Non-transient errors** (fail immediately):
- Config: Invalid JSON, missing fields
- Auth: `401`, `403`
- Tool: Validation errors, not found

### Core Workflow

```bash
# 1. List all servers and tools
$ mcp-cli
github
  • search_repositories
  • get_file_contents
  • create_or_update_file
filesystem
  • read_file
  • write_file
  • list_directory

# 2. With descriptions (use sparingly to avoid context bloat)
$ mcp-cli --with-descriptions
github
  • search_repositories - Search for GitHub repositories
  • get_file_contents - Get contents of a file or directory
filesystem
  • read_file - Read the contents of a file
  • write_file - Write content to a file

# 3. Search tools by pattern
$ mcp-cli grep "*file*"
github/get_file_contents
github/create_or_update_file
filesystem/read_file
filesystem/write_file

# 4. View tool schema
$ mcp-cli github/search_repositories
Tool: search_repositories
Server: github

Description:
  Search for GitHub repositories

Input Schema:
  {
    "type": "object",
    "properties": {
      "query": { "type": "string", "description": "Search query" },
      "page": { "type": "number" }
    },
    "required": ["query"]
  }

# 5. Call tool
$ mcp-cli github/search_repositories '{"query": "mcp server", "per_page": 5}'

# 6. JSON output for scripting
$ mcp-cli github/search_repositories '{"query": "mcp"}' --json | jq '.content[0].text'
```

### Stdin for Complex JSON

Avoid shell escaping issues:

```bash
# Using a heredoc with '-' for stdin (recommended)
mcp-cli server/tool - <<EOF
{"content": "Text with 'single quotes' and \"double quotes\""}
EOF

# Using a variable
JSON='{"message": "Hello, it'\''s a test"}'
echo "$JSON" | mcp-cli server/tool -

# From a file
cat args.json | mcp-cli server/tool -

# Using jq to build complex JSON
jq -n '{query: "mcp", filters: ["active", "starred"]}' | mcp-cli github/search -

# Complex command chaining
mcp-cli filesystem/search_files '{"path": "src/", "pattern": "*.ts"}' --json \
  | jq -r '.content[0].text' \
  | head -1 \
  | xargs -I {} sh -c 'mcp-cli filesystem/read_file "{\"path\": \"{}\"}"'
```

### Configuration

**mcp_servers.json** (compatible with Claude Desktop, Gemini, VS Code):

```json
{
  "mcpServers": {
    "local-server": {
      "command": "node",
      "args": ["./server.js"],
      "env": {
        "API_KEY": "${API_KEY}"
      },
      "cwd": "/path/to/directory"
    },
    "remote-server": {
      "url": "https://mcp.example.com",
      "headers": {
        "Authorization": "Bearer ${TOKEN}"
      }
    }
  }
}
```

**Environment Variable Substitution**: Use `${VAR_NAME}` syntax. Missing variables cause an error unless `MCP_STRICT_ENV=false`.

**Config Resolution Order**:
1. `MCP_CONFIG_PATH` environment variable
2. `-c/--config` command line argument
3. `./mcp_servers.json` (current directory)
4. `~/.mcp_servers.json`
5. `~/.config/mcp/mcp_servers.json`

### Integration with AI Agents

#### System Prompt Integration

```markdown
## MCP Servers

You have access to MCP (Model Context Protocol) servers via `mcp-cli`.

Available Commands:
```bash
mcp-cli                              # List all servers and tool names
mcp-cli <server>                     # Show server tools and parameters
mcp-cli <server>/<tool>              # Get tool JSON schema
mcp-cli <server>/<tool> '<json>'     # Call tool with JSON arguments
mcp-cli grep "<pattern>"             # Search tools by name
```

Workflow:
1. **Discover**: Run `mcp-cli` or `mcp-cli grep "<pattern>"`
2. **Inspect**: Run `mcp-cli <server>/<tool>` to get JSON schema
3. **Execute**: Run `mcp-cli <server>/<tool> '<json>'`

Rules:
1. Always check schema first
2. Quote JSON arguments
3. Use stdin (`-`) for complex JSON
```

#### Claude Code Skill

Create `mcp-cli/SKILL.md` in `~/.claude/skills/`:

```markdown
# MCP CLI Skill

This skill provides access to MCP servers via mcp-cli.

See [SKILL.md](https://github.com/philschmid/mcp-cli/blob/main/SKILL.md)
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_CONFIG_PATH` | Path to config file | (none) |
| `MCP_DEBUG` | Enable debug output | `false` |
| `MCP_TIMEOUT` | Request timeout (seconds) | `1800` |
| `MCP_CONCURRENCY` | Worker pool size | `5` |
| `MCP_MAX_RETRIES` | Retry attempts | `3` |
| `MCP_RETRY_DELAY` | Base retry delay (ms) | `1000` |
| `MCP_STRICT_ENV` | Error on missing ${VAR} | `true` |

### Use Cases

1. **Token-Efficient MCP Access**: Minimize context window usage
2. **Shell Scripting**: Chain MCP tools with jq, pipes, etc.
3. **Agent Tooling**: Provide on-demand tool access to AI agents
4. **Development**: Test MCP servers without full integration
5. **Automation**: Build workflows combining multiple MCP servers

---

## CodexMonitor - Multi-Agent Orchestration

### Architecture Overview

CodexMonitor is a **native macOS Tauri app** for orchestrating multiple Codex agents:

```
┌─────────────────────────────────────────────────────────────┐
│                  CodexMonitor (Tauri App)                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Frontend (React + TypeScript)           │   │
│  │  • Sidebar: Workspace management                     │   │
│  │  • Conversation view: Messages + reasoning          │   │
│  │  • Git panel: Diffs, commits, branches              │   │
│  │  • Plan panel: Turn-by-turn planning                │   │
│  │  • Debug panel: Warnings + errors                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                            ↓ IPC                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │               Backend (Rust)                         │   │
│  │  • Spawn codex app-server per workspace             │   │
│  │  • Stream JSON-RPC events                           │   │
│  │  • Manage worktrees (.codex-worktrees)              │   │
│  │  • Git operations (diff, log, branch)               │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓ stdio
┌─────────────────────────────────────────────────────────────┐
│              Codex app-server (per workspace)               │
│  • Thread management (start, resume, archive)               │
│  • Message streaming                                        │
│  • Model selection (Sonnet, Opus, Haiku)                    │
│  • Skills and prompts                                       │
└─────────────────────────────────────────────────────────────┘
```

### Key Features

#### 1. Workspace Management

```typescript
// Add workspace
await tauri.invoke("add_workspace", {
  name: "my-project",
  path: "/Users/me/projects/my-project"
});

// List workspaces
const workspaces = await tauri.invoke("list_workspaces");

// Update workspace settings
await tauri.invoke("update_workspace_settings", {
  workspace_id: "abc123",
  settings: {
    default_model: "sonnet",
    reasoning_effort: "medium",
    access_mode: "current"  // read-only | current | full-access
  }
});
```

**Workspace State**:
- Persisted to `workspaces.json` in app data directory
- Each workspace spawns one `codex app-server`
- Auto-reconnect on launch and window focus

#### 2. Thread Management

```typescript
// Start new thread
await tauri.invoke("start_thread", {
  workspace_id: "abc123",
  message: "Build a todo app with React"
});

// List threads (filtered by workspace cwd)
const threads = await tauri.invoke("list_threads", {
  workspace_id: "abc123"
});

// Resume thread (loads from disk)
await tauri.invoke("resume_thread", {
  workspace_id: "abc123",
  thread_id: "thread_xyz"
});

// Send user message
await tauri.invoke("send_user_message", {
  workspace_id: "abc123",
  thread_id: "thread_xyz",
  content: "Add user authentication"
});

// Interrupt turn (stop current thinking)
await tauri.invoke("turn_interrupt", {
  workspace_id: "abc123",
  thread_id: "thread_xyz"
});
```

#### 3. Git Worktree Agents

Create isolated git worktrees per agent:

```typescript
// Add worktree agent
await tauri.invoke("add_worktree", {
  workspace_id: "abc123",
  name: "feature-auth",
  branch: "feature/authentication"
});

// Worktree structure:
// worktrees/abc123/
// ├── feature-auth/       # Git worktree for feature-auth agent
// │   ├── .git            # Git metadata (linked to main repo)
// │   └── [project files] # Isolated working directory
// └── bugfix-login/       # Git worktree for bugfix-login agent
//     ├── .git
//     └── [project files]

// Remove worktree
await tauri.invoke("remove_worktree", {
  workspace_id: "abc123",
  worktree_name: "feature-auth"
});
```

**Worktree Benefits**:
- **Isolation**: Each agent works in separate directory
- **Parallel Work**: Multiple agents on different features
- **No Conflicts**: Independent working trees
- **Git Integration**: Commits, branches, diffs per worktree

#### 4. Git Panel

```typescript
// Get git status
const status = await tauri.invoke("get_git_status", {
  workspace_id: "abc123"
});
// Returns: { modified: [...], untracked: [...], staged: [...] }

// Get git diffs
const diffs = await tauri.invoke("get_git_diffs", {
  workspace_id: "abc123",
  file_path: "src/auth.ts"  // Optional: specific file
});

// Get commit log
const log = await tauri.invoke("get_git_log", {
  workspace_id: "abc123",
  max_count: 50
});

// Get remote URL
const remote = await tauri.invoke("get_git_remote", {
  workspace_id: "abc123"
});
// Opens commits on GitHub when remote detected

// List branches
const branches = await tauri.invoke("list_git_branches", {
  workspace_id: "abc123"
});

// Checkout branch
await tauri.invoke("checkout_git_branch", {
  workspace_id: "abc123",
  branch_name: "feature/auth"
});

// Create branch
await tauri.invoke("create_git_branch", {
  workspace_id: "abc123",
  branch_name: "feature/new-feature",
  base_branch: "main"  // Optional
});
```

#### 5. Model Selection & Context

```typescript
// List available models
const models = await tauri.invoke("model_list");
// Returns: ["sonnet", "opus", "haiku"]

// Select model for thread
// (Set via workspace settings)

// Context usage ring
// Displays token usage as visual ring indicator

// Reasoning effort selector
// Options: low, medium, high
```

#### 6. JSON-RPC Event Streaming

**Real-time events** from codex app-server:

```typescript
// Reasoning blocks
{
  "type": "reasoning_block",
  "content": "Planning the authentication flow..."
}

// Tool execution
{
  "type": "tool_use",
  "tool": "write_file",
  "input": { "path": "src/auth.ts", "content": "..." }
}

// Diff display
{
  "type": "diff",
  "file": "src/auth.ts",
  "hunks": [...]
}

// Approval request
{
  "type": "server_request",
  "request_id": "req_123",
  "message": "Approve file write?"
}

// Respond to approval
await tauri.invoke("respond_to_server_request", {
  workspace_id: "abc123",
  request_id: "req_123",
  response: { "approved": true }
});
```

#### 7. Skills & Prompts

```typescript
// List skills
const skills = await tauri.invoke("skills_list");

// Skills menu in UI
// Composer autocomplete for:
// - $skill - Activate skill
// - /prompts:... - Custom prompts from ~/.codex/prompts
// - /review ... - Review commands
// - @file - File references

// Custom prompts load from:
// $CODEX_HOME/prompts (or ~/.codex/prompts)
// Optional frontmatter for description/arguments
```

#### 8. Review Runs

```typescript
// Start review
await tauri.invoke("start_review", {
  workspace_id: "abc123",
  review_type: "uncommitted"  // uncommitted | base_branch | commits | custom
});

// Review types:
// - uncommitted: Review unstaged/staged changes
// - base_branch: Compare against base branch
// - commits: Review specific commits
// - custom: Custom instructions
```

### UI Layout

```
┌─────────────────────────────────────────────────────────────┐
│  CodexMonitor                                    □ ○ ⊗      │
├────────┬────────────────────────────────────────┬───────────┤
│        │                                        │           │
│ Work-  │         Conversation View              │   Git     │
│ spaces │  ┌────────────────────────────────┐   │   Panel   │
│        │  │ [Reasoning]                    │   │           │
│ • main │  │ Planning auth flow...          │   │ Changes:  │
│ • api  │  │                                │   │ ✓ auth.ts │
│ ▸ web  │  ├────────────────────────────────┤   │ ✓ db.ts   │
│        │  │ [Tool: write_file]             │   │           │
│ Wor-   │  │ Writing src/auth.ts            │   │ Commits:  │
│ ktrees │  ├────────────────────────────────┤   │ • feat    │
│        │  │ [User Message]                 │   │ • fix     │
│ + feat │  │ Add login endpoint             │   │           │
│   auth │  └────────────────────────────────┘   │ Branches: │
│        │                                        │ * main    │
│        │  [Composer with image attach]          │   dev     │
│        │  ┌────────────────────────────────┐   │           │
│        │  │ Type message... [📎] [📷]       │   │           │
│        │  └────────────────────────────────┘   │           │
│        │                                        │           │
├────────┴────────────────────────────────────────┴───────────┤
│  Plan Panel │ Debug Panel │ Context: ●●●○○ 60%             │
└─────────────────────────────────────────────────────────────┘
```

**Resizable Panels**:
- Sidebar (workspaces/worktrees)
- Right panel (git)
- Bottom panel (plan/debug)
- Sizes persisted to localStorage

**Responsive Layouts**:
- Desktop: Full layout
- Tablet: Collapsible panels
- Phone: Tabbed navigation

### Integration with Other Patterns

**With autocoder**:
```bash
# Use CodexMonitor to manage autocoder workspaces
# 1. Add autocoder project as workspace
# 2. Monitor feature implementation in real-time
# 3. Review git diffs visually
# 4. Create worktrees for parallel features
```

**With tuicr**:
```bash
# After agent generates code in CodexMonitor:
# 1. View diffs in Git Panel
# 2. Export to terminal with tuicr for detailed review
# 3. Copy feedback to clipboard
# 4. Paste back into CodexMonitor conversation
```

**With git worktrees (claude-task-system pattern)**:
```bash
# CodexMonitor manages worktrees visually
# - Create/delete worktrees from UI
# - Switch between worktree agents
# - View worktree-specific git state
```

### Use Cases

1. **Multi-Project Management**: Work on multiple codebases with separate agents
2. **Parallel Development**: Isolate feature work in git worktrees
3. **Team Collaboration**: Share workspace configurations
4. **Visual Monitoring**: Watch agent reasoning and tool execution
5. **Git Integration**: Manage branches, review diffs, inspect commits

---

## tuicr - Human-in-the-Loop Review

### Architecture Overview

tuicr provides a **GitHub-style diff viewer in the terminal** for reviewing AI-generated code:

```
┌─────────────────────────────────────────────────────────────┐
│                    Git Repository                           │
│  • Detect changes (git diff / jj diff / hg diff)            │
│  • Support unstaged, staged, commits                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                       tuicr TUI                             │
│  ┌──────────────┬──────────────────────────────────────┐   │
│  │ File List    │  Diff View (Unified/Side-by-Side)    │   │
│  │              │                                       │   │
│  │ ✓ auth.rs    │  @@ -42,7 +42,8 @@                  │   │
│  │   config.rs  │  - const TIMEOUT = 300;  [ISSUE]     │   │
│  │   db.rs      │  + const TIMEOUT = 30;               │   │
│  │              │                                       │   │
│  │              │  ... expand (15 lines) ...           │   │
│  │              │                                       │   │
│  │              │  - old code                          │   │
│  │              │  + new code  [SUGGESTION]            │   │
│  └──────────────┴──────────────────────────────────────┘   │
│                                                             │
│  [Comment Mode]                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Type: ISSUE ⎵ SUGGESTION NOTE PRAISE                │   │
│  │ Comment: Magic number should be named constant      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Clipboard Export                           │
│  Structured Markdown optimized for LLM consumption          │
│                                                             │
│  I reviewed your code and have the following comments.     │
│  Please address them.                                      │
│                                                             │
│  Comment types: ISSUE (problems to fix), ...               │
│                                                             │
│  1. **[ISSUE]** `auth.rs:42` - Magic number should be...  │
│  2. **[SUGGESTION]** `config.rs` - Consider adding...     │
└─────────────────────────────────────────────────────────────┘
```

### Key Features

#### 1. Infinite Scroll Diff View

All changed files in one continuous scroll:

```
────────────────────────────────────────────────────────────────
FILE: src/auth.rs
────────────────────────────────────────────────────────────────
@@ -1,10 +1,12 @@
 use bcrypt::{hash, verify};
+use jwt::{encode, decode};

 const SALT_ROUNDS: u32 = 10;
+const JWT_SECRET: &str = "secret";  // [ISSUE] Line 5

────────────────────────────────────────────────────────────────
FILE: src/config.rs
────────────────────────────────────────────────────────────────
@@ -42,7 +42,8 @@
-const TIMEOUT = 300;
+const TIMEOUT = 30;  // [SUGGESTION] Line 43

... expand (15 lines) ...

────────────────────────────────────────────────────────────────
FILE: src/db.rs
────────────────────────────────────────────────────────────────
...
```

**Navigation** (vim keybindings):
- `j/k` - Scroll down/up
- `{/}` - Jump to previous/next file
- `[/]` - Jump to previous/next hunk
- `g/G` - Go to first/last file
- `Ctrl-d/u` - Half page down/up

#### 2. Expandable Context

Hidden context between hunks can be revealed:

```
@@ -10,5 +10,7 @@
 fn login() {

... expand (15 lines) ...  ← Press Enter to reveal

@@ -30,3 +32,5 @@
 fn logout() {
```

**Expanding context**:
- Press `Enter` on "... expand (N lines) ..." line
- Reveals hidden lines between hunks
- Helps understand surrounding code

#### 3. Typed Comments

Four comment types with specific purposes:

| Type | Purpose | Use When |
|------|---------|----------|
| **ISSUE** | Problems to fix | Bugs, errors, security issues |
| **SUGGESTION** | Improvements | Better patterns, optimizations |
| **NOTE** | Observations | Questions, clarifications |
| **PRAISE** | Positive feedback | Good practices, clever solutions |

**Adding comments**:
```
# Line comment (on a diff line)
c → Add line comment
Tab → Cycle type (NOTE → SUGGESTION → ISSUE → PRAISE)
Type comment text
Enter → Save

# File comment (anywhere)
C → Add file comment
Tab → Cycle type
Type comment text
Enter → Save

# Edit/delete comments
i → Edit comment at cursor
dd → Delete comment at cursor
```

#### 4. Review Tracking

Track review progress:

```bash
# Mark file as reviewed
r → Toggle file reviewed

# File list shows review status
✓ auth.rs        [REVIEWED]
  config.rs      [2 COMMENTS]
  db.rs          [UNREVIEWED]
```

**Session persistence**:
- Reviews auto-save to `~/.local/share/tuicr/reviews/`
- Reload on restart in same repository
- Preserves comments and reviewed status

#### 5. Clipboard Export

Export structured Markdown optimized for LLMs:

```markdown
I reviewed your code and have the following comments. Please address them.

Comment types: ISSUE (problems to fix), SUGGESTION (improvements), NOTE (observations), PRAISE (positive feedback)

1. **[ISSUE]** `src/auth.rs:5` - Hard-coded JWT secret is a security risk. Use environment variable.

2. **[SUGGESTION]** `src/config.rs:43` - Consider using a named constant for timeout value instead of magic number.

3. **[NOTE]** `src/auth.rs` - Should we add rate limiting to login endpoint?

4. **[PRAISE]** `src/db.rs:120` - Good use of connection pooling for performance.
```

**Export commands**:
- `y` - Copy review to clipboard
- `:clip` / `:export` - Same as `y`
- `:wq` / `:x` - Save and quit (prompts to copy if comments exist)

### VCS Support

**Detection order**: Jujutsu → Git → Mercurial

```bash
# Git (default)
cd /path/to/git/repo
tuicr

# Jujutsu (requires --features jj at compile time)
cd /path/to/jj/repo
tuicr
# Note: jj repos are Git-backed, so git is tried first

# Mercurial (requires --features hg at compile time)
cd /path/to/hg/repo
tuicr
```

**Supported diff modes**:
- **Unstaged changes**: Default if present
- **Staged changes**: Included with unstaged
- **Commit selection**: If no unstaged/staged changes, select commits

#### Commit Selection

When no unstaged changes:

```
Select commits to review (Space to toggle, Enter to confirm):

○ feat: Add authentication (3 files changed)
● fix: Update timeout constant (1 file changed)
○ docs: Update README (1 file changed)

[Space] Toggle  [Enter] Confirm  [q] Quit
```

### Workflow Example

```bash
# 1. Agent generates code
# (via Claude Code, autocoder, etc.)

# 2. Review changes with tuicr
cd /path/to/project
tuicr

# 3. Navigate and add comments
j j j           # Scroll down
c               # Add comment
Tab Tab         # Cycle to ISSUE type
"Magic number should be named constant"
Enter           # Save comment

# 4. Mark files reviewed
}               # Jump to next file
r               # Mark as reviewed
}               # Next file
r               # Mark as reviewed

# 5. Export feedback
:clip           # Copy to clipboard

# 6. Paste back to agent
# Agent sees structured feedback:
# 1. **[ISSUE]** `config.rs:43` - Magic number...
# 2. **[SUGGESTION]** `auth.rs` - Consider adding...

# 7. Agent fixes issues
# All issues addressed in one pass (batch feedback)

# 8. Review again
tuicr           # Previous review restored from session
# Review new changes
# Repeat until satisfied
```

### Integration with Other Patterns

**With autocoder**:
```bash
# After autocoder generates features
cd generations/my_project
tuicr

# Review all generated code
# Export feedback
# Paste into autocoder for fixes
```

**With CodexMonitor**:
```bash
# After CodexMonitor agent makes changes
# 1. View diffs in Git Panel (visual)
# 2. Export to terminal for detailed review
tuicr

# 3. Add comments
# 4. Export to clipboard
# 5. Paste back into CodexMonitor conversation
```

**With claude-task-system**:
```bash
# After task implementation
tuicr

# Review task changes
# Check if tests are locked (no tampering)
# Verify implementation matches requirements
# Export feedback for agent to address
```

### Keybindings Reference

#### Navigation
- `j/k` / `↓/↑` - Scroll down/up
- `h/l` / `←/→` - Scroll left/right
- `Ctrl-d/u` - Half page down/up
- `Ctrl-f/b` - Full page down/up
- `g/G` - Go to first/last file
- `{/}` - Jump to previous/next file
- `[/]` - Jump to previous/next hunk
- `Enter` - Expand/collapse hidden context
- `zz` - Center cursor

#### Panel Focus
- `Tab` - Toggle focus (file list ↔ diff)
- `;h` - Focus file list
- `;l` - Focus diff view
- `;e` - Toggle file list visibility

#### Review Actions
- `r` - Toggle file reviewed
- `c` - Add line comment (or file comment if not on diff line)
- `C` - Add file comment
- `dd` - Delete comment at cursor
- `i` - Edit comment at cursor
- `v` - Toggle diff view (unified / side-by-side)
- `y` - Copy review to clipboard

#### Comment Mode
- `Tab` - Cycle comment type
- `Enter` / `Ctrl-Enter` / `Ctrl-s` - Save comment
- `Shift-Enter` / `Ctrl-j` - Insert newline
- `Ctrl-w` - Delete word
- `Ctrl-u` - Clear line
- `Esc` / `Ctrl-c` - Cancel

#### Commands
- `:w` - Save session
- `:e` / `:reload` - Reload diff files
- `:clip` / `:export` - Copy review to clipboard
- `:q` - Quit
- `:x` / `:wq` - Save and quit (prompts to copy if comments exist)
- `?` - Toggle help
- `q` - Quick quit

### Use Cases

1. **AI Code Review**: Review AI-generated code before accepting
2. **Batch Feedback**: Collect all comments, send to agent in one pass
3. **Learning**: Understand what agents generate by reviewing carefully
4. **Quality Control**: Maintain standards in AI-assisted development
5. **Documentation**: Use comments as inline documentation for decisions

---

## Integration Patterns

### Pattern 1: Multi-Session Development with Memory

**Repositories**: autocoder + SimpleMem

```python
# Use autocoder for feature implementation
# Use SimpleMem to remember context across sessions

from simplemem import SimpleMemSystem
from autocoder import FeatureManager

# Initialize memory for project
memory = SimpleMemSystem()

# Index all features with context
features = FeatureManager.get_all()
for feature in features:
    memory.add_dialogue(
        speaker="feature",
        content=f"{feature.name}: {feature.description}\n{feature.test_case}",
        timestamp=feature.created_at
    )

memory.finalize()

# During coding session, retrieve relevant features
def get_feature_context(query: str):
    return memory.ask(query, k=5)

# Example:
context = get_feature_context("What authentication features exist?")
# Returns compressed memory of auth-related features
```

**Benefits**:
- Fast feature lookup across large projects
- Token-efficient context retrieval
- Persistent memory of design decisions

---

### Pattern 2: Browser Automation with Review

**Repositories**: agent-browser + tuicr

```bash
# 1. Agent automates browser testing
agent-browser open https://app.example.com
agent-browser snapshot -i --json > snapshot.json

# Agent analyzes snapshot and generates test script
# test.sh:
# agent-browser click @e2
# agent-browser fill @e3 "test@example.com"
# agent-browser click @e5

# 2. Agent modifies code based on UI issues
# (generates fixes in code)

# 3. Review changes with tuicr
tuicr

# 4. Export feedback
:clip

# 5. Agent applies fixes
# Iterates until tests pass
```

**Benefits**:
- End-to-end workflow (browser → code → review)
- Human oversight on automated changes
- Batch feedback reduces iteration cycles

---

### Pattern 3: Multi-Agent Orchestration with Tooling

**Repositories**: CodexMonitor + mcp-cli + SimpleMem

```bash
# 1. Set up MCP servers for agent tooling
# mcp_servers.json:
{
  "mcpServers": {
    "simplemem": {
      "url": "https://mcp.simplemem.cloud/mcp",
      "headers": {"Authorization": "Bearer token"}
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
    }
  }
}

# 2. Use mcp-cli for on-demand tool access
# Agent in CodexMonitor calls:
mcp-cli simplemem/search_memories '{"query": "authentication patterns"}'

# 3. SimpleMem provides token-efficient memory
# Agent retrieves relevant context without bloating prompt

# 4. CodexMonitor visualizes multi-agent coordination
# - Agent 1: Main feature development
# - Agent 2 (worktree): Parallel bug fix
# - Both use SimpleMem for shared knowledge
```

**Benefits**:
- Multi-agent coordination with shared memory
- Token-efficient tooling via mcp-cli
- Visual monitoring via CodexMonitor

---

### Pattern 4: Educational Pipeline

**Repositories**: nanocode → agent-browser → autocoder

```python
# Learning progression:

# 1. Start with nanocode (minimal agent)
python nanocode.py
# Understand basic agent loop, tool use, conversation history

# 2. Add browser automation (agent-browser)
# Extend nanocode with browser tool:
def tool_browser(command: str):
    result = subprocess.run(["agent-browser"] + command.split(), capture_output=True)
    return result.stdout

# 3. Study autocoder (multi-session persistence)
# Learn SQLite state management, two-agent pattern, MCP servers

# 4. Build custom agent combining patterns
# - nanocode's simplicity
# - agent-browser's tooling
# - autocoder's persistence
```

**Benefits**:
- Progressive learning curve
- Hands-on pattern extraction
- Foundation for custom agents

---

### Pattern 5: Production Development Workflow

**Repositories**: All 7 repositories

```bash
# Complete production workflow:

# 1. Initialize project with autocoder
cd autocoder
./start.sh
# Create project: "E-commerce platform with auth, cart, checkout"
# Initializer generates 200 features in features.db

# 2. Monitor with CodexMonitor
# Add autocoder project as workspace
# Visual monitoring of feature implementation

# 3. Use SimpleMem for knowledge retention
# Agent indexes:
# - Feature descriptions
# - Design decisions
# - API specifications
# Token-efficient retrieval during coding

# 4. Browser testing with agent-browser
# Agent tests checkout flow:
agent-browser open http://localhost:3000
agent-browser snapshot -i --json
# Generates automated test scripts

# 5. Review with tuicr
tuicr
# Add comments for issues
# Export feedback

# 6. Access MCP tools via mcp-cli
# Agent uses on-demand tools:
mcp-cli github/search_repositories '{"query": "payment gateway"}'
mcp-cli simplemem/search_memories '{"query": "checkout implementation"}'

# 7. Learn from nanocode
# Study minimal implementation for custom tools
# Extract patterns for domain-specific agents
```

**Benefits**:
- Complete development lifecycle
- Multi-session persistence
- Human oversight at key points
- Token-efficient tooling
- Educational reference

---

## Comparison Matrix

### Memory & State Management

| Repository | Type | Speed | Token Efficiency | Persistence | Best For |
|------------|------|-------|------------------|-------------|----------|
| **SimpleMem** | Semantic compression | ⚡⚡⚡ Fast (388s) | ⭐⭐⭐ 30× fewer tokens | SQLite + LanceDB | Production memory |
| **basic-memory** | Markdown knowledge graph | ⚡⚡ Medium | ⭐⭐ Human-readable | Files + SQLite | Cross-LLM knowledge |
| **autocoder** | SQLite features | ⚡⚡ Medium | ⭐⭐ Feature state | SQLite + git | Multi-session dev |
| **nanocode** | In-memory list | ⚡ Slow | ⭐ Full history | None | Learning/prototyping |

### Tool Integration

| Repository | Tools | Integration | Output | Best For |
|------------|-------|-------------|--------|----------|
| **agent-browser** | Browser automation | Playwright | JSON + refs | Web interaction |
| **mcp-cli** | MCP servers | Stdio + HTTP | JSON + text | On-demand tools |
| **nanocode** | 6 basic tools | Python functions | Text | Education |
| **CodexMonitor** | Git + codex | JSON-RPC | Visual UI | Orchestration |

### Multi-Agent Support

| Repository | Agents | Coordination | State Sharing | UI |
|------------|--------|--------------|---------------|-----|
| **CodexMonitor** | Multiple workspaces + worktrees | Independent | None | Native macOS |
| **autocoder** | 2 (initializer + coding) | Sequential | SQLite | React Web UI |
| **nanocode** | Single | N/A | N/A | Terminal |

### Human-in-the-Loop

| Repository | Review Type | Feedback Format | Workflow | Best For |
|------------|-------------|-----------------|----------|----------|
| **tuicr** | Code review | Typed comments → Markdown | Batch feedback | AI-generated code |
| **CodexMonitor** | Turn interruption | Approvals | Real-time control | Live monitoring |
| **autocoder** | Web UI monitoring | Progress tracking | Passive observation | Background work |

### Learning Curve

| Repository | Complexity | Lines of Code | Dependencies | Learning Value |
|------------|------------|---------------|--------------|----------------|
| **nanocode** | ⭐ Minimal | ~250 | 1 | ⭐⭐⭐ High |
| **agent-browser** | ⭐⭐ Low | ~5,000 | Moderate | ⭐⭐⭐ High |
| **tuicr** | ⭐⭐ Low | ~10,000 | Moderate | ⭐⭐ Medium |
| **mcp-cli** | ⭐⭐ Low | ~3,000 | Low | ⭐⭐ Medium |
| **SimpleMem** | ⭐⭐⭐ Medium | ~15,000 | Moderate | ⭐⭐⭐ High |
| **autocoder** | ⭐⭐⭐ Medium | ~20,000 | Moderate | ⭐⭐⭐ High |
| **CodexMonitor** | ⭐⭐⭐⭐ High | ~30,000 | High | ⭐⭐ Medium |

---

## Quick Reference

### When to Use Which Repository

**Choose SimpleMem when**:
- You need production-grade long-term memory
- Token efficiency is critical
- Fast retrieval (< 400ms) is required
- Working with conversational agents

**Choose agent-browser when**:
- Automating web applications
- AI agents need browser interaction
- Testing JavaScript-heavy sites
- Skipping manual login flows

**Choose autocoder when**:
- Building complete applications from specs
- Need multi-session persistence
- Want feature tracking with SQLite
- Building MVPs or prototypes

**Choose nanocode when**:
- Learning agent architecture
- Prototyping agent patterns
- Teaching others about agents
- Building minimal custom agents

**Choose mcp-cli when**:
- Minimizing context window usage
- Shell-scripting AI workflows
- On-demand MCP tool access
- Testing MCP servers

**Choose CodexMonitor when**:
- Managing multiple agent workspaces
- Need visual monitoring
- Working with git worktrees
- Prefer native macOS UI

**Choose tuicr when**:
- Reviewing AI-generated code
- Need batch feedback workflow
- Want terminal-based reviews
- Maintaining code quality standards

---

## Installation Summary

```bash
# SimpleMem
git clone https://github.com/aiming-lab/SimpleMem
cd SimpleMem
pip install -r requirements.txt
cp config.py.example config.py
# Edit config.py with API key

# agent-browser
npm install -g agent-browser
agent-browser install

# autocoder
git clone https://github.com/leonvanzyl/autocoder
cd autocoder
./start.sh  # or start.bat on Windows

# nanocode
git clone https://github.com/1rgs/nanocode
cd nanocode
export ANTHROPIC_API_KEY="your-key"
python nanocode.py

# mcp-cli
curl -fsSL https://raw.githubusercontent.com/philschmid/mcp-cli/main/install.sh | bash
# or: bun install -g https://github.com/philschmid/mcp-cli

# CodexMonitor
git clone https://github.com/Dimillian/CodexMonitor
cd CodexMonitor
npm install
npm run tauri dev

# tuicr
brew install agavra/tap/tuicr
# or: cargo install tuicr
```

---

## Further Reading

- [SimpleMem Paper (arXiv)](https://arxiv.org/abs/2601.02553)
- [agent-browser Skill](https://github.com/vercel-labs/agent-browser/blob/main/skills/agent-browser/SKILL.md)
- [autocoder Video Tutorial](https://youtu.be/lGWFlpffWk4)
- [nanocode GitHub](https://github.com/1rgs/nanocode)
- [mcp-cli SKILL.md](https://github.com/philschmid/mcp-cli/blob/main/SKILL.md)
- [CodexMonitor README](https://github.com/Dimillian/CodexMonitor)
- [tuicr Website](https://tuicr.dev)

---

**Last Updated**: 2026-01-16
**Repositories**: 7 from GitHub Trending
**Total Reference Collection**: 24 repositories (17 previous + 7 new)
