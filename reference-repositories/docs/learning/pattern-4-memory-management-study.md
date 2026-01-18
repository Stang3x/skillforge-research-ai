# Pattern 4: Memory & Conversation Management - Deep Dive

**Source**: Dify Platform (`api/core/memory/token_buffer_memory.py`)
**Study Date**: 2026-01-16
**Learning Goal**: Understand and implement production-grade memory management for agentic systems

---

## Overview

The Token Buffer Memory pattern solves a critical problem in conversational AI: **how to maintain coherent conversation history without exceeding context limits**. This is essential for agents that need to maintain long-running conversations while staying within LLM token budgets.

### Core Problem
- LLMs have fixed context windows (e.g., Claude: 200K tokens, GPT-4: 128K tokens)
- Long conversations generate history that exceeds these limits
- Naive solutions: truncate randomly (loses context) or crash (bad UX)
- **Solution**: Intelligent token-aware pruning with conversation coherence

---

## Key Components

### 1. Token-Aware Memory Buffer

**Purpose**: Automatically manage conversation history within token limits

**Core Class**:
```python
class TokenBufferMemory:
    def __init__(self, conversation: Conversation, model_instance: ModelInstance):
        self.conversation = conversation
        self.model_instance = model_instance
```

**Key Features**:
1. **Database-backed**: Conversations persisted to SQLAlchemy database
2. **Model-aware**: Uses actual model's tokenizer for accurate counting
3. **Thread extraction**: Maintains conversation coherence across branches
4. **File handling**: Supports multimodal messages (images, documents)

---

## Implementation Deep Dive

### Step 1: Fetching Conversation History

**Location**: `token_buffer_memory.py:117-143`

```python
def get_history_prompt_messages(
    self, max_token_limit: int = 2000, message_limit: int | None = None
) -> Sequence[PromptMessage]:
    """
    Get history prompt messages with intelligent pruning.

    Args:
        max_token_limit: Maximum tokens allowed for history (default: 2000)
        message_limit: Maximum number of messages to fetch (default: 500)

    Returns:
        Sequence of PromptMessage objects within token limit
    """
```

**Key Decisions**:
- **Message Limit**: Cap at 500 messages to prevent DB query explosion
- **Reverse Chronological**: Fetch newest messages first (most relevant)
- **Thread Extraction**: Use `extract_thread_messages()` to maintain coherence

### Step 2: Thread Extraction

**Purpose**: Extract only messages that belong to the current conversation thread

**Why It Matters**:
- Multi-turn conversations can have branching paths
- Users might restart conversations or switch topics
- Only include messages in the active thread for coherence

**Implementation**:
```python
# Line 143
thread_messages = extract_thread_messages(messages)
```

**What This Does**:
- Follows conversation lineage (parent_message_id relationships)
- Excludes orphaned or branched conversations
- Maintains logical conversation flow

### Step 3: Building Prompt Messages with Files

**Location**: `token_buffer_memory.py:44-115`

**Handles Multimodal Content**:
```python
def _build_prompt_message_with_files(
    self,
    message_files: Sequence[MessageFile],
    text_content: str,
    message: Message,
    app_record,
    is_user_message: bool,
) -> PromptMessage:
```

**Supports**:
- User-uploaded images (with detail level: HIGH/LOW)
- Assistant-generated files (charts, PDFs)
- Mixed text + image messages
- File belongs_to filtering (user vs assistant files)

**Example**: Message with image attachment
```python
# Combines text and image content
prompt_message_contents = [
    ImagePromptMessageContent(url="...", detail="high"),
    TextPromptMessageContent(data="What's in this image?")
]
UserPromptMessage(content=prompt_message_contents)
```

### Step 4: Token Counting and Pruning

**Location**: `token_buffer_memory.py:194-202`

**The Core Algorithm**:
```python
# Get accurate token count using model's tokenizer
curr_message_tokens = self.model_instance.get_llm_num_tokens(prompt_messages)

# Prune from oldest if exceeding limit
if curr_message_tokens > max_token_limit:
    while curr_message_tokens > max_token_limit and len(prompt_messages) > 1:
        prompt_messages.pop(0)  # Remove oldest message
        curr_message_tokens = self.model_instance.get_llm_num_tokens(prompt_messages)
```

**Why This Works**:
1. **Accurate Counting**: Uses actual model tokenizer (not approximations)
2. **Oldest-First Removal**: Recent context is most important for coherence
3. **Iterative**: Recalculates tokens after each removal
4. **Safety Check**: Always keeps at least 1 message

**Token Counting Deep Dive**:
- Different models have different tokenizers (GPT-4 ≠ Claude ≠ Llama)
- Multimodal content (images) counted as equivalent text tokens
- System prompts NOT included in history token count (protected)

---

## Advanced Features

### 5. Text-Only History Export

**Location**: `token_buffer_memory.py:204-243`

```python
def get_history_prompt_text(
    self,
    human_prefix: str = "Human",
    ai_prefix: str = "Assistant",
    max_token_limit: int = 2000,
    message_limit: int | None = None,
) -> str:
    """
    Export conversation as formatted text (for models without message API).
    """
```

**Use Cases**:
- Legacy models that expect text-only input
- Export for human review / debugging
- Integration with non-API LLMs (local models)

**Output Format**:
```
Human: What is machine learning?
Assistant: Machine learning is a subset of AI that...
Human: Can you give me an example?
Assistant: Sure! An example is spam detection...
```

---

## Production Patterns Learned

### Pattern 1: Database-Backed Memory
**Anti-pattern**: Store conversation in Python list/dict (lost on crash)
**Pro pattern**: Persist to database, reconstruct on load

```python
# Dify's approach
class TokenBufferMemory:
    def __init__(self, conversation: Conversation, ...):
        self.conversation = conversation  # DB model
        # Load history from database on demand
```

### Pattern 2: Model-Specific Token Counting
**Anti-pattern**: Hardcode approximations like "4 chars = 1 token"
**Pro pattern**: Use model's actual tokenizer

```python
# Accurate counting
curr_message_tokens = self.model_instance.get_llm_num_tokens(prompt_messages)
```

### Pattern 3: Thread Coherence
**Anti-pattern**: Include all messages from conversation_id
**Pro pattern**: Extract only messages in active thread

```python
thread_messages = extract_thread_messages(messages)
```

### Pattern 4: Multimodal Content Handling
**Anti-pattern**: Separate text and image handling
**Pro pattern**: Unified `PromptMessage` with mixed content

```python
# Can include both text and images in single message
UserPromptMessage(content=[
    ImagePromptMessageContent(...),
    TextPromptMessageContent(...)
])
```

---

## Application to Your Research Assistant

### Current State Analysis

Your research assistant (`05_research_assistant_with_apis.py`) currently:
- ✅ Maintains conversation list
- ❌ No token limit checking
- ❌ No automatic pruning
- ❌ No database persistence
- ❌ Loses history on crash

### Implementation Plan

#### Level 1: Basic Token Buffering (Easy - 2 hours)
```python
class SimpleTokenBuffer:
    """Simplified token buffer for research assistant"""

    def __init__(self, max_tokens: int = 8000):
        self.max_tokens = max_tokens
        self.messages = []

    def add_message(self, role: str, content: str):
        """Add message and prune if needed"""
        self.messages.append({"role": role, "content": content})
        self._trim_to_limit()

    def _trim_to_limit(self):
        """Remove oldest user/assistant pairs"""
        # Rough estimation: 4 chars per token
        while self._estimate_tokens() > self.max_tokens and len(self.messages) > 2:
            # Remove oldest pair (user + assistant)
            self.messages.pop(0)
            if len(self.messages) > 0:
                self.messages.pop(0)

    def _estimate_tokens(self) -> int:
        """Rough token estimation"""
        total_chars = sum(len(msg["content"]) for msg in self.messages)
        return total_chars // 4  # Approximation

    def get_messages(self) -> list:
        """Get current conversation history"""
        return self.messages
```

#### Level 2: Accurate Token Counting (Medium - 3 hours)
```python
import anthropic

class AccurateTokenBuffer:
    """Token buffer with accurate counting using Anthropic's API"""

    def __init__(self, client: Anthropic, max_tokens: int = 8000):
        self.client = client
        self.max_tokens = max_tokens
        self.messages = []

    def _count_tokens(self) -> int:
        """Use Anthropic's count_tokens API"""
        response = self.client.messages.count_tokens(
            model="claude-3-5-sonnet-20240620",
            messages=self.messages
        )
        return response.input_tokens

    def _trim_to_limit(self):
        """Accurately prune based on real token count"""
        while self._count_tokens() > self.max_tokens and len(self.messages) > 2:
            self.messages.pop(0)
            self.messages.pop(0)
```

#### Level 3: Full Database Persistence (Hard - 6 hours)
```python
import sqlite3
from datetime import datetime

class PersistentMemory:
    """Full database-backed conversation memory"""

    def __init__(self, conversation_id: str, db_path: str = "conversations.db"):
        self.conversation_id = conversation_id
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        """Create conversations and messages tables"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                created_at TIMESTAMP,
                title TEXT
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT,
                role TEXT,
                content TEXT,
                created_at TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        """)
        self.conn.commit()

    def add_message(self, role: str, content: str):
        """Persist message to database"""
        self.conn.execute(
            "INSERT INTO messages (conversation_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (self.conversation_id, role, content, datetime.now())
        )
        self.conn.commit()

    def get_history(self, limit: int = 100) -> list:
        """Load conversation history from database"""
        cursor = self.conn.execute(
            "SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY created_at DESC LIMIT ?",
            (self.conversation_id, limit)
        )
        messages = [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]
        return list(reversed(messages))  # Return in chronological order
```

---

## Next Steps

### Immediate Actions
1. ✅ Study Pattern 4 documentation
2. 🔄 **Implement Level 1** (Simple Token Buffer) in research assistant
3. ⏳ Test with long conversations (20+ turns)
4. ⏳ Add token usage monitoring

### Future Enhancements
- Study Pattern 5 (Queue-Based Async Execution) for streaming
- Implement conversation summarization for very long chats
- Add export/import functionality for conversation backup
- Integrate with Pattern 7 (Observability) for usage tracking

---

## Key Takeaways

1. **Token Management is Critical**: Production agents MUST handle token limits gracefully
2. **Accurate Counting Matters**: Use model-specific tokenizers, not approximations
3. **Persistence Enables Resilience**: Database-backed memory survives crashes
4. **Thread Coherence**: Extract related messages, not just recent ones
5. **Multimodal Support**: Plan for images, files, not just text

## References

- Source Code: [references/dify/api/core/memory/token_buffer_memory.py](c:\Users\Stang3x\Documents\Personal - Dan\Agentic Workflows\references\dify\api\core\memory\token_buffer_memory.py)
- Documentation: [docs/patterns/dify-production-patterns.md#pattern-4](c:\Users\Stang3x\Documents\Personal - Dan\Agentic Workflows\docs\patterns\dify-production-patterns.md)
- Anthropic Docs: https://docs.anthropic.com/en/docs/build-with-claude/token-counting
