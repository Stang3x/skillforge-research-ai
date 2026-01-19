# skillforge-research-ai
Modular AI research agent with mock web search, finding synthesis, citation generation (APA/MLA/Chicago), and pluggable skills system. Includes local testing stubs and async CLI interface.
# Research Assistant Agent

A conversational AI research assistant built with the Microsoft Agent Framework using GitHub Models. The assistant can help you search for information, synthesize research findings, and provide proper citations.

## Features

- **Web Search**: Search for information on topics using the search_web tool
- **Research Synthesis**: Synthesize findings from multiple sources
- **Citation Generation**: Generate citations in APA, MLA, or Chicago format
- **Conversation Threading**: Maintains context across multiple turns for coherent research discussions
- **Streaming Responses**: Real-time streaming of agent responses

## Prerequisites

- Python 3.8+
- A GitHub account with access to GitHub Models
- A GitHub Personal Access Token (PAT) with appropriate permissions

## Setup

### 1. Clone or navigate to the project directory
```bash
cd research-assistant
```

### 2. Create a Python virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Copy `.env.example` to `.env` and update it with your credentials:
```bash
cp .env.example .env
```

Edit `.env` and add:
```
GITHUB_TOKEN=your_github_personal_access_token
MODEL_ID=openai/gpt-4o-mini  # or other available models
```

### 5. Get your GitHub Personal Access Token
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Click "Generate new token (classic)"
3. Give it a descriptive name
4. Select appropriate scopes (at minimum `read:user`)
5. Copy the token and paste it into your `.env` file

## Usage

Run the research assistant:
```bash
python research_assistant.py
```

### Example Interactions

```
You: What is machine learning?
ResearchAssistant: Machine learning is a subset of artificial intelligence...

You: Can you synthesize the key findings about machine learning?
ResearchAssistant: Based on current research, machine learning is an important area...

You: Provide a citation in APA format
ResearchAssistant: Citation example: Smith, J., & Johnson, K. (2024)...

You: exit
```

## Architecture

### Tools

The agent has access to three main tools:

1. **search_web(query)**: Searches for information about a topic
2. **synthesize_findings(topic, sources)**: Synthesizes research findings
3. **cite_sources(topic, style)**: Generates citations in different formats

### Agent Flow

1. User asks a research question
2. Agent processes the query using available tools
3. Agent streams response in real-time
4. Context is maintained in the thread for follow-up questions

## Available Models

The agent supports all GitHub models, including:
- `openai/gpt-4o` - Most capable
- `openai/gpt-4o-mini` - Faster, cost-effective
- `meta/llama-3.1-8b-instruct` - Open source
- `meta/llama-3.3-70b-instruct` - Larger open source
- And many more...

## Extending the Agent

### Adding New Tools

To add a new research tool, define a function with proper type annotations:

```python
def your_new_tool(
    param: Annotated[str, "Description of parameter."],
) -> str:
    """Tool description."""
    # Implementation
    return result

# Add to tools list in main()
tools = [search_web, synthesize_findings, cite_sources, your_new_tool]
```

### Modifying Instructions

Update the agent instructions in the `main()` function to customize behavior:

```python
agent = ChatAgent(
    chat_client=chat_client,
    name="ResearchAssistant",
    instructions="Your custom instructions here...",
    tools=tools,
)
```

## Limitations

- The search_web tool uses mock data for demonstration
- For production use, integrate with real search APIs (Google Custom Search, Bing Search API, etc.)
- Response quality depends on the selected model

## Next Steps

1. Integrate with real search APIs (Google, Bing, or academic databases)
2. Add database integration for caching research results
3. Implement multi-agent patterns for specialized research domains
4. Add persistent storage for research sessions
5. Enhance tool capabilities with web scraping and PDF analysis

## Support

For issues or questions:
- Check the [Microsoft Agent Framework documentation](https://github.com/microsoft/agent-framework)
- Review [GitHub Models documentation](https://github.com/marketplace/models)
