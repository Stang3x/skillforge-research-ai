# Hands-On Learning Path: Agentic Workflows for Beginners

**Your Profile**: Beginner programmer (< 1 year), prefers hands-on experimentation, seeking research/academic understanding

**Goal**: Build your understanding through progressively complex runnable examples, from 20 lines to complete systems

## Setup

You have: ✅ Python 3.14.2 ✅ pip 25.3

Install the only dependency you need to start:
```bash
pip install anthropic
```

Set your API key (get one from https://console.anthropic.com):
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

---

## Level 1: The Simplest Possible Agent (30 minutes)

**Concept**: An agent is just a loop: Ask LLM → Get response → Repeat

**Experiment 1.1**: Create `experiments/01_simplest_agent.py`

```python
from anthropic import Anthropic

client = Anthropic()

# Single interaction - not even a loop yet
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[{"role": "user", "content": "What is 5 + 3?"}]
)

print(response.content[0].text)
```

**Run it**: `python experiments/01_simplest_agent.py`

**Expected output**: "5 + 3 equals 8"

**What you learned**: The absolute minimum - sending a message to an LLM and getting a response.

---

**Experiment 1.2**: Add a conversation loop

```python
from anthropic import Anthropic

client = Anthropic()
conversation = []

while True:
    user_input = input("You: ")
    if user_input.lower() in ["quit", "exit"]:
        break

    # Add user message to conversation
    conversation.append({"role": "user", "content": user_input})

    # Get response
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=conversation
    )

    assistant_message = response.content[0].text

    # Add assistant response to conversation
    conversation.append({"role": "assistant", "content": assistant_message})

    print(f"Agent: {assistant_message}\n")
```

**Run it**: Have a conversation!

**What you learned**:
- Agents maintain conversation history
- History = list of messages
- This is the foundation of ALL agent systems

---

## Level 2: Adding Tools (1 hour)

**Concept**: Agents become useful when they can DO things (use tools)

**Experiment 2.1**: Agent with a calculator tool

Create `experiments/02_agent_with_tools.py`:

```python
from anthropic import Anthropic
import json

client = Anthropic()

# Define a simple calculator tool
tools = [
    {
        "name": "calculator",
        "description": "Performs basic arithmetic operations",
        "input_schema": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                    "description": "The operation to perform"
                },
                "a": {"type": "number", "description": "First number"},
                "b": {"type": "number", "description": "Second number"}
            },
            "required": ["operation", "a", "b"]
        }
    }
]

# Tool execution function
def execute_calculator(operation, a, b):
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        return a / b if b != 0 else "Error: Division by zero"

# Agent loop with tools
messages = [{"role": "user", "content": "What is 157 * 892?"}]

while True:
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        tools=tools,
        messages=messages
    )

    print(f"Stop reason: {response.stop_reason}")

    # If the agent is done, print final response
    if response.stop_reason == "end_turn":
        print(f"Agent: {response.content[0].text}")
        break

    # If agent wants to use a tool
    if response.stop_reason == "tool_use":
        # Add agent's response (including tool request) to conversation
        messages.append({"role": "assistant", "content": response.content})

        # Execute each tool the agent requested
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"\nAgent wants to use tool: {block.name}")
                print(f"With parameters: {block.input}")

                # Execute the tool
                result = execute_calculator(**block.input)
                print(f"Tool result: {result}")

                # Format result for agent
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(result)
                })

        # Send tool results back to agent
        messages.append({"role": "user", "content": tool_results})
```

**Run it**: `python experiments/02_agent_with_tools.py`

**Expected output**:
```
Stop reason: tool_use
Agent wants to use tool: calculator
With parameters: {'operation': 'multiply', 'a': 157, 'b': 892}
Tool result: 140044
Stop reason: end_turn
Agent: 157 multiplied by 892 equals 140,044.
```

**What you learned**:
- Agents don't know math by default - they need tools
- Tool use is a **two-step loop**: Agent requests tool → We execute → Send result back
- The agent decides WHEN and HOW to use tools
- `stop_reason` tells us what the agent wants to do next

---

**Experiment 2.2**: Add a file reading tool

```python
# Add this to your tools list:
{
    "name": "read_file",
    "description": "Reads the contents of a file",
    "input_schema": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to read"
            }
        },
        "required": ["file_path"]
    }
}

# Add this to your execute functions:
def execute_read_file(file_path):
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File {file_path} not found"
    except Exception as e:
        return f"Error: {str(e)}"

# Update tool execution to handle both tools:
for block in response.content:
    if block.type == "tool_use":
        if block.name == "calculator":
            result = execute_calculator(**block.input)
        elif block.name == "read_file":
            result = execute_read_file(**block.input)
```

**Try asking**: "Read the file at experiments/01_simplest_agent.py and tell me what it does"

**What you learned**: Agents can use multiple tools. YOU decide what tools to give them.

---

## Level 3: Agent Memory (1 hour)

**Concept**: Agents that remember across sessions

**Experiment 3.1**: Simple file-based memory

Create `experiments/03_agent_with_memory.py`:

```python
from anthropic import Anthropic
import json
import os

client = Anthropic()
MEMORY_FILE = "experiments/agent_memory.json"

# Load memory from file
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    return []

# Save memory to file
def save_memory(messages):
    with open(MEMORY_FILE, 'w') as f:
        json.dump(messages, f, indent=2)

# Load previous conversation
conversation = load_memory()
print(f"Loaded {len(conversation)} previous messages")

# Conversation loop
while True:
    user_input = input("You: ")
    if user_input.lower() in ["quit", "exit"]:
        save_memory(conversation)
        print("Memory saved!")
        break

    conversation.append({"role": "user", "content": user_input})

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=conversation
    )

    assistant_message = response.content[0].text
    conversation.append({"role": "assistant", "content": assistant_message})

    print(f"Agent: {assistant_message}\n")
```

**Run it twice**:
1. First time: Say "My name is Alex and I love Python"
2. Exit and run again
3. Second time: Ask "What's my name?"

**Expected**: Agent remembers your name from the previous session!

**What you learned**:
- Memory = saved conversation history
- Simple file storage works for basic memory
- This is how tools like ChatGPT remember your conversations

---

**Experiment 3.2**: Memory with search (semantic memory)

This is more advanced - we'll extract facts and store them separately:

```python
from anthropic import Anthropic
import json
import os

client = Anthropic()
FACTS_FILE = "experiments/agent_facts.json"

def load_facts():
    if os.path.exists(FACTS_FILE):
        with open(FACTS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_facts(facts):
    with open(FACTS_FILE, 'w') as f:
        json.dump(facts, f, indent=2)

def extract_and_store_facts(conversation):
    """Ask the agent to extract facts from conversation"""
    extraction_prompt = f"""
    Review this conversation and extract any important facts about the user:

    {json.dumps(conversation, indent=2)}

    Return ONLY a JSON list of facts, like:
    ["User's name is Alex", "User loves Python", "User is learning about agents"]
    """

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{"role": "user", "content": extraction_prompt}]
    )

    try:
        # Parse the facts from response
        facts_text = response.content[0].text
        # Extract JSON from potential markdown code blocks
        if "```json" in facts_text:
            facts_text = facts_text.split("```json")[1].split("```")[0]
        elif "```" in facts_text:
            facts_text = facts_text.split("```")[1].split("```")[0]

        new_facts = json.loads(facts_text.strip())
        return new_facts
    except:
        return []

# Main conversation loop
conversation = []
facts = load_facts()

print(f"I remember {len(facts)} facts about you:")
for fact in facts:
    print(f"  - {fact}")

while True:
    user_input = input("\nYou: ")
    if user_input.lower() in ["quit", "exit"]:
        # Extract facts before exiting
        new_facts = extract_and_store_facts(conversation)
        facts.extend(new_facts)
        save_facts(facts)
        print(f"Learned {len(new_facts)} new facts!")
        break

    # Add facts to context
    context = "Facts I know about you:\n" + "\n".join(facts) if facts else ""

    conversation.append({"role": "user", "content": f"{context}\n\n{user_input}"})

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=conversation[-10:]  # Only last 10 messages to keep context small
    )

    assistant_message = response.content[0].text
    conversation.append({"role": "assistant", "content": assistant_message})

    print(f"Agent: {assistant_message}")
```

**What you learned**:
- Agents can extract structured data from conversations
- You can store facts separately from full conversation
- This is the basis of systems like SimpleMem you saw in the reference repos

---

## Level 4: Combining Everything (2 hours)

**Experiment 4.1**: Build a personal research assistant

Create `experiments/04_research_assistant.py`:

This agent:
- Has memory (remembers your research topics)
- Has tools (can read files, do calculations)
- Has a specific purpose (help with research)

```python
from anthropic import Anthropic
import json
import os

client = Anthropic()

SYSTEM_PROMPT = """You are a research assistant helping a beginner programmer learn about agentic workflows.

Your capabilities:
- You can read files to analyze code examples
- You can perform calculations
- You remember facts about the user's learning progress

Be encouraging and explain concepts simply."""

tools = [
    {
        "name": "read_file",
        "description": "Read a file's contents",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to file"}
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "calculator",
        "description": "Perform arithmetic",
        "input_schema": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"]
                },
                "a": {"type": "number"},
                "b": {"type": "number"}
            },
            "required": ["operation", "a", "b"]
        }
    },
    {
        "name": "save_learning_note",
        "description": "Save a note about something the user learned",
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "What topic was learned"},
                "note": {"type": "string", "description": "The learning note"}
            },
            "required": ["topic", "note"]
        }
    }
]

def execute_tool(tool_name, tool_input):
    if tool_name == "read_file":
        try:
            with open(tool_input["file_path"], 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error: {str(e)}"

    elif tool_name == "calculator":
        ops = {
            "add": lambda a, b: a + b,
            "subtract": lambda a, b: a - b,
            "multiply": lambda a, b: a * b,
            "divide": lambda a, b: a / b if b != 0 else "Error: Division by zero"
        }
        return ops[tool_input["operation"]](tool_input["a"], tool_input["b"])

    elif tool_name == "save_learning_note":
        notes_file = "experiments/learning_notes.json"
        notes = []
        if os.path.exists(notes_file):
            with open(notes_file, 'r') as f:
                notes = json.load(f)

        notes.append({
            "topic": tool_input["topic"],
            "note": tool_input["note"]
        })

        with open(notes_file, 'w') as f:
            json.dump(notes, f, indent=2)

        return f"Saved note about {tool_input['topic']}"

# Main agent loop
def research_assistant_loop():
    conversation = []

    # Load previous learning notes
    if os.path.exists("experiments/learning_notes.json"):
        with open("experiments/learning_notes.json", 'r') as f:
            notes = json.load(f)
            context = "Previous learning notes:\n" + "\n".join([
                f"- {n['topic']}: {n['note']}" for n in notes
            ])
            conversation.append({"role": "user", "content": context})
            conversation.append({"role": "assistant", "content": "I remember our previous sessions!"})

    print("Research Assistant Ready! (type 'quit' to exit)\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit"]:
            break

        conversation.append({"role": "user", "content": user_input})

        # Agent loop with tools
        while True:
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                system=SYSTEM_PROMPT,
                tools=tools,
                messages=conversation
            )

            if response.stop_reason == "end_turn":
                final_text = next((block.text for block in response.content if hasattr(block, "text")), "")
                conversation.append({"role": "assistant", "content": response.content})
                print(f"\nAssistant: {final_text}\n")
                break

            if response.stop_reason == "tool_use":
                conversation.append({"role": "assistant", "content": response.content})

                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        print(f"[Using tool: {block.name}]")
                        result = execute_tool(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": str(result)
                        })

                conversation.append({"role": "user", "content": tool_results})

if __name__ == "__main__":
    research_assistant_loop()
```

**Try these prompts**:
1. "Read the file experiments/01_simplest_agent.py and explain what it does"
2. "Save a note that I learned about agent loops today"
3. Exit and restart - it remembers your note!

**What you learned**: You just built a complete agentic system with:
- Memory (learning notes)
- Tools (read files, calculate, save notes)
- Purpose (research assistant)
- Personality (encouraging, beginner-friendly)

---

## Level 4.5: Bonus - PDF Analysis Agent (30 minutes)

**Real-world application**: Before continuing to Level 5, try this practical agent!

I've created [experiments/pdf_analysis_agent.py](../experiments/pdf_analysis_agent.py) that analyzes PDFs to find content relevant to agentic workflows.

**What it does**:
- Reads large PDFs in chunks (30 pages at a time)
- Sends each chunk to Claude for analysis
- Scores relevance (0-10) for learning agentic systems
- Stops early if the PDF isn't relevant (saves money!)
- Generates a report with recommendations

**Try it**:

```bash
# Analyze a single PDF
python experiments/pdf_analysis_agent.py "e:\Downloads\Pdf Bank\SomeFolder\document.pdf"

# Analyze all PDFs in a directory
python experiments/pdf_analysis_agent.py "e:\Downloads\Pdf Bank" --batch
```

**Why this matters**: This is a **Level 3 agent** (tools + memory + decisions). It demonstrates:

- Chunking large data
- Progressive analysis with early stopping
- Cost optimization
- Real-world usefulness

Read [experiments/README_PDF_AGENT.md](../experiments/README_PDF_AGENT.md) for complete documentation.

---

## Level 5: Understanding the Reference Repos (ongoing)

Now you're ready to understand the 24 repositories I cloned!

**Start with these in order**:

### 1. [nanocode](../references/nanocode/) - Read this FIRST
- Only 250 lines total
- Does exactly what you just built, but cleaner
- Compare their code to your experiments
- **Exercise**: Run nanocode and see how it's similar to your Level 4 agent

### 2. [SimpleMem](../references/SimpleMem/) - Memory patterns
- Now that you built simple memory (Level 3), understand their advanced version
- They use "semantic compression" - which is just smarter fact extraction
- **Exercise**: Replace your `extract_and_store_facts` with their approach

### 3. [agent-browser](../references/agent-browser/) - Browser tool
- Your agent has file tools. This gives agents browser tools.
- Same pattern: tool definition → execution → return result
- **Exercise**: Add a "browse_web" tool to your Level 4 agent

### 4. [autocoder](../references/autocoder/) - Long-running agents
- Your experiments run once then exit
- autocoder runs for hours/days with SQLite memory
- Same concepts, bigger scale
- **Exercise**: Modify your research assistant to use SQLite instead of JSON files

---

## Next Steps

You now understand:
- ✅ Agent loops (ask → respond → repeat)
- ✅ Tools (how agents DO things)
- ✅ Memory (how agents REMEMBER things)
- ✅ Complete systems (combining all three)

**Your learning path**:
1. Build all 5 experiments above (do this FIRST!)
2. Read nanocode source code
3. Pick ONE advanced repo (SimpleMem, agent-browser, or autocoder)
4. Read its README and understand how it's just Level 4 but bigger
5. Try running it locally

**When you're stuck**: Ask specific questions like:
- "In experiment 2.1, why do we need tool_use_id?"
- "How is SimpleMem's semantic compression different from my Level 3.2?"
- "Can I combine agent-browser with my research assistant?"

**Don't do this**: Try to understand all 24 repos at once. Build the experiments first!

---

## Resources

- [Anthropic Tool Use Guide](https://docs.anthropic.com/en/docs/build-with-claude/tool-use) - Official docs for tools
- [nanocode README](../references/nanocode/README.md) - Simplest reference implementation
- [CLAUDE.md](../CLAUDE.md) - Full reference repo list (for when you're ready)

---

**Start here**: Create the `experiments/` directory and build Experiment 1.1. Message me when you've run it successfully!
