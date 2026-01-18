# MCP-Launchpad - Curated MCP Server Catalog for Agentic Workflows

**Reference**: `references/MCP-Launchpad/`
**Source**: https://github.com/LNDMN/MCP-Launchpad
**Standard**: [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)

## Overview

MCP-Launchpad is a **comprehensive, curated catalog of 200+ MCP (Model Context Protocol) servers** optimized for Docker deployment and AI agent integration. It provides standardized, production-ready tools that agents like Claude Code can use to interact with external systems, databases, APIs, and services.

## Why MCP-Launchpad for Agentic Workflows?

MCP servers are the **tool layer** for AI agents. They enable agents to:
- **Execute code** in sandboxed environments
- **Query databases** (PostgreSQL, MongoDB, SQLite, etc.)
- **Access web services** (GitHub, Slack, Google, AWS, etc.)
- **Process files** (PDFs, images, documents)
- **Search the web** (Brave, Tavily, Exa)
- **Manage memory** (persistent storage across sessions)
- **Communicate** (email, SMS, webhooks)
- **Automate browsers** (Playwright, Puppeteer)

This catalog is essential for building capable agentic systems with real-world tool access.

## Key Features

### 1. Docker-First Deployment

All servers follow a standardized Docker deployment pattern:

```yaml
mcp-server-name:
  image: mcp/server-name:latest
  environment:
    - API_KEY=${API_KEY}
  volumes:
    - ./config:/config
  restart: unless-stopped
```

**Benefits**:
- Consistent deployment across all servers
- Isolated environments for security
- Easy scaling and orchestration
- Reproducible setups

### 2. A2A (Agent-to-Agent) Compatibility

Servers support agent-to-agent communication standard, enabling:
- Agents to call other agents as tools
- Multi-agent orchestration
- Distributed agentic systems
- Agent marketplaces

### 3. Standardized Documentation

Each server includes:
- Clear purpose and use cases
- Configuration examples
- Tool/resource listings
- Integration guides
- Security considerations

### 4. Implementation Templates

MCP-Launchpad provides templates for building new MCP servers:
- Project structure
- Docker configuration
- Testing frameworks
- Documentation standards
- Deployment checklists

---

## MCP Server Categories (200+ Servers)

### 1. Aggregator (Multi-Tool Platforms)

**Purpose**: Servers that provide multiple related tools in one package

**Key Servers**:
- **everything-mcp**: Comprehensive toolkit with 50+ tools
- **mcp-bundle**: Curated collection of essential tools
- **universal-mcp**: General-purpose server suite

**Use Cases**:
- Rapid prototyping without multiple server setup
- Development environments
- All-in-one agent deployments

---

### 2. Art & Culture

**Purpose**: Access to museums, galleries, and cultural institutions

**Key Servers**:
- **rijksmuseum-mcp**: Access to Rijksmuseum collection API
- **met-museum-mcp**: Metropolitan Museum of Art API
- **smithsonian-mcp**: Smithsonian Institution APIs

**Use Cases**:
- Art analysis agents
- Cultural research
- Educational applications
- Image dataset curation

---

### 3. Browser Automation

**Purpose**: Programmatic web browser control and interaction

**Key Servers**:
- **playwright-mcp**: Playwright-based browser automation
- **puppeteer-mcp**: Puppeteer browser control
- **browserbase-mcp**: Cloud browser automation

**Use Cases**:
- Web scraping agents
- Testing and QA automation
- Form filling and submission
- Screenshot and PDF generation
- Dynamic content extraction

**Example Tools**:
```javascript
// Playwright MCP tools
- playwright_navigate(url)
- playwright_click(selector)
- playwright_screenshot(options)
- playwright_fill(selector, value)
- playwright_evaluate(script)
```

---

### 4. Cloud Platforms

**Purpose**: Integration with cloud service providers

**Key Servers**:
- **aws-mcp**: AWS services (S3, EC2, Lambda, etc.)
- **gcp-mcp**: Google Cloud Platform APIs
- **azure-mcp**: Microsoft Azure services
- **cloudflare-mcp**: Cloudflare API access

**Use Cases**:
- Cloud infrastructure management agents
- Deployment automation
- Resource monitoring
- Cost optimization

---

### 5. Code Execution

**Purpose**: Safe, sandboxed code execution environments

**Key Servers**:
- **e2b-mcp**: Secure code sandbox
- **riza-mcp**: Isolated JavaScript/Python execution
- **eval-mcp**: Multi-language code evaluation

**Use Cases**:
- Code generation and testing agents
- Interactive programming assistants
- Algorithm validation
- Educational coding environments

**Security**: All servers use isolated containers/VMs to prevent malicious code execution

---

### 6. Coding Agents

**Purpose**: Specialized agents for software development tasks

**Key Servers**:
- **github-mcp**: GitHub API integration (repos, PRs, issues)
- **gitlab-mcp**: GitLab API access
- **linear-mcp**: Linear issue tracking
- **sentry-mcp**: Error monitoring integration

**Use Cases**:
- Automated code reviews
- Issue triage and management
- CI/CD pipeline orchestration
- Deployment automation

**GitHub MCP Tools**:
```
- create_repository(name, description, private)
- create_pull_request(repo, title, body, base, head)
- list_issues(repo, state, labels)
- create_issue(repo, title, body)
- search_code(query, language)
- get_file_contents(repo, path)
```

---

### 7. Command Line

**Purpose**: Shell command execution and system interaction

**Key Servers**:
- **bash-mcp**: Safe bash command execution
- **shell-mcp**: Cross-platform shell access
- **ssh-mcp**: Remote SSH command execution

**Use Cases**:
- System administration agents
- DevOps automation
- File system operations
- Process management

**Security Note**: Requires careful sandboxing and permission management

---

### 8. Communication

**Purpose**: Email, messaging, and notification services

**Key Servers**:
- **slack-mcp**: Slack API integration
- **email-mcp**: SMTP/IMAP email access
- **twilio-mcp**: SMS and voice communication
- **discord-mcp**: Discord bot integration

**Use Cases**:
- Notification agents
- Chatbot backends
- Customer support automation
- Team collaboration tools

---

### 9. Databases

**Purpose**: Database query and management tools

**Key Servers**:
- **postgres-mcp**: PostgreSQL integration
- **mongodb-mcp**: MongoDB access
- **sqlite-mcp**: SQLite database operations
- **mysql-mcp**: MySQL/MariaDB integration
- **redis-mcp**: Redis cache operations

**Use Cases**:
- Data analysis agents
- Database administration automation
- Query generation and optimization
- Data migration tools

**PostgreSQL MCP Tools**:
```sql
-- Tools available
- query(sql, params)
- list_tables()
- describe_table(table_name)
- create_table(definition)
- insert(table, data)
- update(table, data, where)
```

---

### 10. Date & Time

**Purpose**: Time zone handling, date calculations, scheduling

**Key Servers**:
- **time-mcp**: World clock and time zone conversions
- **calendar-mcp**: Calendar operations
- **worldtime-mcp**: Global time data

**Use Cases**:
- Scheduling agents
- Time zone coordination
- Date calculations
- Calendar management

---

### 11. Developer Tools

**Purpose**: Development utilities and productivity tools

**Key Servers**:
- **docker-mcp**: Docker container management
- **git-mcp**: Git operations
- **npm-mcp**: npm package management
- **jq-mcp**: JSON query and manipulation

**Use Cases**:
- Development workflow automation
- Package dependency management
- Container orchestration
- Version control operations

---

### 12. Ecommerce

**Purpose**: Online shopping and payment platform integrations

**Key Servers**:
- **shopify-mcp**: Shopify API access
- **stripe-mcp**: Payment processing
- **square-mcp**: Square payments and POS

**Use Cases**:
- E-commerce automation agents
- Order processing
- Inventory management
- Payment reconciliation

---

### 13. File Operations

**Purpose**: File reading, writing, and manipulation

**Key Servers**:
- **filesystem-mcp**: Local file system access
- **pdf-mcp**: PDF reading and generation
- **csv-mcp**: CSV parsing and creation
- **image-mcp**: Image processing and manipulation

**Use Cases**:
- Document processing agents
- File organization automation
- Data extraction from files
- Report generation

**PDF MCP Tools**:
```
- extract_text(pdf_path)
- extract_images(pdf_path)
- create_pdf(content, output_path)
- merge_pdfs(pdf_paths, output_path)
- split_pdf(pdf_path, pages)
```

---

### 14. Finance & Crypto

**Purpose**: Financial data and cryptocurrency services

**Key Servers**:
- **coinbase-mcp**: Cryptocurrency data
- **alpaca-mcp**: Stock trading API
- **plaid-mcp**: Banking data aggregation

**Use Cases**:
- Trading bots
- Portfolio management agents
- Financial analysis
- Market monitoring

---

### 15. IoT & Hardware

**Purpose**: Internet of Things and hardware device control

**Key Servers**:
- **homeassistant-mcp**: Home Assistant integration
- **mqtt-mcp**: MQTT protocol support
- **arduino-mcp**: Arduino device control

**Use Cases**:
- Home automation agents
- IoT device orchestration
- Sensor data collection
- Smart device control

---

### 16. Knowledge & Reference

**Purpose**: Access to wikis, encyclopedias, and reference materials

**Key Servers**:
- **wikipedia-mcp**: Wikipedia API
- **wolfram-mcp**: Wolfram Alpha computational engine

**Use Cases**:
- Research agents
- Fact-checking
- Educational assistants
- Knowledge base integration

---

### 17. Machine Learning

**Purpose**: ML model inference and training tools

**Key Servers**:
- **huggingface-mcp**: Hugging Face model access
- **replicate-mcp**: Replicate AI model API
- **elevenlabs-mcp**: Text-to-speech generation

**Use Cases**:
- Multi-modal AI agents
- Model chaining pipelines
- Voice synthesis
- Image generation automation

---

### 18. Memory & Storage

**Purpose**: Persistent memory and state management for agents

**Key Servers**:
- **memory-mcp**: ⭐ **100% Complete** - First production-ready server
- **qdrant-mcp**: Vector database for semantic search
- **chromadb-mcp**: Embedding storage

**Use Cases**:
- Long-term agent memory
- Session persistence across conversations
- Context retrieval
- Knowledge base for agents

**Memory MCP Tools** (First Complete Server):
```javascript
// Store and retrieve agent memories
- store_memory(key, value, metadata)
- retrieve_memory(key)
- search_memories(query, limit)
- delete_memory(key)
- list_all_memories()
```

**Implementation Status**: ✅ Fully implemented, tested, and documented
**Priority**: Highest - foundational for stateful agents

---

### 19. Music & Audio

**Purpose**: Music services and audio processing

**Key Servers**:
- **spotify-mcp**: Spotify API integration
- **audio-processing-mcp**: Audio analysis and manipulation

**Use Cases**:
- Music recommendation agents
- Playlist management
- Audio transcription
- Sound analysis

---

### 20. News & Media

**Purpose**: News aggregation and media content access

**Key Servers**:
- **news-api-mcp**: News API integration
- **rss-mcp**: RSS feed parsing

**Use Cases**:
- News aggregation agents
- Content curation
- Media monitoring
- Trend analysis

---

### 21. Productivity

**Purpose**: Task management and productivity tools

**Key Servers**:
- **notion-mcp**: Notion API integration
- **todoist-mcp**: Todoist task management
- **google-drive-mcp**: Google Drive file access
- **obsidian-mcp**: Obsidian vault operations

**Use Cases**:
- Personal assistant agents
- Task automation
- Note-taking and organization
- Document management

---

### 22. Search

**Purpose**: Web search and information retrieval

**Key Servers**:
- **brave-search-mcp**: Brave Search API
- **tavily-mcp**: Tavily AI search
- **exa-mcp**: Exa semantic search
- **perplexity-mcp**: Perplexity AI search

**Use Cases**:
- Research agents
- Web content discovery
- Fact verification
- Competitive intelligence

**Brave Search Tools**:
```
- web_search(query, count, offset)
- image_search(query, count)
- news_search(query, freshness)
- local_search(query, location)
```

---

### 23. Social Media

**Purpose**: Social platform integration and automation

**Key Servers**:
- **twitter-mcp**: Twitter/X API
- **linkedin-mcp**: LinkedIn integration
- **reddit-mcp**: Reddit API access

**Use Cases**:
- Social media management agents
- Content posting automation
- Sentiment analysis
- Engagement monitoring

---

### 24. Travel & Mapping

**Purpose**: Maps, navigation, and travel services

**Key Servers**:
- **googlemaps-mcp**: Google Maps API
- **amadeus-mcp**: Flight and hotel booking

**Use Cases**:
- Travel planning agents
- Route optimization
- Location-based services
- Trip coordination

---

### 25. Weather

**Purpose**: Weather data and forecasting

**Key Servers**:
- **openweathermap-mcp**: Weather API
- **weather-gov-mcp**: NOAA weather data

**Use Cases**:
- Weather monitoring agents
- Climate analysis
- Agricultural planning
- Event scheduling

---

## Installation & Deployment

### Prerequisites

1. **Docker & Docker Compose** installed
2. **Claude Code** or MCP-compatible client
3. **API Keys** for specific services (as needed)

### Basic Setup

1. **Clone MCP-Launchpad**:
```bash
# Already cloned in references
cd references/MCP-Launchpad
```

2. **Choose Servers to Deploy**:
Review the catalog and select servers relevant to your agentic workflow needs.

3. **Docker Compose Example**:
```yaml
version: '3.8'

services:
  memory-mcp:
    image: mcp/memory:latest
    environment:
      - STORAGE_PATH=/data/memories
    volumes:
      - ./data/memories:/data/memories
    restart: unless-stopped
    ports:
      - "8001:8001"

  github-mcp:
    image: mcp/github:latest
    environment:
      - GITHUB_TOKEN=${GITHUB_TOKEN}
    restart: unless-stopped
    ports:
      - "8002:8002"

  postgres-mcp:
    image: mcp/postgres:latest
    environment:
      - POSTGRES_CONNECTION_STRING=${DATABASE_URL}
    restart: unless-stopped
    ports:
      - "8003:8003"
```

4. **Configure Claude Code**:
Add MCP servers to `.mcp.json`:
```json
{
  "mcpServers": {
    "memory": {
      "url": "http://localhost:8001"
    },
    "github": {
      "url": "http://localhost:8002"
    },
    "postgres": {
      "url": "http://localhost:8003"
    }
  }
}
```

5. **Deploy**:
```bash
docker-compose up -d
```

---

## Priority Implementation Plan

MCP-Launchpad includes a **prioritized rollout plan** for implementing the 200+ servers:

### Phase 1: Core Infrastructure (High Priority)
1. ✅ **Memory Storage MCP** - 100% Complete
2. Code Execution (e2b, riza)
3. File Operations (filesystem, pdf, csv)
4. Database (postgres, sqlite)

### Phase 2: Developer Tools (High Priority)
5. GitHub MCP
6. Docker MCP
7. Git MCP
8. Shell/Bash MCP

### Phase 3: External Services (Medium Priority)
9. Search (Brave, Tavily)
10. Communication (Slack, Email)
11. Cloud Platforms (AWS, GCP)

### Phase 4: Specialized Tools (Lower Priority)
12. Browser Automation
13. Social Media
14. E-commerce
15. IoT/Hardware

---

## Building Custom MCP Servers

MCP-Launchpad provides templates and checklists for creating new servers:

### Implementation Checklist

```markdown
- [ ] Define server purpose and scope
- [ ] Choose base technology (Node.js, Python, etc.)
- [ ] Implement MCP protocol handlers
- [ ] Create Docker container
- [ ] Write comprehensive documentation
- [ ] Add configuration examples
- [ ] Implement error handling
- [ ] Add logging and monitoring
- [ ] Create integration tests
- [ ] Document security considerations
- [ ] Submit to MCP-Launchpad catalog
```

### Server Structure Template

```
mcp-server-name/
├── Dockerfile
├── docker-compose.yml
├── README.md
├── src/
│   ├── index.ts
│   ├── tools/
│   │   ├── tool1.ts
│   │   └── tool2.ts
│   └── resources/
│       └── resource1.ts
├── tests/
│   └── integration.test.ts
└── examples/
    └── config.json
```

---

## Integration with Agentic Workflows

### Use Case 1: Memory-Enabled Agent

```javascript
// Agent with persistent memory across sessions
const agent = {
  name: "ResearchAssistant",
  tools: [
    "memory-mcp",      // Store findings
    "brave-search-mcp", // Web research
    "notion-mcp"        // Save to knowledge base
  ],

  workflow: async (query) => {
    // Retrieve relevant past research
    const context = await memory.search_memories(query, 5);

    // Perform new research
    const results = await brave_search(query);

    // Store new findings
    await memory.store_memory(query, results, {
      timestamp: Date.now(),
      topic: "research"
    });

    // Save to Notion
    await notion.create_page(query, results);
  }
};
```

### Use Case 2: Multi-Tool Development Agent

```javascript
// Agent with full development stack access
const devAgent = {
  name: "FullStackDeveloper",
  tools: [
    "github-mcp",      // Code repositories
    "postgres-mcp",    // Database access
    "docker-mcp",      // Container management
    "e2b-mcp",         // Code execution
    "slack-mcp"        // Team notifications
  ],

  workflow: async (task) => {
    // Check existing code
    const codebase = await github.search_code(task.keywords);

    // Generate and test solution
    const solution = await generateCode(task, codebase);
    const testResults = await e2b.execute(solution.tests);

    // Deploy if tests pass
    if (testResults.passed) {
      await github.create_pull_request(solution);
      await docker.deploy(solution.service);
      await slack.notify("Deployment successful");
    }
  }
};
```

### Use Case 3: Data Analysis Pipeline

```javascript
// Agent with data access and processing tools
const dataAgent = {
  name: "DataAnalyst",
  tools: [
    "postgres-mcp",    // Query databases
    "csv-mcp",         // Export results
    "google-drive-mcp", // Store reports
    "email-mcp"        // Send notifications
  ],

  workflow: async (analysisRequest) => {
    // Query data
    const data = await postgres.query(analysisRequest.sql);

    // Process and export
    const report = await analyzeData(data);
    const csvFile = await csv.create(report);

    // Store and notify
    await googleDrive.upload(csvFile, "Reports/");
    await email.send({
      to: analysisRequest.stakeholders,
      subject: "Analysis Complete",
      attachments: [csvFile]
    });
  }
};
```

---

## Security Considerations

### 1. API Key Management
- Store keys in environment variables
- Use Docker secrets for production
- Never commit keys to repositories
- Rotate keys regularly

### 2. Network Isolation
- Run MCP servers in isolated Docker networks
- Use firewall rules to restrict access
- Implement rate limiting
- Monitor for unusual activity

### 3. Code Execution Safety
- Always use sandboxed environments (e2b, riza)
- Set resource limits (CPU, memory, time)
- Validate inputs before execution
- Log all execution attempts

### 4. Data Privacy
- Encrypt sensitive data at rest
- Use TLS for all network communication
- Implement proper access controls
- Regular security audits

---

## Testing MCP Servers

### 1. Health Check
```bash
curl http://localhost:8001/health
```

### 2. List Available Tools
```bash
curl http://localhost:8001/tools
```

### 3. Test Tool Invocation
```bash
curl -X POST http://localhost:8001/tools/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "memory_store",
    "arguments": {
      "key": "test",
      "value": "Hello, MCP!"
    }
  }'
```

---

## Resources

- **MCP-Launchpad Repository**: `references/MCP-Launchpad/`
- **Model Context Protocol Spec**: https://modelcontextprotocol.io/
- **Docker Documentation**: https://docs.docker.com/
- **A2A Specification**: Agent-to-Agent communication standard
- **MCP Server Template**: `references/MCP-Launchpad/templates/`

---

## Key Takeaways

1. **200+ Production-Ready Servers**: Comprehensive tool catalog for any agentic use case
2. **Docker-First**: Standardized deployment across all servers
3. **Memory MCP First**: Foundation for stateful agents (100% complete)
4. **A2A Compatible**: Enables agent-to-agent communication
5. **Extensible**: Template-driven approach for building custom servers
6. **Security-Focused**: Sandboxed execution and proper isolation
7. **Well-Documented**: Each server includes complete usage guides

---

**MCP-Launchpad is the essential tool catalog for building production-ready agentic systems. Start with Memory MCP for persistent agent state, then expand to domain-specific servers as needed.**
