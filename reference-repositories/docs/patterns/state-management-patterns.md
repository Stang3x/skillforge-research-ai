# State Management Patterns for Agentic Systems

**Extracted from**: AutoGPT, LangGraph, basic-memory, claude-flow, claude-task-system
**Pattern Category**: Architecture & Infrastructure
**Last Updated**: 2026-01-15

## Overview

State management is **critical** for agentic systems that need to:
1. Maintain context across multiple agent executions
2. Persist knowledge between conversations/sessions
3. Coordinate multiple agents with shared state
4. Track workflow progress and enable resumption
5. Build knowledge graphs that grow over time

This document catalogs proven state management patterns from leading agentic frameworks.

---

## Pattern 1: Checkpointing with Graph State (LangGraph)

**Source**: `references/langgraph/`
**Use Case**: Persistent state across agent loop iterations with branching support

### Architecture

```python
from langgraph.graph import StateGraph
from langgraph.checkpoint.sqlite import SqliteSaver

# Define state schema
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    current_task: str
    completed_steps: List[str]
    next_action: Optional[str]
```

**Key Components**:
1. **State Schema** - TypedDict defining all state fields
2. **State Reducer** - Functions that update state (e.g., `add_messages`)
3. **Checkpointer** - Persistence layer (SQLite, PostgreSQL, etc.)
4. **Thread ID** - Unique identifier for conversation/session

### Implementation

```python
# Create checkpointer
memory = SqliteSaver.from_conn_string(":memory:")

# Build graph with checkpointing
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_agent)
workflow.add_node("tools", execute_tools)
workflow.set_entry_point("agent")

# Compile with checkpointer
graph = workflow.compile(checkpointer=memory)

# Use with thread_id for persistence
config = {"configurable": {"thread_id": "conversation-123"}}
result = graph.invoke(initial_state, config)

# Resume later with same thread_id
continued_result = graph.invoke(new_input, config)  # Loads checkpoint automatically
```

### State Reducers

**Purpose**: Define how new values merge with existing state

```python
# Message accumulator
def add_messages(existing: list, new: list) -> list:
    """Append new messages to existing list."""
    return existing + new

# Last-write-wins
def replace(existing: Any, new: Any) -> Any:
    """Replace with new value."""
    return new

# Set union
def union(existing: set, new: set) -> set:
    """Merge sets."""
    return existing | new
```

### Branching & Time Travel

```python
# Get checkpoint history
checkpoints = graph.get_state_history(config)

# Rewind to specific checkpoint
past_checkpoint = checkpoints[5]  # 5 steps back
graph.update_state(config, past_checkpoint.values)

# Branch from checkpoint
branch_config = {"configurable": {"thread_id": "conversation-123-branch"}}
graph.invoke(alternative_input, branch_config)
```

### Advantages
- ✅ Automatic state persistence at each node
- ✅ Time travel and branching support
- ✅ Type-safe state with TypedDict
- ✅ Pluggable backends (SQLite, PostgreSQL, Redis)
- ✅ Concurrent safe with thread isolation

### Limitations
- ❌ Requires explicit state schema definition
- ❌ State limited to JSON-serializable types
- ❌ No cross-thread queries (each thread isolated)

---

## Pattern 2: File-Based State with Markdown (basic-memory)

**Source**: `references/basic-memory/`
**Use Case**: Human-readable persistent knowledge graph with bi-directional sync

### Architecture

```
Markdown Files (~/basic-memory/*.md)
    ↕ (bidirectional sync)
SQLite Database (knowledge graph index)
    ↕ (MCP protocol)
LLM Tools (read/write/search/traverse)
```

**Storage Layers**:
1. **Primary**: Markdown files on filesystem (human-editable)
2. **Index**: SQLite database (queryable knowledge graph)
3. **Sync**: Bidirectional synchronization on file changes

### Data Model

```python
# Entity = node in knowledge graph
class Entity:
    id: int                    # Database ID
    external_id: str           # Stable UUID for API
    title: str                 # Entity title
    entity_type: str           # Type (note, person, etc.)
    entity_metadata: dict      # JSON from frontmatter
    permalink: str             # URI slug
    file_path: str             # Relative path to .md file
    checksum: str              # For change detection
    mtime: float               # File modification time
    observations: List[Observation]  # Facts about entity
    relations: List[Relation]  # Links to other entities

# Observation = atomic fact
class Observation:
    content: str               # Observation text
    category: str              # Semantic type (method, tip, fact)
    context: str               # Optional context
    tags: List[str]            # Hashtags

# Relation = directed link
class Relation:
    from_id: int               # Source entity
    to_id: int                 # Target entity (nullable)
    to_name: str               # WikiLink name (for fuzzy resolution)
    relation_type: str         # Semantic relation (requires, relates_to)
    context: str               # Optional context
```

### Markdown Format

**File Structure**:
```markdown
---
title: Coffee Brewing Methods
type: note
permalink: coffee-brewing-methods
tags:
  - coffee
  - brewing
---

# Coffee Brewing Methods

## Observations

- [method] Pour over extracts more floral notes than French press
- [tip] Grind size should be medium-fine for pour over #brewing
- [fact] Lighter roasts contain more caffeine than dark roasts

## Relations

- requires [[Burr Grinder]]
- relates_to [[Morning Routine]]
- pairs_well_with [[Ethiopian Beans]]
```

**Semantic Patterns**:
- `[category] content #tags (context)` → Observation
- `relation_type [[WikiLink]] (context)` → Relation

### Synchronization

**File → Database (Import)**:
```python
def sync_file_to_db(file_path: Path):
    # 1. Detect changes
    file_stats = os.stat(file_path)
    entity = db.get_entity_by_path(file_path)

    if not needs_sync(entity, file_stats):
        return

    # 2. Parse Markdown
    with open(file_path) as f:
        post = frontmatter.load(f)
        metadata = post.metadata
        content = post.content

    # 3. Extract entities
    parsed = parse_entity_markdown(content)

    # 4. Update database
    with db.transaction():
        entity.update(metadata)
        entity.observations = parsed.observations
        entity.relations = parsed.relations
        entity.mtime = file_stats.st_mtime
        entity.checksum = compute_checksum(file_path)

    # 5. Resolve WikiLinks
    resolve_relations(entity)
```

**Database → File (Export)**:
```python
def sync_db_to_file(entity: Entity):
    # 1. Check if export needed
    current_checksum = compute_checksum(entity.file_path)
    if entity.checksum == current_checksum:
        return

    # 2. Build Markdown
    frontmatter_dict = entity.entity_metadata
    frontmatter_dict.update({
        "title": entity.title,
        "type": entity.entity_type,
        "permalink": entity.permalink,
    })

    content_parts = [f"# {entity.title}\n\n"]

    # Add observations
    if entity.observations:
        content_parts.append("## Observations\n\n")
        for obs in entity.observations:
            tags = " ".join(f"#{tag}" for tag in obs.tags)
            context = f" ({obs.context})" if obs.context else ""
            content_parts.append(f"- [{obs.category}] {obs.content} {tags}{context}\n")

    # Add relations
    if entity.relations:
        content_parts.append("\n## Relations\n\n")
        for rel in entity.outgoing_relations:
            target = f"[[{rel.to_entity.title}]]" if rel.to_entity else f"[[{rel.to_name}]]"
            context = f" ({rel.context})" if rel.context else ""
            content_parts.append(f"- {rel.relation_type} {target}{context}\n")

    # 3. Write to file
    post = frontmatter.Post("".join(content_parts), **frontmatter_dict)
    with open(entity.file_path, "w") as f:
        f.write(frontmatter.dumps(post))

    # 4. Update metadata
    file_stats = os.stat(entity.file_path)
    entity.mtime = file_stats.st_mtime
    entity.checksum = compute_checksum(entity.file_path)
```

**Real-Time Watching**:
```bash
# CLI command for continuous sync
basic-memory sync --watch

# Uses filesystem watcher (watchdog library)
# Debounces events (300ms)
# Auto-imports on file changes
```

### Knowledge Graph Traversal

```python
# MCP tool for LLMs
def traverse_relations(
    identifier: str,
    relation_types: Optional[List[str]] = None,
    depth: int = 1,
    max_depth: int = 3
) -> Dict:
    """Follow relations from entity to build context."""

    entity = get_entity(identifier)
    visited = set()
    result = {"root": entity, "related": []}

    def traverse(current: Entity, current_depth: int):
        if current_depth > depth or current.id in visited:
            return

        visited.add(current.id)

        for relation in current.outgoing_relations:
            if relation_types and relation.relation_type not in relation_types:
                continue

            if relation.to_entity:
                result["related"].append({
                    "entity": relation.to_entity,
                    "relation_type": relation.relation_type,
                    "depth": current_depth,
                })
                traverse(relation.to_entity, current_depth + 1)

    traverse(entity, 1)
    return result
```

### Advantages
- ✅ Human-readable and editable files
- ✅ Works with existing tools (Obsidian)
- ✅ Bi-directional sync (humans and LLMs both contribute)
- ✅ Cross-conversation persistence
- ✅ Multi-LLM access (Claude, ChatGPT, Gemini)
- ✅ Local-first, portable knowledge base

### Limitations
- ❌ File-based conflicts possible (last-write-wins)
- ❌ Limited to Markdown-serializable data
- ❌ Requires filesystem access

---

## Pattern 3: Hierarchical Memory with HNSW (claude-flow)

**Source**: `references/claude-flow/`
**Use Case**: Fast vector search with hierarchical embeddings for production-scale agents

### Architecture

**Memory Stack**:
```
Application Layer
    ↓
AgentDB (SQLite with WAL mode)
    ↓
HNSW Index (Hierarchical Navigable Small World)
    ↓
Local ONNX Embeddings (no API calls)
```

**8 Memory Types**:
1. **Task Memory** - What agent was asked to do
2. **Pattern Memory** - Successful patterns (stored by ReasoningBank)
3. **Success Memory** - What worked well
4. **Failure Memory** - What didn't work
5. **Context Memory** - Environmental information
6. **Relationship Memory** - Agent interactions
7. **Performance Memory** - Benchmarks and metrics
8. **Knowledge Memory** - Domain facts

### HNSW Vector Search

**Implementation**:
```python
import hnswlib

class HNSWMemory:
    def __init__(self, dim=384, max_elements=100000):
        # Initialize HNSW index
        self.index = hnswlib.Index(space='cosine', dim=dim)
        self.index.init_index(
            max_elements=max_elements,
            ef_construction=200,  # Controls recall/build time trade-off
            M=16,  # Number of connections per element
        )
        self.embedder = ONNXEmbedder("all-MiniLM-L6-v2")

    def store(self, text: str, memory_type: str, metadata: dict):
        # Generate embedding locally (no API call)
        embedding = self.embedder.embed(text)

        # Store in HNSW index
        idx = self.get_next_id()
        self.index.add_items([embedding], [idx])

        # Store metadata in SQLite
        self.db.execute("""
            INSERT INTO memory (id, text, memory_type, metadata, embedding_id)
            VALUES (?, ?, ?, ?, ?)
        """, (idx, text, memory_type, json.dumps(metadata), idx))

    def search(self, query: str, k=10, memory_type=None) -> List[dict]:
        # Generate query embedding
        query_embedding = self.embedder.embed(query)

        # HNSW search (150x-12,500x faster than brute force)
        labels, distances = self.index.knn_query([query_embedding], k=k)

        # Retrieve full records from SQLite
        results = []
        for label, distance in zip(labels[0], distances[0]):
            record = self.db.get_memory(label)
            if memory_type and record.memory_type != memory_type:
                continue
            record.relevance_score = 1 - distance
            results.append(record)

        return results
```

**Performance**:
- 150x-12,500x faster than brute force search
- <1ms query time for 100K vectors
- Local embeddings (75x faster than API calls)

### Hyperbolic Embeddings (Poincaré Ball)

**Purpose**: Better representation of hierarchical code relationships

```python
import geoopt

class HyperbolicMemory:
    def __init__(self, dim=384):
        # Poincaré ball manifold
        self.manifold = geoopt.PoincareBall(c=1.0)
        self.encoder = HyperbolicEncoder(dim)

    def embed_hierarchical(self, text: str, parent: Optional[str] = None):
        # Encode text
        euclidean_embed = self.encoder.encode(text)

        # Project to hyperbolic space
        hyperbolic_embed = self.manifold.expmap0(euclidean_embed)

        # If has parent, bias toward parent location
        if parent:
            parent_embed = self.get_embedding(parent)
            # Use geodesic interpolation
            hyperbolic_embed = self.manifold.geodesic(
                t=0.3,  # 30% toward parent
                x=hyperbolic_embed,
                y=parent_embed,
            )

        return hyperbolic_embed

    def distance(self, embed1, embed2):
        # Hyperbolic distance (captures hierarchy better)
        return self.manifold.dist(embed1, embed2)
```

**Advantages for Code**:
- Parent-child relationships (module → class → function)
- Nested structures (directories, packages)
- Inheritance hierarchies
- Call graphs

### Collective Memory (Swarm)

**Hive Mind Pattern**:
```python
class CollectiveMemory:
    def __init__(self):
        self.shared_memory = HNSWMemory()
        self.lru_cache = LRUCache(maxsize=1000)
        self.sqlite_persistence = SqlitePersistence()

    def queen_stores(self, knowledge: str, category: str):
        """Strategic queen stores high-level knowledge."""
        self.shared_memory.store(
            text=knowledge,
            memory_type="strategic",
            metadata={"source": "queen", "category": category}
        )
        self.sqlite_persistence.save(knowledge, "strategic")

    def worker_retrieves(self, query: str, worker_id: str) -> List[str]:
        """Workers retrieve relevant context for their tasks."""
        # Check LRU cache first
        cache_key = f"{query}:{worker_id}"
        if cached := self.lru_cache.get(cache_key):
            return cached

        # Search HNSW index
        results = self.shared_memory.search(query, k=5)

        # Cache for other workers
        self.lru_cache.put(cache_key, results)

        return results

    def consolidate(self, session_id: str):
        """At session end, consolidate to persistent storage."""
        session_memories = self.lru_cache.get_session(session_id)
        for memory in session_memories:
            self.sqlite_persistence.save(memory)
        self.lru_cache.clear_session(session_id)
```

### Advantages
- ✅ 150x-12,500x faster than traditional vector search
- ✅ Local embeddings (no API calls)
- ✅ Hierarchical relationships via Poincaré embeddings
- ✅ Shared swarm memory with LRU cache
- ✅ SQLite persistence for cross-session memory

### Limitations
- ❌ Requires ONNX runtime and hnswlib dependencies
- ❌ Memory limited by index max_elements parameter
- ❌ Embeddings not human-readable

---

## Pattern 4: Git Worktree State (claude-task-system)

**Source**: `references/claude-task-system/`
**Use Case**: Parallel task execution with isolated file system state

### Architecture

```
Main Repository
├── .git/
├── main/ (main worktree)
├── tasks/
│   ├── task-123/ (isolated worktree on branch task/123)
│   ├── task-456/ (isolated worktree on branch task/456)
│   └── task-789/ (isolated worktree on branch task/789)
```

**Key Concept**: Each task gets its own file system working directory with independent branch.

### Implementation

```python
class WorktreeTaskState:
    def __init__(self, task_id: str, base_branch: str = "main"):
        self.task_id = task_id
        self.branch_name = f"task/{task_id}"
        self.worktree_path = Path(f"tasks/{task_id}")

    def create(self):
        """Create isolated worktree for task."""
        # Create branch
        subprocess.run([
            "git", "branch", self.branch_name, self.base_branch
        ])

        # Create worktree
        subprocess.run([
            "git", "worktree", "add",
            str(self.worktree_path),
            self.branch_name
        ])

        # Initialize task state file
        state_file = self.worktree_path / ".task-state.json"
        state_file.write_text(json.dumps({
            "task_id": self.task_id,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "files_modified": [],
            "tests_locked": False,
        }))

    def get_state(self) -> dict:
        """Derive state from filesystem and git."""
        state_file = self.worktree_path / ".task-state.json"
        state = json.loads(state_file.read_text())

        # Derive status from git
        git_status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=self.worktree_path,
            capture_output=True,
            text=True
        )

        state["has_changes"] = bool(git_status.stdout.strip())
        state["files_modified"] = [
            line.split()[1]
            for line in git_status.stdout.split("\n")
            if line.strip()
        ]

        # Check test status
        test_result = self.run_tests()
        state["tests_passing"] = test_result.returncode == 0

        return state

    def cleanup(self):
        """Remove worktree and branch."""
        subprocess.run([
            "git", "worktree", "remove", str(self.worktree_path)
        ])
        subprocess.run([
            "git", "branch", "-D", self.branch_name
        ])
```

### Dynamic State Derivation

**Principle**: Never store state that can be derived from filesystem/git.

```python
def derive_task_status(worktree_path: Path) -> str:
    """Derive task status from observable state."""

    # Check if tests exist
    test_files = list(worktree_path.glob("tests/**/*.py"))
    if not test_files:
        return "awaiting_tests"

    # Run tests
    result = subprocess.run(
        ["pytest", "-v"],
        cwd=worktree_path,
        capture_output=True
    )

    if result.returncode != 0:
        return "tests_failing"

    # Check if implementation exists
    impl_files = list(worktree_path.glob("src/**/*.py"))
    if not impl_files:
        return "awaiting_implementation"

    # Check git status
    git_result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=worktree_path
    )

    if git_result.returncode == 0:  # No staged changes
        return "ready_for_review"
    else:
        return "in_progress"
```

### Advantages
- ✅ True parallel task execution (isolated file systems)
- ✅ No state corruption between tasks
- ✅ Git provides versioning and rollback
- ✅ State derivation prevents staleness
- ✅ Easy to visualize (each task is a directory)

### Limitations
- ❌ Requires Git repository
- ❌ Disk space for multiple worktrees
- ❌ Not suitable for long-running state

---

## Pattern 5: Event Sourcing with Checkpoints (AutoGPT)

**Source**: `references/autogpt/`
**Use Case**: Audit trail of all agent actions with replay capability

### Architecture

```
Event Stream (append-only log)
├── ActionProposed(id=1, action=read_file, args={...})
├── ActionExecuted(id=1, result=Success, output={...})
├── ActionProposed(id=2, action=write_code, args={...})
├── ActionExecuted(id=2, result=Error, error={...})
└── ... (continues)
    ↓
Projections (derived state)
├── Current task context
├── Files modified
├── Commands executed
└── Error history
```

**Key Concepts**:
- **Events** are immutable facts about what happened
- **Projections** are derived views of current state
- **Replay** reconstructs state from events

### Implementation

```python
from dataclasses import dataclass
from enum import Enum
from typing import Any, List

class EventType(Enum):
    ACTION_PROPOSED = "action_proposed"
    ACTION_EXECUTED = "action_executed"
    ERROR_OCCURRED = "error_occurred"
    CHECKPOINT_CREATED = "checkpoint_created"

@dataclass
class Event:
    id: int
    type: EventType
    timestamp: datetime
    data: dict

class EventStore:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.init_schema()

    def init_schema(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                timestamp REAL NOT NULL,
                data JSON NOT NULL
            )
        """)
        self.conn.execute("""
            CREATE INDEX idx_events_type ON events(type)
        """)

    def append(self, event_type: EventType, data: dict) -> Event:
        """Append event to stream (immutable)."""
        cursor = self.conn.execute("""
            INSERT INTO events (type, timestamp, data)
            VALUES (?, ?, ?)
        """, (event_type.value, time.time(), json.dumps(data)))

        self.conn.commit()

        return Event(
            id=cursor.lastrowid,
            type=event_type,
            timestamp=datetime.fromtimestamp(time.time()),
            data=data,
        )

    def get_events(self, since_id: int = 0) -> List[Event]:
        """Get events since checkpoint."""
        cursor = self.conn.execute("""
            SELECT id, type, timestamp, data
            FROM events
            WHERE id > ?
            ORDER BY id ASC
        """, (since_id,))

        return [
            Event(
                id=row[0],
                type=EventType(row[1]),
                timestamp=datetime.fromtimestamp(row[2]),
                data=json.loads(row[3]),
            )
            for row in cursor.fetchall()
        ]

class AgentProjection:
    """Derived state from event stream."""

    def __init__(self, event_store: EventStore):
        self.event_store = event_store
        self.last_event_id = 0
        self.current_task = None
        self.files_modified = set()
        self.errors = []

    def apply(self, event: Event):
        """Update projection from event."""
        if event.type == EventType.ACTION_PROPOSED:
            self.current_task = event.data["action"]

        elif event.type == EventType.ACTION_EXECUTED:
            if event.data["result"] == "Success":
                if event.data.get("files_modified"):
                    self.files_modified.update(event.data["files_modified"])

        elif event.type == EventType.ERROR_OCCURRED:
            self.errors.append({
                "message": event.data["error"],
                "timestamp": event.timestamp,
            })

        self.last_event_id = event.id

    def rebuild(self):
        """Rebuild projection from event stream."""
        self.current_task = None
        self.files_modified = set()
        self.errors = []
        self.last_event_id = 0

        for event in self.event_store.get_events():
            self.apply(event)

    def update(self):
        """Incrementally update from new events."""
        new_events = self.event_store.get_events(since_id=self.last_event_id)
        for event in new_events:
            self.apply(event)
```

### Checkpoint & Replay

```python
class Agent:
    def __init__(self, event_store: EventStore):
        self.event_store = event_store
        self.projection = AgentProjection(event_store)

    async def propose_action(self, action: str, args: dict):
        """Log proposed action."""
        event = self.event_store.append(
            EventType.ACTION_PROPOSED,
            {"action": action, "args": args}
        )
        self.projection.apply(event)

    async def execute_action(self, action_id: int, result: dict):
        """Log executed action."""
        event = self.event_store.append(
            EventType.ACTION_EXECUTED,
            {"action_id": action_id, "result": result}
        )
        self.projection.apply(event)

    def create_checkpoint(self) -> int:
        """Create checkpoint for later replay."""
        event = self.event_store.append(
            EventType.CHECKPOINT_CREATED,
            {"projection_state": {
                "current_task": self.projection.current_task,
                "files_modified": list(self.projection.files_modified),
                "errors": self.projection.errors,
            }}
        )
        return event.id

    def restore_checkpoint(self, checkpoint_id: int):
        """Restore to checkpoint and replay from there."""
        checkpoint_event = self.event_store.get_events()[checkpoint_id - 1]

        # Restore projection state
        state = checkpoint_event.data["projection_state"]
        self.projection.current_task = state["current_task"]
        self.projection.files_modified = set(state["files_modified"])
        self.projection.errors = state["errors"]
        self.projection.last_event_id = checkpoint_id

        # Replay events after checkpoint
        self.projection.update()
```

### Advantages
- ✅ Complete audit trail of agent actions
- ✅ Replay capability for debugging
- ✅ Time travel to any checkpoint
- ✅ Derived state prevents inconsistencies
- ✅ Append-only log (never mutate history)

### Limitations
- ❌ Disk space grows with event count
- ❌ Slow projection rebuild on large event streams
- ❌ Requires careful event schema design

---

## Comparison Matrix

| Pattern | Persistence | Human-Readable | Cross-Session | Multi-Agent | Performance | Best For |
|---------|-------------|----------------|---------------|-------------|-------------|----------|
| **LangGraph Checkpointing** | SQLite/PostgreSQL | ❌ JSON | ✅ Thread ID | ✅ Shared checkpointer | Medium | Conversational agents with branching |
| **basic-memory Markdown** | Files + SQLite | ✅ Markdown | ✅ Permanent | ✅ Multi-LLM | Medium | Knowledge graphs, cross-LLM workflows |
| **claude-flow HNSW** | SQLite + HNSW index | ❌ Vectors | ✅ Permanent | ✅ Collective memory | **Very Fast** | Production agents with fast search |
| **Git Worktree** | Git repository | ✅ Code files | ✅ Branches | ✅ Parallel tasks | Slow | Parallel development tasks |
| **Event Sourcing** | Append-only log | ❌ JSON events | ✅ Permanent | ✅ Shared log | Medium | Audit trails, debugging, replay |

---

## Key Takeaways

1. **Choose based on requirements**:
   - **Conversational**: LangGraph checkpointing
   - **Knowledge building**: basic-memory Markdown
   - **Production scale**: claude-flow HNSW
   - **Parallel tasks**: Git worktree
   - **Audit trail**: Event sourcing

2. **Human-readable state is valuable**: Markdown files (basic-memory) and code files (Git worktree) enable human oversight and editing

3. **Bi-directional sync enables collaboration**: Both agents and humans contribute to knowledge (basic-memory pattern)

4. **Vector search is critical at scale**: HNSW provides 150x-12,500x speedup for large memory systems

5. **Derive state when possible**: Git status and filesystem state prevent staleness (Git worktree pattern)

6. **Event sourcing provides time travel**: Complete audit trail enables debugging and replay

7. **Multi-agent requires shared state**: LangGraph checkpointer, basic-memory, and claude-flow collective memory all support multiple agents

8. **Checkpoints enable resumption**: All patterns support stopping and resuming agent workflows

---

## Related Patterns

- [[agent-loop-patterns]] - Agent execution cycles that use these state patterns
- [[mcp-server-integration]] - MCP servers for persistent state (basic-memory)
- [[progressive-disclosure-pattern]] - Loading state on-demand to reduce tokens

## References

- LangGraph: `references/langgraph/langgraph/checkpoint/`
- basic-memory: `references/basic-memory/src/basic_memory/models/knowledge.py`
- claude-flow: `references/claude-flow/` (RuVector intelligence layer)
- claude-task-system: `references/claude-task-system/` (Git worktree parallelism)
- AutoGPT: `references/AutoGPT/` (Event pipeline)
