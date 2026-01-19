---
title: Agent Loop Patterns
source: "[[AutoGPT]], [[LangGraph]]"
category: Agent Architecture
tags:
  - pattern
  - agent-loop
  - execution-cycle
  - action-selection
---

# Agent Loop Patterns

## Pattern Overview

The agent loop is the fundamental execution cycle that enables autonomous agents to operate: perceive the environment, reason about what to do, take action, and repeat until the goal is achieved. This pattern is central to all agentic systems.

**Core Concept**: Agents operate in a continuous cycle of perception → reasoning → action → observation, with mechanisms to control when the loop continues or terminates.

## The Classical Agent Loop (ReAct Pattern)

The most common agent loop pattern follows the **ReAct (Reasoning and Acting)** paradigm:

```
┌─────────────────────────────────────────┐
│         Agent Loop Cycle                │
│                                         │
│  1. Observe  → 2. Think → 3. Act       │
│       ↑                        ↓        │
│       └────────────────────────┘        │
│           (Repeat until done)           │
└─────────────────────────────────────────┘
```

### Three Phases of Execution

**Phase 1: Observe (Input)**
- Collect current state and context
- Review message history
- Access available tools/commands
- Check constraints and directives

**Phase 2: Think (Reasoning)**
- Analyze current situation
- Determine next best action
- Select tool/command to use
- Generate arguments for tool

**Phase 3: Act (Execution)**
- Execute selected tool/command
- Capture results
- Handle errors
- Update state

## Implementation Pattern 1: LangGraph Graph-Based Loop

LangGraph implements the agent loop as a **state graph** with conditional edges.

### Architecture

```python
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
from typing import Annotated, Sequence, TypedDict

class AgentState(TypedDict):
    """The state that flows through the agent loop"""
    messages: Annotated[Sequence[BaseMessage], add_messages]

# Create the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("agent", call_model)      # Reasoning node
workflow.add_node("action", tool_node)      # Action execution node

# Set entry point
workflow.set_entry_point("agent")

# Add conditional edge (loop control)
workflow.add_conditional_edges(
    "agent",
    should_continue,  # Decision function
    {
        "continue": "action",  # Loop back through tools
        "end": END,            # Terminate loop
    }
)

# Add edge from action back to agent
workflow.add_edge("action", "agent")

# Compile into executable
graph = workflow.compile()
```

### Key Components

#### 1. State Management
```python
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    # add_messages: Special reducer that appends messages
    # instead of replacing them
```

**Why This Matters**: The `add_messages` annotation is a **reducer function** that defines how state updates are merged. Instead of replacing the entire message list, it appends new messages, preserving conversation history.

#### 2. Decision Function (Loop Control)
```python
def should_continue(state) -> str:
    """Determine whether to continue the loop or terminate"""
    messages = state["messages"]
    last_message = messages[-1]

    # If LLM made tool calls, continue the loop
    if last_message.tool_calls:
        return "continue"

    # No tool calls means final answer, terminate
    return "end"
```

**Exit Conditions**:
- **Continue**: Last message contains tool calls → execute tools → loop back
- **End**: Last message has no tool calls → agent provided final answer → terminate

#### 3. Agent Node (Reasoning)
```python
def call_model(state, runtime):
    """The reasoning phase: LLM decides what to do next"""
    model = get_model(runtime.context)  # Dynamic model selection
    messages = state["messages"]

    # LLM reasons about what tool to call (or provides answer)
    response = model.invoke(messages)

    # Return update to state
    return {"messages": [response]}
```

#### 4. Tool Node (Action Execution)
```python
from langgraph.prebuilt import ToolNode

# ToolNode handles tool execution automatically
tool_node = ToolNode(tools)

# Internally:
# 1. Extracts tool calls from last AI message
# 2. Executes each tool
# 3. Returns ToolMessage with results
```

### Complete Working Example

```python
from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# Define tools
tools = [TavilySearchResults(max_results=1)]

# Bind tools to model
model = ChatAnthropic(model="claude-3-sonnet-20240229")
model = model.bind_tools(tools)

# Decision function
def should_continue(state):
    last_message = state["messages"][-1]
    return "continue" if last_message.tool_calls else "end"

# Agent node
def call_model(state):
    response = model.invoke(state["messages"])
    return {"messages": [response]}

# Build graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("action", ToolNode(tools))

workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, {
    "continue": "action",
    "end": END
})
workflow.add_edge("action", "agent")

graph = workflow.compile()

# Execute
result = graph.invoke({"messages": [HumanMessage("What's the weather?")]})
```

## Implementation Pattern 2: AutoGPT Pipeline-Based Loop

AutoGPT implements the agent loop through a **pipeline architecture** with explicit proposal and execution phases.

### Architecture

```python
class Agent(BaseAgent):
    async def propose_action(self) -> ActionProposal:
        """Phase 1: Reasoning - Propose what to do next"""
        # Gather context via pipeline
        resources = await self.run_pipeline(DirectiveProvider.get_resources)
        constraints = await self.run_pipeline(DirectiveProvider.get_constraints)
        commands = await self.run_pipeline(CommandProvider.get_commands)
        messages = await self.run_pipeline(MessageProvider.get_messages)

        # Build prompt with all context
        prompt = self.prompt_strategy.build_prompt(
            messages=messages,
            task=self.state.task,
            commands=function_specs_from_commands(commands),
        )

        # Get LLM to propose action
        response = await self.llm_provider.create_chat_completion(prompt)

        return response.parsed_result

    async def execute(self, proposal: ActionProposal) -> ActionResult:
        """Phase 2: Execution - Execute the proposed action"""
        tool = proposal.use_tool

        try:
            # Execute the tool
            return_value = await self._execute_tool(tool)
            result = ActionSuccessResult(outputs=return_value)
        except AgentException as e:
            result = ActionErrorResult.from_exception(e)

        # Run post-execution hooks
        await self.run_pipeline(AfterExecute.after_execute, result)

        return result
```

### Key Components

#### 1. Component Pipeline System
```python
# Pipeline allows components to contribute to agent behavior
resources = await self.run_pipeline(DirectiveProvider.get_resources)
# Multiple components can implement get_resources()
# Results are aggregated into a single list

# Built-in components:
self.system = SystemComponent()           # System directives
self.history = ActionHistoryComponent()   # Memory management
self.file_manager = FileManagerComponent()
self.code_executor = CodeExecutorComponent()
self.web_search = WebSearchComponent()
```

**Pipeline Pattern**: Components register themselves to provide:
- **Resources** (what the agent has access to)
- **Constraints** (what the agent must/must not do)
- **Best practices** (guidance for good behavior)
- **Commands** (available actions)
- **Messages** (conversation context)

#### 2. Proposal-Execute Separation
```python
# External loop (in application code):
while not done:
    # Phase 1: Agent proposes action
    proposal = await agent.propose_action()

    # Optional: Human approval gate
    if requires_approval(proposal):
        if not await get_human_approval(proposal):
            result = await agent.do_not_execute(proposal, feedback)
            continue

    # Phase 2: Agent executes action
    result = await agent.execute(proposal)

    # Check termination conditions
    done = is_goal_achieved(result)
```

**Benefits**:
- **Human-in-the-loop**: Can approve/deny actions before execution
- **Audit trail**: Proposals logged separately from executions
- **Rollback capability**: Can reject proposal without side effects

#### 3. Prompt Strategy Pattern
```python
class OneShotAgentPromptStrategy:
    def build_prompt(
        self,
        messages: list[ChatMessage],
        task: str,
        commands: list[CommandSpec],
        ai_profile: dict,
        ai_directives: Directives,
    ) -> ChatPrompt:
        """Construct the prompt for the LLM"""

        prompt_parts = [
            self._system_prompt(ai_profile, ai_directives),
            self._constraints(ai_directives.constraints),
            self._resources(ai_directives.resources),
            self._best_practices(ai_directives.best_practices),
            self._commands(commands),
            self._task(task),
            *messages,
        ]

        return ChatPrompt(messages=prompt_parts, functions=commands)
```

**Extensibility**: Different prompt strategies can be swapped:
- `OneShotAgentPromptStrategy` - Single action per cycle
- `PlanAndExecutePromptStrategy` - Multi-step planning
- Custom strategies for domain-specific reasoning

#### 4. Error Handling and Recovery
```python
async def execute(self, proposal: ActionProposal) -> ActionResult:
    try:
        return_value = await self._execute_tool(proposal.use_tool)
        result = ActionSuccessResult(outputs=return_value)

    except AgentTerminated:
        raise  # Propagate termination signal

    except AgentException as e:
        # Recoverable errors become feedback for next iteration
        result = ActionErrorResult.from_exception(e)
        logger.warning(f"{tool} raised an error: {e}")

    # Check if result is too large (would exceed token limit)
    result_tlength = self.llm_provider.count_tokens(str(result))
    if result_tlength > self.send_token_limit // 3:
        result = ActionErrorResult(
            reason=f"Command returned too much output. "
            "Do not execute this command again with same arguments."
        )

    return result
```

**Error Recovery**: Errors become observations fed back into the loop, allowing the agent to adapt its strategy.

## Loop Control Patterns

### Pattern 1: Tool Call Detection (LangGraph)
```python
def should_continue(state):
    """Continue if LLM requested tools, end if it provided answer"""
    last_message = state["messages"][-1]
    return "continue" if last_message.tool_calls else "end"
```

**When to Use**: Simple agents where tool usage indicates incomplete work.

### Pattern 2: Explicit Termination Signal (AutoGPT)
```python
class FinishCommand:
    """Agent calls this to indicate task completion"""
    name = "finish"

    async def execute(self, reason: str):
        raise AgentTerminated(reason)

# In loop:
try:
    result = await agent.execute(proposal)
except AgentTerminated:
    break  # Exit loop
```

**When to Use**: Agents that need explicit "I'm done" signal.

### Pattern 3: Max Iterations Limit
```python
max_iterations = 25

for i in range(max_iterations):
    proposal = await agent.propose_action()
    result = await agent.execute(proposal)

    if is_goal_achieved(result):
        break
else:
    # Hit max iterations without completing
    raise TimeoutError("Agent exceeded maximum iterations")
```

**When to Use**: Always use as safety mechanism to prevent infinite loops.

### Pattern 4: Remaining Steps Budget (LangGraph)
```python
from langgraph.managed import RemainingSteps

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    remaining_steps: RemainingSteps  # Automatically decremented

def call_model(state):
    if state["remaining_steps"] <= 0:
        return {"messages": [AIMessage("Out of steps")]}

    # Normal reasoning
    response = model.invoke(state["messages"])
    return {"messages": [response]}
```

**When to Use**: LangGraph agents where step budget needs to be state-aware.

## State Management Patterns

### Pattern 1: Message-Based State (LangGraph)
```python
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    # State is the conversation history itself
```

**Benefits**:
- Simple and LLM-native
- Easy to inspect and debug
- Automatically provides full context

**Trade-offs**:
- Can grow large (token limits)
- Requires summarization for long conversations

### Pattern 2: Episodic History (AutoGPT)
```python
class EpisodicActionHistory:
    """Manages action history in episodes with summarization"""

    episodes: list[Episode]
    cursor: EpisodeCursor  # Tracks position in history

    def compress_oldest_episode(self):
        """Summarize old episode to reduce token usage"""
        oldest = self.episodes[0]
        summary = self.summarize(oldest)
        self.episodes[0] = Episode(summary=summary)
```

**Benefits**:
- Scalable to long-running agents
- Retains important information while compressing details
- Configurable compression strategies

**Trade-offs**:
- More complex to implement
- Information loss in summarization

### Pattern 3: Structured State (LangGraph Extended)
```python
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    current_plan: list[str]  # Explicit planning state
    completed_steps: set[str]  # Track progress
    context: dict[str, Any]  # Domain-specific data
```

**Benefits**:
- Explicit representation of agent's mental model
- Can track complex workflows
- Enables sophisticated control flow

**Trade-offs**:
- Must manually manage state updates
- More coupling between components

## Tool Integration Patterns

### Pattern 1: Declarative Tool Binding (LangGraph)
```python
from langchain_core.tools import tool

@tool
def search(query: str) -> str:
    """Search for information on the web"""
    return tavily_client.search(query)

# Bind to model
model = ChatAnthropic(model="claude-3-sonnet")
model = model.bind_tools([search])

# Tool execution handled automatically by ToolNode
tool_node = ToolNode([search])
```

**Benefits**:
- Type-safe tool definitions
- Automatic schema generation for LLM
- Framework handles execution

### Pattern 2: Command Registry (AutoGPT)
```python
class Command:
    names: tuple[str, ...]  # Primary name + aliases
    description: str
    parameters: list[Parameter]

    async def __call__(self, **kwargs) -> Any:
        """Execute the command"""
        pass

# Register via component system
class MyComponent(CommandProvider):
    def get_commands(self) -> list[Command]:
        return [
            Command(
                names=("search_web",),
                description="Search the web",
                parameters=[
                    Parameter("query", type=str, required=True)
                ],
                method=self.search,
            )
        ]
```

**Benefits**:
- Components can dynamically provide commands
- Commands can be enabled/disabled at runtime
- Rich parameter validation

## Human-in-the-Loop Patterns

### Pattern 1: Interrupt Points (LangGraph)
```python
graph = workflow.compile(
    interrupt_before=["action"],  # Pause before tool execution
    checkpointer=MemorySaver(),   # Required for interrupts
)

# Execute until interrupt
config = {"configurable": {"thread_id": "1"}}
for event in graph.stream(input, config):
    print(event)
    # Pauses before "action" node

# Get state and resume
state = graph.get_state(config)
print(f"Waiting for approval: {state.next}")

# Resume execution
graph.invoke(None, config)  # Continue from checkpoint
```

**Benefits**:
- Declarative interrupt points
- State automatically saved
- Can modify state before resuming

### Pattern 2: User Interaction Component (AutoGPT)
```python
class UserInteractionComponent(MessageProvider):
    async def get_messages(self) -> list[ChatMessage]:
        """Allow user to inject feedback into the loop"""
        if self.pending_feedback:
            message = ChatMessage.user(self.pending_feedback)
            self.pending_feedback = None
            return [message]
        return []

# In loop:
proposal = await agent.propose_action()

if requires_approval(proposal):
    approval = input(f"Approve {proposal}? (y/n): ")
    if approval != 'y':
        agent.user_interaction.pending_feedback = input("Feedback: ")
        continue
```

**Benefits**:
- Non-blocking feedback injection
- Integrates with component pipeline
- Feedback becomes part of conversation

## Performance Optimization Patterns

### Pattern 1: Fast/Slow Model Strategy
```python
def select_model(state, runtime):
    """Use fast model for simple tasks, slow for complex"""
    last_message = state["messages"][-1]

    # Simple tool calls → fast model
    if is_simple_tool_call(last_message):
        return fast_model.bind_tools(tools)

    # Complex reasoning → powerful model
    return slow_model.bind_tools(tools)

graph = create_react_agent(
    model=select_model,  # Dynamic selection
    tools=tools
)
```

### Pattern 2: Token Budget Management (AutoGPT)
```python
class ActionHistoryComponent:
    def __init__(self, max_tokens: int, token_counter: Callable):
        self.max_tokens = max_tokens
        self.token_counter = token_counter

    async def get_messages(self) -> list[ChatMessage]:
        """Return history that fits within token budget"""
        messages = []
        token_count = 0

        # Add most recent messages first
        for msg in reversed(self.history):
            msg_tokens = self.token_counter(msg)
            if token_count + msg_tokens > self.max_tokens:
                break
            messages.insert(0, msg)
            token_count += msg_tokens

        return messages
```

### Pattern 3: Parallel Tool Execution
```python
from langgraph.types import Send

def call_tools(state):
    """Execute multiple tool calls in parallel"""
    last_message = state["messages"][-1]

    # Create parallel execution tasks
    return [
        Send("execute_tool", {"tool_call": tc})
        for tc in last_message.tool_calls
    ]

workflow.add_conditional_edges("agent", call_tools)
```

## Related Patterns

- [[state-management-patterns]] - Managing agent memory and context
- [[structured-lifecycle-pattern]] - Organizing complex agent workflows
- [[progressive-disclosure-pattern]] - Managing tool and context complexity
- [[mcp-server-integration]] - Providing tools via MCP protocol

## References

- [AutoGPT Agent Implementation](c:\Users\Stang3x\Documents\Personal - Dan\Agentic Workflows\references\AutoGPT\classic\original_autogpt\autogpt\agents\agent.py)
- [LangGraph ReAct Agent](c:\Users\Stang3x\Documents\Personal - Dan\Agentic Workflows\references\langgraph\libs\prebuilt\langgraph\prebuilt\chat_agent_executor.py)
- [LangGraph Examples](c:\Users\Stang3x\Documents\Personal - Dan\Agentic Workflows\references\langgraph\libs\cli\examples\graphs\agent.py)

## Key Takeaways

1. **Core loop is universal**: Observe → Think → Act → (Repeat or Exit)
2. **Graph-based is declarative**: LangGraph's StateGraph makes loop structure explicit
3. **Pipeline-based is flexible**: AutoGPT's component system enables dynamic behavior
4. **Loop control is critical**: Must have clear termination conditions
5. **State management scales differently**: Message-based is simple, episodic scales better
6. **Human-in-the-loop requires checkpointing**: Can't pause without state persistence
7. **Tool integration varies**: Declarative (LangGraph) vs Registry (AutoGPT)
8. **Performance needs dynamic strategies**: Fast/slow models, token budgets, parallel execution
