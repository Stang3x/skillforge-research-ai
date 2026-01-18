# Agent Framework Learning Roadmap

A comprehensive guide to mastering high-priority functions and capabilities of the Microsoft Agent Framework for building AI agents.

---

## 📚 Level 1: Fundamentals (Priority: CRITICAL)

### 1.1 Core Agent Classes
**What to learn:** The basic building blocks of any agent

| Function | Purpose | Priority |
|----------|---------|----------|
| `ChatAgent` | Create a basic conversational agent | 🔴 CRITICAL |
| `ChatAgent.__init__()` | Initialize agent with client, instructions, tools | 🔴 CRITICAL |
| `ChatAgent.run()` | Execute agent synchronously | 🔴 CRITICAL |
| `ChatAgent.run_stream()` | Execute agent with streaming responses | 🔴 CRITICAL |
| `ChatAgent.get_new_thread()` | Create conversation threads for context | 🔴 CRITICAL |

**Learning Path:**
```python
# Start here
from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient

# Initialize client
client = OpenAIChatClient(async_client=openai_client, model_id="model-id")

# Create agent
agent = ChatAgent(chat_client=client, name="MyAgent", instructions="...")

# Run agent
result = await agent.run("Hello")

# Run with streaming (production-grade)
async for chunk in agent.run_stream("Hello"):
    if chunk.text:
        print(chunk.text)
```

### 1.2 Client Configuration
**What to learn:** How to connect to different LLM providers

| Function | Purpose | Priority |
|----------|---------|----------|
| `OpenAIChatClient` | Connect to OpenAI models | 🔴 CRITICAL |
| `AzureOpenAIChatClient` | Connect to Azure OpenAI | 🔴 CRITICAL |
| `AsyncOpenAI` | Async OpenAI client setup | 🔴 CRITICAL |

**Learning Path:**
```python
# GitHub Models
openai_client = AsyncOpenAI(
    base_url="https://models.github.ai/inference",
    api_key="GITHUB_TOKEN"
)

# Azure OpenAI
openai_client = AsyncOpenAI(
    api_key="AZURE_KEY",
    api_version="2024-08-01-preview",
    azure_endpoint="https://your-resource.openai.azure.com/"
)

# Create chat client
chat_client = OpenAIChatClient(async_client=openai_client, model_id="model-id")
```

---

## 📈 Level 2: Essential Patterns (Priority: HIGH)

### 2.1 Tool Definition & Function Calling
**What to learn:** Adding capabilities to your agent

| Function | Purpose | Priority |
|----------|---------|----------|
| `Annotated` type hints | Define tool parameters with descriptions | 🟠 HIGH |
| Function docstrings | Describe tool functionality | 🟠 HIGH |
| Tool registration | Add tools to agent | 🟠 HIGH |

**Learning Path:**
```python
from typing import Annotated

# Define a tool
def get_weather(
    location: Annotated[str, "City name to get weather for"],
    units: Annotated[str, "Temperature units: celsius or fahrenheit"] = "celsius"
) -> str:
    """Get current weather for a location."""
    return f"Weather in {location} is 25°{units[0].upper()}"

# Register with agent
agent = ChatAgent(
    chat_client=chat_client,
    name="WeatherAgent",
    instructions="You are a weather assistant",
    tools=[get_weather]  # Pass as list
)
```

### 2.2 Thread Management for Conversations
**What to learn:** Maintaining context across multiple turns

| Function | Purpose | Priority |
|----------|---------|----------|
| `Agent.get_new_thread()` | Create new conversation thread | 🟠 HIGH |
| `thread` parameter in `run()` | Use thread for context | 🟠 HIGH |
| Thread persistence | Maintain state across calls | 🟠 HIGH |

**Learning Path:**
```python
# Create thread once
thread = agent.get_new_thread()

# Use same thread for multiple turns
msg1 = await agent.run("What's the weather in Seattle?", thread=thread)
msg2 = await agent.run("What about tomorrow?", thread=thread)  # Remembers Seattle

# Stream with thread
async for chunk in agent.run_stream("Any storms?", thread=thread):
    if chunk.text:
        print(chunk.text)
```

### 2.3 Streaming vs Synchronous Execution
**What to learn:** When and how to use streaming

| Pattern | Use Case | Priority |
|---------|----------|----------|
| `agent.run()` | Testing, debugging, simple scripts | 🟠 HIGH |
| `agent.run_stream()` | Production, long responses, UX | 🟠 HIGH |
| Chunk handling | Process streamed tokens | 🟠 HIGH |

**Learning Path:**
```python
# For testing
result = await agent.run("question")
print(result.text)

# For production (better UX)
print("Agent: ", end="", flush=True)
async for chunk in agent.run_stream("question"):
    if chunk.text:
        print(chunk.text, end="", flush=True)
print()
```

---

## 🚀 Level 3: Advanced Capabilities (Priority: MEDIUM)

### 3.1 Model Context Protocol (MCP) Tools
**What to learn:** Integrate pre-built MCP tools

| Class | Purpose | Priority |
|-------|---------|----------|
| `MCPStdioTool` | Shell-based MCP tools (Playwright, etc.) | 🟡 MEDIUM |
| `MCPStreamableHTTPTool` | HTTP-based MCP tools (Microsoft Learn, etc.) | 🟡 MEDIUM |
| `MCPTcpTool` | TCP-based MCP connections | 🟡 MEDIUM |

**Learning Path:**
```python
from agent_framework import MCPStdioTool, MCPStreamableHTTPTool

tools = [
    # Browser automation
    MCPStdioTool(
        name="Playwright",
        description="Browser automation",
        command="npx",
        args=["-y", "@playwright/mcp@latest"]
    ),
    # Documentation
    MCPStreamableHTTPTool(
        name="Microsoft Learn",
        description="Official Microsoft documentation",
        url="https://learn.microsoft.com/api/mcp"
    )
]

agent = ChatAgent(
    chat_client=chat_client,
    name="AssistantWithTools",
    instructions="...",
    tools=tools
)
```

### 3.2 Multi-Agent Patterns
**What to learn:** Orchestrate multiple agents

| Pattern | Purpose | Priority |
|---------|---------|----------|
| Sequential execution | Agent A → Agent B → Agent C | 🟡 MEDIUM |
| Concurrent execution | Run multiple agents in parallel | 🟡 MEDIUM |
| Handoff patterns | Transfer context between agents | 🟡 MEDIUM |

**Learning Path:**
```python
# Sequential pattern
agent_a = ChatAgent(...)
agent_b = ChatAgent(...)

result_a = await agent_a.run(user_input)
result_b = await agent_b.run(result_a.text)

# Concurrent pattern (faster)
results = await asyncio.gather(
    agent_a.run(user_input),
    agent_b.run(user_input)
)

# Handoff pattern
if "need_specialized_help" in result.text:
    specialist_agent = ChatAgent(...)
    result = await specialist_agent.run(user_input)
```

### 3.3 Async Context Managers
**What to learn:** Proper resource management

| Pattern | Purpose | Priority |
|---------|---------|----------|
| `async with` statement | Clean resource cleanup | 🟡 MEDIUM |
| Context manager protocol | Setup and teardown | 🟡 MEDIUM |

**Learning Path:**
```python
# Proper resource management
async with ChatAgent(
    chat_client=chat_client,
    name="MyAgent",
    instructions="...",
    tools=[tool1, tool2]
) as agent:
    result = await agent.run("Hello")
    # Resources automatically cleaned up
```

---

## 🔧 Level 4: Advanced Patterns (Priority: LOW-MEDIUM)

### 4.1 Custom Response Processing
**What to learn:** Handle different response types

| Response Type | Purpose | Priority |
|---------------|---------|----------|
| `chunk.text` | Streamed text tokens | 🟡 MEDIUM |
| `chunk.raw_representation` | Raw API response | 🟡 MEDIUM |
| Tool call detection | Identify function calls | 🟡 MEDIUM |

**Learning Path:**
```python
async for chunk in agent.run_stream(user_input):
    if chunk.text:
        # Regular text response
        print(chunk.text, end="")
    elif (chunk.raw_representation and 
          hasattr(chunk.raw_representation.raw_representation, "choices")):
        # Tool call detected
        choices = chunk.raw_representation.raw_representation.choices[0]
        if hasattr(choices.delta, "tool_calls"):
            print("[Tool Call]")
```

### 4.2 Error Handling & Resilience
**What to learn:** Make agents robust

| Pattern | Purpose | Priority |
|---------|---------|----------|
| Try-except blocks | Catch agent errors | 🟡 MEDIUM |
| Retry logic | Handle transient failures | 🟡 MEDIUM |
| Graceful degradation | Fallback options | 🟡 MEDIUM |

**Learning Path:**
```python
import asyncio

async def run_with_retry(agent, query, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = await agent.run(query)
            return result
        except Exception as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                continue
            raise

# Usage
result = await run_with_retry(agent, "Hello")
```

### 4.3 System Prompting & Instruction Engineering
**What to learn:** Fine-tune agent behavior

| Aspect | Purpose | Priority |
|--------|---------|----------|
| Instruction clarity | Define role and behavior | 🟡 MEDIUM |
| Chain-of-thought prompts | Guide reasoning | 🟡 MEDIUM |
| Output formatting | Specify response structure | 🟡 MEDIUM |

**Learning Path:**
```python
# Excellent instructions
instructions = """You are a specialized research assistant. Your role is to:
1. Search for relevant information using available tools
2. Synthesize findings into clear, structured summaries
3. Always provide citations when possible
4. Ask clarifying questions if the query is ambiguous

When responding:
- Use markdown formatting
- Include section headers
- Provide numbered lists for key points
- Cite sources at the end

If you don't have the information, say so explicitly rather than guessing."""

agent = ChatAgent(
    chat_client=chat_client,
    name="ResearchAssistant",
    instructions=instructions,
    tools=tools
)
```

---

## 📊 Level 5: Production Deployment (Priority: LOW)

### 5.1 Logging & Monitoring
**What to learn:** Observe agent behavior in production

| Tool | Purpose | Priority |
|------|---------|----------|
| Python `logging` | Application logs | 🔵 LOW |
| OpenTelemetry | Distributed tracing | 🔵 LOW |
| Metrics collection | Performance monitoring | 🔵 LOW |

### 5.2 Testing Agents
**What to learn:** Quality assurance

| Test Type | Purpose | Priority |
|-----------|---------|----------|
| Unit tests | Test individual tools | 🔵 LOW |
| Integration tests | Test agent + tools | 🔵 LOW |
| End-to-end tests | Full workflow validation | 🔵 LOW |

### 5.3 Deployment Options
**What to learn:** Getting agents to users

| Platform | Purpose | Priority |
|----------|---------|----------|
| Docker containers | Containerized deployment | 🔵 LOW |
| AWS Lambda | Serverless execution | 🔵 LOW |
| Azure Functions | Microsoft cloud functions | 🔵 LOW |
| Web servers (FastAPI) | REST API endpoints | 🔵 LOW |

---

## 🎯 Recommended Learning Path

### Week 1: Fundamentals
- [ ] Day 1-2: Set up ChatAgent with GitHub Models
- [ ] Day 3-4: Create a simple tool and register it
- [ ] Day 5: Implement thread-based conversations
- [ ] Day 6-7: Practice streaming responses

### Week 2: Hands-On Projects
- [ ] Build a weather assistant (tools + streaming)
- [ ] Build a research assistant (multiple tools, threads)
- [ ] Build a Q&A bot (instructions engineering)

### Week 3: Advanced Patterns
- [ ] Integrate MCP tools
- [ ] Create a two-agent system (handoff pattern)
- [ ] Implement error handling & retries

### Week 4: Production Ready
- [ ] Add logging and monitoring
- [ ] Write unit tests
- [ ] Deploy to cloud platform

---

## 💡 Key Resources

### Official Documentation
- [Agent Framework GitHub](https://github.com/microsoft/agent-framework)
- [OpenAI SDK Documentation](https://platform.openai.com/docs/api-reference)
- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Model Context Protocol](https://modelcontextprotocol.io)

### GitHub Models
- [Available Models](https://github.com/marketplace/models)
- [GitHub Models Documentation](https://docs.github.com/en/github-models)

### Learning Resources
- Agent Framework examples in repository
- Community projects and tutorials
- API reference documentation

---

## ✅ Practice Checklist

### Fundamentals
- [ ] Create and configure ChatAgent
- [ ] Connect to GitHub Models
- [ ] Run synchronous agent
- [ ] Run streaming agent
- [ ] Create and use threads
- [ ] Define and register a simple tool

### Intermediate
- [ ] Create multi-tool agent
- [ ] Implement system instructions
- [ ] Handle different response types
- [ ] Implement error handling
- [ ] Create conversation history

### Advanced
- [ ] Integrate MCP tools
- [ ] Create multi-agent system
- [ ] Implement custom response processing
- [ ] Deploy to cloud
- [ ] Add monitoring/logging

---

## 🚀 Next Steps for Your Research Assistant

Based on your current research assistant, here are high-priority improvements:

1. **Replace mock search with real API** (Week 1)
   - Integrate Google Custom Search API
   - Add DuckDuckGo API integration
   - Use academic databases

2. **Add MCP tools** (Week 2)
   - Playwright for web scraping
   - Microsoft Learn for documentation

3. **Implement persistence** (Week 2)
   - Save research sessions
   - Cache search results

4. **Multi-agent research team** (Week 3)
   - Researcher agent (searches)
   - Analyst agent (synthesizes)
   - Writer agent (formats output)

5. **Deploy as web API** (Week 4)
   - FastAPI wrapper
   - Docker containerization
   - Cloud deployment
