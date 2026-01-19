# Basic Memory: Local-First Knowledge Graph for LLMs

**Reference**: `references/basic-memory/`
**Source**: https://github.com/basicmachines-co/basic-memory
**Maintainer**: Basic Machines Co.
**Type**: MCP Server + CLI Tool

## Overview

Basic Memory is a **local-first knowledge graph system** that enables Large Language Models (LLMs) to build persistent knowledge through natural conversations. It stores everything in simple Markdown files on your computer while providing bi-directional read/write access through the Model Context Protocol (MCP).

## Why Basic Memory for Agentic Workflows?

Basic Memory solves the **ephemeral conversation problem** where each LLM interaction starts fresh with no memory:

1. **Bi-directional Knowledge** - Both humans and LLMs read and write the same files
2. **Local-First** - All data in files you control (`~/basic-memory` by default)
3. **Structured yet Simple** - Familiar Markdown with semantic patterns
4. **Traversable Knowledge Graph** - LLMs follow links between topics automatically
5. **Cross-Conversation Context** - Knowledge persists across sessions, tools, and LLMs
6. **Multi-Platform** - Works with Claude, ChatGPT, Gemini, Claude Code, Codex
7. **Standard Formats** - Compatible with Obsidian and other Markdown editors

## Core Architecture

### Data Model

**Three Core Primitives**:

1. **Entity** - A node in the knowledge graph (maps to a Markdown file)
2. **Observation** - Atomic facts about an entity (Markdown list items with `[category]`)
3. **Relation** - Directed links between entities (WikiLinks with `relation_type [[Target]]`)

### Storage Layers

```
Markdown Files (~/basic-memory/*.md)
    ↕ (bidirectional sync)
SQLite Database (knowledge graph index)
    ↕ (MCP protocol)
LLM Tools (read/write/search/traverse)
```

**Persistence Strategy**:
- **Primary**: Markdown files on filesystem
- **Index**: SQLite database for search and graph queries
- **Sync**: Real-time bidirectional synchronization
- **Portability**: Files are human-readable and editable

## Markdown Format

### Frontmatter (Entity Metadata)

```markdown
---
title: Coffee Brewing Methods
type: note
permalink: coffee-brewing-methods
tags:
  - coffee
  - brewing
created_at: 2025-01-15T10:30:00
---
```

**Fields**:
- `title` (required) - Entity title
- `type` (optional) - Entity type (default: "note")
- `permalink` (auto-generated) - URI slug for references
- `tags` (optional) - List of tags
- Custom metadata fields allowed

**Implementation**: `references/basic-memory/src/basic_memory/markdown/entity_parser.py`
- Uses `python-frontmatter` library
- Normalizes PyYAML type conversions (dates, booleans, numbers → strings)
- Generates permalinks automatically if not provided

### Observations (Atomic Facts)

**Syntax**:
```markdown
- [category] content #tag1 #tag2 (optional context)
```

**Examples**:
```markdown
- [method] Pour over extracts more floral notes than French press
- [tip] Grind size should be medium-fine for pour over #brewing
- [preference] Ethiopian beans have bright, fruity flavors (especially from Yirgacheffe)
- [fact] Lighter roasts generally contain more caffeine than dark roasts
- [experiment] Tried 1:15 coffee-to-water ratio with good results
- [resource] James Hoffman's V60 technique on YouTube is excellent
- [question] Does water temperature affect extraction of different compounds differently?
- [note] My favorite local shop uses a 30-second bloom time
```

**Structure**:
- **Category**: Semantic type (method, tip, fact, question, note, etc.)
- **Content**: The actual observation text
- **Tags**: Optional hashtags for filtering
- **Context**: Optional parenthetical context

**Implementation**: `references/basic-memory/src/basic_memory/markdown/plugins.py`
- Custom markdown-it plugin (`observation_plugin`)
- Parses into `Observation` schema
- Stored in SQLite `observation` table with FK to entity

### Relations (Knowledge Graph Links)

**Syntax**:
```markdown
- relation_type [[WikiLink]] (optional context)
```

**Examples**:
```markdown
- pairs_well_with [[Chocolate Desserts]]
- grown_in [[Ethiopia]]
- contrasts_with [[Tea Brewing Methods]]
- requires [[Burr Grinder]]
- improves_with [[Fresh Beans]]
- relates_to [[Morning Routine]]
- inspired_by [[Japanese Coffee Culture]]
- documented_in [[Coffee Journal]]
```

**Relation Types** (user-defined):
- Semantic relationships like `pairs_well_with`, `requires`, `relates_to`
- No predefined schema - flexible based on domain
- LLMs can traverse relations to gather context

**Implementation**: `references/basic-memory/src/basic_memory/markdown/plugins.py`
- Custom markdown-it plugin (`relation_plugin`)
- Resolves WikiLinks to entity IDs
- Stored in SQLite `relation` table with `from_id` and `to_id`

## Database Schema

### Entity Table

```python
class Entity(Base):
    __tablename__ = "entity"

    # Core identity
    id: int                        # Database-generated numeric ID
    external_id: str               # UUID for API references (stable)
    title: str                     # Entity title
    entity_type: str               # Type (note, person, etc.)
    entity_metadata: dict          # JSON metadata from frontmatter
    content_type: str              # MIME type (text/markdown)

    # Project reference
    project_id: int                # FK to project.id

    # File mapping
    permalink: str                 # URI slug (e.g., "coffee-brewing-methods")
    file_path: str                 # Relative path (e.g., "coffee/brewing.md")
    checksum: str                  # File checksum for change detection

    # File metadata for sync
    mtime: float                   # Unix epoch timestamp
    size: int                      # File size in bytes

    # Timestamps
    created_at: datetime
    updated_at: datetime

    # Relationships
    observations: List[Observation]
    outgoing_relations: List[Relation]  # Relations where this is from_entity
    incoming_relations: List[Relation]  # Relations where this is to_entity
```

**Key Features**:
- **Unique constraints**: `(permalink, project_id)` and `(file_path, project_id)`
- **Indexes**: On `entity_type`, `title`, `created_at`, `updated_at`, `project_id`
- **Cascade delete**: Deleting entity removes all observations and relations
- **Timezone-aware**: All datetime fields stored with timezone info

### Observation Table

```python
class Observation(Base):
    __tablename__ = "observation"

    id: int                        # Primary key
    project_id: int                # FK to project.id
    entity_id: int                 # FK to entity.id (CASCADE on delete)
    content: str                   # Observation text
    category: str                  # Category (method, tip, fact, etc.)
    context: str                   # Optional context
    tags: List[str]                # JSON array of tags

    # Relationships
    entity: Entity
```

**Synthetic Permalink**:
```python
@property
def permalink(self) -> str:
    return f"{entity.permalink}/observations/{category}/{content[:200]}"
```

### Relation Table

```python
class Relation(Base):
    __tablename__ = "relation"

    id: int                        # Primary key
    project_id: int                # FK to project.id
    from_id: int                   # FK to entity.id (CASCADE on delete)
    to_id: int                     # FK to entity.id (nullable - for unresolved links)
    to_name: str                   # WikiLink name (for fuzzy resolution)
    relation_type: str             # Relation type (relates_to, requires, etc.)
    context: str                   # Optional context

    # Relationships
    from_entity: Entity
    to_entity: Entity
```

**Unique Constraints**:
- `(from_id, to_id, relation_type)` - Prevent duplicate relations
- `(from_id, to_name, relation_type)` - Prevent duplicate unresolved relations

**Unresolved Relations**:
- Relations can have `to_id = NULL` if target entity doesn't exist yet
- `to_name` stores WikiLink text for later resolution
- Fuzzy matching with `pg_trgm` for PostgreSQL deployments

## MCP Server Tools

Basic Memory exposes tools through the Model Context Protocol for LLM integration.

### Memory Tools

**create_entities**
```
Create one or more entities with observations and relations
Parameters:
  - entities: List[EntityCreate]
Returns: List of created entity IDs
```

**read_entity**
```
Read a specific entity by permalink or external_id
Parameters:
  - identifier: str (permalink or UUID)
Returns: Entity with observations and relations
```

**update_entity**
```
Update entity metadata, observations, or relations
Parameters:
  - identifier: str
  - updates: EntityUpdate
Returns: Updated entity
```

**delete_entity**
```
Delete an entity and all its observations/relations
Parameters:
  - identifier: str
Returns: Success confirmation
```

**search_entities**
```
Full-text search across entities, observations, and relations
Parameters:
  - query: str
  - limit: int (default: 10)
Returns: List of matching entities with relevance scores
```

**Implementation**: `references/basic-memory/src/basic_memory/mcp/clients/memory.py`

### Knowledge Graph Tools

**traverse_relations**
```
Follow relations from an entity to build context
Parameters:
  - identifier: str (starting entity)
  - relation_types: List[str] (optional filter)
  - depth: int (default: 1, max: 3)
Returns: Graph of related entities
```

**find_path**
```
Find shortest path between two entities
Parameters:
  - from_identifier: str
  - to_identifier: str
Returns: Path with intermediate entities and relations
```

**Implementation**: `references/basic-memory/src/basic_memory/mcp/clients/knowledge.py`

### Project Tools

**create_project**
```
Create a new knowledge project (separate namespace)
Parameters:
  - name: str
  - directory: str (optional)
Returns: Project ID
```

**list_projects**
```
List all available projects
Returns: List of projects with metadata
```

**switch_project**
```
Switch active project context
Parameters:
  - project_id: int
```

**Implementation**: `references/basic-memory/src/basic_memory/mcp/clients/project.py`

## Synchronization Architecture

### File → Database (Import)

**Trigger**: File created or modified on filesystem

**Process**:
1. Detect file change via `mtime` and `size` metadata
2. Parse Markdown into `EntityMarkdown` schema
3. Extract frontmatter → `Entity.entity_metadata`
4. Parse observations with `observation_plugin`
5. Parse relations with `relation_plugin`
6. Resolve WikiLinks to entity IDs (fuzzy matching if needed)
7. Update SQLite database with transaction
8. Update `checksum` and `mtime` for change detection

**Implementation**:
- `references/basic-memory/src/basic_memory/markdown/entity_parser.py`
- `references/basic-memory/src/basic_memory/services/entity_service.py`

### Database → File (Export)

**Trigger**: LLM creates/updates entity via MCP tools

**Process**:
1. Build Markdown from entity data
2. Generate frontmatter from `entity_metadata`
3. Write observations as Markdown list with `[category]` format
4. Write relations as WikiLinks with `relation_type [[Target]]`
5. Write to filesystem at `file_path`
6. Update `mtime`, `size`, and `checksum` in database

**Implementation**:
- `references/basic-memory/src/basic_memory/markdown/markdown_processor.py`
- `references/basic-memory/src/basic_memory/services/entity_service.py`

### Real-Time Sync

**CLI Command**:
```bash
basic-memory sync --watch
```

**Behavior**:
- Monitors `~/basic-memory` directory for changes
- Debounces file system events (300ms)
- Automatically imports changed files
- Resolves conflicts (file mtime wins over database)

**Implementation**: `references/basic-memory/src/basic_memory/cli/commands/db.py`

## Installation & Setup

### Prerequisites
- Python 3.12+
- `uv` tool (recommended) or `pip`

### Installation

```bash
# Install with uv (recommended)
uv tool install basic-memory

# Or with pip
pip install basic-memory
```

### MCP Server Configuration

**Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "basic-memory": {
      "command": "uvx",
      "args": ["basic-memory", "mcp"]
    }
  }
}
```

**VS Code** (User Settings JSON):
```json
{
  "mcp": {
    "servers": {
      "basic-memory": {
        "command": "uvx",
        "args": ["basic-memory", "mcp"]
      }
    }
  }
}
```

**Claude Code** (`.vscode/mcp.json` in workspace):
```json
{
  "servers": {
    "basic-memory": {
      "command": "uvx",
      "args": ["basic-memory", "mcp"]
    }
  }
}
```

### Alternative: Smithery Installation

```bash
npx -y @smithery/cli install @basicmachines-co/basic-memory --client claude
```

Automatically configures Claude Desktop without manual JSON edits.

## Usage Patterns

### Pattern 1: Conversational Knowledge Building

**User Workflow**:
```
1. Chat naturally with LLM about a topic
2. Ask LLM to "create a note about [topic]"
3. LLM uses create_entities MCP tool
4. Markdown file appears in ~/basic-memory/
5. View/edit in Obsidian or any Markdown editor
6. Changes sync automatically back to database
```

**Example**:
```
User: I've been learning about coffee brewing. Pour over gives clearer flavors
      than French press, and water temperature around 205°F works best.

User: Let's create a note about coffee brewing methods.

LLM: [Uses create_entities tool]
     Created "Coffee Brewing Methods" at ~/basic-memory/coffee-brewing-methods.md

User: [Opens file in Obsidian, sees structured content]
```

### Pattern 2: Context Retrieval Across Sessions

**User Workflow**:
```
1. Start new conversation (different day, different LLM)
2. Reference topic by permalink
3. LLM uses read_entity MCP tool
4. LLM traverses relations with traverse_relations tool
5. Builds rich context from knowledge graph
6. Continues conversation with full context
```

**Example**:
```
User (new session): What do I know about pour over coffee?

LLM: [Uses search_entities("pour over coffee")]
     [Uses read_entity("coffee-brewing-methods")]
     [Uses traverse_relations with depth=2]

     Based on your notes:
     - Pour over provides clarity and highlights subtle flavors
     - Water temperature should be 205°F (96°C)
     - Requires a burr grinder for consistent grind size
     - Pairs well with Ethiopian Yirgacheffe beans
     - Your favorite local shop uses a 30-second bloom time
```

### Pattern 3: Knowledge Graph Exploration

**User Workflow**:
```
1. Ask LLM to explore connections between topics
2. LLM uses traverse_relations or find_path tools
3. Discovers semantic relationships
4. Suggests new observations or relations
```

**Example**:
```
User: How does my coffee knowledge relate to my morning routine?

LLM: [Uses traverse_relations("coffee-brewing-methods", depth=2)]

     Found connections:
     - Coffee Brewing Methods → relates_to → Morning Routine
     - Morning Routine → includes → Exercise
     - Exercise → improves_with → Proper Hydration
     - Proper Hydration → relates_to → Coffee Consumption

     Interesting insight: Your exercise routine affects hydration needs,
     which impacts how coffee tastes and affects you.
```

### Pattern 4: Multi-LLM Knowledge Sharing

**Setup**:
```bash
# Same MCP server configured for all LLMs
# All access same ~/basic-memory directory
```

**Workflow**:
```
1. Build knowledge in Claude Desktop
2. Switch to ChatGPT (with basic-memory MCP)
3. Access same knowledge graph
4. Add observations from different perspective
5. Both LLMs see unified knowledge base
```

## Cloud Synchronization (Basic Memory Cloud)

**Features**:
- Cross-device sync (desktop, web, mobile)
- Multi-platform support (Claude, ChatGPT, Gemini, Claude Code, Codex)
- Bidirectional sync between local files and cloud
- Subscription-based authentication

**CLI Commands**:
```bash
# Authenticate with cloud
basic-memory cloud login

# List cloud projects
basic-memory cloud projects list

# Enable sync for project
basic-memory cloud sync --project <project_id> --watch

# Mount cloud storage
basic-memory cloud mount <project_id> ~/cloud-memory
```

**Implementation**: `references/basic-memory/src/basic_memory/cli/commands/cloud/`
- Uses `rclone` for bidirectional sync
- JWT authentication for API access
- Supports multiple projects per account

## Importers

Basic Memory includes importers for converting existing conversation data.

### ChatGPT Importer

```bash
basic-memory import-chatgpt conversations.json
```

Converts ChatGPT export to entities with:
- Conversation → Entity
- Messages → Observations
- Timestamps preserved

### Claude Conversations Importer

```bash
basic-memory import-claude-conversations <directory>
```

Imports Claude conversation exports:
- JSON conversations → Entities
- Maintains conversation structure
- Extracts key topics as separate entities

### Claude Projects Importer

```bash
basic-memory import-claude-projects <directory>
```

Imports Claude Projects data:
- Project → Basic Memory Project
- Documents → Entities
- Relations inferred from references

**Implementation**: `references/basic-memory/src/basic_memory/importers/`

## Key Learnings for Agentic Workflows

### 1. Bi-directional Knowledge is Critical

Traditional RAG systems are **read-only** - LLMs can query but not write. Basic Memory enables:
- LLMs create new knowledge during conversations
- Humans edit knowledge in familiar tools (Obsidian)
- Changes flow bidirectionally
- Knowledge base grows organically

**Pattern**: Agent conversation → entity creation → human refinement → agent reuse

### 2. Local-First Architecture Enables Control

Everything stored in Markdown files you own:
- No vendor lock-in
- Portable knowledge base
- Privacy and security control
- Works offline
- Standard formats (Markdown, SQLite)

**Pattern**: Local-first with optional cloud sync for multi-device access

### 3. Semantic Markup > Pure Text

Simple Markdown patterns provide structure:
- `[category]` observations enable semantic search
- `relation_type [[WikiLink]]` creates traversable graph
- Frontmatter metadata supports rich queries
- Human-readable yet machine-parseable

**Pattern**: Lightweight semantic markup in familiar formats

### 4. Knowledge Graph Traversal Builds Context

LLMs can follow relations automatically:
- Start at entity A
- Traverse `relates_to` relations
- Gather observations from related entities
- Build comprehensive context

**Pattern**: Single starting point → breadth-first traversal → aggregated context

### 5. Cross-Conversation Memory Solves Ephemeral Problem

Each conversation can access full knowledge base:
- No need to paste context manually
- Knowledge accumulates over time
- Insights from past conversations inform new ones
- Multi-session projects remain coherent

**Pattern**: Conversation 1 creates knowledge → Conversation 2 retrieves and extends

### 6. Multi-LLM Access Enables Diverse Perspectives

Same knowledge graph accessible to different LLMs:
- Claude excels at analysis
- ChatGPT excels at creative connections
- Gemini excels at multimodal integration
- All contribute to shared knowledge base

**Pattern**: Use best LLM for each task, unified knowledge substrate

### 7. Unresolved Relations Support Incremental Building

Relations can reference entities that don't exist yet:
- `to_name` stores WikiLink text
- `to_id` nullable until target created
- Fuzzy matching resolves later
- Knowledge graph builds incrementally

**Pattern**: Link first, create later - knowledge grows organically

### 8. Projects Enable Multi-Context Workflows

Separate projects for different domains:
- Personal knowledge
- Work projects
- Research topics
- Client work

Each project has isolated namespace but shares infrastructure.

**Pattern**: One MCP server, multiple isolated knowledge graphs

## Integration with Other Agentic Patterns

### With claude-task-system

```
Feature Definition phase:
  - Document feature requirements as entities
  - Link to architecture decision records (ADRs)
  - Store in basic-memory for persistence

Technical Planning phase:
  - Retrieve feature entity with traverse_relations
  - Access related design patterns
  - Create task entities with relations to feature

Task Execution phase:
  - Workers create observations about implementation progress
  - Update entity with learnings
  - Link to code files with relations
```

### With GET SHIT DONE

```
Session 1 (Day 1):
  - Build knowledge about project architecture
  - Store in basic-memory

Session 2 (Day 7):
  - GSD spawns fresh context
  - Retrieves architecture from basic-memory
  - Continues with full context despite fresh agent

Context persistence across days/weeks without context rot
```

### With claude-flow

```
Queen agent:
  - Stores strategic decisions in basic-memory
  - Creates entities for high-level plans

Worker agents:
  - Retrieve relevant context via read_entity
  - Create observations about task completion
  - Update collective memory

Swarm collective memory enhanced with persistent knowledge graph
```

### With Obsidian Skills

```
Basic Memory provides storage backend
Obsidian skills provide visualization and editing

Workflow:
  1. LLM creates entities via basic-memory MCP
  2. Files appear in ~/basic-memory (Obsidian vault)
  3. Human uses Obsidian graph view to visualize knowledge
  4. Human adds relations and observations in Obsidian
  5. Changes sync back to database automatically
  6. LLM sees updated knowledge graph

Perfect symbiosis: LLM automation + human curation
```

## Technical Implementation Details

### Parser Architecture

**markdown-it with Custom Plugins**:
```python
from markdown_it import MarkdownIt
from basic_memory.markdown.plugins import observation_plugin, relation_plugin

md = MarkdownIt().use(observation_plugin).use(relation_plugin)
```

**Observation Plugin**:
- Regex: `- \[(\w+)\] ([^#(]+)(?:#(\S+))?(?:\(([^)]+)\))?`
- Captures: `[category] content #tags (context)`
- Generates `Observation` objects

**Relation Plugin**:
- Regex: `- (\w+) \[\[([^\]]+)\]\](?:\(([^)]+)\))?`
- Captures: `relation_type [[WikiLink]] (context)`
- Generates `Relation` objects

### Change Detection Strategy

**File → Database**:
```python
def needs_import(entity: Entity, file_stats: os.stat_result) -> bool:
    return (
        entity.mtime != file_stats.st_mtime or
        entity.size != file_stats.st_size
    )
```

**Database → File**:
```python
def needs_export(entity: Entity) -> bool:
    current_checksum = compute_checksum(entity.file_path)
    return entity.checksum != current_checksum
```

**Conflict Resolution**:
- File `mtime` always wins (file is source of truth)
- Database exports only when checksum mismatches
- No merge conflicts - last write wins

### Search Implementation

**SQLite Full-Text Search**:
```sql
CREATE VIRTUAL TABLE search_index USING fts5(
    title,
    content,
    tokenize='porter unicode61'
);
```

**PostgreSQL Full-Text Search**:
```sql
CREATE INDEX ix_search_tsvector
ON entity USING gin(to_tsvector('english', title || ' ' || content));
```

**Fuzzy WikiLink Resolution** (PostgreSQL only):
```sql
CREATE EXTENSION pg_trgm;
CREATE INDEX ix_relation_to_name_trgm
ON relation USING gin(to_name gin_trgm_ops);
```

## Resources & Documentation

**Repository**:
- Main README: `references/basic-memory/README.md` (comprehensive)
- Documentation: https://memory.basicmachines.co
- Website: https://basicmachines.co

**Key Code Paths**:
- Models: `references/basic-memory/src/basic_memory/models/knowledge.py`
- Parser: `references/basic-memory/src/basic_memory/markdown/entity_parser.py`
- Plugins: `references/basic-memory/src/basic_memory/markdown/plugins.py`
- MCP Clients: `references/basic-memory/src/basic_memory/mcp/clients/`
- Services: `references/basic-memory/src/basic_memory/services/entity_service.py`
- Sync: `references/basic-memory/src/basic_memory/cli/commands/db.py`

## Related Patterns

- [[state-management-patterns]] - Persistent state across agent sessions
- [[mcp-server-integration]] - MCP server development patterns
- [[knowledge-graph-patterns]] - Graph-based knowledge representation (to be created)

## Key Takeaways

1. **Bi-directional knowledge** - LLMs and humans both read and write
2. **Local-first architecture** - All data in Markdown files you control
3. **Semantic Markdown** - `[category]` observations + `relation_type [[WikiLink]]` relations
4. **Cross-conversation memory** - Knowledge persists across sessions and LLMs
5. **Traversable knowledge graph** - LLMs automatically follow relations for context
6. **Multi-LLM support** - Works with Claude, ChatGPT, Gemini, Claude Code, Codex
7. **Real-time sync** - File changes ↔ database synchronization
8. **Standard formats** - Compatible with Obsidian and Markdown tools
9. **Incremental building** - Unresolved relations support organic growth
10. **Project isolation** - Multiple separate knowledge graphs per MCP server

Basic Memory transforms LLM interactions from ephemeral conversations into a **growing, interconnected knowledge base** that both humans and AI can contribute to and learn from over time.
