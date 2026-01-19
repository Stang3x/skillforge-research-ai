# n8n Skills for Claude Code - Integration Guide

**Reference**: `references/n8n-skills/`
**Source**: https://github.com/czlonkowski/n8n-skills
**Requires**: [n8n-mcp](https://github.com/czlonkowski/n8n-mcp) MCP server

## Overview

The n8n-skills repository provides **7 expert Claude Code skills** specifically designed for building production-ready n8n workflows programmatically. These skills teach Claude how to use n8n effectively through the n8n-mcp MCP server.

## Why These Skills Matter for Agentic Workflows

n8n is a powerful visual workflow automation platform that can orchestrate agentic systems. These skills enable you to:
- Build n8n workflows conversationally with Claude Code
- Automate workflow creation and validation
- Leverage 2,653+ n8n templates for agentic patterns
- Connect AI agents through n8n's AI workflow capabilities

## The 7 Complementary Skills

### 1. n8n Expression Syntax

**Purpose**: Correct n8n expression syntax and common patterns

**Activates When**:
- Writing expressions
- Using {{}} syntax
- Accessing $json/$node variables
- Troubleshooting expression errors

**Key Concepts**:
```javascript
// Core variables
$json           // Current item data
$node["Node Name"]  // Access other node's data
$now            // Current timestamp
$env            // Environment variables

// CRITICAL GOTCHA: Webhook data location
$json.body      // Webhook data is here, NOT in $json directly!

// Common patterns
{{ $json.name }}                    // Access field
{{ $node["HTTP Request"].json }}    // Access other node
{{ $now.toISO() }}                  // Current timestamp
```

**Common Mistakes**:
- Using `$json.field` for webhook data (should be `$json.body.field`)
- Forgetting `{{}}` wrappers in expression fields
- Using expressions in Code nodes (use JavaScript instead)

---

### 2. n8n MCP Tools Expert (HIGHEST PRIORITY)

**Purpose**: Expert guide for using n8n-mcp MCP tools effectively

**Activates When**:
- Searching for nodes
- Validating configurations
- Accessing templates
- Managing workflows

**Key Features**:

**Tool Selection Guide**:
```bash
# Search for nodes
search_nodes - Find nodes by functionality

# Get node details
get_node_docs - Full documentation for a node

# Validate workflow
validate_workflow - Check workflow before saving

# Access templates
get_template - Retrieve workflow templates
```

**NodeType Format**:
```
When using MCP tools:
- Use: nodes-base.slack
- NOT: n8n-nodes-base.slack

When in actual workflow JSON:
- Use: n8n-nodes-base.slack
- NOT: nodes-base.slack
```

**Validation Profiles**:
```
minimal      - Basic structure check
runtime      - What n8n actually validates
ai-friendly  - Relaxed for iterative development
strict       - Comprehensive validation
```

**Smart Parameters**:
```bash
# For IF nodes, include branch parameter
search_nodes --branch="true" "if node"
```

**Auto-Sanitization**: The MCP server automatically fixes common issues like missing credentials

---

### 3. n8n Workflow Patterns

**Purpose**: Build workflows using 5 proven architectural patterns

**Activates When**:
- Creating workflows
- Connecting nodes
- Designing automation

**The 5 Proven Patterns**:

#### Pattern 1: Webhook Processing
```
Webhook Trigger → Code/IF → Process → Response/Action
Use for: APIs, form submissions, external triggers
```

#### Pattern 2: HTTP API Client
```
Schedule/Manual → HTTP Request → Process → Store/Notify
Use for: API polling, data fetching, integrations
```

#### Pattern 3: Database Operations
```
Trigger → Query/CRUD → Process → Update/Notify
Use for: Data sync, reports, batch operations
```

#### Pattern 4: AI Workflows
```
Trigger → AI Agent → Tools → Response → Action
Use for: Conversational AI, intelligent automation
```

#### Pattern 5: Scheduled Processing
```
Cron → Fetch → Process → Store → Notify
Use for: Reports, backups, monitoring
```

**Workflow Creation Checklist**:
1. Choose pattern based on trigger type
2. Select nodes using search_nodes
3. Configure nodes with proper parameters
4. Connect nodes following pattern
5. Validate with appropriate profile
6. Test with sample data

---

### 4. n8n Validation Expert

**Purpose**: Interpret validation errors and guide fixing

**Activates When**:
- Validation fails
- Debugging workflow errors
- Handling false positives

**Validation Loop Workflow**:
```
1. Build workflow
2. Validate with ai-friendly profile
3. Fix structural issues
4. Validate with runtime profile
5. Fix operation-specific issues
6. Final validation with strict (optional)
```

**Common Validation Errors**:

```json
// Error: Missing required property
{
  "error": "Missing required property: url",
  "node": "HTTP Request",
  "fix": "Add url parameter to node.parameters"
}

// Error: Invalid connection
{
  "error": "Connection source not found",
  "fix": "Ensure source node name matches exactly"
}

// Error: Credential mismatch
{
  "error": "credentialType mismatch",
  "fix": "Use correct credential type for node operation"
}
```

**Auto-Sanitization Behavior**:
- Adds default credentials automatically
- Fixes common parameter issues
- Enables during ai-friendly/minimal validation
- Disable for production with strict profile

**False Positives**:
- AI nodes often have many optional params (safe to ignore)
- Expression validation may flag valid syntax
- Template examples might use deprecated patterns

---

### 5. n8n Node Configuration

**Purpose**: Operation-aware node configuration guidance

**Activates When**:
- Configuring nodes
- Understanding property dependencies
- Setting up AI workflows

**Property Dependency Rules**:

```javascript
// HTTP Request node
{
  sendBody: true,
  contentType: "json"  // Required when sendBody=true
}

// Database nodes
{
  operation: "update",
  updateKey: "id"      // Required for update operation
}

// AI nodes
{
  operation: "message",
  model: "gpt-4"       // Required for most AI operations
}
```

**AI Connection Types** (8 types for AI Agent workflows):
```
1. ai_tool         - Custom tools for agents
2. ai_memory       - Agent memory systems
3. ai_document     - Document loaders
4. ai_embedding    - Vector embeddings
5. ai_vectorStore  - Vector databases
6. ai_retriever    - Information retrieval
7. ai_outputParser - Parse AI responses
8. ai_chain        - Chain multiple AI ops
```

**Common Configuration Patterns**:

```javascript
// Webhook node
{
  path: "webhook-name",
  httpMethod: "POST",
  responseMode: "responseNode"  // or "onReceived"
}

// Code node
{
  mode: "runOnceForAllItems",  // or "runOnceForEachItem"
  jsCode: "// Your code here"
}

// IF node
{
  conditions: {
    string: [
      {
        value1: "={{ $json.status }}",
        operation: "equals",
        value2: "success"
      }
    ]
  }
}
```

---

### 6. n8n Code JavaScript

**Purpose**: Write effective JavaScript code in n8n Code nodes

**Activates When**:
- Writing JavaScript in Code nodes
- Troubleshooting Code node errors
- Making HTTP requests with $helpers
- Working with dates

**Data Access Patterns**:

```javascript
// Access all input items
const items = $input.all();

// Access first item
const firstItem = $input.first();

// Access current item (in runOnceForEachItem mode)
const item = $input.item;

// CRITICAL GOTCHA: Webhook data location
const webhookData = $json.body;  // NOT $json directly!
```

**Correct Return Format**:

```javascript
// CORRECT - Array of objects with json property
return [
  { json: { result: "value1" } },
  { json: { result: "value2" } }
];

// WRONG - Will cause errors
return { result: "value" };  // Missing array wrapper
return [{ result: "value" }];  // Missing json property
```

**Built-in Functions**:

```javascript
// HTTP requests
const response = await $helpers.httpRequest({
  url: 'https://api.example.com/data',
  method: 'GET',
  headers: { 'Authorization': 'Bearer token' }
});

// Date manipulation (Luxon DateTime)
const now = DateTime.now();
const tomorrow = now.plus({ days: 1 });
const formatted = now.toISO();

// JSON path queries
const result = $jmespath($json, 'items[?price > `10`].name');
```

**Top 5 Error Patterns** (covers 62%+ of failures):

```javascript
// 1. Wrong return format
// WRONG: return result;
// RIGHT: return [{ json: result }];

// 2. Undefined variable access
// WRONG: const value = $json.field.subfield;  // Crashes if field undefined
// RIGHT: const value = $json.field?.subfield || 'default';

// 3. Webhook data access
// WRONG: const email = $json.email;
// RIGHT: const email = $json.body.email;

// 4. Async/await mistakes
// WRONG: const data = $helpers.httpRequest({ url });
// RIGHT: const data = await $helpers.httpRequest({ url });

// 5. Array iteration errors
// WRONG: items.forEach(item => { return { json: item } });  // forEach doesn't return
// RIGHT: return items.map(item => ({ json: item }));
```

**10 Production-Tested Patterns**:

```javascript
// 1. Safe property access
const value = $json.path?.to?.property ?? 'default';

// 2. Transform array items
return $input.all().map(item => ({
  json: {
    ...item.json,
    processed: true
  }
}));

// 3. Filter items
return $input.all().filter(item =>
  item.json.status === 'active'
);

// 4. Aggregate data
const total = $input.all().reduce((sum, item) =>
  sum + (item.json.amount || 0), 0
);

// 5. External API call with error handling
try {
  const response = await $helpers.httpRequest({
    url: 'https://api.example.com/data',
    method: 'POST',
    body: { data: $json.body },
    json: true
  });
  return [{ json: response }];
} catch (error) {
  return [{ json: { error: error.message } }];
}

// 6. Date calculations
const startDate = DateTime.fromISO($json.body.date);
const endDate = startDate.plus({ days: 7 });
return [{ json: {
  start: startDate.toISO(),
  end: endDate.toISO()
}}];

// 7. String manipulation
const cleaned = $json.body.text
  .toLowerCase()
  .trim()
  .replace(/[^\w\s]/g, '');

// 8. Conditional logic
const status = $json.body.score > 80 ? 'pass' : 'fail';

// 9. Merge multiple inputs
const merged = $input.all().reduce((acc, item) => ({
  ...acc,
  ...item.json
}), {});

// 10. Generate unique items
const uniqueIds = new Set();
return $input.all().filter(item => {
  if (uniqueIds.has(item.json.id)) return false;
  uniqueIds.add(item.json.id);
  return true;
});
```

---

### 7. n8n Code Python

**Purpose**: Write Python code in n8n Code nodes with proper limitations awareness

**Activates When**:
- Writing Python in Code nodes
- Need to know Python limitations
- Working with standard library

**IMPORTANT**: Use JavaScript for 95% of use cases. Python has significant limitations.

**Python Data Access**:

```python
# Access input items
items = _input.all()

# Access current item's JSON
data = _json

# Access another node's data
other_node = _node["Node Name"]
```

**CRITICAL LIMITATION - No External Libraries**:

```python
# NOT AVAILABLE:
# - requests (use JavaScript $helpers.httpRequest instead)
# - pandas (use JavaScript array methods)
# - numpy (use JavaScript Math)
# - any pip packages

# AVAILABLE - Standard Library Only:
import json
import datetime
import re
import math
import random
import base64
import hashlib
import urllib.parse
```

**Standard Library Patterns**:

```python
# JSON parsing
import json
data = json.loads(_json["raw_string"])
result = json.dumps({"key": "value"})

# Date manipulation
from datetime import datetime, timedelta
now = datetime.now()
tomorrow = now + timedelta(days=1)
formatted = now.isoformat()

# Regex operations
import re
pattern = re.compile(r'\d+')
matches = pattern.findall(_json["text"])

# URL encoding
from urllib.parse import urlencode, quote
params = urlencode({"key": "value"})
encoded = quote("text with spaces")

# Hashing
import hashlib
hash_obj = hashlib.sha256(_json["data"].encode())
hex_digest = hash_obj.hexdigest()
```

**Workarounds for Missing Libraries**:

```python
# Instead of requests, use JavaScript:
# Switch to JavaScript Code node and use:
# const response = await $helpers.httpRequest({...})

# Instead of pandas, use Python dict/list comprehensions:
items = _input.all()
filtered = [item for item in items if item["json"]["value"] > 10]
transformed = [{"new_field": item["json"]["old_field"] * 2} for item in items]

# Instead of numpy, use JavaScript Math or Python math:
import math
result = math.sqrt(value)
```

**When to Use Python**:
- Complex text processing with regex
- Specific standard library algorithms
- Legacy Python logic you're porting
- Date/time calculations with datetime

**When to Use JavaScript Instead**:
- HTTP requests
- API calls
- Data transformations
- Working with JSON
- Almost everything else

---

## Installation

### Prerequisites

1. **Install n8n-mcp MCP Server**:
```bash
# See: https://github.com/czlonkowski/n8n-mcp
npm install -g n8n-mcp

# Configure in .mcp.json
{
  "mcpServers": {
    "n8n": {
      "command": "n8n-mcp",
      "args": [],
      "env": {
        "N8N_API_KEY": "your-api-key",
        "N8N_BASE_URL": "http://localhost:5678"
      }
    }
  }
}
```

2. **Install n8n Skills**:

**Method 1: Plugin Installation** (Recommended)
```bash
/plugin install czlonkowski/n8n-skills
```

**Method 2: Manual Installation**
```bash
# Already cloned in references/n8n-skills
cp -r references/n8n-skills/skills/* ~/.claude/skills/

# On Windows:
xcopy "references\n8n-skills\skills" "%USERPROFILE%\.claude\skills" /E /I
```

**Method 3: Via Marketplace**
```bash
/plugin marketplace add czlonkowski/n8n-skills
/plugin install
# Select "n8n-mcp-skills"
```

---

## Usage Examples

### Building a Webhook to Slack Workflow

**You**: "Build a webhook workflow that sends data to Slack"

**Skills Activate**:
1. **Workflow Patterns** - Identifies webhook processing pattern
2. **MCP Tools Expert** - Searches for Webhook and Slack nodes
3. **Node Configuration** - Guides setup of both nodes
4. **Code JavaScript** - Helps process webhook data from `$json.body`
5. **Expression Syntax** - Maps data to Slack message
6. **Validation Expert** - Validates final workflow

**Result**: Production-ready workflow in one conversation

---

### Processing API Data with AI

**You**: "Create a workflow that fetches API data and uses AI to summarize it"

**Skills Activate**:
1. **Workflow Patterns** - HTTP API Client + AI Workflow patterns
2. **MCP Tools Expert** - Finds HTTP Request and AI nodes
3. **Node Configuration** - Sets up AI Agent with proper connections
4. **Code JavaScript** - Processes API response
5. **Validation Expert** - Validates AI workflow structure

---

## Integration with Your Agentic Workflows

### Use Cases for n8n in Agentic Systems

1. **Agent Orchestration**:
   - Use n8n to coordinate multiple AI agents
   - Route requests based on intent
   - Manage agent state and memory

2. **Tool Integration**:
   - Connect agents to external APIs
   - Database operations for agent memory
   - Webhook endpoints for agent triggers

3. **Workflow Automation**:
   - Automated agent deployment
   - Testing and validation pipelines
   - Monitoring and logging

4. **AI Agent Patterns**:
   - Build conversational agents with AI nodes
   - Chain LLM calls for complex reasoning
   - Implement tool-using agents

### Learning from n8n Skills

**Extract Patterns**:
```bash
# Study the skills structure
cd references/n8n-skills/skills

# Each skill has:
# - SKILL.md (knowledge base)
# - skill.json (metadata)
# - evaluations/ (test cases)
```

**Document in Your Workspace**:
1. Read each SKILL.md
2. Extract relevant patterns for your agents
3. Document in `docs/patterns/n8n-custom-node-patterns.md`
4. Note evaluation approach for testing agents

---

## Key Takeaways

1. **Skills Work Together**: All 7 skills compose seamlessly for end-to-end workflow creation

2. **Evaluation-First Development**: Each skill has 3+ test scenarios - apply this to your agents

3. **MCP-Informed**: Skills are built on real MCP tool responses - shows power of MCP integration

4. **Concise Knowledge**: Each skill under 500 lines - demonstrates effective knowledge compression

5. **Real Examples**: All patterns from 2,653+ templates - emphasizes learning from real implementations

---

## Next Steps

1. **Install n8n-mcp**: Set up the MCP server first
2. **Install Skills**: Use one of the installation methods
3. **Test with Examples**: Try the usage examples above
4. **Build Workflows**: Create your first agentic workflow in n8n
5. **Document Patterns**: Extract patterns to your workspace

---

## Resources

- **n8n-mcp Server**: https://github.com/czlonkowski/n8n-mcp
- **n8n Platform**: https://n8n.io/
- **Skills Repository**: `references/n8n-skills/`
- **2,653+ Templates**: Accessible via n8n-mcp `get_template` tool

---

**This skills package demonstrates how to teach Claude domain-specific expertise through well-structured skills that compose together. Apply these principles to your own agentic system development!**
