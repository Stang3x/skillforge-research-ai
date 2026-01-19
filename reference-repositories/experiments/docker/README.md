# Research Assistant - Docker Deployment

Multi-agent research system with Semantic Scholar integration, packaged for easy deployment.

## Quick Start

### 1. Configure Environment

```bash
cd experiments/docker
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 2. Build and Run

**Option A: Docker Compose (Recommended)**
```bash
# Interactive mode
docker-compose run --rm research-assistant

# Or start in background
docker-compose up -d
docker-compose exec research-assistant bash
```

**Option B: Docker directly**
```bash
# Build
docker build -t research-assistant -f docker/Dockerfile ..

# Run
docker run -it \
  -e ANTHROPIC_API_KEY=your-key-here \
  -v research-data:/app/data \
  research-assistant
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Your Anthropic Claude API key |
| `SEMANTIC_SCHOLAR_API_KEY` | No | Higher rate limits for Semantic Scholar |
| `LOCAL_PDF_DIR` | No | Mount local PDFs directory |
| `LOCAL_EXPORT_DIR` | No | Mount local exports directory |

## Data Persistence

Research data is stored in a Docker volume:

```bash
# View volume
docker volume inspect research-assistant-data

# Backup data
docker run --rm \
  -v research-assistant-data:/data \
  -v $(pwd):/backup \
  alpine tar cvf /backup/research-backup.tar /data

# Restore data
docker run --rm \
  -v research-assistant-data:/data \
  -v $(pwd):/backup \
  alpine tar xvf /backup/research-backup.tar -C /
```

## Features

- **Multi-agent system**: Coordinator, Researcher, Analyst, Writer
- **Knowledge sources**: arXiv, Wikipedia, GitHub, HackerNews, Stack Overflow, Semantic Scholar
- **Exports**: Markdown, PDF, Obsidian vault format
- **Caching**: API response caching to reduce costs
- **Token tracking**: Monitor usage and costs

## Commands

Once inside the container:

```
# Research queries (uses multi-agent system)
> What is machine learning?

# Direct Semantic Scholar search
> scholar transformer attention

# Get paper details
> paper arXiv:2106.09685

# Search authors
> author Yoshua Bengio

# Export notes
> export           # Markdown
> export pdf       # PDF
> obsidian         # Obsidian vault

# View stats
> tokens           # Token usage
> stats            # Cache stats
> notes            # Session notes

# Exit
> quit
```

## Troubleshooting

### API Key Error
```
ERROR: ANTHROPIC_API_KEY is not set!
```
Solution: Create `.env` file with your API key or pass via `-e` flag.

### Rate Limiting
```
Semantic Scholar API rate limit reached
```
Solution: Get a free API key from [Semantic Scholar](https://www.semanticscholar.org/product/api#api-key-form).

### Permission Denied
```
Permission denied: /app/data/...
```
Solution: The container runs as non-root user. Ensure mounted volumes have correct permissions.

## Resource Limits

Default limits in docker-compose.yml:
- CPU: 2 cores max, 0.5 reserved
- Memory: 2GB max, 512MB reserved

Adjust in `docker-compose.yml` under `deploy.resources`.

## Architecture

```
┌─────────────────────────────────────────┐
│           Docker Container              │
│  ┌───────────────────────────────────┐  │
│  │     Research Assistant v17        │  │
│  │  ┌─────────┐  ┌─────────────────┐ │  │
│  │  │ Agents  │  │ Knowledge APIs  │ │  │
│  │  └─────────┘  └─────────────────┘ │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │    Export Manager           │  │  │
│  │  │ (MD, PDF, Obsidian)         │  │  │
│  │  └─────────────────────────────┘  │  │
│  └───────────────────────────────────┘  │
│           │                             │
│  ┌────────▼────────┐                    │
│  │  /app/data      │ ← Docker Volume    │
│  │  (persistent)   │                    │
│  └─────────────────┘                    │
└─────────────────────────────────────────┘
```

## License

MIT License - See main repository for details.
