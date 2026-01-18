---
title: MCP Server Integration Pattern
source: "[[MCP-Launchpad]], [[anthropic-skills]]"
category: Tool Integration
date: 2025-01-15
tags:
  - pattern
  - mcp
  - tools
  - integration
status: documented
---

# MCP Server Integration Pattern

## Overview

**Source**:
- MCP-Launchpad - `references/MCP-Launchpad/`
- Anthropic Skills (mcp-builder) - `references/anthropic-skills/skills/mcp-builder/`

**Purpose**: Enable AI agents to interact with external services, databases, and APIs through well-designed MCP (Model Context Protocol) servers.

## Context

When to use this pattern:
- Agents need to access external services (databases, APIs, cloud platforms)
- Want standardized, reusable tool interfaces
- Need to scale tool capabilities across multiple agents
- Require security isolation for tool execution
- Building agent systems with persistent memory or state

## The Pattern

### MCP Architecture

```
Agent (Claude) <---> MCP Client <---> MCP Server <---> External Service
                         ↑                ↑
                    Tools/Resources   Database/API/File System
```

**Key Components**:
1. **MCP Server**: Exposes tools and resources via MCP protocol
2. **MCP Client**: Built into Claude Code, handles communication
3. **Tools**: Functions the agent can call (actions)
4. **Resources**: Data the agent can read (passive)
5. **Transport**: How client and server communicate (stdio, HTTP)

### Four-Phase MCP Server Development

#### Phase 1: Deep Research and Planning

**1.1 Understand Modern MCP Design**

**API Coverage vs. Workflow Tools**:
```
Option A: Comprehensive API Coverage
├─ Expose all API endpoints as tools
├─ Agents compose operations flexibly
└─ More tools, but granular control

Option B: Specialized Workflow Tools
├─ Higher-level operations (e.g., "create_issue_with_labels")
├─ Convenient for specific tasks
└─ Fewer tools, but less flexible

RECOMMENDED: Prioritize comprehensive coverage
RATIONALE: Some clients support code execution to compose basic tools
```

**Tool Naming and Discoverability**:
```
✓ GOOD: github_create_issue, github_list_repos
  - Consistent prefix
  - Action-oriented naming
  - Immediately discoverable

✗ BAD: create, list_all, get_data
  - No context
  - Ambiguous
  - Hard to find right tool
```

**Context Management**:
```
Agents benefit from:
- Concise tool descriptions (not verbose docs)
- Ability to filter/paginate results
- Focused, relevant data returns

Design tools that return targeted data, not everything.
```

**Actionable Error Messages**:
```
✗ BAD: "Error: Failed to create resource"

✓ GOOD: "Error: Failed to create issue in repo 'user/project'.
         Reason: Missing required field 'title'.
         Fix: Provide 'title' parameter in request.
         Example: { title: 'Bug report', body: '...' }"
```

**1.2 Study MCP Protocol**

Start with sitemap: `https://modelcontextprotocol.io/sitemap.xml`

Key pages (fetch with `.md` suffix):
- `specification/draft.md` - Protocol overview
- Transport mechanisms (streamable HTTP, stdio)
- Tool, resource, and prompt definitions

**1.3 Choose Technology Stack**

**Recommended**:
- **Language**: TypeScript (best SDK, static typing, good AI code generation)
- **Transport**:
  - Streamable HTTP for remote servers (stateless, scalable)
  - stdio for local servers

**1.4 Plan Implementation**

- Review service API documentation
- List endpoints to implement
- Prioritize comprehensive API coverage
- Identify authentication requirements
- Map data models

---

#### Phase 2: Implementation

**2.1 Project Structure**

**TypeScript Example**:
```
mcp-github-server/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts           # Server entry point
│   ├── tools/
│   │   ├── issues.ts      # Issue tools
│   │   ├── repos.ts       # Repository tools
│   │   └── prs.ts         # Pull request tools
│   ├── client/
│   │   └── github.ts      # GitHub API client
│   ├── types/
│   │   └── schemas.ts     # Zod schemas
│   └── utils/
│       ├── errors.ts      # Error handling
│       └── pagination.ts  # Pagination helpers
└── README.md
```

**2.2 Core Infrastructure**

**API Client with Authentication**:
```typescript
import { Octokit } from '@octokit/rest';

class GitHubClient {
  private octokit: Octokit;

  constructor(token: string) {
    this.octokit = new Octokit({ auth: token });
  }

  async createIssue(owner: string, repo: string, title: string, body: string) {
    try {
      const response = await this.octokit.issues.create({
        owner,
        repo,
        title,
        body
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  private handleError(error: any): Error {
    // Transform to actionable error message
    if (error.status === 401) {
      return new Error(
        'Authentication failed. ' +
        'Fix: Ensure GITHUB_TOKEN environment variable is set. ' +
        'Get token at: https://github.com/settings/tokens'
      );
    }
    // ... more error handling
  }
}
```

**Error Handling Helpers**:
```typescript
export class MCPError extends Error {
  constructor(
    message: string,
    public readonly fix?: string,
    public readonly example?: any
  ) {
    super(message);
  }

  toJSON() {
    return {
      error: this.message,
      fix: this.fix,
      example: this.example
    };
  }
}
```

**Response Formatting**:
```typescript
export function formatAsMarkdown(data: any): string {
  // Convert structured data to markdown for readability
  return `
# Issue #${data.number}: ${data.title}

**State**: ${data.state}
**Created**: ${data.created_at}
**URL**: ${data.html_url}

## Description
${data.body || 'No description'}
  `.trim();
}

export function formatAsJSON(data: any): string {
  return JSON.stringify(data, null, 2);
}
```

**2.3 Implement Tools**

**Input Schema with Zod**:
```typescript
import { z } from 'zod';

const CreateIssueSchema = z.object({
  owner: z.string().describe('Repository owner (username or org)'),
  repo: z.string().describe('Repository name'),
  title: z.string().describe('Issue title'),
  body: z.string().optional().describe('Issue description (markdown supported)'),
  labels: z.array(z.string()).optional().describe('Labels to add'),
  assignees: z.array(z.string()).optional().describe('Users to assign')
});

type CreateIssueInput = z.infer<typeof CreateIssueSchema>;
```

**Output Schema**:
```typescript
const IssueOutputSchema = z.object({
  number: z.number(),
  title: z.string(),
  state: z.enum(['open', 'closed']),
  html_url: z.string(),
  created_at: z.string(),
  body: z.string().nullable()
});
```

**Tool Registration**:
```typescript
server.registerTool({
  name: 'github_create_issue',
  description: 'Create a new issue in a GitHub repository',

  inputSchema: {
    type: 'object',
    properties: {
      owner: { type: 'string', description: 'Repository owner' },
      repo: { type: 'string', description: 'Repository name' },
      title: { type: 'string', description: 'Issue title' },
      body: { type: 'string', description: 'Issue description' }
    },
    required: ['owner', 'repo', 'title']
  },

  outputSchema: IssueOutputSchema, // Helps clients understand response

  annotations: {
    readOnlyHint: false,      // This tool modifies data
    destructiveHint: false,   // Not destructive (can be undone)
    idempotentHint: false,    // Creates new issue each call
    openWorldHint: true       // Works with any valid repo
  },

  async execute(input: CreateIssueInput) {
    const validated = CreateIssueSchema.parse(input);
    const issue = await githubClient.createIssue(
      validated.owner,
      validated.repo,
      validated.title,
      validated.body
    );

    // Return both text and structured data
    return {
      content: [
        { type: 'text', text: formatAsMarkdown(issue) },
        { type: 'json', data: issue }
      ]
    };
  }
});
```

**Pagination Support**:
```typescript
const ListIssuesSchema = z.object({
  owner: z.string(),
  repo: z.string(),
  state: z.enum(['open', 'closed', 'all']).default('open'),
  page: z.number().optional().default(1),
  per_page: z.number().optional().default(30).max(100)
});

server.registerTool({
  name: 'github_list_issues',
  // ... schema and description

  async execute(input) {
    const { owner, repo, state, page, per_page } = ListIssuesSchema.parse(input);

    const issues = await githubClient.listIssues(owner, repo, {
      state,
      page,
      per_page
    });

    return {
      content: [{
        type: 'text',
        text: `Found ${issues.length} issues (page ${page})\n\n` +
              issues.map(i => `#${i.number}: ${i.title}`).join('\n')
      }],
      meta: {
        hasMore: issues.length === per_page,
        nextPage: page + 1
      }
    };
  }
});
```

---

#### Phase 3: Review and Test

**3.1 Code Quality Checklist**

- [ ] No duplicated code (DRY principle)
- [ ] Consistent error handling across all tools
- [ ] Full TypeScript type coverage
- [ ] Clear, concise tool descriptions
- [ ] All major API decisions have ADRs
- [ ] Pagination supported where needed
- [ ] Actionable error messages with fix suggestions

**3.2 Build and Test**

**TypeScript**:
```bash
npm run build
npx @modelcontextprotocol/inspector
```

**Test with Inspector**:
```
MCP Inspector running on http://localhost:3000

Available Tools:
- github_create_issue
- github_list_issues
- github_create_pr

Test: github_create_issue
Input: {
  "owner": "test-user",
  "repo": "test-repo",
  "title": "Test issue"
}

Response: ✓ Success
{
  "number": 42,
  "title": "Test issue",
  ...
}
```

---

#### Phase 4: Create Evaluations

**Purpose**: Test whether LLMs can effectively use your MCP server

**4.1 Create 10 Complex Questions**

Process:
1. **Tool Inspection**: List available tools
2. **Content Exploration**: Use READ-ONLY tools to explore data
3. **Question Generation**: Create realistic, complex questions
4. **Answer Verification**: Solve manually to verify answers

**4.2 Evaluation Requirements**

Each question must be:
- **Independent**: Not dependent on other questions
- **Read-only**: Only non-destructive operations
- **Complex**: Requiring multiple tool calls
- **Realistic**: Based on real use cases
- **Verifiable**: Single, clear answer
- **Stable**: Answer won't change over time

**4.3 Example Evaluations**

```xml
<evaluation>
  <qa_pair>
    <question>In the 'anthropics/anthropic-sdk-python' repository, find the most recent closed issue that mentions 'streaming'. What is the issue number?</question>
    <answer>1234</answer>
  </qa_pair>

  <qa_pair>
    <question>Which user has the most open pull requests across all public repositories in the 'facebook' organization?</question>
    <answer>username123</answer>
  </qa_pair>

  <qa_pair>
    <question>Find repositories owned by 'microsoft' that have both 'typescript' AND 'azure' in their description. How many are there?</question>
    <answer>42</answer>
  </qa_pair>
</evaluation>
```

---

## Trade-offs

> [!success] Pros
> - Standardized interface across all tools
> - Reusable across multiple agents/applications
> - Security isolation (server runs separately)
> - Easy to add new capabilities
> - Protocol-level type safety
> - Built-in error handling patterns

> [!warning] Cons
> - Additional deployment complexity (separate server process)
> - Network latency for remote servers
> - Requires MCP client support
> - More boilerplate than direct API calls
> - Learning curve for MCP protocol

---

## Related Patterns

- [[agent-loop-patterns]] - Agents use MCP tools in act phase
- [[state-management-patterns]] - Memory MCP provides persistent state
- [[progressive-disclosure-pattern]] - Tool descriptions use progressive detail

---

## Examples

### Example 1: GitHub MCP Server (Complete)

**Directory Structure**:
```
mcp-github/
├── src/
│   ├── index.ts
│   ├── tools/
│   │   ├── issues.ts          # 5 tools
│   │   ├── repos.ts            # 4 tools
│   │   └── prs.ts              # 6 tools
│   └── client/github.ts
└── evaluations/
    └── github-eval.xml         # 10 questions
```

**Available Tools** (15 total):
```
Issues:
- github_create_issue
- github_list_issues
- github_get_issue
- github_update_issue
- github_add_comment

Repositories:
- github_list_repos
- github_get_repo
- github_search_repos
- github_create_repo

Pull Requests:
- github_create_pr
- github_list_prs
- github_get_pr
- github_merge_pr
- github_request_review
- github_list_pr_files
```

**Example Tool Implementation**:
```typescript
// src/tools/issues.ts
export function registerIssueTools(server: MCPServer, client: GitHubClient) {
  server.registerTool({
    name: 'github_search_issues',
    description: 'Search issues across GitHub repositories',

    inputSchema: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'Search query (supports GitHub search syntax)'
        },
        sort: {
          type: 'string',
          enum: ['created', 'updated', 'comments'],
          description: 'Sort field'
        },
        order: {
          type: 'string',
          enum: ['asc', 'desc'],
          description: 'Sort order'
        }
      },
      required: ['query']
    },

    async execute(input) {
      const results = await client.searchIssues(
        input.query,
        input.sort,
        input.order
      );

      return {
        content: [{
          type: 'text',
          text: `Found ${results.total_count} issues:\n\n` +
                results.items.slice(0, 10).map(i =>
                  `${i.repository_url.split('/').slice(-2).join('/')}#${i.number}: ${i.title}`
                ).join('\n') +
                (results.total_count > 10 ? `\n\n... and ${results.total_count - 10} more` : '')
        }],
        data: results.items
      };
    }
  });
}
```

### Example 2: Memory MCP Server (Persistent Agent State)

**Purpose**: Give agents persistent memory across sessions

**Available Tools**:
```
- memory_store(key, value, metadata)
- memory_retrieve(key)
- memory_search(query, limit)
- memory_delete(key)
- memory_list_all()
```

**Implementation Pattern**:
```typescript
import { createHash } from 'crypto';
import fs from 'fs/promises';

class MemoryStore {
  constructor(private dataPath: string) {}

  async store(key: string, value: any, metadata?: any) {
    const entry = {
      key,
      value,
      metadata,
      timestamp: Date.now(),
      hash: createHash('sha256').update(JSON.stringify(value)).digest('hex')
    };

    await fs.writeFile(
      `${this.dataPath}/${key}.json`,
      JSON.stringify(entry, null, 2)
    );

    return entry;
  }

  async retrieve(key: string) {
    const data = await fs.readFile(`${this.dataPath}/${key}.json`, 'utf-8');
    return JSON.parse(data);
  }

  async search(query: string, limit: number = 10) {
    const files = await fs.readdir(this.dataPath);
    const memories = await Promise.all(
      files.map(f => this.retrieve(f.replace('.json', '')))
    );

    // Simple keyword search (production would use vector embeddings)
    return memories
      .filter(m => JSON.stringify(m.value).toLowerCase().includes(query.toLowerCase()))
      .slice(0, limit);
  }
}
```

**Agent Usage**:
```
Agent: I need to remember user preferences
Agent calls: memory_store("user_prefs", { theme: "dark", lang: "en" })

... later session ...

Agent: What were the user preferences?
Agent calls: memory_retrieve("user_prefs")
Response: { theme: "dark", lang: "en" }
```

### Example 3: Multi-Layer Integration Pattern

**Pattern**: Fallback layers for reliability

```typescript
// From linear-claude-skill
class LinearClient {
  async createIssue(title: string, description: string) {
    // Layer 1: Try MCP tool (fastest)
    try {
      return await mcp.call('linear_create_issue', { title, description });
    } catch (error) {
      // Layer 2: Try SDK (more reliable)
      try {
        return await linearSDK.issues.create({ title, description });
      } catch (sdkError) {
        // Layer 3: Try GraphQL (most comprehensive)
        return await this.graphQLQuery(`
          mutation { issueCreate(input: { title: "${title}", description: "${description}" }) { issue { id } } }
        `);
      }
    }
  }
}
```

---

## Key Takeaways

1. **Prioritize comprehensive API coverage** over convenience workflows
2. **Tool naming matters** - Use consistent prefixes and action-oriented names
3. **Actionable error messages** - Tell agents how to fix problems
4. **Evaluation-driven development** - 10 complex questions test effectiveness
5. **TypeScript recommended** - Best SDK support and static typing
6. **Stateless HTTP for remote** - Easier to scale than stateful connections
7. **Progressive disclosure** - Concise descriptions, detailed only when needed
8. **Multi-layer fallback** - MCP → SDK → GraphQL for reliability

**MCP servers are the foundation for capable, tool-using agents. Invest in quality implementation.**
